# Group Research: group_1272_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_sys_sched_c_sources_o_104bb61dbda2

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_sched.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_sched.c

Implements NetBSD scheduler-related syscalls: POSIX scheduling policy/priority, CPU affinity, priority protection, yield, sysctl exposure, and kauth policy defaults.

Key entry points:
- `sys__sched_setparam` / `do_sched_setparam`: validates policy and realtime priority, finds process/LWP targets, rejects system processes, authorizes via `KAUTH_PROCESS_SCHEDULER_SETPARAM`, updates `l_class` and priority with `lwp_changepri`.
- `sys__sched_getparam` / `do_sched_getparam`: resolves a target LWP, authorizes, reads class/priority, converts kernel priority back to user-visible scheduler priority.
- `sys__sched_setaffinity`: copies in a CPU set, validates CPUs against processor sets/offline state under `cpu_lock`, authorizes, applies affinity to one or more LWPs, and migrates them.
- `sys__sched_getaffinity`: returns the target LWP affinity mask or an all-zero mask when no affinity is set.
- `sys__sched_protect`: implements a weak priority-protection mechanism for `PTHREAD_PRIO_PROTECT`, tracking protect depth and auxiliary priority.
- `sys_sched_yield`: invokes `yield()`.
- `sched_init`: installs scheduler sysctls and a kauth listener.

Important helpers and state:
- `convert_pri` translates between POSIX realtime priorities and NetBSD internal priorities, with special handling for `SCHED_OTHER`.
- `genkcpuset` allocates and imports user CPU masks.
- `sched_listener_cb` allows owners to query scheduling parameters and allows non-privileged setparam only for same-owner, non-realtime-escalating cases; affinity setting is left privileged for secmodel policy.

Concurrency/locking:
- The file documents lock order: `cpu_lock -> proc_lock -> p_lock -> lwp_lock`.
- Affinity changes hold `cpu_lock` across CPU-set validation and LWP updates to avoid races with CPU online/offline and processor-set state.
- Process/LWP traversal is protected by `proc_lock`, `p_lock`, and `lwp_lock` as appropriate.

Research notes:
- This is not filesystem code directly, but it is core process/LWP syscall infrastructure that interacts with user/kernel copying, authorization, and CPU scheduling state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_select.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_select.c

Implements synchronous I/O multiplexing for `select`, `pselect`, `poll`, `pollts`, plus the shared `selinfo` wait/wakeup machinery used by file, socket, device, pipe, and timerfd objects.

Key syscall paths:
- `sys___pselect50`: copies optional `timespec` and signal mask, then calls `selcommon`.
- `sys___select50`: copies optional `timeval`, validates microseconds, converts to `timespec`, then calls `selcommon`.
- `sys_poll`: converts millisecond timeout to `timespec` and calls `pollcommon`.
- `sys___pollts50`: copies optional `timespec` and signal mask, then calls `pollcommon`.

Core scan/wait logic:
- `sel_do_scan`: common loop for select/poll. It sets temporary signal masks, assigns the current LWP to a per-CPU `selcluster`, scans descriptors, handles timeout, sleeps on a sleepq, retries on collisions, and maps restart/blocking errors to select/poll semantics.
- `selcommon`: imports fd sets, rejects absurd descriptor ranges, checks excess fd bits for `EBADF`, allocates stack or heap buffers, scans, and copies result sets back.
- `selscan`: walks input fd masks, calls each file’s `fo_poll`, marks ready descriptors, and supports direct event setting.
- `pollcommon`: imports a `pollfd` array with allocation guardrails, calls common scan, and copies results back.
- `pollscan`: calls `fo_poll` for each fd and sets `revents`, including `POLLNVAL` for bad descriptors.

Selectable-object API:
- `selrecord`: records the current LWP as a named waiter on a `selinfo`, or records a collision if another waiter already exists.
- `selnotify`: posts kqueue notes, wakes the named waiter if present, and wakes collision clusters.
- `sel_setevents`: directly updates select fd sets or poll `revents` when `direct_select` is enabled.
- `selclear`: removes the current LWP from all `selinfo` records after a scan/wait cycle.
- `selrecord_knote` / `selremove_knote`: kqueue integration.
- `selinit` / `seldestroy`: lifecycle for `selinfo`.
- `selsysinit`: initializes per-CPU select clusters.
- `seltrue`: trivial poll helper for always-readable/writable devices.

