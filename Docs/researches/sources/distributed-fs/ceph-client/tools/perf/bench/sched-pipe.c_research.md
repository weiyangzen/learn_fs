# sources/distributed-fs/ceph-client/tools/perf/bench/sched-pipe.c

Purpose: implements `perf bench sched pipe`, a scheduler and IPC benchmark that ping-pongs integer tokens through two pipes between either two processes or two pthreads. It times `loops` round trips and reports elapsed time, usecs/op, and ops/sec using the global `bench_format`.

Important APIs, types, and functions: `struct thread_data` carries task index, pipe ends, optional epoll state, cgroup failure state, and pthread id. `parse_two_cgroups()` parses the `--cgroups SEND,RECV` option. `enter_cgroup()` and `exit_cgroup()` integrate with perf's `util/cgroup.h` helpers and cgroupfs files. `read_pipe()` handles blocking or epoll-assisted nonblocking reads. `worker_thread()` performs the ping-pong loop. `bench_sched_pipe()` parses options, creates pipes with `pipe2()`, forks or starts pthreads, joins/waits, and prints results.

Control flow: command options set `nonblocking`, `threaded`, `loops`, and optional cgroup names. Two pipes are arranged in opposite directions. In threaded mode both workers run under pthreads; in process mode the child runs one worker and the parent runs the other. Each worker optionally enters its assigned cgroup, optionally registers the read end with epoll, then repeatedly writes an int and reads one back.

State and persistence: all benchmark state is process-local except optional cgroup membership writes to `cgroup.threads`, `cgroup.procs`, or v1 `tasks`. The benchmark does not persist files. Failed cgroup entry sets `thread_data.cgroup_failed`; after timing it returns success without reporting numbers, so callers must inspect output.

Dependencies and integration points: depends on Linux pipes, fork, pthreads, epoll, cgroupfs, and perf bench's global `bench_format`. `builtin-bench.c` dispatches this through the `sched` collection.

Risks: `BUG_ON()` aborts on pipe, epoll, read, write, pthread, and syscall failures, so benchmark failures are hard exits. Nonblocking mode depends on epoll readiness and `EWOULDBLOCK` retry behavior. Cgroup path handling assumes preexisting cgroups and permissions. Process mode does not propagate child cgroup failure except through shared output and the child's exit status, because the child mutates its own copy of `threads[0]`.

Test signals: run `perf bench sched pipe`, `perf bench sched pipe -T`, `perf bench sched pipe -n`, and low-loop smoke tests. Exercise missing cgroup, valid cgroup, and unprivileged cases. Compare default and simple formats, and verify threaded cgroup writes use TIDs while process mode uses PIDs.
