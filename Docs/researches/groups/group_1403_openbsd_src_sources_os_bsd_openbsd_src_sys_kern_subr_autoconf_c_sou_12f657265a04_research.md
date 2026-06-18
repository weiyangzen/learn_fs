# Group Research: group_1403_openbsd_src_sources_os_bsd_openbsd_src_sys_kern_subr_autoconf_c_sou_12f657265a04

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included in subset A. All ten listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_autoconf.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_autoconf.c

## Role

Implements OpenBSD kernel autoconfiguration support: device matching, softc allocation, attach/detach, deferred configuration, mountroot-time callbacks, suspend/resume activation, global device lookup, and device reference management.

## Key Behavior

- `config_init()` initializes deferred queues and the global `alldevs` device list.
- `config_search()`, `config_scan()`, and `config_rootsearch()` walk generated `cfdata`/`cfroots` tables, filter unavailable or hibernate-skipped devices, and use match priority to choose the winning attachment candidate.
- `config_attach()` serializes against detach, allocates/uses softc storage, assigns unit numbers, updates `cfdriver` device arrays, marks `cfdata` state, calls `device_register()` and driver attach hooks, processes deferred children, and emits hotplug events.
- `config_make_softc()` creates and names device instances, expands `cd_devs`, and handles wildcard unit selection.
- `config_detach()` serializes against attach, deactivates devices, calls driver detach hooks, verifies child removal in diagnostic builds, frees unit/cfdata state, updates hotplug, and drops references.
- `config_defer()` and `config_process_deferred_children()` support child setup after a parent finishes attaching; `config_mountroot()` and `config_process_deferred_mountroot()` delay work until root is mounted.
- `config_suspend_all()` coordinates quiesce/suspend/powerdown/resume/wakeup ordering for `mpath` and `mainbus`.
- `config_activate_children()` walks direct children and rolls back already-suspended children on suspend failure.
- `device_lookup()`, `device_mainbus()`, `device_mpath()`, `device_ref()`, and `device_unref()` provide active-device lookup and lifetime management.

## Interfaces And Dependencies

Depends on generated kernel configuration tables, `struct cfdata`, `struct cfdriver`, `struct cfattach`, device classes, hotplug support, reboot flags, mutexes, atomic refcounts, `TAILQ`, and driver-supplied match/attach/detach/activate callbacks.

## Notes

The file is central to kernel device-tree lifetime. Correctness depends on keeping attach/detach serialization, `cf_fstate`, wildcard unit allocation, `cd_devs`, and device references consistent. Hibernate boot filters deliberately avoid some classes and drivers during unhibernate probing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_autoconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_blist.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_blist.c

## Role

Implements a preallocated bitmap allocator using a hinted radix tree. It is used for block-like allocation where allocation and free paths must avoid recursive memory allocation, notably swap-space style management.

## Key Behavior

- `blist_create()` computes the radix/skip layout, allocates the `struct blist` and fixed root array, and initializes the radix tree as all allocated.
- `blist_alloc()` and `blist_allocat()` reserve contiguous blocks, decrementing `bl_free` on success.
- `blist_free()` releases a range and panics on inconsistent double-free conditions.
- `blist_fill()` marks a region allocated regardless of prior state and returns how many blocks were newly consumed.
- `blist_resize()` creates a new tree, copies free regions from the old tree, optionally frees newly added blocks, and destroys the old tree.
- `blist_gapfind()` scans for the largest fully free leaf-aligned gap.
- Leaf helpers operate on bitmaps, optimizing single-block allocation and full-bitmap states.
- Meta helpers manage collapsed all-free/all-allocated states, recursively initialize stale children when needed, and maintain `bm_bighint`.
- Debug/standalone code can print and interactively test the allocator outside the kernel.

## Interfaces And Dependencies