Concurrency/locking:
- The documented lock order is object lock before `selcluster_t::sc_lock`.
- `selcluster` distributes wait queues across up to 64 clusters to reduce contention.
- Collision wakeups use a bitmask of affected clusters and `sc_ncoll` generation checks to force rescans.
- Memory barriers guard races between `selrecord`, `selnotify`, and `selclear`.

Research notes:
- This file is central to filesystem-adjacent behavior because VFS files, sockets, devices, pipes, and pseudo-files expose readiness through `fo_poll` and `selinfo`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_select.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_sig.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_sig.c

Implements signal-related syscall front ends and common helpers for signal actions, masks, pending sets, suspension, alternate stacks, signal delivery requests, user contexts, and timed signal waits.

Key syscall wrappers:
- `sys___sigaction_sigtramp`: copies in/out `sigaction` and delegates to `sigaction1`, including trampoline pointer/version handling.
- `sys___sigprocmask14`: copies an optional mask, applies `sigprocmask1` under `p_lock`, and copies out the old mask.
- `sys___sigpending14`: returns combined process/LWP pending signal set.
- `sys___sigsuspend14`: copies optional temporary mask and delegates to `sigsuspend1`.
- `sys___sigaltstack14`: copies stack settings and delegates to `sigaltstack1`.
- `sys_sigqueueinfo` and `sys_kill`: build `ksiginfo_t` and call `kill1`.
- `sys_getcontext` / `sys_setcontext`: copy user context out/in; `setcontext` returns `EJUSTRETURN`.
- `sys_____sigtimedwait50`: delegates to `sigtimedwait1`.

Core helpers:
- `kill1`: validates signal metadata and caller identity for queued signals, dispatches to a process, process group, or broadcast path, and handles POSIX zombie success behavior.
- `sigaction1`: validates signal number, flags, trampoline ABI/version, compat module availability, updates action/trampoline metadata, handles `SIGCHLD` flags, updates ignore/catch sets, clears ignored pending signals, and schedules user-return signal checks.
- `sigprocmask1`: implements `SIG_BLOCK`, `SIG_UNBLOCK`, and `SIG_SETMASK`, removing unmaskable signals and marking pending signals for user return.
- `sigpending1`: combines LWP and process pending sets.
- `sigsuspendsetup` / `sigsuspendteardown`: temporarily replace signal masks for `sigsuspend`, `pselect`, and `pollts`.
- `sigsuspend1`: waits until interrupted and returns `EINTR`.
- `sigaltstack1`: validates and updates per-LWP signal alternate stack.
- `sigtimedwait1`: imports wait set and optional timeout, consumes pending signals if present, waits on the process signal-waiter list, updates remaining timeout on interrupt/restart, and copies out `siginfo`.

Concurrency/locking:
- Most signal state mutations happen under `p_lock`.
- LWP flags are updated with `lwp_lock` when pending signals require user-return processing.
- `sigaction1` uses `kernconfig_lock` around compat module autoloading for legacy signal trampoline support.

Research notes:
- This file is process-control infrastructure rather than filesystem code, but it affects blocking syscalls, restart behavior, and signal interruption semantics used by I/O paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_sig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_socket.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_socket.c

Provides the `fileops` adapter for sockets, making sockets behave as file descriptors for read/write/ioctl/poll/stat/close/kqueue/restart/fpathconf/fadvise paths.

