# sources/distributed-fs/ceph-client/include/linux/sched/isolation.h

Purpose: defines housekeeping CPU types and APIs for CPU isolation, nohz_full, managed IRQ isolation, and partition-aware scheduler domains.

Important APIs and types: `enum hk_type`, `housekeeping_overridden`, `housekeeping_any_cpu()`, `housekeeping_cpumask()`, `housekeeping_enabled()`, `housekeeping_affine()`, `housekeeping_test_cpu()`, `housekeeping_update()`, `housekeeping_init()`, `housekeeping_cpu()`, and `cpu_is_isolated()` are central.

Control flow: boot-time isolation and cpuset partition updates compute masks; kernel subsystems query housekeeping CPUs for timers, RCU, workqueues, managed IRQs, scheduler domains, and noise avoidance. Disabled configs return all CPUs as housekeeping.

State and persistence: housekeeping masks are runtime topology policy derived from boot parameters and cpuset isolation. They persist until updated by isolation mechanisms.

Dependencies and integration points: depends on cpumasks, tick/nohz, init, static keys, and `task_struct` affinity. It integrates scheduler domains with IRQ, timer, RCU, workqueue, and CPU isolation subsystems.

Risks and test signals: risks include scheduling kernel work onto isolated CPUs, stale masks after cpuset changes, alias confusion among housekeeping types, and disabled-config semantic drift. Test `isolcpus`, `nohz_full`, managed IRQ affinity, cpuset isolated partitions, and housekeeping queries on all configs.
