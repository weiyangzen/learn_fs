# Group Research: group_415_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_kern_proc_c_sources__6c841b37033b

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_proc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_proc.c

## Purpose
FreeBSD kernel process-table, process-group, session, process-info export, and whole-system process-stop support. This is a central `sys/kern` implementation file backing PID lookup, `kern.proc.*` sysctls, process/session/job-control bookkeeping, and VM/process metadata reporting.

## Major Responsibilities
- Initializes process-global structures in `procinit()`: PID hash locks, process-group hash, `allproc_lock`, `proctree_lock`, `procid_lock`, `proc_zone`, `pgrp_zone`, and UID hash state.
- Implements type-stable `struct proc` and `struct pgrp` UMA lifecycle hooks: `proc_ctor()`, `proc_dtor()`, `proc_init()`, `proc_fini()`, and `pgrp_init()`.
- Manages PID/process-group/session ID bitmaps with `proc_id_set()`, `proc_id_set_cond()`, and `proc_id_clear()`.
- Provides process lookup helpers: `pfind()`, `pfind_any()`, `pfind_any_locked()`, `pgfind()`, `pget()`, and `proc_iterate()`.
- Handles process-group/session transitions and job-control orphaning through `enterpgrp()`, `enterthispgrp()`, `leavepgrp()`, `pgdelete()`, `killjobc()`, `orphanpg()`, `sess_hold()`, and `sess_release()`.
- Fills user-visible process snapshots in `kinfo_proc` through `fill_kinfo_proc()`, `fill_kinfo_proc_only()`, `fill_kinfo_proc_pgrp()`, `fill_kinfo_thread()`, and `fill_kinfo_aggregate()`.
- Implements `kern.proc` sysctl handlers for process lists, arguments, environment, auxv, executable pathname, ABI name, VM maps, kernel stacks, groups, rlimits, ps strings, umask, OS release, signal trampoline, sigfastblock, and VM layout.
- Implements `stop_all_proc()`, `resume_all_proc()`, and their blocker lock, used by kernel services needing a global stop of user-mode processes.

## Filesystem / VM Relevance
- `proc_get_binpath()` reports a process executable path using `p_textvp`, `p_textdvp`, and `p_binname`. It first tries `vn_fullpath_hardlink()` using the original exec hardlink name, verifies with `namei()`, and falls back to `vn_fullpath()`.
- `kern_proc_vmmap_out()` emits `kinfo_vmentry` records for a process address space, including vnode-backed mappings, vnode attributes, device pager paths, SysV/POSIX shared memory identity, copy-on-write flags, resident counts, and superpage flags.
- `kern_proc_vmmap_resident()` walks VM object backing chains and radix trees to estimate resident pages for map entries, using `pmap_mincore()` to account for superpages.
- Process umask reporting uses `p->p_pd->pd_cmask`; rlimit and executable-path reporting are common inspection hooks used by filesystem tools and procfs-like consumers.

## Locking and Lifetime Model
- `proctree_lock` protects process tree, process groups, sessions, and reaper/job-control relationships.
- PID hash buckets are protected by striped `pidhashtbl_lock[]`; `allproc_lock` protects global process iteration.
- Process state is protected by `PROC_LOCK(p)`; process-group/session state uses `PGRP_LOCK()` and `SESS_LOCK()`.
- `struct proc` and `struct pgrp` zones are `UMA_ZONE_NOFREE`, preserving pointer type stability for concurrent lookup/debug paths.
- Vnode and VM references are explicitly acquired before dropping process or map locks: e.g. `vref()`, `vmspace_acquire_ref()`, `VM_OBJECT_RLOCK()`, and `vn_lock()`.

## Key Interfaces
- Lookup: `pfind()`, `pfind_any()`, `pget()`, `pgfind()`, `proc_iterate()`.
- Process groups/sessions: `enterpgrp()`, `enterthispgrp()`, `leavepgrp()`, `sess_hold()`, `sess_release()`.
- Export: `kern_proc_out()`, `proc_getargv()`, `proc_getenvv()`, `proc_getauxv()`, `proc_get_binpath()`, `kern_proc_vmmap_out()`.
- Sysctl surface: `kern.proc.*` nodes for process table and per-process details.
- Global process quiescing: `stop_all_proc_block()`, `stop_all_proc_unblock()`, `stop_all_proc()`, `resume_all_proc()`.

## Notable Edge Cases
- `pget()` can treat TIDs as process selectors unless `PGET_NOTID` is set.
- `sysctl_kern_proc_args()` uses cached `pargs` when available, otherwise reads `ps_strings` from the target process memory.
- `get_proc_vector()` and 32-bit variant validate argument/environment/auxv vector counts and alignment before copying from target memory.
- VM map export restarts around map timestamp changes so records stay coherent across concurrent address-space modification.
- `stop_all_proc()` deliberately skips kernel/system/traced/exiting processes and loops until no restart conditions remain.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_procctl.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_procctl.c

