# Group Research: group_424_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_subr_kobj_c_sources__87398443fcea

Scope: `Docs/research_subset_a.md` only. All 17 listed FreeBSD kernel source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_kobj.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_kobj.c

## Purpose
Implements FreeBSD's kernel object (`kobj`) runtime support: class compilation, method lookup through base classes, object initialization, allocation, and deletion. This is an object-dispatch substrate used by multiple kernel frameworks, including device and bus abstractions.

## Main Interfaces
- `kobj_class_compile()`, `kobj_class_compile_static()`: build a class operation cache and assign method descriptor IDs.
- `kobj_lookup_method()`: resolves a method descriptor against a class and recursive base-class hierarchy, falling back to the descriptor default method.
- `kobj_create()`, `kobj_init()`, `kobj_init_static()`: allocate or initialize objects and attach compiled ops.
- `kobj_delete()`, `kobj_class_free()`: drop references and free dynamically allocated ops tables.
- `kobj_error_method()`: generic ENXIO-returning default method.

## Implementation Notes
A global mutex protects method ID allocation, class compilation, and class reference counts after normal lock initialization. Static compile/init variants are intentionally restricted to early boot before `kobj_mtx` is initialized. Classes maintain `refs`; each object initialization increments it, and deletion decrements it. Dynamic class ops are freed only when the last reference disappears.

The method cache is initialized to a `null_method` sentinel; lookup itself walks class methods and base classes rather than filling the cache in this file.

## Dependencies
Uses `sys/kobj.h`, `sys/lock.h`, `sys/mutex.h`, malloc type `M_KOBJ`, SYSINIT, and sysctls for method count and optional stats.

## Research Notes
Concurrency is centered on avoiding races between class compilation and object creation/deletion. `kobj_class_compile1()` allocates outside the lock, then rechecks under the lock. Static paths assert early boot constraints. No filesystem-specific logic appears here, but it underpins kernel object polymorphism used elsewhere in OS/device code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_kobj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_lock.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_lock.c

## Purpose
Provides common lock-object initialization/destruction, adaptive delay configuration, debugger display support, and optional lock profiling infrastructure. It is shared by FreeBSD mutex, sx, rw, rm, and lockmgr classes.

## Main Interfaces
- `lock_init()`, `lock_destroy()`: initialize and tear down `struct lock_object`, including lock class index encoding, WITNESS, and lock logging hooks.
- `lock_delay()`, `lock_delay_default_init()`: exponential spin-delay support for lock acquisition loops.
- DDB `show lock`: displays lock class/name and delegates class-specific display.
- Under `LOCK_PROFILING`: profiling hooks for lock acquisition, release, thread exit, sysctl output, reset, and enable.

## Implementation Notes
`lock_classes[]` maps lock class pointers to compact class indices stored in `lo_flags`. `CTASSERT(LOCK_CLASS_MAX == 15)` ensures the fixed layout matches expectations.

The profiling subsystem keeps per-CPU caches of profiling records and per-thread lists of currently held locks. It separates spin and non-spin objects so profiling code can tolerate spinlock acquisition while already profiling a non-spinlock path. Reset disables profiling, publishes the disabled state with fences, waits for critical sections to quiesce, clears per-CPU objects, reinitializes free lists, then restores prior enable state.

Profiling records aggregate hold time, wait time, max values, acquire counts, and contested acquisition counts by `(file, line, lock name)`.

## Dependencies
Uses WITNESS, lock logging, DDB, sysctl, per-CPU storage, scheduler/quiescence primitives, `sbuf`, and optional lock profiling compile-time configuration.

## Research Notes
This file is kernel infrastructure rather than filesystem code, but filesystem and VFS locks depend on these lock-object lifecycle and debugging facilities. The profiling path is careful about CPU migration, reset races, critical sections, and thread exit cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_log.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_log.c

## Purpose
Implements the `/dev/klog` character device, exposing the kernel message buffer to user space log readers such as syslog daemons.

