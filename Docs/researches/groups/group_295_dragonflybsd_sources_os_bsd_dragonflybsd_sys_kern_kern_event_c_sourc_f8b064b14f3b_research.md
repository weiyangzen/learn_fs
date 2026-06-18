# Group Research: DragonFlyBSD `sys/kern` process, event, jail, interrupt, and kernel file helpers

Scope: `Docs/research_subset_a.md`; source tree `sources/os/bsd/dragonflybsd`.

This grouped research covers nine DragonFlyBSD kernel files under `sys/kern`. The files are not filesystem implementations themselves, but they are core OS/VFS-adjacent infrastructure: kqueue/knote event delivery over files, processes, timers, and filesystems; exec/fork/exit lifecycle handling around vnodes, namecache handles, vmspaces, and file descriptor tables; jail root and VFS capability enforcement; kernel file pointer helpers; interrupt infrastructure; I/O scheduling pressure; and process information export.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_event.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_event.c

## Role

Implements DragonFlyBSD's kqueue/kevent core: creation of `DTYPE_KQUEUE` file objects, registration/modification/deletion of knotes, event scanning/copyout, wakeups, filter dispatch, per-kqueue and per-knote lifecycle management, and a precise sleep helper for short kevent timeouts. It derives from FreeBSD kqueue code but has DragonFly-specific token, pool-token, LWP, and file descriptor close-race handling.

## Major Entry Points

- `sys_kqueue()` allocates a file descriptor and `struct kqueue`, initializes pending/list queues, installs `kqueueops`, and attaches it to the caller's file descriptor table.
- `sys_kevent()` validates the descriptor as `DTYPE_KQUEUE`, copies in an optional timeout, and calls `kern_kevent()`.
- `kern_kevent()` processes changelist registrations via a caller-supplied copyin function, posts registration errors/receipts, computes timeout deadlines, scans active events, copies out events, and sleeps/reloads markers when no events are pending.
- `kqueue_register()` handles batched registration. It preloads file pointers for fd-backed filters, serializes registration on `kq_regtd`, finds existing knotes by fd klist or kqueue hash, allocates/caches knotes, attaches filters, handles `EV_ADD`, `EV_DELETE`, `EV_ENABLE`, `EV_DISABLE`, `EV_RECEIPT`, `EV_ONESHOT`, `EV_CLEAR`, `EV_DISPATCH`, and fd close races.
- `kqueue_scan()` walks `kq_knpend` with marker knotes, acquires each knote, revalidates fd-backed notes against `fd_closedcounter`, processes active filters, emits `struct kevent`s, clears/requeues/deletes notes according to flags, and respects marker boundaries for concurrent scans.
- `kqueue_close()` terminates all knotes, drops async owner state, and frees the kqueue.

## Filters Implemented Here

- File-backed filters use `filt_fileattach()` to delegate to the underlying file object's `fo_kqfilter()`.
- Kqueue read filter (`EVFILT_READ` on a kqueue) reports pending event count through `filt_kqueue()`.
- Process filter attaches to live or zombie processes via `pfind()`/`zpfind()`, checks jail visibility with `PRISON_CHECK`, tracks `NOTE_EXIT`, `NOTE_FORK`, `NOTE_EXEC`, `NOTE_CHILD`, `NOTE_TRACK`, and detaches on exit.
- Timer filter allocates a callout per knote, enforces global `kern.kq_calloutmax`, sets `EV_CLEAR`, increments `kn_data` on expiration, and handles callout/delete races with `KN_PROCESSING`, `KN_REPROCESS`, and `KN_DELETING`.
- User filter implements `EVFILT_USER`, including `NOTE_TRIGGER`, `NOTE_FFNOP`, `NOTE_FFAND`, `NOTE_FFOR`, `NOTE_FFCOPY`, and compatibility handling for `EV_CLEAR` during modification.
- Filesystem filter (`EVFILT_FS`) uses a global `fs_klist`, sets `EV_CLEAR`, and ORs hints into `kn_fflags`.

## Internal Mechanics

- Knotes use status bits such as `KN_PROCESSING`, `KN_REPROCESS`, `KN_WAITING`, `KN_DELETING`, `KN_DETACHED`, `KN_ACTIVE`, `KN_QUEUED`, and `KN_DISABLED`.
- `knote_acquire()` and `knote_release()` are the core concurrency protocol. They require the related kqueue token and cause contending threads to sleep/retry because a knote may be stale after blocking.
- `KNOTE_ACTIVATE()` marks a knote active and queues it if not already queued or disabled.
- `knote_attach()` indexes a knote either on the referenced file's `f_klist` for fd filters or on the kqueue's hash table for non-fd filters, and also links it into `kq_knlist`.
- `knote_drop()` removes the knote from both indexes, dequeues it if necessary, drops held file references for fd filters, and returns the object to a per-CPU knote cache.
- `knote()`, `knote_insert()`, `knote_remove()`, `knote_assume_knotes()`, and `knote_fdclose()` are exported helper paths used by other subsystems to notify, move, attach, detach, or close fd-associated knotes.