## Purpose
Implements the FreeBSD `procctl(2)` syscall and kernel dispatcher for per-process and process-group controls. It covers protected-process flags, process reapers, subtree signaling, tracing controls, ASLR/protection policy controls, no-new-privs, W^X mapping policy, parent-death signal, and signal-exit logging policy.

## Major Responsibilities
- Validates and dispatches `sys_procctl()` commands through `procctl_cmds_info[]`.
- Implements protected-process toggling with optional descendant inheritance via `protect_set()`, `protect_setchild()`, and `protect_setchildren()`.
- Implements reaper acquire/release/status/PID-list/kill operations.
- Implements tracing and trapcap controls: `trace_ctl()`, `trace_status()`, `trapcap_ctl()`, `trapcap_status()`.
- Implements process hardening controls: `no_new_privs_*`, `protmax_*`, `aslr_*`, `stackgap_*`, `wxmap_*`, `logsigexit_*`.
- Implements parent-death signal get/set for the calling process.
- Applies commands to a single PID or all visible members of a process group through `kern_procctl()`.

## Reaper Logic
- `PROC_REAP_ACQUIRE` marks the calling process as a subtree reaper.
- `PROC_REAP_RELEASE` abandons children unless the process is `initproc`.
- `PROC_REAP_STATUS` reports current reaper PID, ownership flags, real-init status, child count, descendant count, and first descendant PID.
- `PROC_REAP_GETPIDS` snapshots reaper descendants into `procctl_reaper_pidinfo` records.
- `PROC_REAP_KILL` can signal reaper children or a subtree, tracks already-signaled PIDs with `unrhdr`, handles PID reuse via `P2_REAPKILLED`, and avoids using visibility failures as an oracle.

## Locking and Lifetime Model
- Each command declares required tree locking: shared `proctree_lock`, exclusive `proctree_lock`, or no tree lock.
- `kern_procctl_single()` holds and temporarily references target processes with `_PHOLD()` / `_PRELE()`.
- Reaper subtree killing may drop and reacquire `proctree_lock` around process-group `pg_killsx` synchronization.
- Commands needing whole-process-stop exclusion use the `sapblk` hook and `stop_all_proc_block()`.
- Process-group operations iterate `pg_members` under the required tree lock and per-process locks.

## Security Model
- Visibility and debug checks are command-specific through `p_cansee()` or `p_candebug()`.
- Capability mode blocks reaper kill and records `ktrcapfail()` when tracing is active.
- Signal delivery uses `p_cansignal()` or held credentials with `cr_cansignal()`.
- Protection controls require `PRIV_VM_MADV_PROTECT`.
- Many hardening controls require debug permission when modifying another process.

## Key Interfaces
- User entry: `sys_procctl()`.
- Kernel entry: `kern_procctl()`.
- Command metadata: `procctl_cmds_info[]`.
- Reaper support: `reap_acquire()`, `reap_release()`, `reap_status()`, `reap_getpids()`, `reap_kill()`.
- Policy toggles: ASLR, PROTMAX, stackgap, W^X, no-new-privs, tracing, trapcap, parent-death signal, and signal-exit logging.

## Notable Edge Cases
- Some commands are restricted to `P_PID` only through `one_proc`.
- Some commands translate missing process from `ESRCH` to `EINVAL`.
- `PROC_REAP_KILL` may copy out status even on error so callers can see partial kill results.
- `aslr_status()` and `wxmap_status()` temporarily drop the process lock to acquire `vmspace` references.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_procctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_prot.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_prot.c

## Purpose
Implements process identity, credential, group, visibility, signaling, debugging, and login/session protection syscalls and kernel helpers. This is the core credential/security policy file for UID/GID changes, process visibility checks, signal permission checks, debug permission checks, and `struct ucred` lifecycle.

## Major Responsibilities
- Implements identity getters: `getpid`, `getppid`, `getpgrp`, `getpgid`, `getsid`, `getuid`, `geteuid`, `getgid`, `getegid`, `getgroups`, `getresuid`, and `getresgid`.
- Implements session/process-group setters: `setsid()` and `setpgid()`.
- Implements credential mutation syscalls: `setcred`, `setuid`, `seteuid`, `setgid`, `setegid`, `setgroups`, `setreuid`, `setregid`, `setresuid`, and `setresgid`.
- Implements `issetugid()` and regression-only `__setugid`.
- Implements BSD visibility policies behind `security.bsd.see_other_uids`, `see_other_gids`, and `see_jail_proc`.
- Implements permission checks for process visibility, signal delivery, scheduling, debugging, socket visibility, and waiting.
- Implements credential allocation, copy, reference counting, COW synchronization, batching, group normalization, and process credential installation/removal.
- Implements login name get/set and credential field mutators.