## Main Interfaces
- Device operations: `logopen`, `logclose`, `logread`, `logioctl`, `logpoll`, `logkqfilter`.
- `logtimeout()`: periodic wakeup path for select/poll/kqueue/async readers.
- `log_drvinit()`: initializes condition variable, callout, knote list, and creates the `klog` device.

## Implementation Notes
Only one reader may open the device at a time, guarded by `msgbuf_lock` and `log_open`. On open, a callout is scheduled at `kern.log_wakeups_per_second`; invalid values below one are corrected. Reads block on `log_wakeup` unless `IO_NDELAY` is set, then copy from `msgbufp` using `msgbuf_getbytes()` in 128-byte chunks.

Polling and kqueue readiness are based on `msgbuf_getcount(msgbufp)`. `logtimeout()` checks `msgbuftrigger`; if set, it clears the trigger and wakes selectors, knotes, SIGIO subscribers, and condition-variable waiters, then reschedules itself.

`logioctl()` supports `FIONREAD`, async mode, owner get/set, and deprecated tty process-group aliases.

## Dependencies
Uses `msgbuf_lock`, `msgbufp`, `msgbuftrigger`, condition variables, callouts, select/poll/kqueue, sigio ownership, and FreeBSD character device registration.

## Research Notes
The design decouples writers from sleeping log readers: writers set `msgbuftrigger`, while the callout performs wakeups. This keeps kernel logging usable from sensitive contexts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_mchain.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_mchain.c

## Purpose
Provides `libmchain`, helper routines for constructing and parsing mbuf chains. These helpers are commonly useful for network/filesystem protocol code that needs endian-aware serialization into mbufs.

## Main Interfaces
Write-side `mbchain`:
- `mb_init()`, `mb_initm()`, `mb_done()`, `mb_detach()`, `mb_fixhdr()`.
- `mb_reserve()`, `mb_put_padbyte()`.
- Integer writers: `mb_put_uint8`, `mb_put_uint16be/le`, `mb_put_uint32be/le`, `mb_put_int64be/le`.
- Bulk writers: `mb_put_mem()`, `mb_put_mbuf()`, `mb_put_uio()`.

Read-side `mdchain`:
- `md_init()`, `md_initm()`, `md_done()`.
- Record handling: `md_append_record()`, `md_next_record()`.
- Integer readers: `md_get_uint8`, `md_get_uint16`, endian-specific 16/32/64-bit helpers.
- Bulk readers: `md_get_mem()`, `md_get_mbuf()`, `md_get_uio()`.

## Implementation Notes
`mb_reserve()` grows the chain when current trailing space is insufficient and panics for reservations larger than `MLEN`. `mb_put_mem()` supports system, user, inline byte-copy, zero-fill, and custom copy callbacks. `mb_put_uio()` advances the uio vectors and residuals as it copies.

`md_get_mem()` walks mbufs, detects incomplete chains as `EBADRPC`, and supports skipping by passing `target == NULL`. `md_get_mbuf()` copies a subrange using `m_copym()` and advances the parser.

## Dependencies
Uses mbuf APIs, endian conversion, `copyin`/`copyout`, uio, and module/feature declarations.

## Research Notes
This is a protocol marshalling utility. It is not filesystem-specific, but it supports kernel subsystems that exchange structured records over mbufs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_mchain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_memdesc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_memdesc.c

## Purpose
Implements operations over generic memory descriptors (`struct memdesc`) that may describe virtual addresses, physical addresses, DMA segment lists, uios, mbufs, or VM page arrays. It provides data copy and external-mbuf construction helpers.

## Main Interfaces
- `memdesc_copyback()`: copy from a linear source buffer into descriptor-backed memory.
- `memdesc_copydata()`: copy descriptor-backed memory into a linear destination.
- `memdesc_alloc_ext_mbufs()`: create mbuf chains externally backed by memory described by the descriptor, optionally truncating final partial pages.

