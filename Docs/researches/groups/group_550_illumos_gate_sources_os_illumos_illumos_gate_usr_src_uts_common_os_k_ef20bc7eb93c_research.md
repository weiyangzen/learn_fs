# Group Research: group_550_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_k_ef20bc7eb93c

Scope: `Docs/research_subset_a.md`
Source tree: `sources/os/illumos/illumos-gate`
Files researched: 4

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kmem.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kmem.c

## Purpose

`kmem.c` implements the illumos kernel memory allocator: Bonwick slab caches, per-CPU magazines, vmem-backed heap arenas, allocator debugging, allocation logs, cache kstats, low-memory reaping, crash-dump-safe allocation diversion, and slab consolidation by object move callbacks.

Read completely: 5,459 lines.

## Main Responsibilities

- Provides the public kernel allocation interfaces: `kmem_alloc()`, `kmem_zalloc()`, `kmem_free()`, `kmem_rezalloc()`, `kmem_cache_create()`, `kmem_cache_destroy()`, `kmem_cache_alloc()`, and `kmem_cache_free()`.
- Builds size-indexed allocation caches for normal `kmem_alloc()` requests and routes oversize allocations to `kmem_oversize_arena`.
- Manages slab lifecycle: creates slabs from a cache vmem arena, carves buffers, tracks allocated buffers through embedded or hashed bufctls, and returns empty slabs to vmem.
- Implements per-CPU magazine fast paths plus central full/empty depots for scalable allocation and free.
- Supports allocator diagnostics: redzones, deadbeef/freed patterns, buftags, transaction/content/failure/slab/zero-size logs, stack capture, corruption classification, and panic/debug-entry policy.
- Publishes per-cache kstats and heap availability helpers.
- Reaps caches under memory pressure and periodically resizes hash tables, grows magazine sizes on contention, and scans for fragmentation.
- Supports the slab consolidator, where clients may register move callbacks so kmem can relocate live objects off sparse slabs.
- Diverts allocations during crash dumps to pre-reserved dump-safe memory so heap state remains stable while dumping.
- Initializes the allocator across boot phases, after `/etc/system` tunables are read, and starts maintenance taskqs and periodic update callbacks.

## Important Data Structures And Globals

- `kmem_cache_t`: cache descriptor containing object size/alignment, flags, vmem source, constructors/destructors, slab lists, per-CPU caches, depot lists, hash table, kstat, and optional defrag state.
- `kmem_slab_t`: slab descriptor with cache pointer, free buffer head, base address, chunk/ref counts, partial-slab ordering flags, and consolidator state.
- `kmem_bufctl_t` / `kmem_bufctl_audit_t`: buffer control metadata; audit form records timestamp, thread, stack, content snapshot pointer, cache, slab, and address.
- `kmem_magazine_t`, `kmem_magtype_t`, `kmem_cpu_cache_t`, and `kmem_maglist_t`: magazine-layer objects for CPU-local and depot caching.
- `kmem_defrag_t` and `kmem_move_t`: per-cache consolidation state and pending move callback records.
- `kmem_alloc_table` and `kmem_big_alloc_table`: lookup tables mapping request sizes to backing `kmem_alloc_*` caches.
- Global arenas: `kmem_metadata_arena`, `kmem_msb_arena`, `kmem_cache_arena`, `kmem_hash_arena`, `kmem_log_arena`, `kmem_oversize_arena`, `kmem_va_arena`, `kmem_default_arena`, and firewall arenas.
- Global taskqs: `kmem_taskq` for maintenance/reaping and `kmem_move_taskq` for serialized client move callbacks.

## Slab Layer

`kmem_slab_create()` allocates a slab from the cache arena, initializes it with the uninitialized pattern unless the cache is `KMC_NOTOUCH`, creates slab/bufctl metadata, sets optional redzones and free patterns, and links all buffers onto the slab free list. For hashed caches, slab and bufctl metadata are allocated from metadata caches; for compact no-hash caches, metadata is embedded in the slab/buffer layout.