Uses `swblk_t`, `blmeta_t`, `blist_t`, `SWAPBLK_NONE`, `BLIST_BMAP_RADIX`, and `BLIST_META_RADIX` from `sys/blist.h`. Kernel builds allocate from `M_VMSWAP`; non-kernel builds provide testing shims.

## Notes

Hints are conservative: they may be too high until failed searches refine them, but should not be too low. Allocation is limited to at most one leaf radix per call, while free/fill can span arbitrary ranges.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_blist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_disk.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_disk.c

## Role

Provides OpenBSD disk subsystem support: disklabel checksum/validation, DOS/GPT/FAT partition spoofing, disk attach/detach bookkeeping, open masks, transfer bounds checks, disk accounting, root/swap selection, DUID formatting/mapping, and disk label reads.

## Key Behavior

- `dkcksum()`, `initdisklabel()`, `checkdisklabel()`, and `setdisklabel()` initialize, validate, byte-swap, constrain, checksum, and install OpenBSD disklabels.
- `readdisksector()` and `readdoslabel()` read sector data, synthesize labels from GPT/MBR/FAT, locate OpenBSD label offsets, and then validate on-disk labels when present.
- GPT helpers validate protective MBRs, read and checksum GPT headers/partition arrays, map known GPT UUIDs to OpenBSD fstypes, and expose non-OpenBSD partitions beginning at label partition `i`.
- MBR helpers walk primary and extended partitions, identify OpenBSD A6 partitions, set label bounds, and expose supported foreign partitions.
- `bounds_check_with_label()` rejects malformed or misaligned transfers, returns EOF at partition end, and truncates transfers that extend past a partition.
- `disk_init()`, `disk_construct()`, `disk_attach()`, `disk_attach_callback()`, and `disk_detach()` manage global disk lists, labels, attach timestamps, device numbers, asynchronous label reads, randomness seeding, and softraid attach notifications.
- `disk_openpart()` and `disk_closepart()` maintain block/character/open partition masks to protect open partitions from unsafe relabeling.
- `disk_busy()` and `disk_unbusy()` maintain busy time, transfer counters, seek counts, and entropy contributions.
- `setroot()`, `getdisk()`, `parsedisk()`, and `dk_mountroot()` choose root/swap/dump devices, support askname prompts, DUID-root mapping, NFS boot handling, and filesystem-specific mountroot dispatch.
- `disk_readlabel()`, `disk_map()`, `disk_lookup()`, `duid_equal()`, `duid_iszero()`, and `duid_format()` provide label and DUID utility services.

## Interfaces And Dependencies

Depends on disklabel macros, vnode block/character device operations, `bdevsw`/`cdevsw`, GPT/MBR structures, zlib CRC32, softraid hooks, root/swap globals, autoconf device lists, and filesystem mountroot entry points.

## Notes

This is one of the subset’s storage-relevant kernel files. It bridges physical/media partition metadata with OpenBSD’s disklabel model and boot-time root selection. Label bounds and raw partition preservation are intentionally enforced after reading or setting labels.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_evcount.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_evcount.c

## Role

Implements kernel event counters, mainly for interrupt/event statistics exposed through sysctl. It supports both simple scalar counters and later conversion to per-CPU counters.

## Key Behavior

- `evcount_attach()` initializes an `evcount`, assigns a monotonically increasing ID, records its name/data pointer, and inserts it into the global list.
- `evcount_percpu()` moves counters to a pending per-CPU initialization list before per-CPU setup is complete, or allocates per-CPU counter storage immediately afterward.
- `evcount_init_percpu()` allocates per-CPU counters for pending entries, migrates existing scalar counts into counter slot zero, and returns them to the main list.
- `evcount_detach()` removes a counter and frees per-CPU storage if present.
- `evcount_inc()` increments either the per-CPU counter or scalar count.
- `evcount_sysctl()` reports interrupt counter count, counter values, names, and optional vector data through `KERN_INTRCNT_*` nodes.

## Interfaces And Dependencies

