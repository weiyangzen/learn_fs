# Group Research: group_565_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_s_311084daeb4f

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All five listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/swapgeneric.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/swapgeneric.c

## Purpose

Configures early root filesystem/device boot plumbing for illumos. Despite the historical “root, swap and dump devices” file description, this source is primarily concerned with discovering the root filesystem type and physical boot path, preloading the driver/module stack needed before boot services disappear, initializing the root VFS, and mounting root.

## Main Responsibilities

- Register the module as `root and swap configuration`.
- Load and initialize the selected root filesystem module.
- Create and hold `rootvfs`, then call `VFS_MOUNTROOT(rootvfs, ROOT_INIT)`.
- Resolve root device paths into `dev_t` values through `ddi_pathname_to_dev_t()`.
- Prompt for filesystem/device names when `RB_ASKNAME` is active.
- Read boot properties for root filesystem type and boot path.
- Preload root-path drivers, parent nexus drivers, platform modules, force-loaded modules, NFS boot modules, iSCSI boot modules, and network plumbing.
- Detect special boot forms including ramdisk boot archives, NFS/netboot, iSCSI boot, IP-over-InfiniBand netboot, and USB hub boot paths.

## Key Entry Points

- `_init()`, `_fini()`, `_info()`
  Standard module linkage.

- `rootconf()`
  Final root setup. It initializes cluster boot root configuration, loads the root filesystem module, looks up the VFS switch entry, initializes `rootvfs`, calls `pm_init()`, optionally plumbs network/iSCSI support, mounts root through `VFS_MOUNTROOT()`, records `rootdev`, and logs the mounted root.

- `getrootdev()`
  Converts `rootfs.bo_name` to a device number and retries with an iSCSI physical disk path when needed.

- `getfsname()`
  Console prompt helper used when booting with `RB_ASKNAME`.

- `loadrootmodules()`
  Main early boot module loader. It gets the root filesystem type, loads implementation and platform drivers, resolves and loads root bootpath drivers, preserves DHCP boot properties, preloads `/etc/system` `FORCELOAD` modules, loads NFS/iSCSI boot dependencies, and calls cluster boot preload support.

- `getfstype()`
  Determines a root or swap filesystem type. It maps root `nfs` to `nfsdyn` and `nfs2` to `nfs`, and uses `vfs_getvfssw()` to obtain/load the filesystem switch entry.

- `getphysdev()`
  Determines root/swap physical device path. For swap it verifies `ddi_pathname_to_dev_t()` succeeds and refuses floppy swap devices.

- `load_boot_driver()`
  Resolves aliases to major driver names, performs `modloadonly("drv", ...)`, and on SPARC preloads modules listed in `ddi-forceload`.

- `load_bootpath_drivers()`
  Duplicates and normalizes a boot path, maps it to devinfo, handles x86 leaf-driver fallback, loads IP-over-IB and USB hub support where needed, and loads all parent drivers.

- `load_boot_platform_modules()`
  Loads platform modules or parent drivers for existing hardware nodes.

- `path_to_devinfo()`
  Uses PROM node lookup plus `ddi_walk_devs()` to map a physical path to an illumos devinfo node.

- `netboot_over_ib()` and `netboot_over_iscsi()`
  Detect network boot variants from boot path syntax/properties.

## Important State and Dependencies

- Uses global boot state such as `rootfs`, `rootvfs`, `rootdev`, `boothowto`, `bootops`, `netboot`, `obp_bootpath`, `root_is_ramdisk`, and iSCSI boot properties.
- Depends on VFS switch lookup, kernel module loading, PROM/boot property APIs, DDI/devinfo traversal, STREAMS plumbing, cluster boot hooks, NFS boot helper modules, and iSCSI boot path translation.
- DHCP boot metadata is copied from boot properties into `dhcack`, `dhcacklen`, and `netdev_path` for later userland adoption.

## Filesystem Relevance

This is directly filesystem-relevant boot code. It determines which filesystem implementation becomes root, ensures the required drivers and network/storage modules are resident before mountroot, initializes the root `vfs_t`, and invokes the root filesystem’s `VFS_MOUNTROOT()` operation. It is a critical bridge between firmware boot paths, device discovery, module loading, and the VFS layer.

## Notable Edge Cases