`kmem_slab_alloc()` selects the first partial slab or creates a new one, removes one raw buffer, updates allocation counters, inserts hashed bufctls into the allocated-address hash table, and moves slabs between partial and complete lists. New slabs may be prefilled into magazines when the cache permits it.

`kmem_slab_free()` reverses the process: it finds and validates the buffer, updates audit/logging state, returns the buffer to the slab free list, moves complete slabs back to partial state, and destroys empty slabs. If move callbacks are pending, empty slabs are placed on a defrag deadlist rather than immediately unmapped, preserving the contract that callback buffers remain backed by memory touched only by kmem or the client.

## Magazine And Depot Layer

`kmem_cache_alloc()` first attempts the current CPU's loaded magazine, then the previous magazine, then a full depot magazine, and finally the slab layer. `kmem_cache_free()` mirrors this by returning to the loaded magazine, swapping with an empty previous magazine, obtaining/creating empty depot magazines, or falling through to slab free.

The depot tracks full and empty magazine working sets. `kmem_depot_ws_update()` snapshots minimum occupancy, `kmem_depot_ws_zero()` marks everything reapable, and `kmem_depot_ws_reap()` destroys magazines that fall outside the working set. Magazine size can grow when depot lock contention exceeds `kmem_depot_contention`.

## Debugging And Corruption Detection

Debug modes are controlled by `kmem_flags` and cache creation flags. They add combinations of:

- `KMF_AUDIT`: transaction stack/time logging.
- `KMF_DEADBEEF`: free-pattern verification and poisoning.
- `KMF_REDZONE`: write-past-end detection.
- `KMF_CONTENTS`: saved content snapshots.
- `KMF_LITE`: lower-overhead buftag history.
- `KMF_FIREWALL`: hardware-unmapped page after selected large buffers.

`kmem_error()` classifies allocator failures such as modified free buffers, redzone violations, duplicate frees, bad addresses, corrupted buftags/bufctls, wrong-cache frees, wrong-size frees, and bad base addresses. It records `kmem_panic_info`, prints diagnostic context, emits previous transaction stacks when available, then panics or enters the debugger depending on `kmem_panic`.

`kmem_alloc()` and `kmem_free()` store and validate the original requested size for debug-backed generic allocations, so freeing a cached buffer with the wrong size is reported separately from redzone corruption.

## Reaping And Maintenance

`kmem_reap()` and `kmem_reap_idspace()` throttle and dispatch asynchronous cache reaping. The memory-backed reap path asks each cache's owner reclaim callback for memory, reaps depot magazines, and invokes defrag if enabled. The identifier-space path limits work to caches backed by identifier arenas.

Periodic `kmem_update()` walks all caches and may dispatch:

- hash-table rescale work when allocated-buffer count diverges from hash size,
- magazine resize work when depot contention rises,
- slab-consolidator scans for movable caches.

`kmem_cache_reap_soon()` is a targeted API that zeroes one cache's depot working set and schedules a depot reap without waiting for completion.

## Slab Consolidator

The opening theory statement and implementation define cooperative defragmentation. Clients call `kmem_cache_set_move()` before allocation to install a move callback. Kmem then identifies sparse partial slabs and asks the client to move live objects to destination buffers that kmem has already allocated and constructed.

Client callback responses drive cleanup:

- `KMEM_CBRC_YES`: client moved the object; kmem frees the old buffer.
- `KMEM_CBRC_NO`: client refuses permanently; kmem frees the new buffer and marks the source slab non-movable until the stuck object is freed or notification clears it.
- `KMEM_CBRC_LATER`: temporary refusal; after repeated disbelief the slab is treated as non-movable.
- `KMEM_CBRC_DONT_NEED`: client discards the old object; kmem frees both buffers.
- `KMEM_CBRC_DONT_KNOW`: client cannot safely recognize the object; kmem frees the new buffer and relies on reaping/magazine draining.