Uses `TAILQ`, `struct evcount`, sysctl helpers, interrupt priority masking for scalar reads, and `counters_alloc/read/free/inc()` from the per-CPU counter subsystem.

## Notes

The design allows early boot counters to exist before per-CPU memory is available, then converts them without losing accumulated counts.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_evcount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_extent.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_extent.c

## Role

Implements a general-purpose extent manager for reserving and freeing address/resource ranges. It tracks allocated regions in a sorted list, supports fixed-storage operation for constrained contexts, and provides aligned/bounded allocation.

## Key Behavior

- `extent_create()` creates either a dynamically allocated extent or a fixed-storage extent with preallocated region descriptors; `EX_FILLED` can mark the full range allocated initially.
- `extent_destroy()` frees all region descriptors and the extent descriptor when dynamic.
- `extent_insert_and_optimize()` inserts allocated regions into sorted order and coalesces adjacent regions unless `EX_NOCOALESCE` is set.
- `extent_alloc_region()` and `extent_alloc_region_with_descr()` reserve a specific range, optionally waiting for space or tolerating conflicts.
- `extent_do_alloc()` implements subregion allocation with power-of-two alignment, skew, boundary crossing limits, first-fit (`EX_FAST`) or best-fit behavior, and optional waiting.
- `extent_alloc_subregion()` and descriptor variants wrap `extent_do_alloc()`.
- `extent_free()` removes or shrinks allocated regions, handles middle splits, supports partial conflict-tolerant frees, and wakes waiters.
- Region descriptor helpers allocate from a pool for dynamic extents or from a fixed freelist, with optional fallback to mallocable descriptors.
- Diagnostic/DDB support registers extents globally and prints all tracked regions.

## Interfaces And Dependencies

Uses `struct extent`, `struct extent_region`, `struct extent_fixed`, flags such as `EX_WAITOK`, `EX_WAITSPACE`, `EX_FAST`, `EX_NOCOALESCE`, `EX_BOUNDZERO`, and pool allocation for dynamic descriptors.

## Notes

This allocator models allocated regions, not free regions. Its correctness relies on sorted non-overlapping region lists, careful overflow checks, and descriptor availability before operations that may split or coalesce ranges.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_extent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_hibernate.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_hibernate.c

## Role

Implements machine-independent OpenBSD hibernate suspend/resume support. It records machine and swap metadata, compresses physical memory into swap, writes chunk metadata and a signature block, validates a saved image during boot, reads it into a safe pig area, and restores memory using machine-dependent resume hooks.

## Key Behavior

- Defines the piglet layout: I/O pages, copy/RLE pages, final chunk ordering, hiballoc/zlib workspace, preserved entropy, retguard preservation, chunk table, and bounce area.
- `hibernate_write()` bounds-checks writes to image, chunk table, or signature areas before invoking the device-specific hibernate I/O function.
- `get_hibernate_info()` records hibernate device, disklabel-derived swap signature location, sector size, kernel hash, piglet addresses, I/O hooks, memory ranges, and machine-dependent metadata.
- `preallocate_hibernate_memory()`, `uvm_pmr_alloc_piglet()`, and `uvm_pmr_alloc_pig()` allocate DMA-safe piglet/pig memory while avoiding overlap with resume scratch areas.
- The `hiballoc` arena provides a tiny aligned allocator used by zlib during suspend/resume when normal allocation is unsafe.
- `uvm_pmr_dirty_everything()` clears `PG_ZERO` state after resume because restored memory invalidates assumptions about pre-zeroed free pages.
- `uvm_page_rle()`, `hibernate_calc_rle()`, and `hibernate_write_rle()` encode free-page runs so free physical pages do not need full page data in the compressed image.
- `hibernate_write_chunks()` splits physical memory ranges into hibernate chunks, resets zlib per chunk, writes RLE tokens and page data, records compressed sizes, and updates the chunk table.
- `hibernate_write_chunktable()`, `hibernate_write_signature()`, and `hibernate_clear_signature()` persist or clear metadata in swap.
- `hibernate_resume()` reads and clears the signature, compares memory/kernel signatures, quiesces CPUs/devices, handles stack protector/retguard preservation, switches stacks, and calls unpack.
- `hibernate_read_image()` reads the chunk table, totals compressed image size, allocates pig memory, reads chunks, and prepares resume page tables.
- `hibernate_read_chunks()` orders chunks so non-overlapping regions are restored first, reads compressed chunks into the pig area, and stores final ordering in the piglet.
- `hibernate_unpack_image()`, `hibernate_process_chunk()`, `hibernate_copy_chunk_to_piglet()`, `hibernate_inflate_region()`, and `hibernate_inflate_page()` switch into resume mappings, inflate chunk streams, skip or move special pages, and finally jump to the MD resume vector.
- `hibernate_suspend()` obtains hibernate info, finds swap space, calculates image/chunk offsets, writes chunks, chunk table, and signature, then sends final I/O cleanup notification.
- `hibernate_alloc()` and `hibernate_free()` map/unmap temporary hibernate pages around suspend work.

