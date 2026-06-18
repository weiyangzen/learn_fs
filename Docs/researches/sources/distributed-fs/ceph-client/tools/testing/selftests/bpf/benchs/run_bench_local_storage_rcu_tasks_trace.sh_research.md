# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_local_storage_rcu_tasks_trace.sh

Purpose: convenience runner for the local-storage RCU Tasks Trace benchmark with a large process count and long duration.

Important APIs and functions: finds `rcu_tasks_trace_kthread` with `pgrep`, then runs `./bench --nr_procs 15000 --kthread_pid $kthread_pid -d 600 --quiet local-storage-tasks-trace`.

Control flow: one discovery step, validation of non-empty PID, then one benchmark invocation.

State and persistence: no shell persistence; the benchmark itself forks 15,000 child processes during its run.

Dependencies and integration points: depends on process name visibility, a kernel with `rcu_tasks_trace_kthread`, and ability to run the benchmark with enough privileges/resources.

Risks: `[ -z $kthread_pid ]` is unquoted and can misbehave if multiple PIDs or empty expansion occur; 15,000 processes and 600-second runtime are heavy; direct `./bench` bypasses `run_common.sh`.

Test signals: successful quiet run yields final benchmark summary; missing kthread prints an explicit error.
