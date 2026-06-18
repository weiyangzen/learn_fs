# Group Research: group_411_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_kern_event_c_sources_8bc94967320b

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_event.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_event.c

Read status: complete file reviewed.

This file implements FreeBSD's kqueue/kevent core and the generic knote/knlist machinery used by many kernel objects to publish readiness and lifecycle events. It defines kqueue file operations, kevent syscall handling, filter registration, event scanning, notification delivery, timer/user/process/jail filters, kqueue fork-copy support, and sysctl export of process kqueue state.

Main entry points include `sys_kqueue`, `sys_kqueuex`, `kern_kqueue`, `sys_kevent`, `kern_kevent`, `kern_kevent_fp`, `kern_kevent_anonymous`, `kqfd_register`, `kqueue_add_filteropts`, `kqueue_del_filteropts`, `knote`, `knlist_add`, `knlist_remove`, `knlist_cleardel`, `knote_fdclose`, `knote_fork`, `knote_triv_copy`, and `kern_proc_kqueues_out`. The `kqueueops` table exposes kqueues as file descriptors with ioctl, poll, kqfilter, stat, close, fork, and kinfo handlers.

Core state is built around `struct kqueue`, `struct knote`, per-kqueue fd lists and non-fd hash lists, the global `sysfilt_ops[]` filter table, `knote_zone`, and `kq_ncallouts` bounded by `kern.kq_calloutmax`. Locking is central: `kq_lock` serializes each queue, `kq_global` orders nested kqueue interactions, `filterops_lock` protects dynamic filter refs, and `kn_influx` plus `KQ_FLUXWAIT` coordinates teardown or modification while a knote is being scanned or copied.

The syscall path copies change records in bounded `KQ_NEVENTS` batches, registers or updates knotes with `kqueue_register`, then drains ready events through `kqueue_scan`. `kqueue_scan` handles blocking timeouts, disabled knotes, oneshot/drop semantics, event revalidation, EV_CLEAR/EV_DISPATCH behavior, batched copyout, and wakeups for threads waiting on in-flux knotes. Capability rights are enforced via `CAP_KQUEUE_CHANGE` and `CAP_KQUEUE_EVENT`.

Built-in filters include fd-backed file/vnode/socket-style filters delegated to `fo_kqfilter`, kqueue-read filters, process filters with `NOTE_EXIT`, `NOTE_EXEC`, `NOTE_FORK`, and `NOTE_TRACK`, jail filters, callout-backed timers with absolute/relative sbintime support, and EVFILT_USER state machines. Timer filters maintain per-knote callout data, pause timers for stopped/killed processes, enforce the global callout cap, and support re-add touch updates.

Lifecycle paths are extensive. `kqueue_drain` marks a queue closing, waits for extra refs, drops all knotes, drains taskqueue work, and wakes poll/select waiters. `kqueue_close` removes the queue from the filedesc list and releases credentials and accounting. `knote_drop` and `knote_drop_detached` detach from source knlists, remove queue membership, release fd and filter refs, and free UMA knotes. `knlist_detach` supports autodestroy lists, while `knlist_cleardel` handles disappearing event sources.

Fork support implements `KQUEUE_CPONFORK`: `kqueue_fork_alloc` creates the destination kqueue, and `kqueue_fork_copy_*` copies eligible knotes with filter-specific `f_copy` hooks while respecting fd validity, fhold, knlist membership, active queue state, and in-flux markers.

Integration points include file descriptor tables, proc/jail lifecycle notification, callouts, taskqueues, Capsicum rights, poll/select, sysctl `kern.proc.kq`, KTRACE compatibility, 32-bit compat conversion, and external filterops from signal and filesystem modules.

Risk areas are lock ordering and in-flux correctness, fd reuse races around `fget_noref_unlocked`, nested kqueue notification recursion, timer callout drain/reschedule races, process tracking note creation under `NOTE_TRACK`, and exact queue count accounting under EV_CLEAR, EV_DISPATCH, EV_ONESHOT, and EV_DROP paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_event.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_exec.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_exec.c

Read status: complete file reviewed.

This file implements process image replacement, exec argument management, executable permission checks, VM replacement, user stack setup, image activator registration, and core dump output helpers. It is the central `execve(2)` path for named files, file-descriptor exec, and MAC-aware exec.

