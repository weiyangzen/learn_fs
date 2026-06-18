# Group Research: group_1263_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_kern_proc_c_sources_o_40d7e80e90ca

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_proc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_proc.c

## Purpose

`kern_proc.c` is NetBSD's central machine-independent process implementation. It manages global process lists, PID/LWP lookup tables, process allocation, process groups, sessions, process-specific storage, process visibility authorization, process credential update coordination, and `kern.proc*` sysctl reporting.

## Main Responsibilities

- Maintains `allproc`, `zombproc`, `proc_lock`, and the pserialize-protected PID table.
- Initializes `proc0`, `lwp0` linkage, `session0`, `pgrp0`, cwd, filedesc, limits, vmspace, signal state, and kernel credentials.
- Allocates and frees process IDs and LWP IDs.
- Implements process lookup by PID/LID and process group lookup.
- Implements session/process-group transitions for `setsid`, `setpgid`, and spawn paths.
- Maintains job-control counters and orphaned process-group behavior.
- Provides process-specific-data key/container wrappers.
- Coordinates process credential modification for ID-changing syscalls.
- Implements process information sysctls, process argument/environment export, executable path, cwd, and auxv extraction.

## Core Data Model

The PID table maps `pid & pid_tbl_mask` to `struct pid_table` entries. `pt_slot` encodes one of: free slot, process placeholder, or LWP pointer, using low pointer bits. `pt_pgrp` separately pins process-group/session IDs in the PID namespace. The table expands by doubling, redistributing entries into the new mask space, publishing the new table with release ordering, then waiting for pserialize readers before freeing the old table.

`proc0` is statically allocated and never freed. It owns the initial kernel process state, default resource limits, cwd info, file descriptor table, vmspace, sigacts, session, and process group.

## Initialization Flow

`procinit()` initializes process lists, `proc_lock`, pserialize state, the initial PID table, reserves PID 1 for `init`, creates process-specific-data state, creates the process pool cache, and registers a `KAUTH_SCOPE_PROCESS` listener.

`proc0_init()` initializes proc0 locks/cvs, links `lwp0`, installs proc0 into `allproc` and `pgrp0`, creates credentials, initializes cwd/limits/filedesc/vmspace/sigacts, and constructs DTrace process state.

`procinit_sysctl()` registers `security.expose_address`, `kern.proc`, `kern.proc2`, and `kern.proc_args`.

## PID and LWP Lookup

Lookup is table-based rather than list-based. `proc_find()`, `proc_find_lwpid()`, and `proc_find_raw()` resolve processes through the PID table under `proc_lock`. `proc_find_lwp()` requires `p->p_lock`; `proc_find_lwp_unlocked()` runs in a pserialize read section and returns a locked LWP if the LID, process, and state still match. The first LWP usually usurps the process PID slot; when that LWP exits, `proc_free_lwpid()` converts the slot back to a process placeholder.

## Process Groups and Sessions

`proc_enterpgrp()` enforces POSIX session/process-group rules: only self or children may be changed, target children must be in the same session and not have execed, session leaders cannot move except no-op, new process groups must use the target process PID, and zombie pgrps cannot be joined. New sessions allocate `struct session`, clear controlling-terminal ownership, copy login state, and clear `S_LOGIN_SET`.

`fixjobc()` updates process-group job-control eligibility. `orphanpg()` sends `SIGHUP` and `SIGCONT` to stopped members of newly orphaned groups. `pg_delete()` removes tty process-group references and frees pgrp/session structures when final references drop.

## Sysctl and Process Introspection

`sysctl_doeproc()` implements both legacy `KERN_PROC` and newer `KERN_PROC2`. It iterates zombies before active processes to avoid duplicate reporting while processes move between lists, checks `KAUTH_PROCESS_CANSEE`, supports PID/pgrp/session/tty/UID/GID filters, and uses `p_reflock` or marker nodes for stability.

