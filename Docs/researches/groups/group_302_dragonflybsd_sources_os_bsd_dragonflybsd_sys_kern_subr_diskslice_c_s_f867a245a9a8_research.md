# Group Research: group_302_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_subr_diskslice_c_s_f867a245a9a8

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_diskslice.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_diskslice.c

## Summary
Implements DragonFly BSD cooked disk-slice support: validating I/O against slices and disklabel partitions, translating logical offsets to media offsets, serving disklabel/slice ioctls, and managing in-core `struct diskslices` lifecycle.

## Main Responsibilities
- `dscheck()` validates `bio_offset` and transfer size against the requested slice/partition, protects reserved label areas, clips EOF reads, and returns a pushed BIO with translated media offset.
- `dsioctl()` handles disklabel, media-size, sector-size, partition-info, slice-info, sync/reprobe, and write-label ioctls.
- `dsmakeslicestruct()`, `dsgone()`, `free_ds_label()`, and `set_ds_label()` allocate, free, and update in-core slice/disklabel state.
- `dsopen()`, `dsclose()`, `dsisopen()`, and `dssize()` track open partitions and trigger disk or slice reprobes when label areas were written.

## Important Behavior
Whole-disk raw access is special: labels are not interpreted for `WHOLE_DISK_SLICE`, normal partition numbers below 128 are rejected, and higher partition numbers can be encoded into the high byte of the BIO offset for raw pass-through. For normal slices, partition bounds come from the loaded disklabel ops. Label writes set `DSF_REPROBE`, and close/ioctl paths send synchronous disk management messages followed by `devfs_config()`.

## Risks
Callers must reload disk/slice pointers after `dsclose()` or ioctls that reprobe because `ssp` and `sp` may be invalidated. Offset translation assumes sector alignment and power-of-two sector size at key points. Reserved-area writes require `ds_wlabel`; otherwise they fail with `EROFS`. Accessing a partition before its disklabel is loaded or present returns errors.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_diskslice.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_eventhandler.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_eventhandler.c

## Summary
Provides the kernel eventhandler registry: named lists of callback entries sorted by priority, protected by a global LWKT token.

## Main Responsibilities
- Defines `M_EVENTHANDLER` allocation type and the global `eventhandler_lists`.
- `eventhandler_register()` finds or lazily creates a named list, initializes entries, and inserts the callback by priority.
- `eventhandler_deregister()` removes one handler or clears an entire list.
- `eventhandler_find_list()` locates a named eventhandler list.

## Important Behavior
Registration is MPSAFE under `evlist_token`. Priority insertion is O(n), but equal-priority append is effectively O(1). Dynamically created list names are stored immediately after the allocated `eventhandler_list` structure.

## Risks
Deregistering an entire list frees entries but does not remove the list structure itself. Callers must pass the correct list/tag pairing; the file notes a missing diagnostic check.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_eventhandler.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_fattime.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_fattime.c

## Summary
Converts between POSIX `timespec` values and MS-DOS FAT date/time fields, including the FAT hundredths/odd-second byte.

## Main Responsibilities
- `timespec2fattime()` encodes date, time, and optional hundredths byte from a `timespec`.
- `fattime2timespec()` decodes FAT date/time/hundredths fields back to a `timespec`.
- Uses lookup tables for month/day placement within four-year leap cycles.
- Handles FAT’s 1980 epoch and the non-leap-year 2100 correction.

## Important Behavior
FAT stores timestamps as local calendar time unless the `utc` argument requests UTC-style conversion. In this DragonFly version, the local-time offset hooks are placeholders using `0`, so UTC and local paths currently do not differ. Dates before 1980 are clamped to 1980-01-01 on encode.

## Risks
Invalid FAT fields are not deeply validated; decode trusts the packed date/time values and table indexing. The optional `TEST_DRIVER` block appears stale relative to exported function names and is not normal kernel build code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_fattime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_firmware.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_firmware.c

## Summary
Implements the loadable firmware registry and autoload/unload machinery for firmware images backed by kernel modules.

## Main Responsibilities
- Maintains a fixed `FIRMWARE_MAX` table of `priv_fw` records.
- `firmware_register()` and `firmware_unregister()` add/remove named firmware images and parent/child module relationships.
- `firmware_get()` looks up firmware, autoloading a module by image name when permitted.
- `firmware_put()` drops references and may request deferred unload.
- `loadimage()` and `unloadentry()` run module reference/release work on a dedicated firmware taskqueue.
- Module glue creates the taskqueue and validates clean unload.