## VFS/File-System Relevance

- Kqueues are file objects and integrate through `struct fileops`; read/write return `ENXIO`, ioctl supports `FIOASYNC` and `FIOSETOWN`, stat reports pending event count as FIFO-like metadata.
- Fd-backed filters depend on underlying file/vnode/socket/device implementations through `fo_kqfilter()`.
- `knote_fdclose()` removes all knotes that reference a closing descriptor and is part of file descriptor/VFS close correctness.
- `EVFILT_FS` exposes filesystem-wide notifications through the global `fs_klist`.
- Process filters interact with exec/fork/exit paths via `KNOTE(&p->p_klist, NOTE_...)`.

## Concurrency and Synchronization

- Uses LWKT pool tokens for kqueues and klists rather than a single global lock.
- Registration is serialized per kqueue with `kq_regtd` and `KQ_REGWAIT` while still supporting recursive registration from `NOTE_TRACK`.
- Scan markers prevent concurrent scans from duplicating or skipping events and support reload/keep/insert modes.
- Close races are addressed by snapshotting `fd_closedcounter`, holding file pointers, and checking `checkfdclosed()` after possible blocking attachment and during scan.
- Non-MPSAFE filters are wrapped with `get_mplock()`/`rel_mplock()`.
- Timer callout paths cannot sleep, so they open-code acquisition behavior and use reprocess flags.

## Tunables and Limits

- `kern.kq_calloutmax` caps timer callouts.
- `kern.kq_checkloop` guards against pathological kevent scan loops.
- `kern.kq_sleep_threshold` determines when precise timeout sleeping should avoid busy looping.
- Per-CPU knote caches retain up to `KNOTE_CACHE_MAX` knotes each.

## Research Notes

- This file is central to polling/select emulation and event notification for the rest of the kernel.
- Any analysis of vnode readiness, file close behavior, process lifecycle notifications, or filesystem event hints should include this file's knote state machine.
- The most fragile areas are the intentional stale-pointer retry loops, fd close interlocks, timer callout deletion races, and marker-based scanning semantics.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_event.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_exec.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_exec.c

## Role

Implements process image replacement for `execve()` and `fexecve()`: argument/environment copyin, executable vnode lookup/open/permission checks, image activator dispatch, first-page mapping, vmspace replacement, user stack construction, descriptor and signal cleanup, setuid/setgid credential handling, text vnode/namecache tracking, and exec image activator registration.

## Major Entry Points

- `sys_execve()` checks `SYSCAP_NOEXEC`, initializes a name lookup for the user path, copies arguments, calls `kern_execve()`, frees args, and aborts the process on lethal post-vmspace errors.
- `sys_fexecve()` obtains a vnode-backed file from a descriptor, requires read-only/readable access, supplies a `/dev/fd/N` path for interpreted scripts, and calls `kern_execve()` with the file.
- `kern_execve()` is the central exec path. It resolves the executable vnode, checks permissions, maps the first page, dispatches image activators, handles interpreter recursion, creates the new stack, unshares fd/signal tables as needed, resets process state, applies credentials, updates process text vnode/namecache, posts exec notifications, and sets registers.
- `exec_new_vmspace()` is called by image activators at the point of no return. It kills other LWPs, sets `P_INEXEC`, stalls external process holders, replaces or clears the vmspace, removes user mappings, resets TID state, and creates the new stack mapping.

## Argument and Stack Handling

- `exec_copyin_args()` uses an object cache sized for `PATH_MAX + ARG_MAX`, stores argv strings followed by env strings, stores the filename separately at `buf + ARG_MAX`, handles `argv == NULL` as `EFAULT`, and supplies the filename as argv[0] if the argv array is empty.
- `exec_copyout_strings()` builds the initial user stack: argv vector, env vector, ELF auxargs space, argument/environment strings, randomized stack gap, spare space, execpath for rtld, signal trampoline code, and `ps_strings`.
- `stackgap_random` is sysctl-controlled and must be zero, negative fixed gap, or a positive power of two no larger than 16 pages.
- Process argument caching stores argv bytes in `p_args` if the cache size is within `ps_arg_cache_limit`.

## Executable File and VM Handling