`kmem_move_buffers()` scans backward from the least-used partial slabs, issues move requests while carefully dropping `cache_lock`, and uses `KMEM_SLAB_MOVE_PENDING` plus the deadlist to prevent slab destruction races. `kmem_cache_move_notify()` lets clients later report that a previously stuck object may now be movable.

## Initialization And Boot Phases

`kmem_init()` starts by initializing kstats and metadata arenas, creates a temporary allocator so `/etc/system` tunables can be read, destroys the temporary caches, then recreates arenas/caches with final tunables. It chooses large-page heap backing when appropriate, configures firewall thresholds, initializes logs, STREAMS messages, zones ZSD, taskq/logging, platform aligned allocation, ID caches, and netstack hooks.

`kmem_thread_init()` creates the move taskq and maintenance taskq. `kmem_mp_init()` registers CPU setup callbacks, starts periodic update scheduling, and finishes taskq MP initialization. `kmem_cpu_setup()` purges and re-enables magazines on CPU unconfiguration to keep per-CPU cache state valid.

## Crash Dump Allocation Diversion

`kmem_dump_init()` reserves a heap area for dump-time allocations. `kmem_dump_begin()` marks caches as dump-divertible or dump-unsafe based on their arena flags, disables current magazine rounds on the dumping CPU, and routes eligible allocations through `kmem_cache_alloc_dump()`. `kmem_cache_free_dump()` recycles constructed dump buffers in a simple freelist or suppresses normal frees while the reserved area is available. `kmem_dump_finish()` reports reserved-area exhaustion and optional usage statistics.

## Notable Risks And Invariants

- The allocator relies on strict lock ordering: per-cache locks, per-CPU locks, depot locks, global cache linkage, and taskq serialization are carefully separated.
- Cache constructors and destructors must obey strong contracts; destructors must tolerate newly constructed objects, and move callbacks must not free either buffer passed to them.
- Debug behavior can change object layout and allocation routing, especially for firewalled and buftagged caches.
- Empty slab destruction is intentionally deferred when move callbacks are pending; violating this would break client recognition assumptions and could expose unmapped memory during callbacks.
- `kmem_alloc(0, KM_SLEEP)` is treated as deprecated and is optionally warned or panicked, while non-sleeping zero-size allocation returns `NULL`.

## Research Relevance

For filesystem and storage research, this file defines the allocator contracts used by vnode caches, buffer caches, transaction objects, ZFS structures, task queues, and driver/storage metadata. The reclaim callback model, cache kstats, low-memory reaping, and slab-consolidator move contract are especially relevant to long-lived filesystem objects and memory-pressure behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ksensor.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ksensor.c

## Purpose

`ksensor.c` implements the genunix side of the illumos kernel sensor framework. It lets kernel providers register sensor operations and metadata while a separate ksensor character driver creates/removes user-visible minor nodes under `/dev/sensors`.

Read completely: 869 lines.

## Main Responsibilities

- Maintains global sensor registration state independent of the load state of the ksensor character device.
- Tracks sensors by stable numeric IDs in an AVL tree and by owning `dev_info_t` in per-DIP lists.
- Provides `ksensor_create()` and `ksensor_remove()` for providers, including helper `ksensor_create_scalar_pcidev()` for PCI scalar sensors.
- Provides `ksensor_register()` and `ksensor_unregister()` for the ksensor character driver callback interface.
- Implements serialized sensor access through `ksensor_hold_by_id()` and `ksensor_release()`.
- Dispatches sensor operations `ksensor_op_kind()` and `ksensor_op_scalar()` after obtaining a valid provider hold.
- Handles provider detach/re-attach semantics so stale minor nodes can trigger driver reconfiguration rather than disappearing immediately.
- Cleans up permanently removed devices through DDI unbind callbacks and deferred taskq work.

## Important Data Structures And Globals

