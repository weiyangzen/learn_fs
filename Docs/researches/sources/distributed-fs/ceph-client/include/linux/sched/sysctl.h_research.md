# sources/distributed-fs/ceph-client/include/linux/sched/sysctl.h

Purpose: declares scheduler-related sysctl constants and tunable state.

Important APIs and types: `sysctl_hung_task_timeout_secs`, `enum sched_tunable_scaling`, `NUMA_BALANCING_*` mode bits, and `sysctl_numa_balancing_mode` are the main symbols.

Control flow: sysctl handlers and scheduler/MM code read these values to control hung-task timeout reporting, scheduler tunable scaling mode, and NUMA balancing modes. Disabled configs provide constants so callers avoid ifdefs.

State and persistence: state is runtime sysctl/global tunable data; persistence depends on userspace sysctl configuration, not the header.

Dependencies and integration points: integrates scheduler, hung-task detector, NUMA balancing, and sysctl infrastructure.

Risks and test signals: risks include disabled-config constants masking writes, invalid scaling mode handling, and NUMA mode bit confusion. Test sysctl reads/writes, hung-task detector config, NUMA balancing mode changes, and disabled feature builds.