- `exec_check_permissions()` requires no `MNT_NOEXEC` on the executable mount or top-level mount, at least one execute bit, regular file type, nonzero size, successful `VOP_EACCESS(VEXEC)`, no active writers (`v_writecount`), and successful `VOP_OPEN(FREAD)`.
- `exec_map_page()` maps executable file pages through the vnode's VM object, first trying shared object/page lookup and falling back to `vm_page_grab()` plus `vm_pager_get_page()`.
- `exec_map_first_page()` maps page zero for image activators; `exec_unmap_page()` and `exec_unmap_first_page()` release lwbuf and page holds.
- `exec_new_vmspace()` either executes from a resident vmspace copy, clears a private vmspace, or creates a new vmspace when the old one is shared.

## Process State Changes

- Other LWPs are killed for multithreaded exec via `killalllwps(1)`.
- Shared file descriptor tables are copied so descriptors cannot remain shared after exec.
- Shared signal action tables are copied so `execsigs()` can reset handlers privately.
- Per-LWP and per-process user mappings are removed; virtual kernel state is not inherited.
- Profiling stops, `FD_CLOEXEC` descriptors close, caught signals reset, process/thread command names update, `P_EXEC` is set, vfork parent wait state is cleared, `AFORK` is cleared, and registers are initialized.

## Credentials and Security

- Setuid/setgid is honored only when mount flags allow it and the process is not traced.
- Set-id exec disables tracing unless `ktrace_suid` allows it for privileged callers, clears parent-death signal, applies descriptor safety checks for fds 0..2, updates effective uid/gid, and clears local varsym state.
- Saved uid/gid are updated to POSIX values after exec.
- `caps_exec(p)` adjusts credentials/capabilities for the new image.

## VFS/File-System Relevance

- Exec is fundamentally vnode-backed here: namecache lookup (`nlookup`), `cache_vget()`, vnode attributes, `VOP_EACCESS`, `VOP_OPEN`, vnode pager page-in, `vn_fullpath()`, `vn_mark_atime()`, and persistent `p_textvp`/`p_textnch` are all managed in this file.
- `fexecve()` depends on descriptor-to-vnode resolution and honors close-on-exec behavior for interpreted scripts.
- Mount flags (`MNT_NOEXEC`, `MNT_NOSUID`) directly affect execution.

## Research Notes

- The `vmspace_destroyed` flag has two meanings: any point-of-no-return state and ownership of clearing `P_INEXEC`.
- Error handling after `exec_new_vmspace()` can return `-1`, causing the caller to terminate the process.
- Interpreter recursion preserves/rewrites lookup state and must clean up first-page and vnode references before retrying.
- This file is essential for research into executable file access, text vnode lifetime, VM object reads through VFS, and process lifecycle interactions with file descriptors.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_exit.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_exit.c

## Role

Implements process and LWP termination, `exit`, extended LWP/process exit, killing peer LWPs, zombie transition, wait/reap semantics, child reparenting, exit callbacks, and asynchronous dead-LWP cleanup. It is closely tied to file descriptor teardown, vmspace release, text vnode/namecache release, kqueue cleanup, jail/reaper behavior, and resource accounting.

## Major Entry Points

- `sys_exit()` terminates the process through `exit1()`.
- `sys_extexit()` can exit only the current LWP when other LWPs remain, or the whole process otherwise.
- `killalllwps()` marks `P_WEXIT`, sets `LWP_MP_WEXIT`, sends `SIGKILL` to all other LWPs, waits until only the current LWP remains, and optionally cleans flags for exec reuse.
- `exit1()` performs full process teardown and never returns.
- `lwp_exit()` performs per-LWP teardown and ends in `cpu_lwp_exit()`.
- `sys_wait4()`, `sys_wait6()`, and `kern_wait()` implement wait semantics, zombie reaping, stopped/continued state reporting, `WNOWAIT`, and wait filtering by pid, pgrp, sid, uid, gid, and jail id.

## Process Exit Flow

- Refuses to let pid 1 die without panicking.
- Cleans varsym state, kills peer LWPs, kills task-leader peers, posts stop/exit tracing events, sets `P_POSTEXIT`, and stores `p_xstat`.
- Runs registered `at_exit` callbacks.
- Stops profiling, clears pending signal sets, terminates real-time timer callout, clears `sigio` ownership, closes and releases the file descriptor table via `fdfree()`, removes peer linkage, and exits SYSV semaphores.
- Releases virtual-kernel state and calls `vmspace_relexit()` early to drop user address-space resources while sleeping is still allowed.
- Handles session-leader controlling terminal shutdown and revoke semantics.
- Performs accounting, destroys ktrace state, releases `p_textvp`, drops `p_textnch`, handles vfork `P_PPWAIT`, and moves the process to the zombie list.
- Releases owned reaper state, reparents children to init or a subreaper, sends parent-death signals, accumulates rusage, posts `NOTE_EXIT`, reparents self to reaper when parent ignores/no-waits `SIGCHLD`, signals parent, frees limits, and exits final LWP.

