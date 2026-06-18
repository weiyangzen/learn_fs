# sources/distributed-fs/ceph-client/tools/rcu/rcu-updaters.sh

Purpose: samples RCU update-side and grace-period primitives with bpftrace and prints a histogram of call counts.

Important APIs/functions: the script builds an optional `exitclause` from the first argument, then runs one `bpftrace -e` program with many `kprobe:` targets including `call_rcu`, SRCU, Tasks RCU, barrier, synchronize, poll-state, and `rcu_gp_init`. The action is `@counts[func] = count();`.

Control flow: if a duration is provided, add an interval probe that exits after that many seconds. Otherwise, tell the user to use control-C. The bpftrace program accumulates counts by probed function name until termination.

State and persistence: no files or persistent state. Aggregation lives in bpftrace maps and is printed by bpftrace on exit.

Dependencies and integration: requires bpftrace, kprobe support, sufficient privileges, and kernel symbols for the named functions. It tolerates missing functions by relying on bpftrace diagnostics while continuing with available probes.

Risks: kprobe availability varies with config, inlining, and symbol visibility. High-frequency probes can add overhead. Shell interpolation of `duration` is simple and assumes a numeric value. The count for `rcu_gp_init()` is normal non-expedited grace periods, while other entries are primitive invocations, so interpretation is not one uniform unit.

Test signals: run with a short duration, run without duration and interrupt, validate behavior when some symbols are absent, and compare expected increases while running workloads that call RCU primitives.