- `ksensor_t`: per-sensor object with mutex/CV, flags, waiter count, ID, name, class, provider ops, provider argument, owning `ksensor_dip_t`, list linkage, and AVL linkage.
- `ksensor_dip_t`: per-provider-DIP object containing the `dev_info_t`, DDI unbind callback, removal flag, and sensor list.
- `ksensor_g_mutex`: global lock protecting `ksensor_dips`, `ksensor_avl`, callback registration state, and ID-space use.
- `ksensor_ids`: ID allocator for sensor minor IDs.
- `ksensor_cb_dip`, `ksensor_cb_create`, `ksensor_cb_remove`: single registered character-driver callback endpoint.
- Sensor flags: `KSENSOR_F_NOTIFIED`, `KSENSOR_F_VALID`, and `KSENSOR_F_BUSY`.
- DIP flag: `KSENSOR_DIP_F_REMOVED`.

## Sensor Lifetime

The framework distinguishes provider detach from permanent device removal. `ksensor_create()` makes a sensor valid and visible; `ksensor_remove()` only clears `KSENSOR_F_VALID` and drops the provider ops/arg. The sensor object and minor-node identity remain so a later user access can attempt to reconfigure the provider's parent and revive the sensor, matching normal devfs behavior for detached devices.

Permanent removal is handled by `ksensor_dip_unbind_cb()`. The synchronous callback removes the provider from global lists, marks it removed, and removes all sensors from the ID AVL so new lookups fail. Deferred taskq cleanup then notifies the character driver to remove minors, waits for active/busy users and waiters to drain, frees each sensor, and frees the `ksensor_dip_t`.

## Access Path

`ksensor_hold_by_id()` performs the framework's open-like validation:

- Looks up the ID under the global lock.
- Rejects permanently removed provider DIPs.
- Serializes access with `KSENSOR_F_BUSY`; signalable waiters restart lookup after the busy holder exits.
- Drops framework locks before entering the devinfo tree.
- Enters the parent DIP, takes a hold on the provider DIP, and exits the parent.
- Rechecks removal and validity after the hold.
- If invalid, calls `ndi_devi_config()` on the parent to attempt reattach and then verifies that the sensor became valid.

`ksensor_release()` drops the provider DIP hold, clears busy, and wakes waiters. `ksensor_op_kind()` and `ksensor_op_scalar()` are thin wrappers that hold, invoke the provider operation vector, and release.

## Provider API

`ksensor_create()` requires a non-NULL DIP, ops, name, class, and output ID pointer, and only succeeds while the provider DIP is attaching. It creates a `ksensor_dip_t` on first use, registers a DDI unbind callback, reuses an existing invalid sensor with the same name/class, or allocates a new sensor ID. If the character driver is registered, it calls the create callback and sets `KSENSOR_F_NOTIFIED` on success.

`ksensor_remove()` requires the provider to be attaching or detaching. It finds the owning DIP and invalidates either the requested ID or all IDs (`KSENSOR_ALL_IDS`) by clearing valid state and provider callbacks.

`ksensor_create_scalar_pcidev()` validates that the provider is PCI/PCIe, reads the `reg` property, derives bus/device identifiers, picks a class from the sensor kind, and creates a name of the form `<bus>.<device>:<name>`.

## Character Driver API

Only one ksensor character driver can register. `ksensor_register()` stores its callbacks and walks all registered sensors, invoking the create callback for each and setting `KSENSOR_F_NOTIFIED` when successful. `ksensor_unregister()` validates the registering DIP, clears all notified flags, and removes callback pointers; it does not call the remove callback because the driver can remove its minors during detach.

## Locking And Concurrency

The file documents and follows these lock rules:

- `ksensor_g_mutex` protects global data and is acquired before any individual sensor mutex.
- A thread should not hold two sensor mutexes.
- No framework locks should be held while entering or manipulating devinfo tree state.
- Unless a sensor is actively held, users must recheck provider removal and sensor validity.

The busy flag serializes attach/revalidation and provider operation dispatch per sensor. Deferred unbind cleanup waits for both `KSENSOR_F_BUSY` and waiter count to drop before freeing a sensor.

## Notable Risks And Invariants