## LWP Exit and Reaping

- `lwp_exit()` releases user scheduler state, unmaps per-thread shared page, sets `LWP_MP_WEXIT`, exits virtual-kernel LWP state, terminates per-LWP kqueue used by select/poll, drops Linux compatibility callbacks, releases cached credentials and limits, clears per-thread fd cache, waits for `lwp_lock`, folds LWP rusage into process rusage, exits disk/I/O scheduler state, removes non-master LWPs from the RB tree, and queues them to per-CPU dead-LWP taskqueues.
- `lwp_wait()` waits for final thread-exit interlocks (`TDF_MP_EXITSIG`, refs, flags) before stack/thread disposal.
- `lwp_dispose()` releases the process hold, detaches the thread/LWP relationship, frees the LWKT thread, and frees the LWP.
- `deadlwp_init()` creates per-CPU tokens/lists/tasks for dead LWP reaping.

## Wait and Zombie Reaping

- `kern_wait()` validates options, scans children under the parent's token, filters by id type, and handles Linux clone wait behavior.
- For `SZOMB` children and `WEXITED`, it obtains zombie ownership, waits for all LWPs to exit, reaps any remaining LWPs, stalls until references drop, fills status/rusage/siginfo, honors `WNOWAIT`, restores ptrace-attached children to original parents when needed, removes zombie process structures, updates parent child rusage, frees credentials, arguments, signal actions, vmspace, uidpcpu, and `struct proc`.
- Stopped/trapped and continued states are reported without full reaping.
- Parent sleeping is interlocked through `p_waitgen`.

## VFS/File-System Relevance

- `fdfree()` closes process file descriptors during exit.
- `p_textvp` and `p_textnch` are released on exit, matching references acquired by exec/fork.
- `vmspace_relexit()` and `vmspace_exitfree()` release mmap/file-backed VM resources, potentially triggering vnode I/O for unlinked mapped files.
- Controlling terminal cleanup can revoke tty access.
- `kqueue_terminate(&lp->lwp_kqueue)` tears down select/poll event resources held by each LWP.

## Reparenting and Reapers

- `proc_reparent()` safely moves a child between parent child lists by holding old parent, child, and new parent tokens, retrying on races.
- `exit1()` uses `reaper_exit()`, `reaper_get()`, and parent signal settings to decide whether children or the exiting process move to a subreaper.

## Research Notes

- The exit path intentionally releases `p_token` around large vmspace release/free operations to avoid stalling global process scans.
- Zombie reaping is split from exit: exit moves the process to zombie state; wait owns final process structure destruction.
- This file is required context for event notification (`NOTE_EXIT`), text vnode lifetime, descriptor teardown, mmap cleanup, and process-scoped filesystem resource release.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_exit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_fork.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_fork.c

## Role

Implements process and LWP creation: `fork`, `vfork`, `rfork`, `lwp_create`, low-level LWP cloning, fork callbacks, process start scheduling, and process reaper control (`procctl`). It controls inheritance or sharing of vmspaces, file descriptor tables, credentials, signal actions, text vnode/namecache references, jail flags, virtual-kernel state, and scheduler/disk scheduler state.

## Major Entry Points

- `sys_fork()` calls `fork1()` with copied fd table and normal process creation flags, then starts the child and returns child pid.
- `sys_vfork()` calls `fork1()` with shared memory and parent-wait flags, starts the child, and waits for `P_PPWAIT` to clear.
- `sys_rfork()` supports creating no new process while unsharing parts of the current process, or creating a child with caller-selected sharing flags.
- `sys_lwp_create()` and `sys_lwp_create2()` create a new LWP in the current process, optionally constrained by a CPU mask.
- `fork1()` is the main process creation/unsharing routine.
- `start_forked_proc()` transitions the child from `SIDL` to runnable state and handles vfork parent synchronization.
- `sys_procctl()` implements subreaper acquisition/release/status/kill and parent-death signal controls.

## Process Creation Flow