## Implementation Notes
Copy paths dispatch on `md_type`:
- `MEMDESC_VADDR`: direct `memcpy`.
- `MEMDESC_PADDR`: direct-map physical access via `PHYS_TO_DMAP`, requiring `PMAP_HAS_DMAP`.
- `MEMDESC_VLIST`: virtual DMA segments.
- `MEMDESC_PLIST`: physical DMA segments.
- `MEMDESC_MBUF`: `m_copyback()` / `m_copydata()`.
- `MEMDESC_VMPAGES`: `uiomove_fromphys()`.
- `MEMDESC_UIO`: intentionally rejected with panic; callers should use `uiomove`.

External mbuf allocation supports normal external buffers for virtual memory and `M_EXTPG` physical-page mbufs for physical addresses, physical segment lists, and VM pages. Helpers carefully handle page alignment, first-page offsets, full-page runs, last-page lengths, `MBUF_PEXT_MAX_PGS`, and optional truncation to avoid trailing partial pages.

## Dependencies
Uses VM page/pmap APIs, mbuf external page storage, bus DMA segments, uio, and `memdesc.h` callback types.

## Research Notes
This file is directly relevant to storage/network I/O boundaries: it provides a common way to treat physical pages, DMA lists, and mbufs uniformly while preserving zero-copy opportunities.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_memdesc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_module.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_module.c

## Purpose
Handles bootloader-preloaded module metadata: locating modules by name/type, fetching metadata attributes, deleting preload records, relocating pointers, and dumping decoded metadata.

## Main Interfaces
- `preload_initkmdp()`: locates kernel metadata and optionally panics if absent.
- Search helpers: `preload_search_by_name()`, `preload_search_by_type()`, `preload_search_next_name()`, `preload_search_info()`.
- Fetch helpers: `preload_fetch_addr()`, `preload_fetch_size()`.
- Mutation/relocation: `preload_delete_name()`, `preload_bootstrap_relocate()`.
- Diagnostics: `preload_dump()`, debug sysctl `debug.dump_modinfo`, DDB `show preload`.

## Implementation Notes
Metadata is TLV-like: a 32-bit type and 32-bit length followed by rounded-up data. Records begin with `MODINFO_NAME`; searches iterate until a zero type/length terminator. `preload_search_info()` scans within one record and stops when it loops to the initial metadata type.

`preload_delete_name()` marks fields as `MODINFO_EMPTY` and frees bootstrap memory when both address and size are found. `preload_bootstrap_relocate()` adjusts pointer-valued metadata after early physical-to-virtual relocation for known attributes.

Dump formatting decodes standard `MODINFO_*` and many `MODINFOMD_*` metadata types, printing strings, sizes, VM offsets, flags, or omitting raw buffers.

## Dependencies
Uses linker metadata definitions, machine metadata constants, `sbuf`, VM bootstrap free, sysctl, and DDB.

## Research Notes
This file influences boot-time module discovery for kernel components, including filesystem modules and boot resources. The parser assumes trusted bootloader-provided metadata and relies on terminators/alignment.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_module.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_msan.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_msan.c

## Purpose
Implements FreeBSD's Kernel Memory Sanitizer runtime support, adapted from NetBSD KMSAN. It provides compiler ABI hooks, shadow/origin metadata handling, runtime reporting, thread TLS, wrapper functions, atomic wrappers, bus-space wrappers, and DMA synchronization instrumentation.

## Main Interfaces
Core KMSAN:
- `kmsan_init()`, `kmsan_thread_alloc()`, `kmsan_thread_free()`.
- `kmsan_intr_enter()`, `kmsan_intr_leave()`: nested interrupt context accounting.
- `kmsan_shadow_map()`, `kmsan_orig()`, `kmsan_mark()`, `kmsan_check()`.
- Descriptor helpers: `kmsan_mark_bio()`, `kmsan_check_bio()`, `kmsan_mark_mbuf()`, `kmsan_check_mbuf()`, `kmsan_check_uio()`.

Compiler ABI:
- `__msan_metadata_ptr_for_load/store_*`.
- `__msan_poison()`, `__msan_unpoison()`, `__msan_poison_alloca()`, `__msan_warning()`, `__msan_get_context_state()`, `__msan_test_shadow()`.