- Provider create/remove calls are constrained to attach/detach contexts; callers outside those contexts receive `EAGAIN`.
- `ksensor_hold_by_id()` intentionally drops locks around devinfo operations, so it must repeat removal/validity checks after reacquiring locks.
- `ksensor_release()` assumes a provider DIP hold was successfully obtained by the hold path.
- `ksensor_unregister()` panics if called by a DIP other than the registered character driver.
- Callback create failures leave sensors registered but not marked notified; a later character-driver register or sensor recreation can retry notification.

## Research Relevance

For storage and OS research, `ksensor.c` is not filesystem-specific, but it shows a modern illumos pattern for separating kernel provider registration from devfs-visible character devices. Its detach/reconfigure behavior, devinfo holds, unbind callbacks, and minor persistence are directly relevant to driver lifetime models used elsewhere in the device and storage stack.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ksensor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kstat_fr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kstat_fr.c

## Purpose

`kstat_fr.c` implements the core illumos kernel statistics framework. It creates, indexes, installs, snapshots, updates, zones, deletes, and times kstats exposed through `/dev/kstat`, including foundational system, VM, page, poll, and I/O timing statistics.

Read completely: 1,455 lines.

## Main Responsibilities

- Maintains global kstat AVL indexes by KID and by module/instance/name/zone visibility.
- Assigns and increments `kstat_chain_id` so `/dev/kstat` consumers can detect chain changes.
- Supports zone visibility lists for kstats visible to all zones, selected zones, or zone-specific readers.
- Allocates kstat headers and optional physical data from a boot-time buffer and later from a `vmem` arena.
- Initializes built-in kstats such as `kstat_headers`, `kstat_types`, `sysinfo`, `vminfo`, `segmap`, `biostats`, `var`, `system_misc`, `system_pages`, and `pollstats`.
- Provides default update and snapshot routines, including long-string named kstat support and I/O time normalization.
- Creates, installs, deletes, dormants, reactivates, and deletes-by-name kstats.
- Provides queue/timer accounting helpers for kstat I/O and event-timer users.

## Important Data Structures And Globals

- `ekstat_t`: private wrapper around `kstat_t`, adding allocation size, owner thread, wait CV, AVL nodes, and a zone visibility list.
- `kstat_zone_t`: singly linked zone ID list for visibility checks.
- `kstat_chain_lock`: protects AVL trees and `kstat_chain_id`.
- `kstat_chain_id`: monotonically updated chain/KID source, reserved initially for well-known kstats.
- `kstat_initial` / `kstat_initial_ptr` / `kstat_initial_avail`: early boot allocation pool before the kstat arena exists.
- `kstat_arena`: later vmem arena for kstat allocations.
- `kstat_avl_bykid` and `kstat_avl_byname`: primary lookup indexes.
- `kstat_data_type[]`: type descriptors for raw, named, interrupt, I/O, and event-timer kstats.
- `system_misc_kstat` and `system_pages_kstat`: built-in named-stat backing storage updated dynamically.

## Zone Visibility

The file models three kstat visibility classes: well-known kstats whose data changes per reading zone, kstats exported to a specific list of zones, and kstats visible to all zones. `kstat_zone_find()` accepts `ALL_ZONES` matches or exact zone IDs. `kstat_zone_add()` and `kstat_zone_remove()` mutate a kstat's visibility list and bump `kstat_chain_id`, treating visibility changes like install/delete events for userland chain consumers.

AVL comparison includes zone comparison after KID or name equality, so a name lookup is effectively module/instance/name/visible-zone. Non-global zones are disallowed from writing kstats by framework policy.

## Lookup And Ownership

`kstat_hold()` is the shared hold primitive for both AVL indexes. It searches under `kstat_chain_lock`, waits if another thread owns the matching `ekstat_t`, then records `curthread` as owner. `kstat_rele()` clears ownership and broadcasts waiters. Public lookup wrappers are `kstat_hold_bykid()` and `kstat_hold_byname()`.

This owner field serializes framework operations on an individual kstat without holding the chain lock across provider update/snapshot work.

## Allocation And Initialization