- Validates incompatible fd flags and handles the non-`RFPROC` case by modifying the current process's vmspace and file descriptor sharing.
- Locks process group signal delivery when requested to avoid missing process-group signals during fork.
- Enforces global `maxproc` and per-uid `RLIMIT_NPROC`; increments `nprocs` before blocking allocations.
- Allocates and partially initializes `struct proc` as `SIDL`, assigns fork id, initializes token/spin/RB tree, inherits/holds the current reaper, allocates per-CPU uid accounting storage, and adds the process to allproc.
- Copies the parent process's copy region, holds credentials, sets `P_JAILED` when inherited credentials are jailed, references cached args, enters disk scheduler state, copies or shares signal actions, sets parent signal, references text vnode and copies text namecache handle.
- Handles file descriptors by creating a fresh table (`RFCFDG`), copying (`RFFDG`), or sharing with filedesc-to-leader tracking.
- Inherits limits, tty-control flags, sugid flag, virtual-kernel state, process group membership, parent/child list membership, varsym state, itimer callout, and ktrace state.
- Creates first LWP with `lwp_fork1()`, performs `vm_fork()`, wakes umtx waiters when COW may alter physical addresses, completes LWP/thread setup with `lwp_fork2()`, runs fork callbacks, sets start time and accounting flags, posts `NOTE_FORK`, and returns the child.

## LWP Creation

- `lwp_fork1()` allocates and copies the LWP copy region, initializes tokens/spin/list state, and temporarily preserves the parent's TID for fork/vfork correctness with `/dev/lpmap`.
- `lwp_fork2()` assigns vmspace, handles alt-stack inheritance/reset depending on shared memory, applies scheduler fork heuristics, allocates an LWKT thread, holds credentials for the thread, calls `cpu_fork()`, initializes per-LWP kqueue, inserts the LWP into the process RB tree with unique TID resolution, marks the process maybe-threaded, and copies blockallsigs state for lpmap when needed.
- `lwp_create1()` copies user parameters, optional CPU mask, forces exclusive limit access, creates and prepares an LWP, copies TID(s) to user memory, and schedules it.

## File-System and VFS Relevance

- Fork preserves `p_textvp` with `vref()` and copies `p_textnch`; exit and exec later release or replace these references.
- File descriptor table behavior is controlled by `RFCFDG`, `RFFDG`, or sharing; this affects open file/vnode reference inheritance.
- `vm_fork()` determines vmspace sharing or COW behavior for file-backed mappings.
- Per-LWP kqueue initialization underpins select/poll support for new threads/processes.
- Jail state is inherited through credentials and reflected in `P_JAILED`.

## Reaper Support

- `PROC_REAP_ACQUIRE` creates a subreaper owned by the caller unless already owned.
- `PROC_REAP_RELEASE` drops ownership and restores parent reaper linkage.
- `PROC_REAP_STATUS` reports owned status, refs, and head child pid.
- `PROC_REAP_KILL` walks descendants under a reaper and sends a signal without crossing subreaper boundaries unless flags restrict to direct children.
- `reaper_hold()`, `reaper_drop()`, `reaper_init()`, `reaper_exit()`, `reaper_get()`, `reaper_sigtest()`, and `reaper_kill()` manage reference-counted subreaper topology.

## Research Notes

- Error unwinding in `fork1()` relies on later labels but the fully initialized path dominates; process structures become globally visible early as `SIDL`.
- `wake_umtx_threads()` is a fork-specific COW correctness hook for user mutex waits keyed by physical address.
- The file is a key companion to `kern_exec.c` and `kern_exit.c` for tracking descriptor, vnode, namecache, vmspace, jail, and event-notification inheritance across process lifecycle boundaries.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_fork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_fp.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_fp.c

## Role

Provides an in-kernel file pointer API for opening, reading, writing, statting, mapping, closing, and shutting down files without necessarily using user-visible file descriptors. It wraps VFS/fileops functionality for kernel consumers that need file-like operations.

## Major Entry Points

- `fp_open()` allocates a file object, sets credentials from the current process when available, performs name lookup with `NLC_LOCKVP`, converts flags with `FFLAGS()`, calls `vn_open()`, and drops the file on failure.
- `fp_vpopen()` converts an already referenced and locked vnode into a file pointer. It rejects symlinks and sockets, validates write/read access, calls `VOP_ACCESS()`, allocates a file object, sets credentials, calls `VOP_OPEN()`, and transfers the vnode reference to the file on success.
- `fp_pread()` and `fp_read()` construct a single-iovec `uio` and call `fo_read()`, supporting explicit offsets for pread and retry/all semantics for full reads.
- `fp_pwrite()` and `fp_write()` mirror the read helpers using `fo_write()`.
- `fp_stat()` calls `fo_stat()`.
- `fp_mmap()` implements descriptor-backed mappings for regular files, character devices, POSIX shared memory, and `/dev/zero`-style anonymous mappings.
- `fp_close()` drops the file reference; `fp_shutdown()` delegates to `fo_shutdown()`.

## VFS/File-System Relevance