## Credential Model
- `struct ucred` references are optimized with split `cr_users` and `cr_ref` accounting.
- Threads whose `td_realucred` matches the credential use `td_ucredref` to avoid frequent shared cache-line refcount traffic.
- `crcowget()`, `crcowfree()`, `crcowsync()`, `credbatch_add()`, and `credbatch_final()` manage COW and batched inactive-thread credential release.
- `crget()`, `crhold()`, `crfree()`, `crcopy()`, `crdup()`, `crcopysafe()`, and `crfree_final()` manage allocation and lifetime.
- `proc_set_cred()` and `proc_set_cred_enforce_proc_lim()` install process credentials and update process-count accounting.

## Group Handling
- Supplementary groups are normalized by sorting and duplicate removal in `groups_normalize()`.
- `group_is_supplementary()` uses binary search, relying on normalized groups.
- `groupmember()` checks effective GID plus supplementary groups; `realgroupmember()` checks real GID plus supplementary groups.
- `crsetgroups()`, `crsetgroups_internal()`, and `crsetgroups_and_egid()` update credential group arrays after `crextend()` ensures capacity.

## Security and Policy Hooks
- MAC hooks are integrated throughout setuid/setgid/setgroups/setcred, visibility, signaling, scheduling, debugging, socket visibility, and wait checks.
- Jail checks use `prison_check()` and parent-jail tamper rules via `cr_can_tamper_with_subjail()`.
- RACCT/RCTL hooks update accounting after credential changes.
- Debugging is controlled by `security.bsd.unprivileged_proc_debug`, `P_SUGID`, `P_INEXEC`, `P2_NOTRACE`, securelevel restrictions on `initproc`, and credential subset checks.
- Signal delivery is constrained by jail, MAC, BSD visibility, conservative `P_SUGID` signal policy, UID matching, and cross-jail tamper privilege.

## Key Interfaces
- Visibility: `cr_cansee()`, `p_cansee()`, `cr_bsd_visible()`, `cr_canseesocket()`.
- Permissions: `cr_cansignal()`, `p_cansignal()`, `p_cansched()`, `p_candebug()`, `p_canwait()`.
- Credentials: `crget()`, `crhold()`, `crfree()`, `crcopy()`, `crdup()`, `crcopysafe()`, `proc_set_cred()`, `proc_unset_cred()`.
- Identity mutators: `change_euid()`, `change_ruid()`, `change_svuid()`, `change_egid()`, `change_rgid()`, `change_svgid()`.
- Login/session: `sys_getlogin()`, `sys_setlogin()`, `setsugid()`.

## Notable Edge Cases
- Legacy FreeBSD 14 `getgroups`/`setgroups` compatibility treats effective GID as the first group.
- `kern_setcred()` builds the full new credential before MAC checks, then installs atomically under the process lock.
- Real UID changes can fail when process-count limits are enforced unless privilege overrides them.
- `crsetgroups()` accepts unsorted input and normalizes it before use.
- `allow_ptrace` is exposed as a tunable `security.bsd.allow_ptrace`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_prot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_racct.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_racct.c

## Purpose
Implements FreeBSD RACCT resource accounting and its integration with optional RCTL resource controls. It tracks per-process and container resource usage for users, login classes, and jails, enforces denyable allocations when RCTL is enabled, and periodically updates decaying resources such as CPU and I/O rates.

## Major Responsibilities
- Defines RACCT resource type flags in `racct_types[]`: reclaimable, inheritable, denyable, decaying, sloppy, and million-scaled resources.
- Allocates and destroys `struct racct` instances with `racct_create()` and `racct_destroy()`.
- Adds, sets, subtracts, and force-updates process and credential resource usage.
- Propagates usage to real UID, jail hierarchy, and login-class RACCT containers.
- Integrates fork/exit lifecycle through `racct_proc_fork()`, `racct_proc_fork_done()`, and `racct_proc_exit()`.
- Moves accounting between credentials on credential changes through `racct_proc_ucred_changed()`.
- Tracks CPU runtime, wallclock, percent CPU, and decaying I/O resources.
- Implements process throttling through AST scheduling and a `racctd` kernel process.

## Accounting Flow
- `racct_add_locked()` optionally calls `rctl_enforce()` before increasing denyable resources.
- `racct_set_locked()` computes a diff from the current process amount and propagates positive or negative deltas to credential containers.
- `racct_sub()` requires droppable resources and asserts that released amount does not exceed process usage.
- `racct_add_cred_locked()` and `racct_sub_cred_locked()` update real UID, all containing prisons, and login class.
- `racct_sub_racct()` clamps sloppy/decaying drops to zero and asserts exact accounting for normal reclaimable resources.