`kstat_alloc()` rounds each allocation to `KSTAT_ALIGN` and uses `kstat_initial` before `kstat_arena` exists. Once `kstat_init()` creates the arena, it reserves the initial allocations in vmem using `vmem_xalloc()` so early kstats become accounted arena allocations.

`kstat_init()` creates the kstat arena and installs the foundational kstats. `kstat_headers` is KID 0 and exposes the header chain itself; `kstat_types` enumerates type IDs. Several virtual kstats point directly at kernel structures or externally maintained named arrays.

## Creation, Install, Delete

`kstat_create()` delegates to `kstat_create_zone()` with `ALL_ZONES`. `kstat_create_zone()` validates type, persistent/virtual incompatibility, variable-size physical restrictions, and legal `ks_ndata`; synthesizes a name when `ks_name` is NULL; handles namespace collision; and reactivates matching dormant kstats when parameters are compatible.

New kstats are inserted invalid into both AVL trees, assigned the next unused KID from `kstat_chain_id`, and initialized with default update/snapshot handlers. `kstat_install()` verifies variable-size locking, detects named long strings, rejects writable long-string named kstats that rely on the default snapshot routine, rehydrates dormant persistent kstats through a write update, then clears `KSTAT_FLAG_INVALID` under the chain lock.

`kstat_delete()` refuses deletion while the caller holds the provider data lock. Persistent kstats are updated one last time, marked dormant, and reset to default framework handlers. Nonpersistent kstats are removed from both AVL trees, chain ID is bumped, zone-list allocations are freed, the hold is released, and memory is returned to the arena.

## Snapshot And Update

`default_kstat_update()` recalculates `ks_data_size` for variable-size named kstats with long strings. `default_kstat_snapshot()` handles write permissions, copies data, normalizes `KSTAT_TYPE_IO` unscaled times, accounts for in-progress wait/run queue transactions, and copies variable-length named strings into the snapshot buffer while rewriting their pointers to point inside that buffer.

`header_kstat_update()` counts visible, non-invalid kstats for the current zone and sets the header data size. `header_kstat_snapshot()` copies visible kstat headers in increasing KID order while the chain lock is held, matching the `/dev/kstat` two-pass contract.

## Built-In System Kstats

`system_misc_kstat_update()` reports CPU count, lbolt, deficit, clock interrupts, VAC state, process count, load averages, boot time, and nanoseconds per tick. For non-global zones, it uses pool pset CPU count when enabled, zone load averages, zone boot time, zone-relative lbolt, and zone process count.

`system_pages_kstat_update()` reports memory and VM page values such as `physmem`, kernel module allocation counts from `kobj_stat_get()`, `freemem`, `availrmem`, page scanner thresholds, `pagesfree`, `pageslocked`, `pagestotal`, low-memory scan/throttle counters, and `pp_kernel` derived from installed memory minus boot/kernel/user-lock reservations.

## Queue And Timer Accounting

The non-SPARC C implementations of `kstat_waitq_enter()`, `kstat_waitq_exit()`, `kstat_runq_enter()`, `kstat_runq_exit()`, `kstat_waitq_to_runq()`, and `kstat_runq_back_to_waitq()` update unscaled timestamps, queue counts, elapsed queue time, and length-time integrals. `default_kstat_snapshot()` later scales these for users.

`kstat_timer_start()` records a high-resolution start time. `kstat_timer_stop()` updates stop time, elapsed event duration, min/max duration, cumulative elapsed time, and event count.

## Notable Risks And Invariants

- The header kstat update/snapshot pair assumes `kstat_chain_lock` is held across sizing and copyout to prevent chain growth from overrunning the caller's buffer.
- Variable-size kstats must provide `ks_lock`; `kstat_install()` panics if they do not.
- Persistent virtual kstats are rejected because the provider backing pointer would become invalid after provider unload.
- Writable named kstats containing long strings must provide a custom snapshot routine.
- Zone visibility changes bump the chain ID, which can surprise readers that treat only install/delete as chain changes.

## Research Relevance