`fill_proc()`, `fill_eproc()`, and `fill_kproc2()` build exported process records while conditionally scrubbing kernel pointers according to `security.expose_address` and kauth. `sysctl_kern_proc_args()` handles argv/env counts and values, pathname, and cwd. `copy_procargs()` reads `ps_strings`, vector pointers, and user strings page by page from the target vmspace. `fill_cwd()` locks cwdinfo and formats paths through `getcwd_common()`, tying this file to VFS-visible process context.

## Security and Concurrency Notes

The process kauth listener allows ordinary process entries/args/open-files visibility, restricts environment visibility to matching real/saved UID, and gates kernel pointer exposure. `proc_crmod_enter()` and `proc_crmod_leave()` synchronize process credential updates and mark sibling LWPs to refresh cached credentials.

Key locks are `proc_lock` for global process/session/PID structures, `p->p_lock` for per-process state and LWP lists, `p_reflock` for process lifetime during readers, pserialize for unlocked PID-table readers, and `tty_lock` for controlling-terminal/process-group interlocks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_prot.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_prot.c

## Purpose

`kern_prot.c` implements process identity and protection syscalls: PID/session/group queries, UID/GID queries, UID/GID mutation, supplemental groups, `setsid`, `setpgid`, `issetugid`, and session login-name access.

## Main Responsibilities

- Implements simple query syscalls: `getpid`, `getppid`, `getuid`, `geteuid`, `getgid`, `getegid`, and combined return variants.
- Implements process group/session syscalls: `getpgrp`, `getsid`, `getpgid`, `setsid`, and `setpgid`.
- Implements UID/GID mutation through `do_setresuid()` and `do_setresgid()`, plus `setuid`, `seteuid`, `setreuid`, `setgid`, `setegid`, and `setregid`.
- Implements `getgroups` and `setgroups`.
- Implements `__getlogin` and `__setlogin`.
- Implements `issetugid`.

## Credential Mutation Model

`do_setresuid()` and `do_setresgid()` allocate a new credential, enter process credential modification through `proc_crmod_enter()`, check whether requested IDs are permitted by current real/effective/saved IDs, and otherwise ask kauth for `KAUTH_PROCESS_SETID`. If nothing changes, they leave without installing a new credential.

UID changes also update process and LWP accounting with `chgproccnt()` and `chglwpcnt()`, excluding the first LWP from the LWP accounting adjustment. Successful changes clone the old credential, update requested real/effective/saved IDs, and publish through `proc_crmod_leave(..., true)`, marking the process `PK_SUGID`.

## Process Group and Session Behavior

`sys_setsid()` delegates to `proc_enterpgrp(p, p->p_pid, p->p_pid, true)` and returns the process PID. `sys_setpgid()` normalizes `pid == 0` to the caller PID and `pgid == 0` to the target PID, rejects negative pgid, and delegates all policy to `proc_enterpgrp()`.

`getpgrp`, `getsid`, and `getpgid` use `proc_lock` while reading process group/session state.

## Groups and Login Name

`sys_getgroups()` returns the group count when `gidsetsize == 0`; otherwise it validates user capacity and copies groups out via kauth credential helpers. `sys_setgroups()` builds a fresh credential group list with `kauth_cred_setgroups()` and commits through `kauth_proc_setgroups()`.

`sys___getlogin()` copies the session login name under `proc_lock`. `sys___setlogin()` requires `KAUTH_PROCESS_SETID`, copies a bounded user string, warns when a non-session-leader changes an already set login name, marks `S_LOGIN_SET`, and stores the new session login.

## Security Notes

Non-privileged ID changes are limited to values matching allowed current IDs according to the wrapper's flags. Privileged override goes through kauth. `issetugid` reports `PK_SUGID`, covering not only setuid exec but also later ownership/credential changes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_prot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ras.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ras.c

## Purpose