## Important Behavior
`fw.name` marks a registered image; `file` marks an autoloaded module whose unload handling is still pending. Parent firmware records receive refcount bumps from child images. Autoload is blocked by `SYSCAP_NOKLD` privilege failure or positive `securelevel`.

## Risks
The registry is a fixed 30-slot static array because external users hold firmware pointers. `firmware_unregister()` preserves `file` for autoloaded entries, so cleanup depends on later unload task state. Module unload fails if any image remains registered.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_firmware.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_gtaskqueue.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_gtaskqueue.c

## Summary
Implements group taskqueues and taskqgroups, a FreeBSD-compatible task execution facility used for grouped per-CPU/softirq work.

## Main Responsibilities
- Creates and runs `gtaskqueue` instances with queued and active task tracking.
- Supports enqueue, cancel, drain, block/unblock, and thread startup.
- Implements `grouptask_block()` / `grouptask_unblock()` around `TASK_NOENQUEUE`.
- Implements `taskqgroup_create()`, attach/detach, CPU-specific attach, CPU binding tasks, and drain-all behavior.
- Defines `TASKQGROUP_DEFINE(softirq, ncpus, 1)`.

## Important Behavior
Queue execution tracks active tasks through `gtaskqueue_busy` records with sequence numbers, enabling drain operations to distinguish already-running tasks from later work. `gtaskqueue_drain_tq_queue()` inserts a high-priority barrier task. Taskqgroups distribute tasks by least-loaded queue while avoiding duplicate `uniq` identifiers on a queue when possible.

## Risks
`gtaskqueue_free()` is marked unused, and `taskqgroup_destroy()` is empty, so lifecycle ownership is limited. Interrupt CPU binding code is disabled with `#if 0`. Detach blocks and drains the grouptask before removal; callers must not enqueue after detach.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_gtaskqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_kcore.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_kcore.c

## Summary
Small shared kernel/libkcore helper for exporting file table state into `struct kinfo_file`.

## Main Responsibilities
- Defines `_KERNEL_STRUCTURES` and includes shared kcore/kinfo headers.
- `kcore_make_file()` zeroes and fills a user-visible `kinfo_file` from a kernel `struct file`.
- Copies file descriptor number, owning pid/uid, file pointer, data pointer, type, refcount, message count, offset, and flags.

## Important Behavior
The file comment says this source is shared between kernel and `libkcore` and must remain synchronized. Kernel use expects callers to hold the required spinlocks.

## Risks
It is a raw snapshot helper; consistency depends entirely on caller-side locking around the source `struct file`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_kcore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_kobj.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_kobj.c

## Summary
Implements DragonFly’s kernel object method dispatch support: class compilation, method lookup/cache, object creation, and class reference lifetime.

## Main Responsibilities
- Initializes the global `kobj_token` at boot.
- Assigns descriptor IDs for method cache indexing.
- Compiles `kobj_class_t` classes into `kobj_ops` cache tables.
- Resolves methods through class methods, recursive base classes, or descriptor defaults.
- Provides cached dispatch via `kobj_lookup_method_cache()`.
- Creates, initializes, and deletes kobj instances with class refcounting.

## Important Behavior
Each compiled class gets a cache initialized to a null method. The cache slot is selected by `desc->id & (KOBJ_CACHE_SIZE - 1)`, and misses fall back to full method lookup. Class compile has a preemption race guard: if another thread compiled first, the extra table is freed.

## Risks
Descriptor unregister is a stub. Class uninstantiate frees ops when refs reach zero, so object lifetime must match class refcounts. Base-class search order is recursive and first-match.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_kobj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_log.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_log.c

## Summary
Implements the `/dev/klog` character device that exposes the kernel message buffer to syslog-style readers.

## Main Responsibilities
- Provides open, close, read, ioctl, and kqueue filter devops for `klog`.
- Blocks readers until `msgbufp` advances, unless opened nonblocking.
- Supports `FIONREAD`, async I/O ownership, SIGIO delivery, and deprecated tty process-group ioctls.
- Periodically checks `msgbuftrigger` with a callout and wakes readers/kqueue waiters.
- Creates the device at driver SYSINIT.