For filesystem and storage research, kstats are the primary kernel telemetry surface for VFS, disk, NFS, ZFS, VM, page cache, and allocator behavior. This file defines the concurrency, snapshot, zone visibility, and persistent-stat contracts that storage subsystems rely on when publishing metrics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kstat_fr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ksyms_snapshot.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ksyms_snapshot.c

## Purpose

`ksyms_snapshot.c` builds an ELF-format snapshot of the kernel symbol table for the ksyms subsystem. It walks loaded symbol sections, rewrites symbol/string offsets into a compact snapshot, emits ELF/program/section headers, and returns the size required or emitted.

Read completely: 207 lines.

## Main Responsibilities

- Defines a small synthetic ELF container containing program headers, `.symtab`, `.strtab`, and `.shstrtab`.
- Walks all allocated symbol-table sections in `ksyms_arena`.
- Emits local symbols, global symbols, and strings as separable passes.
- Rewrites each emitted symbol's `st_name` to the snapshot string-table offset and forces `st_shndx` to `SHN_ABS`.
- Computes total snapshot size even when the caller buffer is too small.
- Protects symbol snapshot consistency with `ksyms_lock` as a reader.

## Important Data Structures And Globals

- `ksyms_header_t`: synthetic ELF header, two program headers, four section headers, and section-name string table.
- `ksyms_walkinfo_t`: walk state containing emit callback, target pointer, remaining buffer length, total logical size, selected action mask, and per-action byte totals.
- `ksyms_shstrtab`: fixed section-name string table for `.symtab`, `.strtab`, and `.shstrtab`.
- Action flags: `KW_HEADER`, `KW_LOCALS`, `KW_GLOBALS`, and `KW_STRINGS`.
- `ksyms_lock`: global readers-writer lock for symbol snapshot operations.
- `ksyms_arena`: vmem arena whose allocations are walked to find symbol sections.

## Walk And Emit Flow

`ksyms_emit()` accounts bytes for an action and copies them only if that action is selected and enough buffer space remains after subtracting the requested size. It always advances total logical size for selected actions, letting callers learn the required snapshot length.

`ksyms_walk_one()` interprets each walked allocation as a symbol section header, finds the linked string table, iterates symbols from index 1, copies each symbol to a temporary, rewrites the symbol name offset to the current snapshot string-table size, marks it absolute, and emits the symbol as local or global according to `ELF_ST_BIND()`. It then emits the corresponding NUL-terminated name string.

`ksyms_walk()` initializes walk state, optionally emits the synthetic header, emits the required zero symbol and initial empty string, walks `ksyms_arena`, and returns total selected size.

## Snapshot Construction

`ksyms_snapshot()` first performs a sizing walk over all actions. It then constructs `ksyms_header_t` by copying the running kernel module ELF header and overriding offsets/counts for this synthetic image. It creates two load program headers from `s_text`/`e_text` and `s_data`/`e_data`, with the data segment marked read/write/execute.

The `.symtab` section starts immediately after the synthetic header and contains locals followed by globals. Its `sh_info` is the count of local symbols. The `.strtab` section follows the symbol table. The `.shstrtab` section points into the embedded `shstrings` member. Finally, it emits header, locals, globals, and strings as four ordered walks under the read lock.

## Notable Risks And Invariants

- The code assumes `ksyms_arena` allocations walked with `VMEM_ALLOC` are symbol-section headers linked to valid string-section headers.
- Symbol index 0 and string offset 0 are explicitly synthesized because ELF symbol hash chains use index 0 as the terminator.
- `kw_size[action]` indexing depends on sparse action values up to `KW_STRINGS` and the array being sized as `KW_STRINGS + 1`.
- If the caller buffer is short, `kw_resid` goes negative and later emits are counted but not copied.
- Snapshot consistency depends on the read lock preventing concurrent symbol-table mutation during the sizing and emission passes.

## Research Relevance

For filesystem/storage research, this file is mainly diagnostic infrastructure. Kernel symbol snapshots support debugging, crash analysis, and tooling that may resolve stack traces from allocator, kstat, VFS, or storage subsystems.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ksyms_snapshot.c -->