`kern_ras.c` implements restartable atomic sequences for architectures defining `__HAVE_RAS`. A registered user address range is restarted at its beginning if interrupted while executing inside the range.

## Main Responsibilities

- Maintains per-process `p_raslist` entries.
- Looks up interrupted addresses with `ras_lookup()`.
- Copies RAS registrations on fork with `ras_fork()`.
- Removes all registrations with `ras_purgeall()`.
- Implements `sys_rasctl()` for install, purge, and purge-all operations.

## Behavior

`ras_lookup(p, addr)` disables kernel preemption, walks the process RAS list, and returns the registered start address if `addr` is strictly inside a registered range. Otherwise it returns `(void *)-1`. The lookup path intentionally takes no list lock; mutation paths use `p_auxlock` and `ras_sync()`.

`ras_sync()` forces a cross-call barrier when the current process is multithreaded and the system has multiple CPUs, ensuring removed entries are not freed while another CPU could still see them.

## Install and Purge

`ras_install()` rejects zero-length ranges, user-address overflows, out-of-range addresses, overlapping ranges, and registrations beyond `ras_per_proc`, defaulting to 16. New entries are prepended to `p_raslist`.

`ras_purge()` requires an exact start and length match, unlinks the entry under `p_auxlock`, syncs, and frees it. Missing entries return `ESRCH`. `sys_rasctl()` returns `EOPNOTSUPP` when the architecture lacks RAS support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ras.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_rate.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_rate.c

## Purpose

`kern_rate.c` provides small generic kernel rate-limiting helpers.

## Functions

`ratecheck(lasttime, mininterval)` uses `getmicrouptime()` and allows an event if the elapsed interval is at least `mininterval`, or if `lasttime` is zero so the first message is not suppressed. On allow, it updates `lasttime`.

`ppsratecheck(lasttime, curpps, maxpps)` implements per-second packet/event limiting. It resets the counter on the first call or after at least one second, allows all events when `maxpps < 0`, allows events while `*curpps < maxpps`, and increments the counter unless it is already `INT_MAX`.

## Integration Notes

These helpers are subsystem-neutral and are commonly used to throttle repeated kernel messages or event handling without embedding local timing logic in callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_rate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_reboot.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_reboot.c

## Purpose

`kern_reboot.c` implements the machine-independent reboot syscall wrapper and shared reboot entry point.

## Main Responsibilities

`kern_reboot(howto, bootstr)` serializes reboot attempts with an atomic CAS on a static `rebooter` LWP pointer. If another LWP is already rebooting, later callers sleep in `kpause("reboot", ...)`. It sets `shutting_down`, handles the cold-boot shortcut, writes adjusted time back to the time-of-day clock when syncing is allowed and the kernel is not panicking, then delegates final machine-dependent work to `cpu_reboot()`.

`sys_reboot()` requires `KAUTH_SYSTEM_REBOOT`. It copies an optional boot string only when `RB_STRING` is set, then calls `kern_reboot()`.

## Notes

Most shutdown details remain in per-port `cpu_reboot()` implementations. The file explicitly notes that common reboot behavior could be refactored into this MI layer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_reboot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_resource.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_resource.c

## Purpose

`kern_resource.c` implements process resource controls and accounting: priority/nice syscalls, rlimits, rusage accounting, process limit copy-on-write, core-name handling, and per-process `CTL_PROC` sysctl nodes.

## Main Responsibilities

- Registers a process kauth listener for priority and rlimit authorization.
- Implements `getpriority`, `setpriority`, `setrlimit`, `getrlimit`, and `getrusage`.
- Maintains patchable maxima `maxdmap` and `maxsmap`.
- Computes process/LWP runtime and memory usage.
- Manages `struct plimit` reference counts and copy-on-write lifetime.
- Copies/frees `struct pstats`.
- Implements `CTL_PROC` helpers for PaX flags, core name, stop flags, and individual rlimit soft/hard values.