Runtime wrappers:
- Memory/string/copy wrappers: `kmsan_memcpy`, `kmsan_memmove`, `kmsan_memset`, `kmsan_memcmp`, `kmsan_strcpy`, `kmsan_strcmp`, `kmsan_strlen`, `kmsan_copyin`, `kmsan_copyout`, `kmsan_copyinstr`.
- User access wrappers: `kmsan_fubyte`, `kmsan_fueword*`, `kmsan_suword*`, `kmsan_casueword*`.
- Atomic and bus-space wrappers generated by macros.
- `kmsan_bus_dmamap_sync()`.

## Implementation Notes
KMSAN tracks one shadow byte per application byte and origin metadata encoded by machine-dependent helpers. Unsupported addresses and disabled KMSAN use dummy shadow/origin pages; separate dummy write shadow avoids false positives from instrumentation stores.

Reports decode origins as stack, kmem, malloc, or UMA and try to resolve symbols or stack-variable descriptors. Reporting is suppressed while already reporting, inside KDB, after panic, or when the current thread has `TDP2_SAN_QUIET`.

Thread-local state has four nested contexts for interrupt nesting. The initial thread uses static TLS; later threads allocate `M_KMSAN` storage and mark kernel stacks uninitialized.

DMA sync handling checks buffers on prewrite and marks them initialized on postread for virtual-address and mbuf descriptors.

## Dependencies
Requires machine KMSAN address translation/origin encoding, pmap sanitizer mappings, compiler instrumentation ABI, atomic and bus sanitizer headers, VM, mbuf, bio, memdesc, copyin/out, linker symbol lookup, sysctl, and stack tracing.

## Research Notes
This is a correctness/debug runtime with broad kernel impact. Filesystem, block, and network paths interacting with DMA, mbufs, uios, and copies can surface uninitialized-memory bugs through these hooks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_msan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_msgbuf.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_msgbuf.c

## Purpose
Provides generic circular kernel message buffer support used by printk/logging and `/dev/klog`.

## Main Interfaces
- `msgbuf_init()`, `msgbuf_reinit()`, `msgbuf_clear()`.
- Writers: `msgbuf_addchar()`, `msgbuf_addstr()`.
- Readers: `msgbuf_getchar()`, `msgbuf_getbytes()`, `msgbuf_peekbytes()`.
- Utilities: `msgbuf_getcount()`, `msgbuf_copy()`, `msgbuf_duplicate()`.

## Implementation Notes
The buffer uses read/write sequence numbers modulo `size * 16`, not plain indices. This preserves ordering across wraps while keeping arithmetic bounded. `msgbuf_getcount()` clamps unread length to buffer size, treating overwritten data as lost.

`msgbuf_reinit()` attempts to preserve old content when magic, size, and checksum match. On mismatch, it clears the buffer and optionally reports the failure when bootverbose is enabled. Reinit assumes old contents did not end in a newline, setting `MSGBUF_NEEDNL`.

`msgbuf_addstr()` handles priority prefixes (`<pri>`), optional timestamps, carriage-return filtering, newline tracking, and insertion of a newline when priority changes mid-line. Timestamps are controlled by `kern.msgbuf_show_timestamp`.

All public read/write operations acquire the message buffer spin mutex. `msgbuf_duplicate()` copies both metadata and backing bytes while holding the source lock.

## Dependencies
Uses `struct msgbuf`, spin mutexes, sysctl, time uptime/microtime, and helper macros in `sys/msgbuf.h`.

## Research Notes
This file is the core data structure behind kernel logging. It supports crash/boot continuity by checksum-based recovery and careful wrap handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_msgbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_param.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_param.c

## Purpose
Initializes global kernel sizing and timing parameters from compile-time defaults, tunables, detected physical memory, and virtualization status.