## Important Behavior
Only one opener is allowed through `log_open`. Reads handle circular message-buffer wrap and may discard old data if the reader falls too far behind. `log_wakeups_per_second` controls callout polling frequency.

## Risks
Message loss is accepted when the log reader lags behind the ring buffer. Wakeups are periodic rather than immediate. Async signaling depends on `sc_sigio` ownership and `LOG_ASYNC`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_module.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_module.c

## Summary
Implements accessors and debug dumping for bootloader-provided preloaded module metadata.

## Main Responsibilities
- Stores global `preload_metadata`.
- Searches preloaded records by name, type, next name, or metadata attribute.
- Deletes a preloaded module record by marking fields `MODINFO_EMPTY`.
- Relocates physical pointers to kernel virtual addresses during bootstrap.
- Pretty-prints module metadata through `debug.dump_modinfo`.

## Important Behavior
Metadata is parsed as aligned TLV records with `u_int32_t` type/length headers. Name lookup compares both the full loader path and its basename. `preload_search_info()` stops when it loops back to the starting record type.

## Risks
All walkers assume well-formed loader metadata ending in zero headers. `preload_bootstrap_relocate()` only fixes known pointer-bearing fields. Deletion marks records empty but does not compact the metadata stream.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_module.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_param.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_param.c

## Summary
Defines global kernel sizing parameters, boot-time tunable processing, and simple virtual-machine guest detection.

## Main Responsibilities
- Defines globals for `hz`, process/file limits, callouts, buffer counts, swap/bcache caps, and user address-space limits.
- `detect_virtual()` inspects SMBIOS loader environment strings for known hypervisors.
- `init_param1()` reads early tunables not scaled by memory.
- `init_param2()` computes memory-scaled limits such as `maxusers`, `maxproc`, `maxfiles`, and `ncallout`.
- Exposes `kern.vmm_guest`, `kern.maxssiz`, `kern.maxthrssiz`, and `kern.vmm_vendor`.

## Important Behavior
`maxusers` defaults from available physical/KVA MB when unset. `maxproc` is bounded by available KVA to avoid kmap exhaustion. `ncallout` is derived from process and file counts but capped at about five minutes of timer-wheel coverage.

## Risks
These globals influence broad kernel capacity and are initialized very early. Formula changes can shift process, descriptor, callout, and VM-space limits across the whole system. VM detection depends on exact SMBIOS strings.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_param.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_power.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_power.c

## Summary
Provides a minimal power-management callback registry and power-profile state notification.

## Main Responsibilities
- `power_pm_register()` installs a power-management backend callback for one PM type.
- `power_pm_get_type()` reports the registered PM type.
- `power_pm_suspend()` validates standby/suspend/hibernate requests and calls the backend.
- `power_profile_get_state()` / `power_profile_set_state()` manage performance/economy profile state.
- Emits `power_profile_change` eventhandler notifications on profile changes.

## Important Behavior
Only one PM type is accepted unless the existing type matches. Suspend requests are ignored if no backend is registered or if the sleep state is unsupported.

## Risks
There is no locking around global PM/profile state. Profile logging assumes only known profile constants, printing non-performance as `economy`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_power.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_prf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_prf.c

## Summary
Implements kernel printf/logging, message-buffer management, sysctl access to dmesg, pointer redaction, console/tty printing, and small formatting helpers.

## Main Responsibilities
- Provides `kprintf`, `kvprintf`, `log`, `uprintf`, `tprintf`, `ttyprintf`, `ksprintf`, `ksnprintf`, and allocated snprintf helpers.
- Implements `kvcprintf()` format parsing for integer, string, pointer, width, precision, length modifiers, `%n`, and BSD `%pb%i` bitfield formatting.
- Writes to console, controlling tty, and/or kernel message buffer through `kputchar()`.
- Maintains `msgbufp` ring buffer with `msgbufinit()`, `msglogchar()`, and `msgaddchar()`.
- Exposes `kern.msgbuf` and `kern.msgbuf_clear` sysctls.
- Runs `consttyd` to mirror message-buffer output to `constty`.
- Provides `hexdump()` and `kprint_cpuset()`.

## Important Behavior
Console output is serialized with a hard critical-section spinlock when possible, but may drop serialization to avoid nested hard-interrupt deadlocks. `security.ptr_restrict` can mask or replace `%p` output unless panicking, dumping, or in DDB. `security.unprivileged_read_msgbuf` controls whether non-root/non-wheel readers can access `kern.msgbuf`.