- This file is a direct kernel-facing bridge to the VFS layer: `nlookup_init()`, `vn_open()`, `VOP_ACCESS()`, `vn_writechk()`, `VOP_OPEN()`, `VOP_GETATTR_FP()`, vnode type checks, vnode VM objects, and `vm_mmap()` are all used.
- `fp_vpopen()` documents vnode ownership transfer precisely: on success the file pointer inherits the vnode ref and unlocks it; on failure the caller remains responsible for `vput()`.
- `fp_mmap()` validates that the file is `DTYPE_VNODE`, allows only regular files or character devices, derives maximum protections from file flags and vnode attributes, rejects private/copy mappings for character devices, special-cases zero devices to anonymous mappings, and passes the vnode handle to VM.

## Error and Partial I/O Semantics

- Reads/writes reject `nbytes > LONG_MAX`.
- Partial transfer with `ERESTART`, `EINTR`, or `EWOULDBLOCK` is treated as success for pread/pwrite/write; `fp_read(all)` loops until complete, EOF, or unrecoverable error.
- `fp_read(all)` returns `ESPIPE` if it cannot fill the full request despite no direct error.
- Nonblocking `EWOULDBLOCK` is only hidden for partial reads when `all == 0`.

## Research Notes

- This file is useful for kernel subsystems that need to load/store data through VFS without installing descriptors.
- `fp_mmap()` is mostly adapted from the normal mmap path and should be compared with `vm/vm_mmap.c` when researching mmap behavior.
- The API assumes current thread/process credentials in several places; pure kernel thread handling is explicitly noted for `fp_open()`, but `fp_vpopen()` dereferences `td->td_proc->p_ucred`, so callers need process context there.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_fp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_intr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_intr.c

## Role

Implements machine-independent interrupt management for DragonFlyBSD: hard interrupt and software interrupt registration, per-CPU interrupt thread creation, fast/slow interrupt dispatch, MP-lock handling for non-MPSAFE handlers, interrupt livelock mitigation, emergency interrupt polling, interrupt entropy registration, stray interrupt reporting, and interrupt count/name sysctls.

## Major Entry Points

- `register_swi()` and `register_swi_mp()` register software interrupt handlers on a selected/default CPU.
- `register_int()` registers hard or soft interrupt handlers, allocates records, creates emergency and normal interrupt threads as needed, updates fast/slow counts, sets MP-lock requirements, configures entropy, installs machine-level vectors, and updates soft interrupt lookup arrays.
- `unregister_swi()` and `unregister_int()` remove handler records, adjust fast/slow counts, teardown machine vectors when last handler leaves, clear MP-lock requirement if possible, update high-frequency flags, and free records.
- `sched_ithd_soft()`, `sched_ithd_hard()`, and virtual-kernel variants schedule interrupt threads.
- `ithread_fast_handler()` is called from vector code to run `INTR_CLOCK` fast handlers directly when possible, otherwise schedule the interrupt thread.
- `ithread_handler()` is the interrupt thread loop for normal dispatch, unmasking, randomness, and livelock state management.
- `ithread_emergency()` polls interrupt handlers at a sysctl/tunable-controlled rate for systems where normal interrupts are unreliable.
- `intr_init()` allocates the per-CPU/per-interrupt `intr_info` matrix and initializes IDs.

## Dispatch Model

- Each CPU/intr pair has an `intr_info` with a handler list, interrupt thread, random source state, count, running flag, fast/slow counts, flags, livelock state, and cpuid/intr identifiers.
- Fast interrupts are handlers marked `INTR_CLOCK`; slow handlers run through the interrupt thread.
- If any handler in a chain is not `INTR_MPSAFE`, the interrupt thread acquires the MP lock while processing the chain.
- Optional serializers can wrap handler calls with `lwkt_serialize_handler_call()` or try semantics for fast/emergency paths.
- `i_running` is only manipulated on the interrupt thread's CPU; remote scheduling uses IPIs.

## Livelock and Emergency Polling

- Livelock sysctls: `kern.livelock_limit`, `kern.livelock_limit_hi`, `kern.livelock_lowater`, and `kern.livelock_debug`.
- High-frequency interrupts can use the higher limit only when unshared.
- When an interrupt exceeds the per-second limit, the thread enters `ISTATE_LIVELOCKED`, a periodic systimer limits wakeups, and normal state resumes below low-water.
- Emergency polling is controlled by tunable/sysctl `kern.emergency_intr_enable` and `kern.emergency_intr_freq`, capped at 20000 Hz.

## Sysctls and Observability