## Interfaces And Dependencies

Depends on UVM physical memory/page queues, swap metadata, disklabel reads, block device strategy I/O, zlib, SHA256, pmap mapping primitives, machine-dependent hibernate hooks, stack protector guard state, retguard symbols, autoconf device suspend, and swap device globals.

## Notes

The implementation is highly order-sensitive. After interrupts are disabled and resume mappings are active, normal kernel services and global data cannot be assumed safe. The signature is cleared before attempting resume to avoid repeated failed resumes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_hibernate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_kubsan.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_kubsan.c

## Role

Provides OpenBSD kernel handlers for Clang undefined-behavior sanitizer callbacks. It records sanitizer events, rate/batch processes them via timeout, formats readable diagnostics, and optionally enters DDB.

## Key Behavior

- Defines ABI-compatible UBSan data structures for source locations, type descriptors, overflow, bounds, nullability, pointer overflow, shift, type mismatch, invalid value, and unreachable reports.
- `__ubsan_handle_*()` entry points convert compiler sanitizer callbacks into a compact `kubsan_report`.
- `kubsan_init()` allocates a fixed report array during boot and starts periodic reporting.
- `kubsan_defer_report()` suppresses duplicate source locations using a high bit in `sl_line`, reserves one of 32 slots atomically, and copies the report.
- `kubsan_report()` drains report slots, formats diagnostics per sanitizer kind, handles newly arrived reports, and reschedules itself.
- `kubsan_format_int()`, integer deserializers, shift helpers, and `kubsan_kind()` convert ABI-encoded values into readable messages.
- `kubsan_format_location()` and `pathstrip()` shorten absolute build paths to paths beginning after `/sys/`.
- `kubsan_unreport()` clears the reported bit when no report slot was available, allowing a future report attempt.

## Interfaces And Dependencies

Uses OpenBSD atomics, timeout scheduling, early boot page allocation, optional DDB entry, kernel printing, and Clang UBSan runtime symbol names.

## Notes

The implementation deliberately does not abort on undefined behavior. Reports are lossy under bursts because there are only 32 slots, but duplicate-location suppression reduces repeated noise.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_kubsan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_log.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_log.c

## Role

Implements kernel logging buffers, `/dev/klog` read/poll/kqueue/async behavior, and the `sendsyslog` syscall path used to forward userland syslog messages to syslogd or the console.

## Key Behavior

