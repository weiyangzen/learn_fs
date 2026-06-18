# Group Research: group_1400_openbsd_src_sources_os_bsd_openbsd_src_sys_kern_kern_clock_c_source_16692f60ad94

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/openbsd-src`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_clock.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_clock.c

## Purpose
Implements OpenBSD's high-level clock handling: initializing clock rates, maintaining hardclock ticks, converting time values to ticks, handling profiling/statistical clock samples, and exporting clock rate data via sysctl.

## Main Responsibilities
- Initializes `hardclock_period`, `statclock_avg`, `statclock_min`, `statclock_mask`, and `profclock_period` in `initclocks()`.
- Starts machine-specific clock setup via `cpu_initclocks()` and `cpu_startclock()`.
- Maintains global `ticks` and `jiffies` in `hardclock()`.
- Updates timeout machinery through `timeout_hardclock_update()`.
- Converts `timeval` and `timespec` durations to scheduler ticks with overflow-aware rounding in `tvtohz()` and `tstohz()`.
- Starts/stops profiling clocks per process using `startprofclock()` and `stopprofclock()`.
- Charges CPU time and resource usage in `statclock()`.
- Reports `struct clockinfo` through `sysctl_clockrate()`.

## Key Data
- `stathz`, `profhz`, `profprocs`: statistics/profiling clock rates and active profiling count.
- `ticks`: initialized near `INT_MAX` to exercise wraparound behavior.
- `jiffies`: volatile compatibility/global tick counter.
- `statclock_is_randomized`: controls whether statistical clock advances by random periods.

## Notable Control Flow
`statclock()` chooses user/kernel/interrupt/idle/spin accounting based on `clockframe` state, updates per-CPU `spc_cp_time` under `pc_lock`, updates per-thread `tusage`, and calls `schedclock()` every fourth statistical tick.

## Dependencies
Uses CPU clock hooks, timeout subsystem, scheduler accounting, UVM vmspace sizing, `clockintr` request helpers, and sysctl support.

## Research Notes
This file is the policy/accounting layer above `kern_clockintr.c`; it does not manage the per-CPU event queue itself.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_clockintr.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_clockintr.c

## Purpose
Implements the per-CPU clock interrupt scheduling framework used by hardclock, statclock, itimer, profiling clock, round-robin scheduling, and arbitrary bound clock interrupt callbacks.

## Main Responsibilities
- Initializes each CPU's `clockqueue` and optional hardware `intrclock`.
- Binds/unbinds `struct clockintr` objects to CPUs.
- Maintains a sorted pending queue by nanosecond expiration.
- Dispatches expired clock interrupt callbacks from `clockintr_dispatch()`.
- Rearms or triggers the hardware interrupt clock when the next expiration changes.
- Provides deterministic and randomized clock request advancement.
- Aggregates clock interrupt statistics for `sysctl_clockintr()`.
- Provides DDB display helpers for pending/running/idle clock interrupts.

## Key Entry Points
- `clockintr_cpu_init()`: prepares a CPU clock queue, staggers periodic events, binds primary CPU hardclock.
- `clockintr_trigger()`: starts dispatch when an intrclock exists.
- `clockintr_dispatch()`: runs expired callbacks, handles reschedule requests, records lateness/earliness/spurious stats.
- `clockintr_advance()` and `clockrequest_advance()`: advance periodic events.
- `clockrequest_advance_random()`: advances randomized statclock periods.
- `clockintr_cancel()` / `clockintr_cancel_locked()`: remove pending interrupts and suppress in-flight rescheduling.
- `clockintr_bind()` / `clockintr_unbind()`: attach/detach callbacks from a CPU queue.
- `clockqueue_pend_insert()` / `clockqueue_pend_delete()`: sorted queue operations.
- `nsec_advance()`: advances an expiration past `now`, returning skipped periods.

## Key Data
- `struct clockqueue`: owns mutex, pending queue, all-bound queue, current request, stats, running interrupt, and optional hardware intrclock.
- `struct clockrequest`: passed to callbacks to reschedule themselves.
- `CQ_IGNORE_REQUEST` prevents a running interrupt from being requeued after cancellation/rescheduling races.
- `CQ_NEED_WAKEUP` supports `CL_BARRIER` unbind semantics.

## Concurrency
All queue mutation is protected by `cq_mtx` at `IPL_CLOCK`. Dispatch drops the mutex while invoking callbacks, then reacquires it to process reschedule/cancel state.

## Research Notes
The queue is simple sorted insertion rather than a heap. The design favors small per-CPU event sets and explicit callback rescheduling.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_clockintr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_descrip.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_descrip.c

## Purpose
Implements process file descriptor tables, file object allocation/lifetime, descriptor duplication, close, fcntl, flock, fd-table fork/exec behavior, and `/dev/fd` duplication support.

## Main Responsibilities
- Initializes file and filedesc pools in `filedesc_init()`.
- Maintains descriptor allocation bitmaps with `fd_used()`, `fd_unused()`, `find_next_zero()`, and `find_last_set()`.
- Provides safe file reference lookup with `fd_getfile()` and `fd_getfile_mode()`.
- Implements `dup`, `dup2`, `dup3`, and `fcntl(F_DUPFD*)` via `dodup3()` and `finishdup()`.
- Implements `fcntl()` flags, async ownership, POSIX advisory locks, and lock queries.
- Implements `close`, `fstat`, `fpathconf`, `flock`, `closefrom`, and `getdtablecount`.
- Allocates and expands fd tables through `fdalloc()` and `fdexpand()`.
- Creates file objects with `falloc()` / `fnew()` and destroys them with `closef()` / `fdrop()`.
- Shares, copies, and frees file descriptor tables for fork/exit with `fdshare()`, `fdcopy()`, and `fdfree()`.
- Handles close-on-exec and close-on-fork in `fdprepforexec()`.

## Key Data
- Global `filehead`, `numfiles`, `file_pool`, `fdesc_pool`.
- `fhdlk`: protects global file list and must work with and without `KERNEL_LOCK()`.
- `fd_fplock`: synchronizes descriptor slots with `fd_getfile()`.
- `fd_lomap` / `fd_himap`: two-level bitmap for free descriptor search.
- `UF_EXCLOSE`, `UF_FORKCLOSE`, `UF_PLEDGEOPEN`, `UF_PLEDGED`: per-fd flags.

## Notable Behavior
- `finishdup()` installs the new file pointer under `fd_fplock`, copies/adjusts fd flags, closes replaced descriptors after dropping the fd table lock, and notifies kqueue via `knote_fdclose()`.
- `fdcopy()` skips close-on-fork descriptors, kqueue descriptors, and descriptors whose reference count is too high.
- `closef()` handles POSIX record lock cleanup before dropping the final file reference.
- `dupfdopen()` supports `/dev/fd/N`, with additional checks for sugid execution.

## Dependencies
Interacts heavily with VFS/vnodes, kqueue close notifications, pledge, ktrace, resource limits, sockets/pipes, credentials, and advisory locking.

## Research Notes
The file carefully separates descriptor-table locking from file-reference locking so concurrent close/dup and lookup can be made race-resistant.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_descrip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_event.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_event.c

## Purpose
Implements OpenBSD kqueue/kevent, knote lifecycle, filter dispatch, poll/select backing kqueues, process/signal/timer/user/file filters, and klist notification infrastructure.

## Main Responsibilities
- Initializes kqueue and knote pools.
- Provides kqueue file operations (`kqueueops`) for descriptor-backed kqueues.
- Creates kqueues through `sys_kqueue()`, `sys_kqueue1()`, and `dokqueue()`.
- Processes changelists and event delivery through `sys_kevent()`.
- Registers, modifies, enables/disables, and deletes knotes via `kqueue_register()`.
- Scans active event queues with marker knotes in `kqueue_scan()`.
- Purges/closes/terminates kqueues safely.
- Supports poll/select through per-thread `p_kq`, serial IDs, and `kqpoll_init()` / `kqpoll_done()` / `kqpoll_exit()`.
- Provides generic `klist` operations for subsystems that own event sources.

## Supported Filters
- `EVFILT_READ` / `WRITE` / `VNODE` / `DEVICE` / `EXCEPT`: file descriptor filters delegated to fileops `fo_kqfilter`.
- `EVFILT_PROC`: process lifecycle events, including `NOTE_EXIT`, `NOTE_FORK`, `NOTE_TRACK`, and `NOTE_EXEC`.
- `EVFILT_SIGNAL`: signal delivery counts.
- `EVFILT_TIMER`: timeout-backed relative/absolute timers with unit validation.
- `EVFILT_USER`: user-triggered events with fflag control operations.
- Special internal filters: `seltrue_filtops`, `dead_filtops`, and `badfd_filtops`.

## Key Data
- `struct kqueue`: active queue, mutex, knote hash/list tables, refcount, state flags, fd table owner.
- `struct knote`: registered event, filterops, status flags, file/process/timer/user state.
- `kqueue_ps_list_lock`: serializes process/signal knote list changes.
- `kq_usereventsmax`: per-process limit for timer/user events.

## Notable Control Flow
`kqueue_register()` validates filter and identifier, finds or allocates a knote, attaches it to the kqueue's fd list or hash, calls filter attach/modify/delete callbacks outside `kq_lock` where needed, handles fd-close races with `fd_checkclosed()`, and activates ready knotes.

`kqueue_scan()` sleeps if no events are active, inserts start/end marker knotes to bound a scan, acquires knotes one at a time, processes filter state, applies oneshot/clear/dispatch rules, handles revoked vnode dead filters, and requeues persistent events.

## Lifetime and Concurrency
Knotes use `KN_PROCESSING` and `KN_WAITING` to serialize concurrent scan/register/remove paths. `knote_acquire()` can drop locks and force callers to restart. Kqueue references are held during scans via `KQREF()` / `KQRELE()`.

## Dependencies
Tied to fd close notifications from `kern_descrip.c`, process fork/exit from `kern_fork.c` and `kern_exit.c`, timeout subsystem, VFS fileops, scheduler task queues, pledge, ktrace, and signal state.

## Research Notes
This is a central event fanout layer. It combines descriptor-indexed knote arrays for fd filters with a hash table for non-fd filters.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_event.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_exec.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_exec.c

## Purpose
Implements `execve(2)` image replacement: executable validation, argument/environment copying, VM command execution, stack setup, credentials/security transitions, fd cleanup, and shared signal/timekeep page mapping.

## Main Responsibilities
- Frees image-loader package allocations with `exec_free_package()`.
- Validates executable vnodes in `check_exec()`.
- Implements `sys_execve()` end to end.
- Copies argv/env strings and auxiliary pointer space with `copyargs()`.
- Creates and maps the shared signal trampoline object in `exec_sigcode_map()`.
- Creates and maps the shared read-only timekeep page in `exec_timekeep_map()`.

## Key Exec Flow
1. Enters single-threading and marks `PS_INEXEC`.
2. Performs namei lookup with pledge/unveil exec constraints.
3. Uses `check_exec()` to verify regular executable file, mount flags, execute permission, and loader compatibility.
4. Copies fake interpreter args, argv, and env into a kernel arg buffer.
5. Calculates stack gap randomization and final stack footprint.
6. Commits by killing other threads, clearing profiling, and replacing the vmspace.
7. Runs loader VM commands and maps stack/guard regions.
8. Copies argv/env and `ps_strings` to user stack.
9. Resets fd flags, signals, TCB, kbind state, pledge/unveil state, timers, and accounting details.
10. Handles setuid/setgid credential transitions and ensures fd 0/1/2 are open for sugid exec.
11. Maps timekeep and signal trampoline pages, calls ELF fixup and machine register setup, then returns `EJUSTRETURN`.

## Security and Policy
- Honors `MNT_NOEXEC` and `MNT_NOSUID`.
- Blocks sugid programs under exec promises.
- Clears unveil state unless exec pledge is active.
- Clears tracing for unprivileged traced setuid/setgid exec.
- Sets `PS_SUGID`, `PS_SUGIDEXEC`, and image flags such as `PSI_WXNEEDED`, `PSI_PROFILE`, `PSI_NOBTCFI`.

## Failure Modes
Before commit, errors unwind package, vnode, namei, and arg-buffer state. After VM replacement, fatal failures call `exit1(..., SIGABRT, EXIT_NORMAL)`.

## Dependencies
Uses VFS/namei, exec switch loaders, UVM, signal subsystem, file descriptors, pledge/unveil, credentials, ktrace, timers, and machine-specific register/mapping hooks.

## Research Notes
This file is the process image transition boundary; it coordinates most per-process security and address-space state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_exit.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_exit.c

## Purpose
Implements process/thread exit, zombie creation, wait/waitid/wait4, reparenting, ptrace orphan handling, and deferred resource reclamation by the reaper thread.

## Main Responsibilities
- Implements `sys_exit()` and `sys___threxit()`.
- Performs main exit teardown in `exit1()`.
- Schedules post-switch cleanup with `exit2()`.
- Frees proc structures with `proc_free()`.
- Runs the `reaper()` kernel thread to free uareas/vmspace and notify parents.
- Implements wait logic in `dowait6()`, `sys_wait4()`, and `sys_waitid()`.
- Finishes zombie collection in `proc_finish_wait()`.
- Handles ptrace parent restoration with `process_untrace()`.
- Reparents children with `process_reparent()`.
- Fully destroys processes with `process_zap()`.

## Key Exit Flow
`exit1()` marks the thread exiting, coordinates single-threaded process exit, records exit status, detaches the thread from active lists, aggregates usage, exits poll kqueue state, closes fd tables, cancels timers, clears tracing/unveil/pins, tears down VM, removes proc/process from lookup lists, reparents children, accumulates rusage, calls `cpu_exit()`, deactivates pmap, and enters scheduler exit.

`exit2()` runs after the dead thread is no longer executing on its old stack/vmspace; it queues the proc on `deadproc` and wakes `reaper()`.

`reaper()` frees remaining VM resources, marks processes as zombie, fires `knote_processexit()`, posts `SIGCHLD`, wakes waiters, or destroys no-zombie processes directly.

## Wait Semantics
`dowait6()` supports `P_ALL`, `P_PID`, and `P_PGID`; handles exited, trapped, stopped, and continued children; supports `WNOWAIT` and `WNOHANG`; and checks the orphan list for ptrace-related parent handoff cases.

## Concurrency
Exit uses `ps_mtx`, deadproc spin-style mutex, process flags, and no-sleep sections after removing proc from global lookup lists. Resource-heavy VM cleanup is deferred to the reaper.

## Dependencies
Interacts with scheduler, UVM, fd cleanup, kqueue process notes, signals, ptrace, accounting, ktrace, semaphores, pledge/unveil cleanup, process groups, and resource limits.

## Research Notes
The split between `exit1()`, `exit2()`, and `reaper()` is central: immediate exit cannot sleep after a certain point, while final VM/uarea reclamation may block.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_exit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_fork.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_fork.c

## Purpose
Implements process fork, vfork, thread fork, kernel/system process creation support, pid/tid allocation, and machine-independent trampoline setup for new threads.

## Main Responsibilities
- Implements `sys_fork()`, `sys_vfork()`, and `sys___tfork()`.
- Allocates thread (`struct proc`) state in `thread_new()`.
- Initializes process (`struct process`) state in `process_initialize()` and `process_new()`.
- Enforces global and per-user thread/process limits in `fork_check_maxthread()` and `fork1()`.
- Schedules new runnable threads with `fork_thread_start()`.
- Creates user threads with `thread_fork()`.
- Allocates random tids and pids with `alloctid()` and `allocpid()`.
- Prevents fast pid reuse via `oldpids[]` and `freepid()`.
- Performs trampoline setup in `proc_trampoline_mi()`.

## Key Fork Flow
`fork1()` checks limits, increments process counts, allocates a U-area, creates a proc and process, copies/shares fd table and vmspace according to flags, copies signal/credential/resource state, performs `cpu_fork()`, assigns pid/tid, links into global pid/process lists and parent/pgid lists, handles ptrace fork reporting, clears embryo state, schedules the child, sends fork knotes, updates fork stats, and handles `FORK_PPWAIT` synchronization.

## Thread Fork Flow
`thread_fork()` creates a new `P_THREAD` proc in the existing process, shares fd/vmspace pointers, copies CPU context with stack/TCB, links into `ps_threads`, copies suspend/single-thread state if needed, optionally copies out tid, and schedules it.

## Key Flags
- `FORK_FORK`, `FORK_VFORK`, `FORK_PPWAIT`
- `FORK_SHAREVM`, `FORK_SHAREFILES`
- `FORK_PTRACE`
- `FORK_NOZOMBIE`, `FORK_SYSTEM`, `FORK_IDLE`

## Dependencies
Uses UVM fork/share, fd copy/share, signal action copy, limits, credentials, scheduler, process groups, ptrace, ktrace, kqueue process fork notes, and machine-specific `cpu_fork()`.

## Research Notes
PIDs are randomized except PID 1. TIDs are randomized within `TID_MASK` and exposed to userland with `THREAD_PID_OFFSET`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_fork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_intrmap.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_intrmap.c

## Purpose
Provides a generic interrupt-to-CPU mapping helper for devices with multiple interrupt vectors/rings.

## Main Responsibilities
- Builds a reference-counted snapshot of CPUs usable for interrupts.
- Excludes secondary SMT threads when `__HAVE_CPU_TOPOLOGY` is available.
- Chooses an interrupt count bounded by requested count, maximum count, and usable CPU count.
- Optionally rounds interrupt count down to a power of two.
- Builds a per-device CPU map offset by device unit to spread interrupts across devices.
- Exposes mapping count and ring-to-CPU lookup.

## Key Entry Points
- `intrmap_create()`: creates an interrupt map for a device.
- `intrmap_destroy()`: frees map and drops CPU snapshot reference.
- `intrmap_count()`: returns number of interrupts/rings.
- `intrmap_cpu()`: returns the CPU assigned to a ring.

## Key Data
- `struct intrmap_cpus`: refcounted usable CPU array.
- `struct intrmap`: interrupt count, grid size, CPU snapshot, per-ring CPU indices.
- Global `intrmap_cpus`, `intrmap_ncpu`, and `intrmap_lock`.

## Notable Algorithm
`intrmap_create()` picks a grid divisor of usable CPU count and offsets by `dv_unit`, so devices with the same number of rings are distributed rather than all starting on CPU zero.

## Dependencies
Uses device unit numbers, global CPU enumeration, malloc/free, refcounts, and rwlock protection.

## Research Notes
This is device-agnostic infrastructure adapted from network ring mapping ideas.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_intrmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_kthread.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_kthread.c

## Purpose
Provides kernel thread creation, exit, and deferred creation queue support.

## Main Responsibilities
- Creates kernel threads with `kthread_create()`.
- Exits current kernel thread with `kthread_exit()`.
- Queues deferred thread creation callbacks with `kthread_create_deferred()`.
- Runs deferred callbacks once normal kernel-thread creation is available via `kthread_run_deferred_queue()`.

## Key Behavior
`kthread_create()` calls `fork1()` from `proc0` with `FORK_SHAREVM`, `FORK_SHAREFILES`, `FORK_NOZOMBIE`, and `FORK_SYSTEM`, then sets the process command name.

`kthread_exit()` logs non-zero exits and calls `exit1()`.

Deferred creation stores callbacks in a `SIMPLEQ` until `kthread_create_now` is set.

## Dependencies
Uses `fork1()`, `exit1()`, proc0, malloc/free, and kernel locking.

## Research Notes
Kernel threads are implemented as system processes/threads sharing proc0 resources and normally do not leave waitable zombies.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_kthread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_ktrace.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_ktrace.c

## Purpose
Implements kernel tracing (`ktrace`) state management, trace record construction, permission checks, trace syscall control, and append writes to trace vnodes.

## Main Responsibilities
- Sets and clears per-process trace state with `ktrsettrace()` and `ktrcleartrace()`.
- Initializes trace headers with pid/tid/command metadata.
- Emits trace records for syscall entry/return, namei, genio, signals, structs, user records, exec args/env, pledge failures, and pinsyscall events.
- Implements `sys_ktrace()` and `doktrace()` to enable/disable tracing for pid, process group, or descendants.
- Recursively applies operations with `ktrsetchildren()`.
- Writes records with `ktrwrite()`, `ktrwrite2()`, and `ktrwriteraw()`.
- Enforces trace permission policy with `ktrcanset()`.

## Key Data
- Per-process `ps_traceflag`, `ps_tracevp`, and `ps_tracecred`.
- `KTRFAC_ROOT` marks tracing established by root and restricts later modification.
- Trace records are written as `struct ktr_header` plus up to two payload iovecs.

## Notable Behavior
- Trace vnode references and credentials are held while active; vnode `v_writecount` is adjusted.
- `ktrwriteraw()` appends with `IO_UNIT | IO_APPEND`.
- Any write failure logs a notice and clears tracing for all processes using that vnode/credential pair plus the current process.
- Trace construction sets `P_INKTR` to avoid tracing recursion.

## Security
`ktrcanset()` allows tracing only when caller real uid/gid match target real/saved ids, target is not sugid/root-traced, or caller is root.

## Dependencies
Uses VFS/namei, credentials, process lists, syscalls, pledge/unveil for opening trace files, scheduler pause for large trace writes, ktrace points from other kernel files, and kernel lock for vnode writes.

## Research Notes
The trace output path is intentionally conservative: failures disable tracing broadly for the affected output.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_ktrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_lock.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_lock.c

## Purpose
Implements OpenBSD machine-independent kernel lock, mutex primitives, DDB mutexes, and producer/consumer generation locks.

## Main Responsibilities
- Initializes and wraps `kernel_lock`.
- Implements MI multiprocessor ticket-style `__mp_lock` when configured.
- Implements MI mutexes with fast atomic acquire and slow parking/waiter path when configured.
- Provides uniprocessor mutex fallback.
- Provides DDB mutex enter/leave.
- Initializes WITNESS lock metadata.
- Provides `pc_lock` producer/consumer generation protocol.

## Key Entry Points
- `_kernel_lock_init()`, `_kernel_lock()`, `_kernel_unlock()`, `_kernel_lock_held()`.
- `__mp_lock()`, `__mp_unlock()`, `__mp_release_all()`, `__mp_acquire_count()`, `__mp_lock_held()`.
- `mtx_enter_try()`, `mtx_enter()`, `mtx_leave()`.
- `db_mtx_enter()`, `db_mtx_leave()`.
- `pc_sprod_enter/leave()`, `pc_mprod_enter/leave()`, `pc_cons_enter/leave()`.

## Mutex Design
The MP mutex fast path CASes `mtx_owner` from zero to current CPU. The contended path spins briefly, then uses hashed parking lots with waiter records and a low bit in owner state to indicate waiters. IPL raising/restoration is handled per mutex via `mtx_wantipl` and `mtx_oldipl`.

## MP Lock Design
The MI MP lock stores per-CPU recursion depth/ticket and global `mpl_users`/`mpl_ticket`. Lock acquisition takes a ticket and spins until served; recursion is tracked per CPU.

## pc_lock Design
`pc_lock` uses an odd/even generation counter. Producers make generation odd while updating and even after completion; consumers retry if the generation changes or is observed odd.

## Dependencies
Uses atomic operations, interrupt priority control, scheduler spin accounting, WITNESS, DDB, percpu cacheline alignment, and memory barriers.

## Research Notes
This file contains low-level synchronization primitives used by many other files in this group, especially clock/accounting and descriptor/event paths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_malloc.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_malloc.c

## Purpose
Implements the kernel `malloc(9)` allocator over `kmem_map`, including bucketed small allocations, large page allocations, diagnostics, statistics, sysctl reporting, DDB printing, and overflow-safe `mallocarray()`.

## Main Responsibilities
- Computes bucket index with `BUCKETINDX()`.
- Allocates memory with `malloc()`.
- Frees memory with `free()`.
- Sizes kernel malloc arena with `kmeminit_nkmempages()`.
- Initializes `kmem_map`, buckets, usage metadata, stats names, and bucket strings in `kmeminit()`.
- Exports allocator state through `sysctl_malloc()`.
- Prints DDB malloc stats with `malloc_printit()`.
- Provides `mallocarray()` overflow checking.

## Allocation Behavior
Small allocations use power-of-two buckets. If a bucket freelist is empty, pages are allocated from `kmem_map`, split into bucket-sized elements, poisoned in diagnostic builds, and linked onto the freelist. Large allocations above `MAXALLOCSAVE` allocate rounded page ranges directly and record page count in `kmemusage`.

## Free Behavior
`free()` determines allocation size from `kmemusage`, validates bounds/alignment in diagnostic builds, detects likely double free by checking poison state and freelist membership, poisons freed objects, and returns small objects to bucket freelists or large objects to `kmem_map`.

## Key Data
- `kmem_map`, `kmembase`, `kmemlimit`, `kmemusage`.
- `bucket[MINBUCKET + 16]`.
- Optional `kmemstats[M_LAST]`.
- `malloc_mtx` protects bucket/stat state.
- `memname[]`, `memall`, and `buckstring` support diagnostics/sysctl.

## Arena Sizing
`kmeminit_nkmempages()` derives arena pages from physical memory, with caps based on `VM_KERNEL_SPACE_SIZE`, unless `nkmempages` is preconfigured.

## Dependencies
Uses UVM kernel maps, malloc type definitions, sysctl, mutexes, tracepoints, DDB, and optional KMEMSTATS/DIAGNOSTIC support.

## Research Notes
`mallocarray()` is a small but important safety wrapper: it panics or returns NULL on multiplication overflow depending on `M_CANFAIL`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_physio.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_physio.c

## Purpose
Implements raw physical I/O between devices and user buffers, bypassing the buffer cache, plus the default `minphys()` transfer limiter.

## Main Responsibilities
- Validates block-aligned `uio_offset`.
- Allocates a temporary `struct buf` from `bufpool`.
- Iterates user iovecs and splits transfers according to `minphys`.
- Locks user memory for device I/O with `uvm_vslock_device()`.
- Maps user buffers for device strategy routines using direct device mapping or `vmapbuf()`.
- Calls the supplied device `strategy()` routine.
- Waits for `B_DONE`, handles `B_ERROR`, updates iovec/uio accounting, and unlocks memory.
- Frees temporary buffer state.
- Caps transfer size to `MAXPHYS` in `minphys()`.

## Key Flow
For each iovec segment, `physio()` sets `B_BUSY | B_PHYS | B_RAW | B_READ/B_WRITE`, sets `b_blkno` from `uio_offset`, limits `b_bcount`, locks/maps the user address range, invokes strategy, sleeps at `splbio()` until completion, unmaps/unlocks, computes completed bytes from `b_bcount - b_resid`, advances the uio, and exits on error or short transfer.

## Safety Checks
- Rejects non-`DEV_BSIZE`-aligned offsets.
- Avoids signed overflow by limiting `b_bcount` to `LONG_MAX` before `minphys`.
- Asserts `minphys` and strategy do not produce invalid counts.

## Dependencies
Uses buffer pool, bio priority/sleep, UVM device memory locking, vmap/vunmap buffer helpers, and device strategy callbacks.

## Research Notes
This is a classic BSD raw I/O helper. It deliberately bypasses caching and relies on caller-provided strategy/minphys routines for device-specific constraints.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_physio.c -->