## Main Interfaces
- `init_param1()`: early boot parameters not scaled by memory.
- `init_param2(long physpages)`: parameters scaled/clamped by physical memory.
- `sysctl_kern_vm_guest()`: stringifies detected VM guest type.

## Implementation Notes
`init_param1()` selects `hz` from `kern.hz`, `HZ`, or `HZ_VM` when running as a guest, clamps it to min/max, then derives `tick`, `tick_sbt`, `tick_bt`, and `tick_seconds_max`. It also initializes stack pages, vnode lock pause max, swap/buffer-cache KVA caps, message buffer size, process size limits, max supplementary groups, PID limit, and unmapped buffer allowance.

`init_param2()` derives `maxusers`, `maxproc`, `maxprocperuid`, `maxfiles`, `maxfilesperproc`, `nbuf`, `bio_transient_maxcnt`, `maxphys`, `nswbuf`, and `maxpipekva`. It clamps process and file limits to memory-derived maxima and rounds `maxphys` up to a power of two when needed.

The VM guest sysctl maps enum values to stable strings and uses a static assert to ensure the table covers all enum values.

## Dependencies
Uses tunables, sysctls, VM page sizing, pmap/kernel address limits, vnode/buffer globals, and scheduler tick globals.

## Research Notes
This file affects filesystem and block I/O through `maxphys`, buffer-cache sizing, vnode timing pause values, message-buffer size, and process/file limits.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_param.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_pcpu.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_pcpu.c

## Purpose
Provides machine-independent per-CPU (`pcpu`) and dynamic per-CPU (`dpcpu`) support.

## Main Interfaces
- `pcpu_init()`, `pcpu_destroy()`, `pcpu_find()`: lifecycle and lookup for `struct pcpu`.
- `dpcpu_init()`: initializes per-CPU dynamic storage from linker defaults.
- `dpcpu_alloc()`, `dpcpu_free()`, `dpcpu_copy()`: module-oriented dynamic per-CPU allocator and initializer.
- `sysctl_dpcpu_quad()`, `sysctl_dpcpu_long()`, `sysctl_dpcpu_int()`: aggregate per-CPU counters.
- DDB commands for `dpcpu_off`, `pcpu`, and all pcpu display.

## Implementation Notes
`pcpu_init()` clears the architecture-provided structure, records CPU ID, installs it in `cpuid_to_pcpu`, links it into `cpuhead`, calls machine-dependent initialization, initializes rm queue links, and records zpcpu offset.

`dpcpu_init()` copies static linker-section defaults into a CPU's dynamic area and records its offset in `dpcpu_off`. `dpcpu_startup()` seeds the module dynamic area with `modspace` and initializes an sx lock. Allocation is first-fit with pointer-size rounding. Freeing reinserts a sorted extent and merges adjacent free regions.

General UMA per-CPU zones for 4/8/16/32/64-byte allocations are created during counter startup.

## Dependencies
Uses DPCPU macros, UMA per-CPU zones, SMP CPU iteration, sx locks, malloc type `M_PCPU`, DDB, WITNESS display, and machine pcpu hooks.

## Research Notes
Per-CPU storage is central for scalable counters, scheduler state, lock profiling, PRNG state, and filesystem/VFS hot-path metrics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_pcpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_pctrie.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_pctrie.c

## Purpose
Implements FreeBSD's path-compressed radix trie (`pctrie`) over 64-bit keys. It supports locked operations, SMR-protected unlocked lookups, iterators, range lookups, insertion, removal, replacement, and incremental reclamation.

## Main Interfaces
Lookup:
- `pctrie_lookup()`, `pctrie_lookup_unlocked()`.
- `pctrie_lookup_range()`, `pctrie_lookup_range_unlocked()`.
- `pctrie_lookup_ge()`, `pctrie_lookup_le()`, `pctrie_subtree_lookup_lt()`.

Iterator operations:
- `pctrie_iter_lookup()`, `pctrie_iter_lookup_range()`.
- `pctrie_iter_next()`, `pctrie_iter_prev()`, `pctrie_iter_stride()`.
- `pctrie_iter_lookup_ge()`, `pctrie_iter_lookup_le()`, jump variants.
- `pctrie_iter_remove()`, `pctrie_iter_value()`.