## Risks
Message-buffer updates are intentionally race-tolerant and can lose data on wrap or SMP races. `kvcprintf()` stops trusting the remaining format string after an unknown specifier because arguments may be misaligned. `kern.msgbuf` access control is security-sensitive because logs may contain kernel pointers or sensitive text.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_prf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_prof.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_prof.c

## Summary
Implements process profiling setup and deferred user profiling counter updates.

## Main Responsibilities
- `sys_profil()` handles the profiling syscall, validates scale, installs profiling buffer parameters, and starts/stops the profiling clock.
- `addupc_intr()` records a pending profiling tick from interrupt context.
- `addupc_task()` performs faultable copyin/copyout to update the user sample buffer.

## Important Behavior
Scale is 16-bit fixed point with `0x10000` representing 1.0. Interrupt-side collection only stores the last pending pc/tick pair and requests an AST-style profiling tick. Task-side update disables profiling if user memory copy fails.

## Risks
Ticks can be lost if interrupt updates overwrite pending profile state before the task path runs. The profile buffer is user memory, so bad mappings stop profiling.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_prof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_rbtree.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_rbtree.c

## Summary
Tiny support file for generic red-black tree scanning synchronization.

## Main Responsibilities
- Provides `rb_spin_lock()` and `rb_spin_unlock()` wrappers around DragonFly spin locks.
- Supports `RB_SCAN` helper linkage when tree scans occur under shared locks.

## Important Behavior
The comment describes use with shared VM object locks, where temporary scan-info linkage needs its own spinlock.

## Risks
Correctness depends on higher-level RB tree users supplying and using the spinlock consistently around scan linkage.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_rbtree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_rman.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_rman.c

## Summary
Implements the kernel resource manager for bus/CPU hardware resource ranges, including allocation, sharing, activation, release, and sysctl enumeration.

## Main Responsibilities
- `rman_init()` / `rman_fini()` initialize and destroy resource managers.
- `rman_manage_region()` adds managed free regions.
- `rman_reserve_resource()` allocates ranges with alignment, sharing, and optional activation.
- `rman_activate_resource()` / `rman_deactivate_resource()` manage `RF_ACTIVE`.
- `rman_release_resource()` deallocates and merges adjacent free ranges.
- `rman_make_alignment_flags()` converts sizes to alignment flag encodings.
- `hw.bus.rman` sysctl exposes resource-manager and resource records.

## Important Behavior
Managed regions are kept in sorted TAILQs. Allocations split free regions into two or three pieces as needed. Shared allocations require exact compatible ranges and sharing flags. Timeshare activation rejects a resource if another sharer is already active.

## Risks
`RMAN_GAUGE` is explicitly unimplemented. `rman_manage_region()` is not robust against duplicate/overlapping region programming errors. Sysctl enumeration uses temporary holds to avoid teardown races; `rman_fini()` waits for these holds before freeing resources.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_rman.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_sbuf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_sbuf.c

## Summary
Implements `sbuf`, a bounded/auto-extending string buffer abstraction shared by kernel and userland builds.

## Main Responsibilities
- Creates and deletes sbufs with static, dynamic, or dynamically allocated structure storage.
- Supports append, copy, printf formatting, trim, set position, finish, data, length, and error inspection.
- Supports optional drain callbacks for streaming output.
- Kernel build adds `sbuf_uionew()`, `sbuf_bcopyin()`, and `sbuf_copyin()`.
- Supports nested sections and padding via `sbuf_start_section()` / `sbuf_end_section()`.

## Important Behavior
Auto-extension grows to powers of two up to a page-sized threshold and then rounds by page-sized increments. Finished sbufs are NUL-terminated and must be finished before `sbuf_data()`. Drain callbacks consume buffered bytes and may leave remaining data shifted to the front.

## Risks
Most operations assert correct unfinished/finished state only under invariants. Copyin helpers reject or truncate based on available space and extension success. Drained sbufs cannot use APIs that require stable internal data.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_sbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_scanf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_scanf.c

## Summary
Provides compact kernel `sscanf` support for scanning from an in-memory string.

## Main Responsibilities
- `ksscanf()` wraps `kvsscanf()`.
- `kvsscanf()` parses literals, whitespace, width, suppression, `h/hh/l/q` length modifiers, `%d/%i/%o/%u/%x/%p`, `%s`, `%c`, `%[...]`, and `%n`.
- Uses `strtoq` / `strtouq` for numeric conversion after collecting a bounded token.
- `__sccl()` builds scanset character-class tables.

