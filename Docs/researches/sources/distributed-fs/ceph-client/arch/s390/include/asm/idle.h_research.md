# sources/distributed-fs/ceph-client/arch/s390/include/asm/idle.h

Purpose: This header defines per-CPU idle accounting data and exported sysfs attributes for s390 idle reporting.

Important APIs/types/functions: `struct s390_idle_data` stores idle counts, accumulated idle time, entry clock/timer values, and MT-cycle snapshots. `s390_idle` is declared per-CPU, and `dev_attr_idle_count` plus `dev_attr_idle_time_us` expose attributes.

Control flow: Idle entry/exit code updates the per-CPU structure, and device/sysfs code reads the exported attributes to report counts and time.

State and persistence: State persists per CPU in `s390_idle`; entry fields are transient timestamps used to accumulate totals.

Dependencies and integration points: It depends on Linux per-CPU and device attribute support and integrates with CPU idle, accounting, and sysfs CPU device reporting.

Risks and test signals: Accounting must be CPU-local and monotonic across idle transitions. Tests should cover idle sysfs reads, CPU hotplug, tickless idle, and virtualization environments with steal/MT-cycle behavior.