## Priority Handling

`sys_getpriority()` supports `PRIO_PROCESS`, `PRIO_PGRP`, and `PRIO_USER`, returning the lowest nice value found. `sys_setpriority()` applies `donice()` over the selected process set. `donice()` checks owner-style permission, clamps the requested nice value to `PRIO_MIN..PRIO_MAX`, asks kauth for `KAUTH_PROCESS_NICE`, and updates scheduling priority with `sched_nice()`.

## Resource Limits

`dosetrlimit()` validates the target limit and `cur <= max`, skips unchanged values, authorizes with `KAUTH_PROCESS_RLIMIT`, privatizes shared limits, clamps data/stack/file/process/thread limits to kernel maxima, and stores the new value under `pl_lock`.

For `RLIMIT_STACK`, it rejects limits below current stack use, rounds page sizes, and updates VM map protections to expose or hide stack pages as the soft stack limit changes.

## Runtime and Rusage Accounting

`addrulwp()` adds an LWP's accumulated runtime and estimates the active running slice if needed. `calcru()` combines process and LWP runtime, apportions elapsed time across user/system/interrupt ticks, and keeps reported user/system time monotonic. `getrusage1()` handles `RUSAGE_SELF` and `RUSAGE_CHILDREN`; `ruspace()` fills memory-size rusage fields from `vmspace`; `rulwps()` folds LWP usage into process usage.

## `plimit` and Sysctl Support

Limits are shared after fork until mutation. `lim_copy()` deep-copies rlimits and core-name state, carefully handling concurrent core-name length changes. `lim_privatise()` installs a writable private copy and keeps the old limit on `pl_sv_limit` so unlocked readers are not invalidated prematurely. `lim_free()` releases chained saved limits with memory barriers.