Key structures and entry points:
- `socketops`: file operation table for `DTYPE_SOCKET`.
- `ifioctl`: function pointer for interface ioctl handling, defaulting to `eopnotsupp`.
- `soo_read`: delegates to `so_receive`.
- `soo_write`: delegates to `so_send`.
- `soo_ioctl`: handles socket fd ioctls including nonblocking mode, async mode, read/write byte counts, send buffer space, owner/process group, at-mark query, SCTP peeloff, interface ioctls, and protocol-specific ioctls.
- `soo_poll`: delegates to `sopoll`.
- `soo_stat`: fills `S_IFSOCK` stat data and delegates protocol stat under socket lock.
- `soo_close`: calls `soclose` and clears `f_socket`.
- `soo_restart`: delegates to `sorestart`.
- `soo_fpathconf`: supports `_PC_PIPE_BUF`.
- `soo_posix_fadvise`: returns `ESPIPE`.

Concurrency/locking:
- Uses `solock`/`sounlock` when mutating socket state or querying protocol stat.
- Protocol-specific ioctls run under `KERNEL_LOCK` unless handled by MP-safe interface ioctl path later.

Research notes:
- This is a bridge between generic file descriptor operations and the socket subsystem; it participates in readiness polling through `soo_poll`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_syscall.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_syscall.c

Implements machine-independent indirect syscall dispatch. The file is parameterized by `SYS_SYSCALL`, so it can be included for native and compat indirect syscall implementations.

Key behavior:
- `SYS_SYSCALL_biglockcheck`: diagnostic-only assertion that a syscall did not leak the kernel big lock.
- `SYS_SYSCALL`: reads the indirect syscall number, masks it by `SYS_NSYSENT - 1`, counts it, rejects indirect-to-indirect syscalls, dispatches through the emulation’s `sysent` table, and integrates tracing.

Trace and compat handling:
- Fast path skips tracing when `p_trace_enabled` is false.
- Trace path calls `trace_enter`, syscall handler, and `trace_exit`.
- Under `NETBSD32_SYSCALL`, syscall args are widened into a local `register_t` array for tracing.

Research notes:
- This file is small but important syscall-table glue. It has no filesystem-specific logic, but all indirect syscall behavior depends on this dispatch path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_timerfd.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_timerfd.c

Implements Linux-compatible `timerfd` support: timer objects associated with file descriptors, readable when expirations are pending, and integrated with poll/select/kqueue/stat/restart semantics.

Core state:
- `struct timerfd` wraps `struct itimer`, a read condition variable, `selinfo`, waiter count, cancel-on-set/cancelled/restarting flags, and stat timestamps.
- All timerfd state is protected by `itimer_lock()`.

Timer behavior:
- `timerfd_fire`: increments `it_overruns` on each firing and wakes waiters.
- `timerfd_realtime_changed`: handles `CLOCK_REALTIME` changes for `TFD_TIMER_CANCEL_ON_SET`.
- `timerfd_fire_count` and `timerfd_is_readable`: expose pending-expiration/readability state.

Lifecycle:
- `timerfd_create`: allocates and initializes `timerfd`, condition variable, select info, birth time, and underlying `itimer`.
- `timerfd_destroy`: poisons/finalizes the timer, destroys wait structures, and frees memory.

File operations:
- `timerfd_fop_read`: requires an 8-byte read, blocks unless nonblocking, returns `ECANCELED` for cancelled realtime timers, copies expiration count, and resets overruns.
- `timerfd_fop_ioctl`: supports `FIONBIO`, `FIONREAD`, and `TFD_IOC_SET_TICKS`.
- `timerfd_fop_poll`: reports read readiness or records with `selrecord`.
- `timerfd_fop_stat`: reports count/timestamps and FIFO-like mode.
- `timerfd_fop_close`: destroys the timerfd.
- `timerfd_fop_kqfilter`, `timerfd_filt_read`, `timerfd_filt_read_detach`: EVFILT_READ support.
- `timerfd_fop_restart`: wakes blocked reads with restart semantics so close/revalidation can proceed.

Syscalls:
- `do_timerfd_create` / `sys_timerfd_create`: validate clock and flags, allocate fd/file, set `DTYPE_TIMERFD`, apply close-on-exec/nonblock.
- `do_timerfd_gettime` / `sys_timerfd_gettime`: validate fd type and return current timer state.
- `do_timerfd_settime` / `sys_timerfd_settime`: validate flags/times, optionally return old value, convert relative values to absolute deadlines, arm/disarm timer, reset expiration count, and update cancellation/timestamps.