Main entry points include `sys_execve`, `sys_fexecve`, `sys___mac_execve`, `pre_execve`, `post_execve`, `kern_execve`, `exec_cleanup`, `exec_map_first_page`, `exec_unmap_first_page`, `exec_onexec_old`, `exec_new_vmspace`, `exec_map_stack`, `exec_copyin_args`, `exec_alloc_args`, `exec_free_args`, `exec_args_add_fname`, `exec_args_add_arg`, `exec_args_add_env`, `exec_args_adjust_args`, `exec_copyout_strings`, `exec_check_permissions`, `exec_register`, `exec_unregister`, `core_write`, `core_output`, and `sbuf_drain_core_output`.

The main control flow is `sys_*execve` -> `pre_execve` -> argument copyin -> `kern_execve` -> `do_execve` -> image activator dispatch. `pre_execve` single-threads multithreaded processes at an exec boundary, and `post_execve` either upgrades successful exec to `SINGLE_EXIT` so old sibling threads die or releases the single-thread boundary on failure. `exec_cleanup` frees the old vmspace after successful replacement.

`do_execve` sets `P_INEXEC`, resolves the executable by path, interpreter vnode, or fd, audits the vnode, checks permissions, maps the first page, computes setuid/setgid/MAC credential transitions, and iterates registered `execsw` image activators. Interpreted scripts loop back through `interpret`, dropping text refs and vnode state from the script before activating the interpreter. After activation it copies strings and aux data to the new stack, unshares fds and paths, closes close-on-exec descriptors, resets signals, updates process names, installs credentials, updates text vnode/binname fields, emits kqueue `NOTE_EXEC`, notifies DTrace/PMC/HWT hooks, and initializes registers.

Permission checks require a regular non-empty executable file on an executable mount, pass MAC and VOP access checks, set a text reference with `VOP_SET_TEXT`, and open the vnode for read. Security-sensitive handling includes Capsicum path restrictions for interpreter resolution, suppression of setid transitions on `MNT_NOSUID`, tracing, capability mode, or `P2_NO_NEW_PRIVS`, fd safety for setid exec, clearing inherited death signals on credential changes, and resetting syscall tracing for setid programs.

VM setup is split between `exec_new_vmspace` and `exec_map_stack`. The former destroys or replaces the address space, handles shared-page cleanup, drops System V shared memory, clears ASLR/W^X/wirefuture map flags, invokes process-exec handlers, and calls ABI-specific `sv_onexec`. The latter maps the main stack, applies ASLR stack offset, maps the ABI shared page or guard page, and records `vm_stacktop`, `vm_maxsaddr`, and shared page base.

Argument handling uses preallocated exec KVA ranges stored in a global and per-CPU cache. `exec_prealloc_args_kva` initializes ranges, `exec_alloc_args_kva` obtains one, and the low-memory handler advances a generation so freed ranges get `MADV_FREE`. String assembly enforces `ARG_MAX`, preserves filename, argument, and environment order, and supports interpreter prepending through `exec_args_adjust_args`.

Core dump helpers write sparse or compressed memory segments. `core_output` faults user pages in runs, writes present pages, extends holes for absent pages, tolerates EFAULT from truncated mapped files, and can return EINTR if SIGKILL arrives when `kern.core_dump_can_intr` is enabled. `sbuf_drain_core_output` safely drains procstat-like notes even when called with the process lock held.

Sysctls expose `kern.ps_strings`, `kern.usrstack`, `kern.stackprot`, `kern.ps_arg_cache_limit`, `kern.disallow_high_osrel`, `security.bsd.map_at_zero`, core dump packing toggles, and interruptible core dump behavior.

Risk areas are rollback after partial exec, vnode lock/ref/text accounting across interpreter loops, setid credential timing, old vmspace cleanup when exec failure occurs after VM destruction, argument KVA lifetime under low memory, fd table unsharing before close-on-exec, and coredump behavior for changing user mappings.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_exit.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_exit.c

Read status: complete file reviewed.

This file implements process exit, asynchronous syscall-exit handling, abort logging, wait/wait6/pdwait, zombie reaping, reparenting, reaper subtree cleanup, orphan tracking for ptrace, and process-parent notification.

Main entry points include `sys__exit`, `kern_exit`, `exit1`, `exit_onexit`, `proc_set_p2_wexit`, `sys_abort2`, `kern_abort2`, `sys_wait4`, `sys_wait6`, `sys_pdwait`, `kern_wait`, `kern_wait6`, `kern_pdwait`, `proc_reap`, `proc_reparent`, `proc_add_orphan`, `proc_clear_orphan`, `proc_realparent`, and `reaper_abandon_children`.