- Root `nfs` naming is rewritten for dynamic NFS version selection.
- `netboot` and iSCSI boot are treated as mutually exclusive in `rootconf()`.
- NFS boot preloads several STREAMS/RPC/MAC/NFS helper modules while boot services can still supply I/O.
- iSCSI boot preloads network, iSCSI, and disk drivers, then attaches the pseudo `iscsi` node during root configuration.
- x86 may lack a complete PROM stub for the leaf boot device, so the code falls back to parent path lookup plus explicit leaf driver load.
- USB boot through hubs force-loads `hubd` because PROM-compatible properties can otherwise bind hub nodes to the wrong driver.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/swapgeneric.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sysent.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sysent.c

## Purpose

Defines the illumos system call dispatch tables and DTrace systrace wrappers. This file maps syscall numbers to kernel entry points, argument counts, return-value conventions, loadable syscall placeholders, native/compatibility ABI variants, and systrace instrumentation shims.

## Main Responsibilities

- Declare syscall implementation prototypes used by the dispatch tables.
- Define `SYSENT_*` initializer macros for syscall ABI metadata.
- Build the native `sysent[NSYSCALL]` table.
- Build the `sysent32[NSYSCALL]` table when `_SYSCALL32_IMPL` is enabled.
- Provide `nosys_ent` for unimplemented syscalls.
- Export `syscallnames` storage allocated elsewhere.
- Provide DTrace systrace entry/return wrapper functions for native and 32-bit syscalls.

## Sysent Table Model

Each `struct sysent` entry encodes:

- Argument count.
- Return-value layout flags such as `SE_64RVAL`, `SE_32RVAL1`, and `SE_32RVAL2`.
- Optional argument-structure syscall handler.
- Optional reserved field.
- C-callable function pointer or generic AP trampoline.

Important macros:

- `SYSENT_C()` for direct C-style syscalls returning 64-bit.
- `SYSENT_CI()` for direct C-style syscalls returning one 32-bit value.
- `SYSENT_2CI()` for two 32-bit return registers.
- `SYSENT_AP()` for legacy argument-structure syscalls using `syscall_ap`.
- `SYSENT_CL()` for native long-sized returns.
- `SYSENT_LOADABLE()` / `SYSENT_LOADABLE32()` for loadable syscall slots.
- `SYSENT_NOSYS()` for invalid or unsupported slots.
- `IF_LP64`, `IF_sparc`, `IF_x86`, and `IF_386_ABI` to select table entries without large `#ifdef` blocks inside the table.

## Native Syscall Coverage

The native table maps syscall numbers 0-255. Filesystem and VFS-facing entries include:

- File descriptor I/O: `read`, `write`, `readv`, `writev`, `pread`, `pwrite`, `preadv`, `pwritev`, `close`, `fcntl`, `ioctl`, `fdsync`, `sendfilev`.
- Path operations: `open`, `openat`, `unlink`, `unlinkat`, `link`, `linkat`, `rename`, `renameat`, `symlink`, `symlinkat`, `readlink`, `readlinkat`, `resolvepath`, `getcwd`.
- Metadata operations: `stat`, `lstat`, `fstat`, `fstatat`, `stat64`, `lstat64`, `fstat64`, `fstatat64`, `chmod`, `fchmod`, `fchmodat`, `chown`, `lchown`, `fchown`, `fchownat`, `mknod`, `mknodat`, `mkdir`, `mkdirat`, `rmdir`, `umask`.
- Filesystem operations: `mount`, `umount2`, `sync`, `statvfs`, `fstatvfs`, `statvfs64`, `fstatvfs64`, `statfs32`, `fstatfs32`, `sysfs`, `pathconf`, `fpathconf`, `acl`, `facl`.
- VM/file mapping operations: `mmap`, `mmapobj`, `mprotect`, `munmap`, `mincore`, `memcntl`.
- Loadable historical or subsystem slots: `nfssys`, `sharefs`, `autofssys`, `rpcsys`, `portfs`, `door`, `kaio`, and others.

## 32-bit Compatibility Table

When `_SYSCALL32_IMPL` is compiled, `sysent32` maps ILP32 processes on an LP64 kernel to ABI-specific wrappers:

- 32-bit pointer/size conversions for `read32`, `write32`, `pread32`, `pwrite32`, `readv32`, `writev32`, `readlink32`, and `readlinkat32`.
- 32-bit stat/statvfs variants such as `stat32`, `fstat32`, `lstat32`, `fstatat32`, `stat64_32`, and `statvfs64_32`.
- 32-bit STREAMS message wrappers `getmsg32`, `putmsg32`, `getpmsg32`, and `putpmsg32`.
- 32-bit signal/time/context wrappers such as `sigaction32`, `sigaltstack32`, `sigqueue32`, `stime32`, `times32`, and `waitsys32`.
- Large-file compatibility entries at syscall numbers 213-225.

## DTrace Systrace Hooks

- `systrace_stub()` is an empty probe target.
- `dtrace_systrace_syscall()` wraps native syscall execution, fires entry probes, honors `t_dtrace_stop` process stop requests, invokes the underlying syscall, converts nonzero `lwp_errno` to `-1`, and fires return probes.
- `dtrace_systrace_syscall32()` performs the same function for the 32-bit table.
- `dtrace_systrace_rtt()` fires a return-to-trap systrace return probe for the current syscall when the normal wrapper path is not used.

## Filesystem Relevance

This file is the syscall-level entry map for almost every user-visible filesystem operation. VFS, filesystem, vnode, file-descriptor, pathname, mount, ACL, stat, large-file, and memory-mapped-file behavior all become reachable through the syscall table entries defined here. It also controls ABI routing for 32-bit filesystem calls on a 64-bit kernel.

## Notable Edge Cases

- Several historical syscall numbers are preserved as loadable or `nosys` slots for ABI stability.
- LP64 kernels intentionally mark many 32-bit large-file native entries as `nosys` because the 64-bit C library maps them to native calls.
- Native syscall 0 is `nosys` on LP64 but `indir` on non-LP64.
- DTrace can request a process stop before the syscall body runs.
- Systrace return probes use different high-word casts between native and 32-bit wrappers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sysent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/task.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/task.c

## Purpose

Implements illumos kernel task objects: process groupings associated with projects and zones for resource accounting, resource controls, signal/administrative targeting, processor binding, fair-share scheduling integration, and extended accounting commit.

A task is a collection of processes with a common project ID and common initial parent lineage. The code manages task identity, membership, lifetime, resource-control state, per-task usage accounting, kstats, and final extended-accounting commit.

## Main Responsibilities

- Maintain a global task ID namespace and ID-to-task hash.
- Create, hold, release, attach, detach, change, and destroy `task_t` objects.
- Track per-task process count, LWP count, CPU time, and usage snapshots.
- Register task resource controls:
  - `task.max-lwps`
  - `task.max-processes`
  - `task.max-cpu-time`
- Integrate task/project changes with credentials, FSS scheduler state, zones, and resource-control callbacks.
- Initialize primordial `task0` and attach `p0`.
- Publish per-task `nprocs` kstats.
- Commit completed task accounting asynchronously through `exacct_queue`, with a backup commit thread when taskq dispatch fails.

## Locking and Lifetime Model

- `task_hash_lock` protects the global task hash and ID lookup.
- `tk_hold_count` is atomically updated for members and observers.
- Task membership list fields `tk_memb_list`, `p_tasknext`, and `p_taskprev` are protected by `pidlock`.
- A process’s `p_task` is read under `pidlock` or `p_lock` and changed with both.
- `tk_usage_lock` protects task usage structures.
- `tk_cpu_time_lock` protects tick-to-second CPU accounting.
- `zone_nlwps_lock` protects `tk_nlwps`, `tk_nprocs`, project task counts, and related task/project limits.
- Task teardown removes the task from the hash before committing accounting, so no new observer can find it.

## Key Entry Points

- `task_hold_by_id_zone()` / `task_hold_by_id()`
  Find a task by ID with zone visibility checks and return it held.

- `task_hold()` / `task_rele()`
  Manage task references. The final release removes the task from the hash, updates project task counts, deletes kstats, and dispatches extended-accounting commit.

- `task_create()`
  Allocates a new task, assigns an ID, holds the destination project and zone, duplicates ancestor resource controls, records ancestor task ID, inserts into the hash, and creates kstats.

- `task_attach()`
  Inserts a process into the task’s circular membership list and sets `p_task`.

- `task_begin()`
  Initializes start time and attaches the first member, then runs resource-control duplicate callbacks once process-to-task linkage exists.

