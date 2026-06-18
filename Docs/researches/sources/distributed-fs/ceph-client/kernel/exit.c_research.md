# sources/distributed-fs/ceph-client/kernel/exit.c

Purpose: implements process and thread termination, parent notification, reparenting, zombie reaping, wait-family syscalls, oops death handling, and cleanup ordering from `exit(2)`, `exit_group(2)`, fatal signals, and kernel oopses to `do_task_dead()`.

Important APIs/types/functions: exit APIs include `do_exit()`, `make_task_dead()`, `do_group_exit()`, `release_task()`, `put_task_struct_rcu_user()`, `mm_update_next_owner()`, `rcuwait_wake_up()`, and syscall wrappers for `exit`/`exit_group`. Wait APIs include `kernel_waitid_prepare()`, `kernel_wait4()`, `kernel_wait()`, `__do_wait()`, `pid_child_should_wake()`, `__wake_up_parent()`, and syscall wrappers for `waitid`, `wait4`, optional `waitpid`, and compat waits.

Control flow: `do_exit()` synchronizes group exit/coredumps, emits ptrace and tracing notifications, cancels io_uring work, marks `PF_EXITING`, collects accounting, handles last-thread group cleanup, stops perf before `exit_mm()`, tears down memory, IPC, files, fs, tty, namespaces, task work, thread state, autogroup and cgroups, flushes ptrace hardware breakpoints, enters tasks-RCU exit, reparents children, notifies parents, releases final policies/caches, checks locks/stack use, exits RCU, frees lockdep state, and calls `do_task_dead()`. `make_task_dead()` repairs unsafe oops context before exit or parks recursive faults.

Wait control flow: `do_wait()` installs a child waitqueue entry and loops through `__do_wait()`. The scanner validates PID filters, walks children and ptraced children, handles an optimized PID case, and delegates to `wait_consider_task()`. Zombie waits claim `EXIT_ZOMBIE` with cmpxchg, aggregate resource usage, fill wait info/status, and release tasks. Stopped and continued waits consume signal state under `sighand->siglock`.

State and persistence: key state includes task `exit_state`, `exit_code`, signal group-exit flags and accounting, pid links, parent relationships, child/ptrace lists, mm owner, wait queues, and sysfs/sysctl oops counters. It is memory-resident but visible through wait syscalls, pidfds, proc, taskstats, connector events, audit, and tracepoints.

Dependencies and integration points: touches scheduler, signals, ptrace, perf/hw breakpoints, mm, cgroups, namespaces, tty, audit, accounting, taskstats, futexes, io_uring, kcov/kmsan, user events, proc/pidfs, RCU/tasks RCU, lockdep, memcg, pid namespaces, and compat syscall handling.

Risks: ordering is critical: perf and deferred unwinds must stop before mm teardown; reparenting must respect subreapers and pid namespaces; wait paths must avoid double reaping; group exit must coordinate coredumps; and recursive oops handling must not return to damaged context. Locking spans `tasklist_lock`, `sighand->siglock`, seqlocks, task locks, RCU, and wait queues.

Test signals: LTP and kernel selftests should cover exit status encoding, `waitid()` options, pidfd waits, `WNOWAIT`, `WNOHANG`, stopped/continued reporting, ptrace reparenting, clone child selection, subreapers, orphaned pgrp SIGHUP/SIGCONT, coredumps, multithreaded `exit_group()`, and oops policy.