`kern_exit` handles the normal syscall path and the ptrace remote syscall case. If `TDB_SCREMOTEREQ` is active it stores the desired exit status/signal, marks `P_ASYNC_EXIT`, and schedules `TDA_ASYNC_EXIT`; otherwise it calls `exit1` directly. `initexit` registers the async-exit AST handler.

`exit1` is the full process teardown path. It protects init from accidental death, clears kernel AST cleanup, marks write-exit flags, single-threads and terminates other threads, stores exit code/signal, drains limit callouts, audits the exit, kills task peers for task leaders, runs process-exit event handlers, stops profiling and interval timers, calls ABI exit hooks, releases sigio ownership, frees procdesc and filedesc tables, removes peer links, releases VM resources and accounting, drops text vnode/binname references, frees limits, removes the process from allproc and prison lists, reparents children and orphans, emits DTrace/kqueue exit notifications, handles procdesc exit suppression of parent signals, queues SIGCHLD or custom parent signal, flushes signal queues, transitions to `PRS_ZOMBIE`, accumulates child rusage, and calls `thread_exit`.

Wait handling is centered on `kern_wait6`. `wait6_checkopt` validates flags, `proc_to_reap` filters children by id type and options, and `wait6_check_alive` reports traced, stopped, or continued live children. `proc_reap` finalizes zombies: it supports `WNOWAIT`, moves ptraced children back to their real parent when appropriate, removes pid hash and sibling links, clears reaper/orphan state, leaves process groups, detaches the process knlist, folds rusage into the waiting parent, releases RACCT state, credentials, pargs, sigacts, threads, VM/machine resources, MAC state, and drops the process-tree reference.

`kern_pdwait` mirrors wait semantics for process descriptors. It validates rights with `cap_pdwait_rights`, uses the procdesc's process pointer under `proctree_lock`, supports live stopped/trapped/continued reporting, reaps zombies, and sleeps on the procdesc channel when blocking.

Reparenting and reaper logic maintain parent, original-parent, orphan, and reaper-subtree invariants. `proc_realparent` resolves ptrace/orphan cases, `proc_reparent` moves children between parent lists and queues pending child status to the old parent, and `reaper_abandon_children` moves a dying reaper's subtree to its own reaper. `proc_clear_orphan` preserves `P_TREE_FIRST_ORPHAN` markers.

`kern_abort2` logs bounded user-provided reason text and up to 16 pointer arguments, then exits with SIGABRT on valid input or SIGKILL when user data is inaccessible. Compatibility `owait` routes to `kern_wait`.

Sysctls include `kern.kill_on_debugger_exit`, controlling whether traced children are killed when a debugger exits, and `kern.wait_dequeue_sigchld`, controlling SIGCHLD dequeue behavior when waiting on live process events.

Risk areas are lock ordering across `proctree_lock`, `allproc_lock`, proc locks, and pgrp/session locks; lost wakeups around zombie transition; ptrace orphan/reparent edge cases; procdesc exit races; async exit reentry; resource accounting exactly once; and preserving child waitability while preventing stale process references.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_exit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_fail.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_fail.c

Read status: complete file reviewed.

This file implements the FreeBSD failpoint facility, allowing runtime fault injection through sysctl strings. It parses failpoint programs, installs them atomically, evaluates them cheaply when enabled, supports probabilistic/count/pid-qualified actions, reports state, and garbage-collects old settings after concurrent users drain.

Main public entry points include `fail_point_init`, `fail_point_destroy`, `fail_point_alloc_callout`, `fail_point_is_off`, `fail_point_eval_nontrivial`, `fail_point_sysctl`, `fail_point_sysctl_status`, and `fail_sysctl_drain_func`. The debug sysctl `debug.fail_point.test_trigger_fail_point` exercises the test failpoint.

The internal model uses `struct fail_point`, `struct fail_point_setting`, and `struct fail_point_entry`. A setting contains a queue of entries; each entry has a type, argument, probability in millionths, optional fire count, optional pid restriction, stale flag, and parent pointer. Settings are swapped via `fail_point_swap_settings`, while readers take references by incrementing `fp_ref_cnt` before reading `fp_setting`.