- `hw.intrnames` emits slash-separated handler names per CPU/intr slot, defaulting to `irqN`.
- `hw.intrcnt_all` and `hw.intrcnt` emit interrupt counters for all CPU/intr slots.
- Stray interrupts are rate-limited and eventually silenced after repeated reports.

## File-System Relevance

- This is not VFS code, but block devices, storage controllers, network filesystems, timers, and device-backed files rely on this interrupt dispatch infrastructure.
- Interrupt randomness and livelock behavior can indirectly affect storage latency and kernel responsiveness under I/O-heavy workloads.

## Research Notes

- Registration migrates the current thread to the target CPU to initialize per-CPU structures and then migrates back.
- Handler records can become invalid after handler calls, so loops store `next` before dispatch.
- Invariant checks verify that interrupt handlers do not leak spinlocks, tokens, or MP locks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_intr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_iosched.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_iosched.c

## Role

Implements a small per-thread/per-CPU I/O scheduling pressure adjustment layer used before buffer-cache write or inode-modifying operations. It tracks recent write bytes, computes each thread's share of outstanding write pressure, and waits on dirty-buffer thresholds proportionally.

## Major Entry Points

- `bwillwrite(int bytes)` is called before intended writes. It invokes `bd_heatup()`, charges bytes to the current thread with `badjiosched()`, computes a dirty-buffer wait target from `hidirtybufspace`, and calls `bd_wait()`.
- `bwillread(int bytes)` is currently a no-op placeholder.
- `bwillinode(int n)` is called before inode-modifying operations. It uses a page-sized charge, scales the heatup count by the computed factor, and waits.
- `biosched_done(thread_t td)` clears a thread's outstanding write-byte accounting and subtracts it from the current CPU bucket.

## Internal Mechanics

- `ioscpu[SMP_MAXCPU]` stores per-CPU aggregate write-byte pressure.
- `badjiosched()` sums all CPU totals, caps additions to avoid `size_t` overflow, updates `td->td_iosdata.iowbytes`, decays the thread and CPU totals based on ticks elapsed up to a ten-second window, and computes a percentage share.
- Debug sysctl `iosched.debug` can print per-thread factor information.

## VFS/File-System Relevance

- This file is directly related to write throttling and dirty buffer pressure, which affects filesystem writeback and metadata-heavy workloads.
- `bwillinode()` indicates metadata/inode operations are intentionally included in I/O pressure accounting even without a byte count from the caller.

## Research Notes

- The algorithm is intentionally simple and approximate; it uses current CPU accounting in `biosched_done()` and in decay, so migration behavior is worth checking if analyzing fairness.
- Comments contain misspellings of "integer"; no behavioral impact.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_iosched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_jail.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_jail.c

## Role

Implements DragonFlyBSD jail creation, jail attachment, prison lifecycle/refcounting, jail IP address handling, jail sysctl reporting/control, and jailed privilege checks. It is important to filesystem research because jail roots are namecache handles, attach uses chroot, and jail capabilities gate mount and VFS operations.

## Major Entry Points

- `sys_jail()` validates privilege, copies jail versioned input, allocates a `struct prison`, copies IPv4/IPv6 address storage, copies hostname, applies default capabilities, and calls `kern_jail()`.
- `kern_jail()` looks up and stores the jail root path as `pr_root`, initializes varsym and IP caches, assigns a prison id, links the prison globally, creates per-jail sysctls, and attaches the current process.
- `sys_jail_attach()` validates privilege and attaches to an existing jail.
- `kern_jail_attach()` finds the prison, performs `kern_chroot(&pr->pr_root)`, holds the prison, atomically updates process credentials to point at the prison, sets `P_JAILED`, and applies restricted-root caps.
- `prison_hold()` and `prison_free()` manage prison references and final cleanup.
- `prison_priv_check()` decides whether a jailed credential may exercise a specific system capability.

## Jail Root and VFS Behavior

- Jail creation resolves `j->path` with `nlookup()` and stores a namecache handle in `pr->pr_root` via `cache_copy()`.
- Attach performs a chroot to the stored prison root.
- `sysctl_jail_list()` reports jail id, host, root path from `cache_fullpath()`, and jail IPs.
- `prison_free()` drops `pr_root` with `cache_drop()`.
- Default and per-jail capability bits include VFS-relevant controls: `vfs_chflags`, `vfs_mount_nullfs`, `vfs_mount_tmpfs`, `vfs_mount_devfs`, `vfs_mount_procfs`, and `vfs_mount_fusefs`.
- `prison_priv_check()` conditionally allows mount capabilities based on the prison's `pr_caps` bits and otherwise restricts sensitive root/network/jail operations.

## IP and Network Handling