- `task_detach()`
  Removes a process from its task membership list, tears off observational rctls from task/project rctl sets, and clears process task links.

- `task_change()`
  Moves a process between tasks, adjusting LWP/process counters and extended-accounting microstate ownership.

- `task_join()`
  Moves `curproc` into a new task during `settaskid()`-style operations. It updates credentials for project ID, allocates FSS buffers, changes task membership, updates all threads’ project pointers, and optionally marks the new task final.

- `task_end()`
  Final frees after accounting commit: releases project and zone holds, frees usage and inherited usage buffers, frees rctl set, returns task ID, and frees the task cache object.

- `task_cpu_time_incr()`
  Called by clock accounting to convert accumulated CPU ticks into task CPU seconds.

- `task_init()`
  Initializes caches, ID space, task hash, rctls, primordial `task0`, and p0 task membership.

- `task_commit_thread_init()` / `task_commit()`
  Starts and runs the backup commit thread used if `taskq_dispatch(exacct_queue, ...)` fails during final release.

## Resource Control Behavior

- `task_lwps_usage()` / `task_lwps_test()` / `task_lwps_set()` expose and enforce task LWP limits.
- `task_nprocs_usage()` / `task_nprocs_test()` / `task_nprocs_set()` expose and enforce task process limits.
- `task_cpu_time_usage()` / `task_cpu_time_test()` expose CPU-time usage and threshold testing; CPU-time rctl is configured as non-denying, CPU-time, infinite-capable, seconds-based, and unobservable.

## Filesystem Relevance

This is not filesystem code, but it is part of the OS resource-control and accounting substrate used by filesystem-facing workloads. Filesystem daemons, kernel service processes, zones, and user processes doing file I/O are accounted and limited through tasks/projects. Extended accounting can include file-service workload attribution, and kernel task queues are used to commit task accounting records.

## Notable Edge Cases

- `task_rele()` may be called with `pidlock` held, so final accounting dispatch uses `TQ_NOSLEEP | TQ_NOQUEUE` and falls back to a dedicated commit list/thread.
- `task_create()` duplicates ancestor task rctls without callbacks first because the process-to-new-task linkage is not established yet.
- `task_join()` must operate on a stopped or effectively single-threaded process and returns with `p_lock` held.
- Thread project changes wake waiting threads and clear `TS_PROJWAITQ` so they do not remain on an obsolete project wait queue.
- Final `task_end()` must not reference any process; membership is already gone.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/task.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/taskq.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/taskq.c

## Purpose

Implements illumos kernel task queues: a general-purpose asynchronous execution facility for deferring work to kernel threads. It supports traditional FIFO task queues, dynamic bucketed task queues with per-task worker threads, global `system_taskq`, CPU-percentage thread-count adjustment, suspend/resume, CPR integration, kstats, debug fault injection, and taskq lifetime management.

## Main Responsibilities

- Initialize taskq and taskq-entry caches.
- Create and destroy static and dynamic task queues.
- Dispatch work with normal allocation, no-sleep allocation, no-allocation, front insertion, no-backlog, and preallocated-entry variants.
- Maintain worker threads for fixed/static queues.
- Maintain dynamic taskq workers distributed across hash buckets plus a shared idle bucket.
- Provide backlog queues when dynamic taskqs are resource constrained.
- Grow dynamic buckets on demand and redistribute worker threads to buckets that have backlog but no workers.
- Support taskq suspension, resumption, waiting, empty checks, and membership checks.
- Adjust thread counts for `TASKQ_THREADS_CPU_PCT` queues when CPUs or processor sets change.
- Publish kstats for static and dynamic queues.

## Queue Types

### Static Task Queues

Static task queues use:

- A single circular doubly linked `tq_task` queue.
- A `tq_freelist` of reusable `taskq_ent_t` objects.
- One or more long-lived worker threads running `taskq_thread()`.
- FIFO execution when `nthreads == 1`; otherwise order is not guaranteed.
- `tq_threadlock` reader/writer synchronization to suspend execution.

Important paths:

- `taskq_dispatch()` allocates a task entry and enqueues it with `TQ_ENQUEUE()` or `TQ_ENQUEUE_FRONT()`.
- `taskq_dispatch_ent()` enqueues caller-provided preallocated entries and never frees them.
- `taskq_thread()` manages thread creation/exit, executes queued work, records runtime stats, and frees or preserves entries depending on preallocation.

