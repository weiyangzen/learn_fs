# sources/distributed-fs/ceph-client/kernel/sched/debug.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/debug.c` implements scheduler observability and debugfs/proc reporting. It exposes scheduler feature toggles, tunable scaling, dynamic preemption mode, verbose scheduler-domain debug trees, deadline-server controls, `/sys/kernel/debug/sched/debug`, SysRq scheduler dumps, per-runqueue printers, and `/proc/<pid>/sched` task output. The file was read as a complete 1403-line source.

## Important APIs, Types, and Functions

Formatting helpers include `SEQ_printf()`, `nsec_high()`, `nsec_low()`, and `SPLIT_NS()`. Feature control uses `sched_feat_names`, optional `sched_feat_keys`, `sched_feat_show()`, `sched_feat_set()`, and `sched_feat_write()`. Debugfs initialization is in `sched_init_debug()`, with file operations for `features`, `verbose`, `preempt`, `tunable_scaling`, `debug`, and fair/ext deadline-server `runtime` and `period`. Scheduler-domain debug is handled by `update_sched_domain_debugfs()`, `dirty_sched_domain_sysctl()`, and `register_sd()`. Printing APIs include `print_cfs_rq()`, `print_rt_rq()`, `print_dl_rq()`, `print_cpu()`, `sched_debug_header()`, `sched_debug_show()`, `sysrq_sched_debug_show()`, `proc_sched_show_task()`, `proc_sched_set_task()`, and `resched_latency_warn()`.

## Control Flow

At late init, `sched_init_debug()` creates the top-level `sched` debugfs directory and registers control/report files. Feature writes copy a small user buffer, strip it, serialize with CPU hotplug read lock and inode lock, then update `sysctl_sched_features` and static keys. Scaling writes parse an integer and call `sched_update_scaling()`. Dynamic preempt writes parse a mode string and call `sched_dynamic_update()`.

Verbose scheduler-domain debug is lazy and CPU-aware: enabling `verbose` calls `update_sched_domain_debugfs()`, which allocates `sd_sysctl_cpus`, creates a `domains` tree, and creates per-CPU/per-domain files for domain tunables and flags. Dirty CPUs are marked for later rebuild.

The main sched debug seq iterator emits a header at position 0 and one online CPU per later position. Each CPU dump prints rq clocks/counters, CFS/RT/DL rq stats, and a task table. `/proc/<pid>/sched` prints task execution, wait, sleep, block, migration, PELT, uclamp, policy, deadline, NUMA, and sched-ext fields depending on config. Deadline-server debugfs writes stop the server, apply validated runtime/period parameters through `dl_server_apply_params()`, restart it, and log enable/disable transitions.

## State and Persistence Behavior

State includes debugfs dentries, `sched_debug_verbose`, optional static keys for scheduler features, `sd_sysctl_cpus`, server runtime/period fields stored in per-rq deadline-server entities, and task schedstats reset by `proc_sched_set_task()`. Debugfs settings are runtime-only and do not persist across reboot.

## Dependencies and Integration Points

The file depends on debugfs, seq_file, scheduler core data structures, sched domains, cgroups/autogroups, NUMA balancing, schedstats, uclamp, sched-ext, dynamic preemption, static branches, and deadline-server APIs from `deadline.c`. It integrates with `/proc`, SysRq, debugfs, and scheduler sysctl-style global tunables.

## Risks and Edge Cases

Debug code reads many live scheduler fields and must avoid sleeping or lock inversions on hot paths. Feature static-key changes require CPU hotplug serialization. Scheduler-domain debugfs rebuild can be called before debugfs init and must no-op safely. Group path printing uses a trylock and fallback buffer to avoid global buffer contention. Deadline-server runtime/period writes can disable servers and risk starvation; validation enforces runtime <= period and period bounds, but operational impact remains large.

## Test Signals

Signals include mounting debugfs and reading every sched file; writing valid/invalid `features`, `tunable_scaling`, and dynamic preempt modes; enabling/disabling verbose domains across CPU hotplug; writing fair/ext server runtime and period and checking error paths; reading `/proc/<pid>/sched` for fair, RT, and deadline tasks; SysRq scheduler dump smoke tests; and lockdep coverage while dumping under scheduler stress.
