# sources/distributed-fs/ceph-client/include/linux/sched/hotplug.h

Purpose: declares scheduler callbacks used by CPU hotplug state transitions.

Important APIs and types: `sched_cpu_starting()`, `sched_cpu_activate()`, `sched_cpu_deactivate()`, optional `sched_cpu_wait_empty()`, optional `sched_cpu_dying()`, and `idle_task_exit()` form the interface.

Control flow: CPU hotplug core invokes scheduler hooks as CPUs start, become active, deactivate, drain runnable tasks, and die. Non-hotplug builds provide NULL hooks for unavailable phases.

State and persistence: state lives in runqueues, scheduler domains, and idle tasks, not in this header. It is runtime CPU topology state.

Dependencies and integration points: integrates CPU hotplug with scheduler runqueue activation, migration, and idle-task lifecycle.

Risks and test signals: risks include tasks left on deactivated CPUs, incorrect NULL hook use, and scheduler-domain mismatch after hotplug. Test CPU online/offline loops, hotplug under load, RT/deadline tasks during teardown, and no-hotplug builds.