### Dynamic Task Queues

Dynamic task queues use:

- `tq_buckets[0..tq_nbuckets-1]` for hashed work distribution.
- One extra idle bucket at `tq_buckets[tq_nbuckets]`.
- Per-bucket freelists of idle worker-backed entries.
- Per-bucket backlog lists for deferred work without an available worker.
- One ordinary backing taskq thread used only for overflow/extension jobs.
- Worker threads running `taskq_d_thread()` and servicing buckets through `taskq_d_svc_bucket()`.

Dispatch flow:

1. Hash `arg` and current CPU hint with `TQ_HASH()` to select a bucket.
2. Try `taskq_bucket_dispatch()` on the selected bucket.
3. Try `taskq_idlebucket_dispatch()` to move an idle worker to the selected bucket.
4. For sleepable dispatches, call `taskq_bucket_extend()` to create a worker and retry.
5. If allowed, enqueue the job on the bucket backlog.
6. Schedule `taskq_bucket_overflow()` on the backing queue to try extension or redistribution.

Dynamic task queues do not support `TQ_NOALLOC` or `TQ_FRONT` in public dispatch assertions. `TQ_NOQUEUE` prevents backlog use and is important for dependent tasks that could deadlock if queued behind each other.

## Key Entry Points

- `taskq_init()`
  Creates `taskq_ent_cache`, `taskq_cache`, the instance ID arena, and the CPU-percentage taskq list.

- `taskq_mp_init()`
  Registers CPU setup callbacks and synchronizes CPU-percentage queues after MP startup.

- `system_taskq_init()`
  Creates global dynamic `system_taskq`.

- `taskq_create()`, `taskq_create_instance()`, `taskq_create_proc()`, `taskq_create_sysdc()`
  Public constructors for kernel task queues, with optional instance IDs, target process, and system duty cycle scheduling.

- `taskq_create_common()`
  Shared constructor. It validates incompatible flags, computes bucket/thread limits, canonicalizes the name, prepopulates entries when requested, holds the taskq process’s zone, starts static backing thread(s), initializes dynamic buckets and idle workers, allocates instance IDs, and installs kstats.

- `taskq_destroy()`
  Deletes kstats, unregisters CPU-percentage queues, waits for queued/running work, stops static backing threads, frees cached entries, closes and drains dynamic buckets, waits for dynamic worker exit, releases the zone hold, and frees the taskq object.

- `taskq_dispatch()`
  Main public dispatch routine for both static and dynamic task queues.

- `taskq_wait()` / `taskq_wait_id()`
  Wait until all already queued/running work has completed. For dynamic queues it also waits for per-bucket allocation and backlog counts to drain.

- `taskq_suspend()` / `taskq_resume()` / `taskq_suspended()`
  Suspend and resume execution. Static queues block workers through `tq_threadlock`; dynamic queues mark buckets suspended so new dispatches fail or backlog.

- `taskq_member()`
  Checks `thread->t_taskq`.

## Important Internal Helpers

- `taskq_ent_alloc()` / `taskq_ent_free()`
  Manage static taskq entry allocation, freelist reuse, min/max allocation throttling, and max-allocation wait signaling.

- `taskq_ent_exists()`
  Checks whether a backing queue already has a specific `func(arg)` entry, used to avoid duplicate overflow extension jobs.

- `taskq_thread_create()`
  Creates static/backing taskq threads, including LWP-backed or duty-cycle threads when requested, and waits during initial creation until enough threads can service requests.

- `taskq_thread_wait()`
  Common wait helper with CPR-safe handling.

- `taskq_backlog_dispatch()` / `taskq_backlog_enqueue()`
  Allocate and enqueue dynamic backlog entries, update backlog stats, and wake a newly idle bucket worker if one appeared between dispatch attempts.

- `taskq_d_svc_bucket()`
  Dynamic worker bucket loop. It runs assigned work, drains backlog, puts the worker entry on the bucket freelist, waits briefly, and migrates away if idle.

- `taskq_d_thread()`
  Dynamic worker lifecycle. It services buckets, searches for backlog across buckets, migrates to the idle bucket, waits with timeout, exits when surplus/closing, and updates dynamic thread counts.

- `taskq_bucket_extend()`
  Creates a stopped worker thread, links its entry into a bucket freelist, accounts thread creation, and starts the thread. It observes memory pressure and max-thread limits.