`sysctl_proc_corename()` validates visibility and `KAUTH_PROCESS_CORENAME`, and only accepts names equal to `core`, `/core`, or ending in `.core`. `sysctl_proc_stop()` reads/writes fork/exec/exit stop flags. `sysctl_proc_plimit()` reads or updates individual soft/hard rlimit values through `dosetrlimit()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_resource.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_runq.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_runq.c

## Purpose

`kern_runq.c` implements NetBSD's machine-independent scheduler run queue mechanics: per-CPU priority queues, enqueue/dequeue, preemption requests, multiprocessor CPU selection, load stealing, idle balancing, scheduler statistics, next-LWP selection, sysctl tunables, and DDB runqueue printing.

## Main Responsibilities

- Initializes scheduler balancing tunables in `runq_init()`.
- Attaches per-CPU scheduler state and run queues in `sched_cpuattach()`.
- Maintains per-priority `TAILQ` run queues and priority bitmaps.
- Enqueues/dequeues runnable LWPs.
- Requests user/kernel/idle preemption.
- Chooses CPUs for runnable LWPs and migrates/steals LWPs on MP systems.
- Updates scheduler statistics and selects the next LWP.
- Exposes `kern.sched` sysctl tunables.

## Run Queue Model

Each CPU has `struct schedstate_percpu` with run queues indexed by effective priority, `spc_bitmap[]` for non-empty priority queues, `spc_count` for runnable LWPs, `spc_mcount` for migratable runnable LWPs, and `spc_maxpriority` for the highest runnable priority.

`sched_enqueue()` inserts LWPs according to scheduling class and preemption state: `SCHED_OTHER` usually at tail, `SCHED_FIFO` at head when preempting, and `SCHED_RR` at head or tail depending on time-slice use. `sched_dequeue()` removes an LWP, updates counts, clears migration state, and recomputes `spc_maxpriority` by scanning bitmaps.

## Preemption

`sched_resched_cpu()` compares incoming priority with the CPU's current priority and sets idle, user-preempt, or kernel-preempt flags. It drops scheduler locks before poking remote CPUs when requested, avoiding immediate lock contention on wakeup. `sched_resched_lwp()` derives target CPU and priority from an LWP in `LSRUN`.

## Multiprocessor Balancing

`sched_migratable()` rejects offline CPUs and enforces affinity and processor-set constraints. `lwp_cache_hot()` keeps recently run timeshare LWPs sticky. `sched_bestcpu()` scans packages and cores, preferring idle first-class CPUs and otherwise lower competing priority and shorter queues. `sched_takecpu()` spreads new LWPs, handles vfork children specially, prefers idle siblings/core CPUs, and falls back to global CPU selection.

`sched_idle()` first completes pending migrations, then steals from SMT siblings, then scans packages subject to `skim_interval`. `sched_catchlwp()` steals migratable non-bound LWPs while avoiding cache-hot LWPs under gentle stealing. `sched_preempted()` and `sched_vforkexec()` set up target CPU migration for second-class CPU use and vfork/exec teleporting.

## Statistics and Debugging

`sched_lwp_stats()` updates sleep time, CPU-bound `LW_BATCH` state, tick sums, scheduler hooks, and DTrace `curthread`. `sched_nextlwp()` returns idle when there is no local work or migration is pending; otherwise it selects the first LWP in the highest-priority queue and marks it on-CPU. DDB support prints per-CPU runqueue state and process/LWP scheduling state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_runq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_rwlock.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_rwlock.c

## Purpose

`kern_rwlock.c` implements NetBSD kernel reader/writer locks. The implementation is partially adaptive: waiters spin while a write owner is actively running on a CPU, and otherwise block on turnstiles with priority inheritance support.

## Main Responsibilities

- Implements `_rw_init`, `rw_init`, `rw_destroy`, `rw_vector_enter`, `rw_vector_exit`, and `rw_vector_tryenter`.
- Implements `rw_downgrade()` and `rw_tryupgrade()`.
- Provides diagnostic held-state helpers: `rw_read_held`, `rw_write_held`, `rw_lock_held`, and `rw_lock_op`.
- Integrates with LOCKDEBUG, LOCKSTAT, turnstiles, sleep queues, pserialize assertions, and priority inheritance through `rw_owner()`.

## Lock Word Model

`rw->rw_owner` encodes either a writer LWP pointer or a reader count plus flags: `RW_WRITE_LOCKED`, `RW_HAS_WAITERS`, `RW_WRITE_WANTED`, and optional `RW_NODEBUG`. Readers acquire by adding `RW_READ_INCR`; writers acquire by adding the current LWP pointer plus `RW_WRITE_LOCKED`. CAS and swap operations update the owner word with acquire/release memory barriers.

## Acquisition and Release

`rw_vector_enter()` chooses reader or writer acquisition parameters, checks for self-deadlock on writer ownership, spins if the write owner is running on CPU and there are no effective sleep waiters, then uses turnstiles when it must block. Readers wait when a writer holds or wants the lock; writers wait on any reader or writer ownership.

`rw_vector_exit()` subtracts the reader or writer encoding. If the lock becomes free with waiters, it uses the turnstile interlock to wake readers or writers. Write release prefers waking all blocked readers when present; reader release can hand off to the longest-waiting writer or wake writers to compete while `RW_WRITE_WANTED` blocks new readers.

## Try, Downgrade, Upgrade

`rw_vector_tryenter()` performs non-blocking acquisition and returns 0 on contention. `rw_downgrade()` converts a write lock to one read hold, waking blocked readers when appropriate while preserving writer-wanted state. `rw_tryupgrade()` succeeds only if the caller is the sole reader, converting that read hold to write ownership.

## Concurrency Notes

`rw_oncpu()` requires preemption disabled while checking whether a write owner is still running. Turnstile blocking provides priority inheritance through the `rw_syncobj` owner callback. Diagnostic helpers are explicitly assertion-only and should not be used to make lock-protocol decisions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_rwlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_rwlock_obj.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_rwlock_obj.c

## Purpose

`kern_rwlock_obj.c` implements dynamically allocated, reference-counted rwlock objects. Each object embeds a `krwlock_t`, a magic value, and a reference count, padded to a cache coherency unit.

## Data Structure

`struct krwobj` contains:

- `ro_lock`: embedded rwlock.
- `ro_magic`: identity check using `RW_OBJ_MAGIC`.
- `ro_refcnt`: object reference count.
- padding sized for cacheline/coherency-unit layout.

## Functions

`rw_obj_alloc()` allocates with `kmem_intr_alloc(..., KM_SLEEP)`, asserts coherency alignment, initializes the embedded rwlock, and sets refcount 1.

`rw_obj_tryalloc()` is the non-sleeping allocation variant using `KM_NOSLEEP`, returning NULL on allocation failure.

`rw_obj_hold()` validates magic/refcount and atomically increments the reference count.

`rw_obj_free()` drops a reference with release/acquire barriers. If references remain, it returns false. On the last reference, it destroys the embedded rwlock, frees the object, and returns true.

`rw_obj_refcnt()` returns the current reference count without additional locking.

## Notes

This file is a small lifetime wrapper around `kern_rwlock.c`, for subsystems that need separately allocated lock objects shared by reference.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_rwlock_obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_scdebug.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_scdebug.c

## Purpose

`kern_scdebug.c` provides syscall debugging support when `SYSCALL_DEBUG` is enabled, plus indirect syscall implementations included from generated `sys_syscall.c`.

## Main Responsibilities

- Includes generated indirect syscall handlers twice: once as `sys_syscall` and once as `sys___syscall`.
- Defines runtime syscall debug flags under `SYSCALL_DEBUG`.
- Exposes global `scdebug`, defaulting to call, return, and argument logging.
- Supports optional KERNHIST logging.
- Initializes the syscall debug history buffer in `scdebug_init()` when both syscall debug and kernhist are enabled.

## Call Logging

`scdebug_call(code, args)` checks `SCDEBUG_CALLS`, finds the current process, emulation, and sysent entry, skips invalid/unimplemented syscalls unless `SCDEBUG_ALL` is set, and logs syscall number/name and arguments. The KERNHIST path avoids `%s` and uses literal format strings because history records are formatted later.

## Return Logging

`scdebug_ret(code, error, retval)` checks `SCDEBUG_RETURNS`, applies the same invalid/unimplemented filtering, and logs return error plus two return values either to kernhist or printf.

## Compat/Emulation Notes

`CODE_NOT_OK` accounts for `__HAVE_MINIMAL_EMUL`, so the debug path does not assume every emulation has a full syscall table. The generated indirect syscall functions are present for ports whose syscall entry code does not special-case `SYS_syscall` and `SYS___syscall`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_scdebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_sdt.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_sdt.c

## Purpose

`kern_sdt.c` provides machine-independent backend glue for Statically Defined Tracing kernel probes. It lets modules compiled with SDT probes link and load even when active DTrace kernel support is not present.

## Main Responsibilities

- Defines the `sdt` provider with `SDT_PROVIDER_DEFINE(sdt)`.
- Declares SDT link sets for providers, probes, and argument types.
- Provides global `sdt_probe_func`, initially set to `sdt_probe_stub`.
- Implements `sdt_probe_stub()`, `sdt_init()`, and `sdt_exit()`.
- Defines the `sdt:::set-error` probe with one integer argument.

## Behavior

`sdt_probe_stub()` should not normally be called. If it is called, it prints a diagnostic and dumps known provider, probe, and argument-type names from the link sets.

`sdt_init(dtrace_probe)` installs the real DTrace probe function. `sdt_exit()` restores the stub.

## Notes

This is compatibility/linkage infrastructure, not the active tracing engine. Runtime probe execution depends on DTrace installing the real probe callback.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_sdt.c -->