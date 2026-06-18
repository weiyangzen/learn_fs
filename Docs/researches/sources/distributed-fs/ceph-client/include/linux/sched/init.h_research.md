# sources/distributed-fs/ceph-client/include/linux/sched/init.h

Purpose: declares scheduler initialization entry points.

Important APIs and types: `sched_init()` and `sched_init_smp()` are the only exported prototypes.

Control flow: boot code calls early scheduler initialization, then SMP scheduler initialization once CPU topology and multiprocessor setup are ready.

State and persistence: scheduler runqueues, domains, classes, and boot tasks are initialized by implementation code; this header owns no state.

Dependencies and integration points: integrates kernel boot sequencing with scheduler core and SMP bring-up.

Risks and test signals: risks are ordering regressions with CPU/topology initialization. Test boot on UP/SMP configurations, early initcall ordering, and CPU hotplug after boot.