Supported action types are `off`, `panic`, `return`, `break`, `print`, `sleep`, `pause`, `yield`, and `delay`. Evaluation applies probability, pid, and count filters, then executes the first non-continuing matching action. `print` can request continuation using its argument. `sleep` can either block through `tsleep` or queue a timeout callout when `FAIL_POINT_USE_TIMEOUT_PATH` is set. `pause` sleeps until the failpoint is changed or disabled. Sleep actions in `FAIL_POINT_NONSLEEPABLE` contexts are converted to busy delays.

Sysctl setting is serialized by `sx_fp_set`. `fail_point_set` parses a new program into a fresh setting, removes impossible zero-probability or zero-count entries, truncates unreachable entries after permanent `off` or `pause`, wakes paused threads when needed, and swaps the setting into the failpoint. Old settings remain on a garbage list until no evaluator references exist. `fail_point_drain` is used during destroy to swap off the setting, wake paused waiters, wait for refs to drain, drain any callout, and restore or clean state.

The parser accepts chains of terms separated by `->`. Each term supports optional probability like `12.5%`, optional count like `3*`, a type name, optional integer argument in parentheses, and optional `[pid N]`. `parse_number` rounds fractional probabilities to the supported precision, and `FP_MAX_ENTRY_COUNT` bounds sysctl-provided chains.

Status output converts active entries back to text and can optionally include sleeping/paused thread counts and, with `STACK`, stack traces for sleepers. Sysctl output uses an sbuf drain callback to stream to the sysctl request.

Concurrency design depends on atomic refcounts, a spin mutex for the garbage list, and the sleepable sx lock for set/get operations. Old settings are not freed while any evaluator might still be walking them, and stale entries are ignored until collection.

Risk areas are refcount correctness in `fail_point_setting_get_ref/release_ref`, races between evaluator stale marking and sysctl replacement, pause/sleep wakeup semantics during destroy, parser acceptance of malformed chains, count decrement atomicity, and the distinction between sleepable and non-sleepable failpoints.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_fail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_ffclock.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_ffclock.c

Read status: complete file reviewed.

This file implements the optional feed-forward clock syscall and high-level time access layer when `FFCLOCK` is enabled, with ENOSYS stubs otherwise. It exposes absolute time, uptime, interval conversion, sysclock selection sysctls, and user/kernel estimate exchange.

Main functions under `FFCLOCK` include `ffclock_abstime`, `ffclock_difftime`, the `ffclock_*time` and `ffclock_*uptime` wrapper family, `ffclock_*difftime` wrappers, `sys_ffclock_getcounter`, `sys_ffclock_setestimate`, and `sys_ffclock_getestimate`.

`ffclock_abstime` reads the feed-forward counter, either through the fast last-tick path or direct counter read plus conversion, then snapshots `ffclock_estimate` using `update_ffcount` as a generation check. It applies optional leap-second adjustment, optional boot-time subtraction for uptime clocks, and optional error-bound calculation based on elapsed counter time, absolute error, and rate error. `ffclock_difftime` converts a counter delta to bintime and optionally computes interval error bounds from the current estimate's rate error.

The sysctl tree adds `kern.sysclock`, `kern.sysclock.ffclock`, `kern.sysclock.available`, `kern.sysclock.active`, `kern.sysclock.ffclock.version`, and `kern.sysclock.ffclock.ffcounter_bypass`. The active sysclock handler exposes `"feedback"` and `"feed-forward"` and allows switching `sysclock_active` by string.

The wrapper functions provide standard FreeBSD clock APIs backed by ffclock: wall-clock bintime/nanotime/microtime, fast get* variants, uptime variants with `FFCLOCK_UPTIME`, and difference conversions from `ffcounter` deltas. They compose flags such as `FFCLOCK_LERP`, `FFCLOCK_LEAPSEC`, `FFCLOCK_FAST`, and `FFCLOCK_UPTIME`.

Syscalls support userland synchronization daemons and applications. `sys_ffclock_getcounter` returns the current counter or EAGAIN if unavailable. `sys_ffclock_setestimate` requires `PRIV_CLOCK_SETTIME`, copies in an estimate, updates global `ffclock_estimate` under `ffclock_mtx`, and increments `ffclock_updated` so timehands pick up the new estimate. `sys_ffclock_getestimate` copies out the current estimate under the same mutex.

When `FFCLOCK` is not compiled in, the three syscalls return `ENOSYS`, preserving syscall symbols without enabling functionality.