- `taskq_bucket_overflow()`
  Asynchronous extension request that tries to create a worker, then redistributes if extension fails.

- `taskq_bucket_redist()`
  Redirects a worker from an over-provisioned donor bucket to a recipient bucket that has backlog and no threads.

- `taskq_kstat_update()` / `taskq_d_kstat_update()`
  Populate static and dynamic taskq kstats.

## Data Structures

- `taskq_t`
  Queue object with locks, dispatch/wait CVs, thread targets, flags, freelists, backing queue, dynamic bucket array, process/zone context, kstats, and counters.

- `taskq_ent_t`
  Work item and/or worker token. Stores list links, function, argument, either bucket pointer or flags, worker thread pointer, and per-entry CV.

- `taskq_bucket_t`
  Dynamic bucket with lock, backlog list, freelist, counts for allocated/free/backlog entries, flags, CV, total runtime, and statistics.

- `tqstat_t`
  Per-bucket statistics for hits, misses, overflow/backlog use, dispatch-triggered creates, thread creates/deaths, maximum thread count, and backlog peak.

## Locking Model

- Bucket locks are ordered before `tq_lock` where both are needed.
- Idle bucket lock precedes hashed bucket locks in documented multi-bucket cases.
- `taskq_cpupct_list` is protected by `cpu_lock`.
- `tq_lock` protects static queue state, thread target changes, allocation counts, and backing queue state.
- `tq_threadlock` gates execution for static queue suspend/resume.
- Dynamic bucket state is protected by each bucket’s `tqbucket_lock`.
- Dynamic per-bucket statistics are intentionally not strongly synchronized.

## Filesystem Relevance

Task queues are core kernel infrastructure used by filesystems, VFS, storage drivers, networking, STREAMS, ZFS-related services, and asynchronous cleanup paths. Filesystem code often needs to defer work out of interrupt, lock-held, or nonblocking contexts; `taskq.c` supplies that mechanism. The dynamic taskq behavior is especially relevant for high-volume storage/filesystem work that needs concurrency without a single global queue bottleneck.

## Notable Edge Cases

- `TASKQ_DYNAMIC`, `TASKQ_CPR_SAFE`, and `TASKQ_THREADS_CPU_PCT` are mutually incompatible.
- `TASKQ_DUTY_CYCLE` and `TASKQ_THREADS_LWP` cannot use `p0` as the taskq process.
- `TASKQ_NOQUEUE` on dynamic dispatch avoids backlog deadlocks for dependent tasks.
- Static taskq max allocation is advisory for sleeping dispatches; it throttles by waiting up to one second rather than blocking indefinitely on task completion.
- Dynamic worker creation is suppressed under low memory unless the target bucket has no workers.
- Dynamic taskq destruction avoids waking every idle-bucket worker at once; idle workers wake each other in sequence.
- Dynamic migration uses sentinel functions `taskq_d_migrate` and `taskq_d_redirect` that should never actually run.
- `taskq_wait()` must not be called from a taskq worker in the same queue.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/taskq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/timer.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/timer.c

## Purpose

Implements POSIX clock and per-process timer syscalls for illumos. It provides clock backend registration, `clock_gettime` / `clock_settime` / `clock_getres`, POSIX timer creation/deletion/set/get/overrun behavior, signal and event-port notification, timer cleanup on process/LWP lifecycle events, and 32-bit ABI conversions.

## Main Responsibilities

- Maintain a `clock_backend[CLOCK_MAX]` dispatch table.
- Allocate timers from `clock_timer_cache`.
- Enforce `timer_max`, dynamically raised to at least `4 * NCPU`.
- Store timers in each process’s growable `p_itimer` array.
- Lock individual timers using bits in `it_lock` plus `p_lock` and `it_cv`.
- Coordinate deletion with active lockers and backend callbacks.
- Deliver timer expiration by signal queue or event port.
- Support `SIGEV_NONE`, `SIGEV_SIGNAL`, `SIGEV_PORT`, and `SIGEV_THREAD` event forms, with thread notification mapped through event-port style handling.
- Clean up timers when processes exit, LWPs exit, LWPs bind, or associated ports close.

## Key Entry Points

- `clock_timer_init()`
  Creates timer cache and initializes `timer_max`.