Mutation/reclaim:
- `pctrie_insert_lookup_strict()`, `pctrie_insert_lookup()`, `pctrie_iter_insert_lookup()`, `pctrie_insert_node()`.
- `pctrie_remove_lookup()`, `pctrie_replace()`.
- `pctrie_reclaim_begin/resume()` and callback variants.
- `pctrie_zone_init()`, `pctrie_node_size()`.

## Implementation Notes
Leaves are tagged pointers using `PCTRIE_ISLEAF`; interior nodes store owner prefix, compressed level, parent pointer, child popmap, and child array. `pn_popmap` records non-null children for locked traversal and mutation. SMR access uses `smr_entered_load()` and avoids relying on `pn_popmap` for consistency during unlocked range lookup.

Insertion first searches for the target; if a null leaf slot is found, it inserts directly. If an existing leaf/subtree conflicts, the caller allocates a branch node and `pctrie_insert_node()` computes the highest differing level, sets ownership, installs old/new children, and publishes the node with ordered SMR store semantics.

Removal compresses away interior nodes that become single-child. Reclamation walks and prunes subtries incrementally, optionally calling a callback for leaves.

## Dependencies
Uses `sys/pctrie.h`, SMR primitives, libkern bit helpers, DDB, and pointer-tagging contracts.

## Research Notes
This trie is relevant to VM and filesystem page/object indexes: it is optimized for sparse 64-bit key spaces and supports lockless readers where callers can provide SMR protection.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_pctrie.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_physmem.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_physmem.c

## Purpose
Maintains early physical memory region tables, exclusion regions, and derived availability lists for VM allocation, crash dumps, and RAM resource reservation.

## Main Interfaces
- `physmem_hardware_region()`: add usable physical RAM region.
- `physmem_exclude_region()`: add exclusion region with flags such as no-alloc/no-dump.
- `physmem_avail()`, `physmem_all()`: generate availability arrays.
- `physmem_excluded()`: query if a range is fully excluded.
- Kernel-only `physmem_init_kernel_globals()`: fills `phys_avail`, `dump_avail`, `physmem`, `realmem`, and `Maxmem`.
- Diagnostics: `physmem_print_tables()`, DDB `show physmem`.
- Kernel-only RAM pseudo-driver reserves memory resources.

## Implementation Notes
Two sorted static arrays track hardware and exclusion regions. `insert_region()` insertion-sorts and merges compatible overlapping/adjacent regions. Exact duplicate exclusions with different nonzero flags are upgraded by OR-ing flags.

`regions_to_avail()` walks hardware regions against sorted exclusions, page-aligns hardware bounds, splits around exclusions, merges adjacent output entries, optionally enforces a maximum physical memory byte cap from `hw.physmem`, and returns count plus page totals.

`physmem_hardware_region()` filters page zero because physical address zero conflicts with `pmap_extract()` failure semantics. It also avoids the top megabyte near the maximum physical address to prevent wrap/end-of-address-space problems.

The RAM pseudo-driver reserves non-excluded/non-dump physical ranges as bus memory resources.

## Dependencies
Uses VM page macros, `phys_avail`, `dump_avail`, bus resource APIs, nexus driver attachment, optional ACPI sizing, and DDB.

## Research Notes
This file directly shapes what memory the VM and dump subsystems see. Storage/filesystem behavior can be indirectly affected through dump availability and physical-memory sizing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_physmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_pidctrl.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_pidctrl.c

## Purpose
Implements a small PID-style controller utility with sysctl visibility. It is intended for kernel subsystems that need feedback control over a process variable.

## Main Interfaces
- `pidctrl_init()`: zeroes and configures setpoint, interval, wind-up bound, and inverse gain values.
- `pidctrl_init_sysctl()`: exposes controller state and tunables under a caller-provided sysctl node.
- `pidctrl_classic()`: classic signed PID output.
- `pidctrl_daemon()`: interval-aware daemon-style controller producing non-negative incremental output.

