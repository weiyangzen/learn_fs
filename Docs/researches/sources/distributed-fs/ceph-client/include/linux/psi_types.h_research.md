# sources/distributed-fs/ceph-client/include/linux/psi_types.h

Purpose: defines the data model for Pressure Stall Information accounting: task-state counters, resource pressure states, per-CPU sampling buckets, trigger windows, and PSI group aggregation state.

Important APIs and types: `enum psi_task_count`, task bitmasks such as `TSK_IOWAIT` and `TSK_MEMSTALL`, `enum psi_res`, `enum psi_states`, `PSI_ONCPU`, and `PSI_STATE_RESCHEDULE` encode scheduler pressure. `struct psi_group_cpu` stores per-CPU task counts, state masks, times, and previous samples. `struct psi_window` tracks trigger windows. `struct psi_trigger` records threshold, state, event wait queue, kernfs file, rate limiting, and aggregator type. `struct psi_group` holds parent linkage, per-CPU data, averages, delayed work, average and RT-poll triggers, totals, and polling task/timer control.

Control flow: scheduler-side updates modify `psi_group_cpu` task counts and state masks; aggregator work samples per-CPU times into group totals and averages; triggers compare window growth against thresholds and wake waiters, with separate average and RT-poll aggregation paths.

State and persistence: all structures are runtime accounting state. Per-CPU fields are cacheline-separated for scheduler updates vs aggregation reads. Trigger lists and totals live per PSI group, usually system or cgroup.

Dependencies and integration points: depends on kthreads, timers, seqlock-related infrastructure, krefs, wait queues, cgroups through users, and scheduler clocks. It is consumed by `psi.h` implementation and cgroup/proc exposure.

Risks and test signals: risks include false sharing on hot scheduler fields, overflow/truncation in `u32 times`, trigger rate-limit mistakes, RT polling lifetime races, and state-mask bugs for full vs some pressure. Test per-resource pressure generation, cgroup hierarchy aggregation, trigger windows, RT polling activation/deactivation, IRQ accounting configs, and disabled `CONFIG_PSI` layout.