- `clock_add_backend()` / `clock_get_backend()`
  Register and retrieve clock backends.

- `clock_settime()`
  Checks backend validity and `secpolicy_settime()`, copies in native or 32-bit timespec, validates it, and calls backend `clk_clock_settime()`.

- `clock_gettime()`
  Calls backend `clk_clock_gettime()` and copies out native or 32-bit timespec, checking 32-bit overflow.

- `clock_getres()`
  Handles POSIX NULL-`tp` no-op semantics, calls backend resolution function, and copies out native or 32-bit result.

- `timer_create()`
  Validates clock/backend and notification event, allocates sigqueue and `itimer_t`, finds or grows a per-process timer slot, initializes signal/port metadata, associates event-port resources when requested, calls backend `clk_timer_create()`, copies out timer ID, and releases the new timer.

- `timer_gettime()`
  Grabs the timer, calls backend `clk_timer_gettime()`, releases it, and copies out native or 32-bit interval spec.

- `timer_settime()`
  Optionally returns old time, copies in and validates new interval/value, grabs timer, calls backend `clk_timer_settime()`, and releases it.

- `timer_delete()`
  Grabs and deletes a timer.

- `timer_getoverrun()`
  Returns the last overrun value under `p_lock`.

- `timer_lwpexit()`
  Clears `it_lwp` for timers created by the exiting LWP.

- `timer_lwpbind()`
  Notifies backends when the creating LWP’s CPU binding changes.

- `timer_exit()`
  Deletes all timers for the current process and frees the process timer array.

## Internal Helpers

- `timer_lock()` / `timer_unlock()`
  Serialize access to an individual timer while holding `p_lock`.

- `timer_delete_locked()`
  Marks a timer for removal, waits for blockers to observe removal, clears the process timer slot, calls backend deletion, dissociates/free event-port resources, handles pending sigqueue lifetime, and frees the timer.

- `timer_grab()` / `timer_release()` / `timer_delete_grabbed()`
  Public-syscall-friendly wrappers around timer lookup and locking.

- `timer_get_id()`
  Finds an unused timer ID and grows `p_itimer` by doubling up to `timer_max`, handling races while `p_lock` is dropped for allocation.

- `timer_fire()`
  Backend callback for expirations. It increments pending/overrun state, sends event-port notifications, or queues timer signals with `sigaddqa()`.

- `timer_signal()`
  Signal-queue completion callback that transfers pending count to `it_overrun` and clears pending state.

- `timer_port_callback()`
  Event-port delivery callback that reports pending count as event count and resets the timer pending counter.

- `timer_close_port()`
  Scans current process timers and detaches/free event-port resources for the closing port.

## Locking and Lifetime Model

- `p_lock` protects process timer slot lookup, timer lock bits, deletion state, and signal timer overrun access.
- `it_mutex` protects `it_pending`, port event resources, and races between `timer_fire()` and `timer_signal()`.
- Deletion sets `ITLK_REMOVE` before removing the process slot, ensuring new `timer_grab()` calls fail.
- Backend `clk_timer_delete()` must guarantee `timer_fire()` has completed and will not be called again for that timer.
- Pending signal queue memory is freed immediately only when no pending signal references it; otherwise `sq_func` is set to `NULL` for synchronous freeing later in `siginfofree()`.

## Filesystem Relevance

This is timer/syscall infrastructure rather than filesystem logic. It still matters to filesystem behavior because timed waits, signal interruption, event ports, asynchronous daemons, and timeout-driven kernel/user workflows depend on accurate clock and timer delivery. Filesystem services using event ports or signal-driven control paths rely on this substrate.

## Notable Edge Cases

- `clock_getres(clock, NULL)` returns success without validating the clock ID, matching POSIX behavior noted in the source.
- `timer_create()` uses short `oldsigevent` copyin for binary compatibility.
- 32-bit callers get explicit timespec/itimerspec conversion and overflow checks.
- `SIGEV_THREAD` and `SIGEV_PORT` both allocate event-port resources.
- Timer IDs are array indexes and may skip newly freed lower slots after a racing resize.
- If a timer’s creating LWP exits, behavior is documented as undefined to users; illumos clears `it_lwp` and leaves backend state otherwise intact.
- `timer_close_port()` iterates up to `timer_max` using `timer_grab()`, so sparse timer arrays are handled by failed grabs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/timer.c -->