- `initmsgbuf()` validates or initializes the persistent kernel message ring and ensures resumed/reused buffers start on a new line.
- `initconsbuf()` allocates a console message buffer.
- `msgbuf_putchar()` and `msgbuf_putchar_locked()` append characters to circular buffers and count dropped bytes when writers overrun readers.
- `logopen()` and `logclose()` enforce single-open `/dev/klog`, initialize kqueue/sigio state, manage the periodic wakeup timeout, and release any registered syslog socket.
- `logread()` blocks or returns `EWOULDBLOCK` when empty, reports dropped bytes, copies ring data to userland, and advances the read pointer.
- `logkqfilter()` and filter callbacks expose readable state through kqueue.
- `logwakeup()` defers wakeups from arbitrary printf contexts by setting a flag without taking locks; `logtick()` periodically performs kqueue, SIGIO, and sleep wakeups.
- `logioctl()` supports `FIONREAD`, async mode, owner/pgrp operations, and privileged `LIOCSFD` registration of the syslogd socket.
- Log stash support stores a bounded queue of userland syslog messages while syslogd is unavailable, tracks drops, and replays messages in order when possible.
- `sys_sendsyslog()` bounds user message length, tries to flush stashed messages, sends the current message, and stashes non-`EFAULT` failures.
- `dosendsyslog()` sends to syslogd’s socket if registered, otherwise honors `LOG_CONS` by stripping priority and writing to console/cnputc fallback.

## Interfaces And Dependencies

Uses `struct msgbuf`, `/dev/klog` device entry points, kqueue, sigio, timeouts, vnode/console output, socket `sosend`, rwlocks, mutexes, `copyin`, `uiomove`, and optional ktrace.

## Notes

`log_mtx` is kept as a leaf lock so kernel printf paths remain usable in many contexts. Actual wakeups are deferred to `logtick()` to avoid taking heavier locks from arbitrary logging call sites.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_percpu.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_percpu.c

## Role

Implements per-CPU memory allocation wrappers and per-CPU counters, with separate multiprocessor and uniprocessor implementations.

## Key Behavior

- In multiprocessor builds, `percpu_init()` initializes a pool of `struct cpumem` arrays sized for `ncpusfound`.
- `cpumem_get()`/`cpumem_put()` allocate and free one object per CPU from a supplied pool.
- `cpumem_malloc()`/`cpumem_free()` allocate and free cacheline-rounded per-CPU malloc storage.
- `cpumem_malloc_ncpus()` reuses CPU 0 boot memory and allocates the remaining CPU slots.
- `cpumem_first()` and `cpumem_next()` provide iteration over per-CPU slots.
- `counters_alloc()` reserves an extra generation word plus counter slots per CPU; `counters_free()` releases them.
- `counters_read()` uses a generation counter protocol with memory barriers to read stable per-CPU counter snapshots and sum them.
- `counters_zero()` clears counters and generation words across CPUs.
- In uniprocessor builds, all APIs collapse to a single allocation and `counters_read()`/`counters_zero()` protect access with `splhigh()`.

## Interfaces And Dependencies

Uses pools, malloc types, cacheline sizing, memory barriers, `yield()`, interrupt priority masking, and counter macros/functions declared in `sys/percpu.h`.

## Notes

The MP counter layout reserves a generation word before the counters so writers can make readers retry when observing an update in progress. The UP implementation preserves API shape without cacheline or multi-slot overhead.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_percpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_poison.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_poison.c

## Role

Provides small memory poison helpers used to mark freed objects with recognizable values and later detect post-free modification.

## Key Behavior

- `poison_value()` derives one of four 32-bit poison patterns from the object’s page number, using configurable `DEADBEEF0`/`DEADBEEF1` defaults when provided.
- `poison_mem()` writes the selected poison value into the first 64 bytes, rounded down to whole 32-bit words.
- `poison_check()` verifies the same bounded region and reports the first mismatching word index and expected poison value.

## Interfaces And Dependencies

Uses `PAGE_SHIFT`, `uint32_t`, and basic kernel types from `sys/param.h`.

## Notes

Only the first 64 bytes are poisoned or checked. The address-derived pattern makes adjacent pages less likely to share identical poison text while keeping the operation cheap.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_poison.c -->