## Periodic Worker
- `racctd()` runs once per second.
- It decays container I/O throttles, walks all processes under `allproc_lock`, updates CPU/wallclock usage, updates percent CPU, then performs a second pass to throttle or wake processes based on PCPU availability.
- It updates UID, login-class, and jail container PCPU after process accounting is refreshed.

## Locking and Lifetime Model
- `racct_lock` serializes RACCT state.
- Process resource operations require `PROC_LOCK(p)` when dereferencing `p_ucred`.
- Container iteration uses callbacks that acquire and release `racct_lock`.
- Process exit zeroes PCPU, drops reclaimable resources, releases RCTL state, and destroys the process RACCT under lock.

## Key Interfaces
- Allocation/lifetime: `racct_create()`, `racct_destroy()`.
- Process usage: `racct_add()`, `racct_add_force()`, `racct_set()`, `racct_set_force()`, `racct_set_unlocked()`, `racct_sub()`.
- Credential/container usage: `racct_add_cred()`, `racct_sub_cred()`, `racct_move()`.
- Limits: `racct_get_limit()`, `racct_get_available()`.
- Lifecycle: `racct_proc_fork()`, `racct_proc_fork_done()`, `racct_proc_exit()`, `racct_proc_ucred_changed()`.

## Notable Edge Cases
- RACCT can be compiled/tuned disabled; almost every public entry returns early when `racct_enable` is false.
- `racct_proc_fork()` rolls back with `racct_proc_exit(child)` if inheritable accounting or NPROC/NTHR charging fails.
- Kernel/system processes and low-CPU processes are exempt from throttling.
- Disk I/O accounting uses current process charging and is force-added because these limits are not denyable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_racct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_rangelock.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_rangelock.c

## Purpose
Implements FreeBSD scalable range locks used by subsystems that need byte/range-granular read/write exclusion, commonly for file or VM-object style ranges. The implementation starts in a compact “cheating” mode and falls back to a precise SMR-protected range queue when conflicts require real range tracking.

## Major Responsibilities
- Initializes/destroys `struct rangelock` with `rangelock_init()` and `rangelock_destroy()`.
- Provides read/write lock and trylock entry points: `rangelock_rlock()`, `rangelock_tryrlock()`, `rangelock_wlock()`, and `rangelock_trywlock()`.
- Releases locks with `rangelock_unlock()`.
- Supports callers that may recursively acquire on the same lock through `rangelock_may_recurse()`.
- Provides DDB inspection under `show rangelock`.

## Cheating Mode
- Controlled by debug tunable `debug.rangelock_cheat`.
- A newly initialized lock behaves like a compact whole-object read/write lock using bits in `lock->head`.
- Multiple readers can enter without allocating queue entries.
- A conflicting request sets `RL_CHEAT_DRAINING`, waits for existing cheat holders to leave, wakes sleepers, and transitions to precise non-cheat mode.
- Trylocks in cheat mode fail without draining when a conflict exists.

## Precise Range-Lock Mode
- Uses `struct rl_q_entry` queue entries allocated from an SMR UMA zone.
- Queue entries store start/end offsets, read/write flags, next links, deferred-free links, and invariant owner thread.
- Implements sorted insertion and conflict detection based on range overlap and read/read compatibility.
- Marked next pointers represent logically removed entries; dead entries are physically unlinked and freed after SMR exit.
- Read validation only checks later conflicting writers; write validation checks prior overlapping entries before the writer.

## Locking and Memory Model
- Uses atomic pointer operations for queue head/next updates.
- Uses SMR sections around queue traversal and CAS insertion/removal.
- Uses sleep queues on `lock->sleepers` for precise-mode conflicts and on `lock->head` for cheat-mode draining.
- Drops and reacquires Giant around sleeps.
- `rangelock_unlock_int()` marks the entry, clears sleeper state, and broadcasts waiters.

## Key Interfaces
- `rangelock_init(struct rangelock *)`
- `rangelock_destroy(struct rangelock *)`
- `rangelock_rlock(lock, start, end)`
- `rangelock_tryrlock(lock, start, end)`
- `rangelock_wlock(lock, start, end)`
- `rangelock_trywlock(lock, start, end)`
- `rangelock_unlock(lock, cookie)`
- `rangelock_may_recurse(lock)`

## Notable Edge Cases
- Cheat-mode cookies are sentinel pointer values rather than allocated queue entries.
- Recursive/conflicting acquisition by the same thread is asserted against in precise mode.
- Trylock failure after insertion may leave the entry marked and defer freeing until safe.
- Destroying a non-cheat lock drains marked entries and waits if any live entry remains.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_rangelock.c -->