Risk areas are lockless estimate snapshot consistency, generation wrap assumptions, precision/overflow in fixed-point error-bound multipliers, sysclock string matching, privilege enforcement for estimate updates, and behavior when hardware counter reads return zero.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_ffclock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_fork.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_fork.c

Read status: complete file reviewed.

This file implements process creation and rfork variants, including `fork`, `vfork`, `rfork`, process descriptors, PID allocation, non-process rfork unsharing, child process initialization, vfork parent waiting, and child return-to-userland setup.

Main entry points include `sys_fork`, `sys_pdfork`, `sys_vfork`, `sys_rfork`, `sys_pdrfork`, `fork1`, `fork_exit`, and `fork_return`. Internal helpers include `sysctl_kern_randompid`, `fork_findpid`, `fork_norfproc`, `do_fork`, `ast_vfork`, and `fork_init`.

Syscall wrappers populate `struct fork_req` with appropriate flags. `fork` uses `RFFDG | RFPROC`; `pdfork` adds `RFPROCDESC`; `vfork` uses `RFPPWAIT | RFMEM`; `rfork` accepts user flags with validation and maps `RFSPAWN` to a vfork-like spawn mode that drops caught signals; `pdrfork` combines rfork semantics with process descriptor creation.

PID allocation is handled by `fork_findpid`, using `lastpid`, optional `kern.randompid`, `pid_max`, and proc id bitmaps for pid, process group, session, and reaper ids. It avoids PID collisions with other id namespaces and supports `RFHIGHPID` for boot-time high pid allocation.

`fork1` validates flags, enforces process descriptor constraints, handles rfork-without-`RFPROC` by calling `fork_norfproc`, increments global `nprocs` against `maxproc`, serializes with process-group signal delivery via `pg_killsx`, optionally single-threads the parent, allocates a procdesc fd, allocates/recycles `proc` and first `thread`, forks or shares vmspace, performs swap reservation, copies credentials, initializes RACCT/MAC state, enforces `RLIMIT_NPROC`, allocates a process knlist, and calls `do_fork`. Failure paths unwind vmspace, proc refs, procdesc fd, credentials, RACCT, MAC, and process counts.

`fork_norfproc` supports rfork operations that alter the current process rather than create a new one. It may single-thread the process, calls `vm_forkproc` with no child proc, clears or unshares file descriptor/path tables for `RFCFDG`/`RFFDG`, then releases the single-thread boundary.

`do_fork` performs the actual child initialization. It copies selected proc/thread fields, assigns PID, links into allproc, prison, pid hash, and tid hash, allocates/copies fd and path descriptors according to RFCFDG/RFFDG/share flags, sets scheduler state, copies signal actions or shares them, applies spawn/kernel-process signal handling flags, copies text vnode/binname refs, inherits selected flags, forks limits/COW/thread state/stats, handles RFTHREAD peer lists, inserts the child into process group and parent/reaper lists, calls `vm_forkproc`, updates fork/vfork/rfork/kthread counters, initializes procdesc state, invokes process_fork handlers, marks `PRS_NORMAL`, notifies DTrace, arranges vfork parent wait state, emits `knote_fork`, handles ptrace fork events, completes RACCT fork accounting, and either makes the child runnable or returns it stopped.

`ast_vfork` enforces vfork parent synchronization by waiting while the child has `P_PPWAIT`, handling suspension checks, then optionally reporting `PTRACE_VFORK`. `fork_init` registers this AST. `fork_exit` is the machine-independent entry for new child threads from MD trampoline code: it finishes scheduler fork state, stashes dead threads, calls the supplied child callout, handles erroneous kernel-thread returns, invokes ABI schedtail, and enters `userret`. `fork_return` handles ptrace stop-at-fork and syscall-exit reporting, kills the child if its prison died mid-fork, and emits KTRACE syscall return records.

Integration points include process accounting, jails, MAC, RACCT, Capsicum process descriptors, ptrace, kqueue `NOTE_FORK`, DTrace, VM/swap, fd/path descriptors, pgrp signal serialization, proc id bitmaps, scheduler hooks, and syscall return conventions.

Risk areas are failure unwinding after partial child visibility, process count and uid count accounting, `pg_killsx` signal serialization, vfork `P_PPWAIT` wakeups, procdesc initialization ordering, PID namespace collision checks, ptrace fork reparenting, RFTHREAD peer cleanup, and preserving parent/child locks in the expected order.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_fork.c -->