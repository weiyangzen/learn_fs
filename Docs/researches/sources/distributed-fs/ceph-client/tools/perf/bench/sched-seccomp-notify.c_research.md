# sources/distributed-fs/ceph-client/tools/perf/bench/sched-seccomp-notify.c

Purpose: implements `perf bench sched seccomp-notify`, measuring seccomp user notification round-trip cost for intercepted `gettid` syscalls. It creates a seccomp filter with `SECCOMP_RET_USER_NOTIF`, forks a syscall-generating child, services notifications in the parent, and reports total time and per-call rate.

Important APIs, types, and functions: `seccomp()` wraps the raw `__NR_seccomp` syscall. `user_notif_syscall()` builds a BPF seccomp program that traps one syscall number and returns allow for the rest. `user_notification_sync_loop()` repeatedly receives `struct seccomp_notif`, validates the syscall, and replies with `struct seccomp_notif_resp` whose return value is `USER_NOTIF_MAGIC`. `bench_sched_seccomp_notify()` owns option parsing, filter installation, fork, optional sync wakeup flag, timing, child kill, and output.

Control flow: the parent sets `PR_SET_NO_NEW_PRIVS`, installs a filter using `SECCOMP_FILTER_FLAG_NEW_LISTENER`, then forks. The child sets `PR_SET_PDEATHSIG` and loops on `gettid`; as long as the intercepted syscall returns `USER_NOTIF_MAGIC`, it continues. The parent optionally enables `SECCOMP_USER_NOTIF_FD_SYNC_WAKE_UP`, services exactly `loops` notifications, kills the child, validates it died by `SIGKILL`, and prints in default or simple format.

State and persistence: no persistent state is written. Kernel state includes a seccomp listener fd and a child under the inherited seccomp filter. The listener drives all timing state, and the child is intentionally killed after the measured loop.

Dependencies and integration points: requires Linux seccomp user notification support, BPF filter definitions, `ioctl(SECCOMP_IOCTL_NOTIF_RECV/SEND)`, `prctl`, fork, and perf bench globals. It is registered in `builtin-bench.c` under `sched`.

Risks: old kernels or headers may lack notification features, though fallback defines cover the sync flag constants. Any unexpected syscall number, ioctl failure, fork failure, or wait mismatch exits via `err()` or `errx()`. The usage string contains a typo (`secccomp-notify`). The child spins forever unless the parent completes or dies, so cleanup relies on `PDEATHSIG` and explicit `SIGKILL`.

Test signals: smoke test with a small `--loop`, with and without `--sync-mode`, and on kernels with seccomp notify enabled. Confirm simple output is just elapsed time, default output reports the requested loop count, and failure modes are clear on unsupported kernels.