Research notes:
- This file directly exercises generic fd/fileops, select/poll, kqueue, and stat integration patterns relevant to pseudo-files and kernel file descriptor objects.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_timerfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/syscalls.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/syscalls.c

Generated syscall-name table from `syscalls.master`, produced by `makesyscalls.sh`. It should not be edited manually.

Contents:
- `syscallnames[]`: canonical syscall names indexed by syscall number, from 0 through 511.
- `altsyscallnames[]`: optional libc-style alternate names for selected syscall numbers, otherwise `NULL`.

Notable coverage in this group:
- Scheduler syscalls are named at 346-351: `_sched_setparam`, `_sched_getparam`, `_sched_setaffinity`, `_sched_getaffinity`, `sched_yield`, `_sched_protect`.
- Select/poll modern names include `__select50`, `__pselect50`, `__pollts50`, plus legacy compat entries.
- Signal entries include `__sigaction_sigtramp`, `__sigpending14`, `__sigprocmask14`, `__sigsuspend14`, `____sigtimedwait50`, `sigqueueinfo`, `getcontext`, and `setcontext`.
- Socket table names include classic socket calls and `__socket30`.
- Timerfd names are 177-179: `timerfd_create`, `timerfd_settime`, `timerfd_gettime`.

Conditional generation:
- Includes conditional names for options like `_LP64`, `NTP`, and `_KERNEL_OPT`.
- Uses generated comments for obsolete, excluded, filler, and unimplemented syscall slots.

Research notes:
- This file contains no dispatch implementation; it is metadata used for names, tracing, diagnostics, and generated syscall infrastructure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/syscalls.conf -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/syscalls.conf

Configuration input for NetBSD syscall generation.

Key settings:
- Generates syscall names to `syscalls.c`.
- Generates syscall numbers to `../sys/syscall.h`.
- Generates syscall switch table to `init_sysent.c`.
- Generates syscall argument header to `../sys/syscallargs.h`.
- Adds extra argument-header includes for `idtype.h`, `mount.h`, `sched.h`, `acl.h`, and `socket.h`.
- Generates autoload data to `syscalls_autoload.c`.
- Generates rump syscall outputs and map files.
- Lists supported compatibility option prefixes from `compat_09` through `compat_110`.
- Sets `switchname="sysent"`, `namesname="syscallnames"`, `constprefix="SYS_"`, `emulname="netbsd"`, and `nsysent=512`.

Research notes:
- This file controls how `makesyscalls.sh` emits the generated syscall artifacts used by this group.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/syscalls.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/syscalls_autoload.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/syscalls_autoload.c

Generated syscall autoload table from `syscalls.master`, produced by `makesyscalls.sh`. It maps syscall numbers to kernel modules that should be autoloaded when optional or compatibility syscall implementations are needed.

Core content:
- `netbsd_syscalls_autoload[]`: array of `{ SYS_..., "module" }` entries terminated by `{ 0, NULL }`.

Major module groups:
- Compatibility modules: `compat_09`, `compat_12`, `compat_13`, `compat_16`, `compat_20`, `compat_30`, `compat_40`, `compat_43`, `compat_50`, `compat_60`, `compat_90`, `compat_100`, and SysV compatibility variants.
- Optional subsystem modules: `ptrace`, `nfsserver`, `lfs`, `openafs`, `sysv_ipc`, `ksem`, `mqueue`, and `aio`.
- Some entries are conditional on build options such as `_LP64`, `NTP`, and `_KERNEL_OPT`.

Relevant relationships:
- LFS syscalls map to `lfs`.
- AIO syscalls map to `aio`.
- POSIX message queues map to `mqueue`.
- SysV IPC and semaphore operations map to `sysv_ipc` or compatibility SysV modules.
- Compatibility select/poll/time/signal syscalls map to the corresponding compat modules.

Research notes:
- This file has no hand-written behavior, but it is part of syscall dispatch availability: missing optional implementations can be loaded on demand based on this table.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/syscalls_autoload.c -->