## Implementation Notes
The controller stores proportional error, older error, integral, derivative, input, output, and last tick. Gains are inverse divisors (`Kpd`, `Kid`, `Kdd`) and are clamped to at least one to avoid division by zero.

`pidctrl_classic()` computes signed error as `setpoint - input`, clamps integral between `-bound` and `bound`, computes derivative from the previous error, and returns the sum of scaled P/I/D terms.

`pidctrl_daemon()` resets accumulated interval state when enough ticks have elapsed. Within an interval it adjusts error relative to previous output, clamps integral at zero lower bound, computes a non-negative incremental output, and accumulates `pc_output`.

## Dependencies
Uses `ticks`, sysctl APIs, and `sys/pidctrl.h`.

## Research Notes
This is generic kernel control logic. It has no direct filesystem behavior, but it may be used by background subsystems needing bounded adaptive work scheduling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_pidctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_power.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_power.c

## Purpose
Provides generic power-management device/sysctl glue and a global power profile notification mechanism.

## Main Interfaces
- Character device `/dev/power` with `power_ioctl()`, supporting `PIOTRANSITION`.
- Sleep type conversion: `power_name_to_stype()`, `power_stype_to_name()`.
- Provider registration: `power_pm_register()`, `power_pm_get_type()`.
- Transition request: `power_pm_suspend()`.
- Profile state: `power_profile_get_state()`, `power_profile_set_state()`.

## Implementation Notes
`power_init()` creates `/dev/power` owned by root/operator mode 0660. The ioctl path requires write permission and accepts a `uint32_t` transition value, checks enum overflow, then calls `power_pm_suspend()`.

`power_pm_register()` installs one provider type unless the same type is already registered, records supported sleep types, and picks default standby/suspend/hibernate stypes based on provider capabilities. Actual suspend is deferred through `taskqueue_thread`; `power_pm_deferred_fn()` invokes the provider callback with `POWER_CMD_SUSPEND`.

Sysctls expose supported sleep types and allow standby/suspend/hibernate type selection by string, rejecting unknown or unsupported values.

`power_profile_set_state()` updates global performance/economy state and invokes the `power_profile_change` eventhandler on changes.

## Dependencies
Uses character devices, sysctl, `taskqueue_thread`, eventhandlers, power enums/names, and credential/device creation APIs.

## Research Notes
This is OS power infrastructure. Filesystem relevance is indirect: suspend/hibernate transitions and power-profile changes affect storage quiescing and background work policy elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_power.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_prf.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_prf.c

## Purpose
Implements kernel formatted output, logging integration, message-buffer initialization/sysctls, hexdump utilities, and sbuf drains. This is the central `printf`/`log` formatting path for FreeBSD kernel code.

## Main Interfaces
Output/logging:
- `printf()`, `vprintf()`, `log()`, `vlog()`, `uprintf()`, `tprintf()`, `vtprintf()`.
- `log_console()`: copies console output into the message log.
- Internal `_vprintf()`, `putchar()`, `prf_putchar()`, `prf_putbuf()`.

Formatting:
- `sprintf()`, `vsprintf()`, `snprintf()`, `vsnprintf()`, `vsnrprintf()`.
- `kvprintf()`: scaled-down kernel formatter.
- `ksprintn()`: numeric conversion helper.

Message buffer:
- `msgbufinit()`.
- Sysctls `kern.msgbuf` and `kern.msgbuf_clear`.
- DDB `show msgbuf`.

Diagnostics:
- `hexdump()`, `sbuf_hexdump()`.
- `counted_warning()`.
- `sbuf_putbuf()`, `sbuf_printf_drain()`, DDB sbuf drain.

## Implementation Notes
Output flags route formatted characters to console, tty, and/or log. Console/log output may be buffered when `PRINTF_BUFR_SIZE` is defined. `vlog()` writes to log and only falls back to console when no log reader is open. `vprintf()` writes to console and log, then triggers message-buffer wakeups unless panicked.