## Important Behavior
Numeric conversion uses a fixed 32-byte token buffer. `%i` performs base autodetection; `%p` is treated as hexadecimal pointer input. Return values follow scanf-style assigned count, match failure, and input failure behavior.

## Risks
Callers must provide adequately sized destination buffers for `%s`, `%c`, and scansets. Floating-point flags exist in comments/macros but floating conversions are not implemented. Scanset range behavior intentionally preserves old V7-compatible quirks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_scanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_sglist.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_sglist.c

## Summary
Implements scatter/gather list allocation and construction from physical, kernel virtual, user virtual, mbuf, and uio ranges.

## Main Responsibilities
- Allocates, frees, clones, builds, and measures `struct sglist`.
- Appends contiguous physical ranges and coalesces adjacent physical segments.
- Translates kernel/user virtual buffers through `pmap_kextract()` or `pmap_extract()`.
- Appends mbuf chains and uio vectors.
- Consumes uio data while updating iov base/length, residual, and offset.
- Splits, joins, and slices scatter/gather lists.

## Important Behavior
Append operations save the original segment count and last-segment length so failures can roll back partial changes. User and uio paths require a valid thread/pmap for `UIO_USERSPACE`. `sglist_split()` refuses to modify shared lists with refcount greater than one.

## Risks
Segment capacity exhaustion returns `EFBIG`; callers must size lists correctly or handle partial consume behavior. Physical contiguity is detected only by adjacent physical addresses. Split/join/slice APIs require empty destination lists when provided.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_sglist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_sleepqueue.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_sleepqueue.c

## Summary
Implements a FreeBSD-compatible `sleepq*()` API shim on top of DragonFly’s `tsleep` wait-channel/domain mechanisms.

## Main Responsibilities
- Initializes a 1024-bucket wait-channel hash table and object cache for `sleepqueue_wchan`.
- `sleepq_lock()` creates/refs and spin-locks a wait-channel record.
- `sleepq_release()` drops refs, recycles/free-lists idle records, and unlocks.
- `sleepq_add()` records current-thread sleepqueue state and calls `tsleep_interlock()`.
- Supports timeout setup, sleeper counts, wait variants, type query, signal, and broadcast.
- Provides no-op thread setup/teardown hooks for compatibility.

## Important Behavior
The implementation records state in `struct thread` and enacts the actual sleep only on `sleepq_wait*()`. Queue numbers map to DragonFly domains `PDOMAIN_FBSD0 + queue * PDOMAIN_FBSDINC`. Free wchan records are retained per bucket up to `SLEEPQ_FREEPERSLOT`.

## Risks
The file explicitly says this is for FreeBSD compatibility, such as Linux KPI code. It assumes callers follow the FreeBSD lock/add/wait/release protocol. The `lock_object` invariant association mentioned in comments is not implemented.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_sleepqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_taskqueue.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_taskqueue.c

## Summary
Implements DragonFly’s regular taskqueue subsystem: prioritized deferred tasks, timeout tasks, software-interrupt queues, and per-CPU thread-backed taskqueues.

## Main Responsibilities
- Creates, finds, frees, blocks, unblocks, and runs taskqueues.
- Enqueues tasks by priority, counts repeated enqueues through `ta_pending`, and supports optional cross-queue migration via `taskqueue_enqueue_optq()`.
- Supports timeout tasks backed by callouts.
- Cancels and drains normal, simple, and timeout tasks.
- Starts taskqueue worker threads and runs their loop.
- Defines `swi`, `swi_mp`, and per-CPU `taskqueue_thread[MAXCPU]` queues at SYSINIT.

## Important Behavior
Tasks are not individually locked; the file warns not to share one task across per-CPU queues. `taskqueue_run()` passes the pending count to the task function and wakes waiters after completion. Thread-backed enqueue temporarily drops the spinlock around `wakeup_one()`.

## Risks
Freeing a queue marks it inactive and drains/rendezvous with worker threads; new enqueues then fail with `EPIPE`. Timeout cancellation must coordinate both callout state and queued task state. Cross-queue migration relies on careful `ta_queue` fences and can leave pending work on the original queue.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_taskqueue.c -->