- Supports legacy version 0 single IPv4 jails and DragonFly version 1 multi no-IP/IPv4/IPv6 jails.
- `prison_ipcache_init()` caches first loopback and non-loopback IPv4/IPv6 addresses.
- `prison_replace_wildcards()`, `prison_remote_ip()`, and `prison_local_ip()` translate loopback/wildcard behavior for jailed processes.
- `prison_get_nonlocal()` and `prison_get_local()` return cached addresses and optionally copy them into caller-provided sockaddr storage.
- `jailed_ip()` checks whether an address belongs to the prison.
- `prison_if()` restricts socket address families or IPs according to prison capabilities.

## Sysctl Surface

- Global defaults under `jail.defaults` define default prison capability bits.
- `jail.list` exposes active jail metadata to non-jailed callers.
- `jail.jailed` reports whether the current request credential is jailed.
- `prison_sysctl_create()` creates a per-jail node with mutable bits for system, network, and VFS mount capabilities; `prison_sysctl_done()` frees it.

## Synchronization

- `jail_lock` protects the global prison list, prison id assignment, jail count, and IP list scans.
- Prison references are atomically counted, with final list removal under `jail_lock`.
- Process credential updates occur under `p_token` and use `cratom_proc()` to avoid mutating shared credentials.

## Research Notes

- The jail root is held as a namecache handle rather than only a vnode/path string, which is relevant to namespace and chroot behavior.
- `prison_find()` returns a prison pointer after dropping `jail_lock`; callers that need lifetime stability must hold the prison. `kern_jail_attach()` calls it while outer `sys_jail_attach()` holds the same recursive-capable jail lock, then `prison_hold()` before publishing into credentials.
- The VFS mount capability matrix here is a primary policy hook for filesystem operations inside jails.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_jail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_kinfo.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_kinfo.c

## Role

Fills `kinfo_proc` and `kinfo_lwp` structures for kernel and libkvm consumers. It translates live or zombie `proc`, `lwp`, and kernel-thread state into stable exported process information, including credentials, process groups, sessions, controlling terminals, VM sizes, jail id, rusage, scheduling state, and wait channels.

## Major Entry Points

- `fill_kinfo_proc(struct proc *p, struct kinfo_proc *kp)` zeroes and fills process-level fields. Caller must hold `p->p_token`.
- `fill_kinfo_lwp(struct lwp *lwp, struct kinfo_lwp *kl)` fills or aggregates LWP-level fields into an existing structure.
- `fill_kinfo_proc_kthread(struct thread *td, struct kinfo_proc *kp)` creates synthetic process/LWP information for kernel threads without a user process.

## Process Data Exported

- Process address, fd table pointer, flags, state, lock/acct/trace flags, signal masks, start time, command name, pid/ppid, process group/session/job-control data, controlling tty device and foreground pgrp/session ids, exit status, thread count, nice value, swap time, VM map size, resident count, text/data/stack sizes, jail id, self rusage, and child rusage.
- Credentials include uid, groups, ruid/svuid, rgid/svgid, and a copied subset of capability bits.
- Null checks protect zombied/deallocating process fields such as pgrp, session, ucred, sigacts, vmspace, parent pointer, and tty state.

## LWP and Kernel Thread Data Exported

- LWP pid/tid, flags, state, lock, thread flags, MP lock count, scheduler priorities, realtime priority, tick counters, pctcpu, sleep time, original/current CPU, estimated CPU, rusage, signal list/mask, wait channel, wait message, and command name.
- If an LWP is marked runnable but neither LWKT nor user scheduler run-queue flags indicate it is queued, status is adjusted to sleep.
- Kernel threads are reported with pid/tid `-1`, `P_SYSTEM`, idle vs active state, one thread, kernel thread address, priority data, tick counters, CPU id, wait channel/message, and command name.

## Dual Kernel/Userland Compilation

- The file is compiled by both kernel and libkvm.
- In non-kernel builds it defines local `timevalfix()`, `timevaladd()`, and `ruadd()` helpers and declares `devid_from_dev()` externally.
- In kernel builds it uses `get_mplock_count()` for MP lock count; userland reports zero.

## VFS/File-System Relevance

- Exports fd table pointer and controlling tty device id.
- Reports VM sizes and resident counts relevant to file-backed mappings.
- Exports jail id for process visibility and jail-scoped filtering.
- Used by process inspection tools that often correlate open files, cwd/root, tty, and VM state from other kinfo/procfs paths.

## Research Notes

- This file is read-only/export logic and does not mutate process state.
- `fill_kinfo_proc()` explicitly supports zombie/deallocation races through defensive null checks.
- `fill_kinfo_lwp()` doubles as an aggregator, so callers must zero/prepare the target structure as documented.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_kinfo.c -->