`kvprintf()` supports common integer/string/char/pointer formats plus kernel-specific `%b` bitfield decoding and `%D` hexdump formatting. Kernel `%n` is intentionally unsupported, but consumes the pointer argument to keep argument walking aligned. Unknown formats are emitted literally and stop further conversion because argument alignment is no longer trustworthy.

`msgbufinit()` places `struct msgbuf` at the end of the supplied memory, attempts to preserve old contents across remap/reinit, fetches `kern.boot_tag` on first mapping, and prints a boot tag if configured.

`kern.msgbuf` requires `PRIV_MSGBUF`, peeks the entire buffer without consuming it, skips the first incomplete line after wrap, and appends a NUL terminator. `kern.msgbuf_clear` clears under `msgbuf_lock`.

## Dependencies
Uses console, tty, msgbuf, syslog priorities, proc/session locks, sysctl privilege checks, DDB, sbuf, tslog, and kernel panic/KDB state.

## Research Notes
This file is foundational for observing all filesystem and storage code. Its locking and context behavior matter because logging can be called from interrupts, panic paths, and early boot.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_prf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_prng.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_prng.c

## Purpose
Provides fast per-CPU pseudo-random number generation using PCG. This is not cryptographic randomness; it is a lightweight kernel PRNG utility.

## Main Interfaces
- `prng32()`, `prng32_bounded()`.
- `prng64()`, `prng64_bounded()`.

## Implementation Notes
The file defines per-CPU PCG state for 32-bit and 64-bit random generation. On platforms without 128-bit PCG operations, a local `pcg64u_random_t` gangs two 32-bit PCG states into one 64-bit generator. Bounded 64-bit generation uses rejection sampling with `threshold = -bound % bound`.

`prng_init()` seeds every CPU's 32-bit and 64-bit state with seed value `1` during `SI_SUB_CPU`. Each public function enters a critical section, uses the current CPU's DPCPU state, and exits the critical section so execution cannot migrate midway through state update.

## Dependencies
Uses PCG routines from `sys/prng.h`, DPCPU storage, `CPU_FOREACH`, critical sections, SMP/pcpu APIs, and SYSINIT.

## Research Notes
This is deterministic fast PRNG infrastructure for non-security uses such as randomized backoff or sampling. Filesystem code may use it for low-stakes randomized behavior, but not for entropy.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_prng.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_prof.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_prof.c

## Purpose
Implements the `profil(2)` system call and user-mode profiling sample updates.

## Main Interfaces
- `sys_profil()`: enables/disables profiling for the calling process.
- `addupc_intr()`: records a pending profiling tick from interrupt context.
- `addupc_task()`: performs the actual user profiling buffer update in a context where copyin/copyout are allowed.

## Implementation Notes
Profiling uses a fixed-point scale with 16 fractional bits; `scale == 0` disables profiling. `sys_profil()` validates scale, updates `p_stats->p_prof` under process/profile locks, and starts or stops the profiling clock.

`PC_TO_INDEX()` maps a program counter to a sample-buffer byte offset: `(pc - offset) * scale >> 16`, rounded down to an even address for `u_short` counters.

`addupc_intr()` is interrupt-safe: it checks range under `PROC_PROFLOCK`, then stores the PC/tick count in thread fields, sets `TDP_OWEUPC`, and schedules an AST. It may lose samples if overloaded and a later tick overwrites pending state.

`addupc_task()` runs later, validates the process is still profiling, increments `p_profthreads`, computes the target address, unlocks around `copyin`/`copyout`, adds ticks to the 16-bit counter, and stops profiling if user buffer access fails. It coordinates with `P_STOPPROF` waiters.

## Dependencies
Uses process/profile locks, AST scheduling, copyin/copyout, profiling clock hooks, and process statistics.

## Research Notes
This is process accounting/profiling infrastructure. It is not filesystem-specific, but profiling can be used to measure filesystem-heavy workloads.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_prof.c -->