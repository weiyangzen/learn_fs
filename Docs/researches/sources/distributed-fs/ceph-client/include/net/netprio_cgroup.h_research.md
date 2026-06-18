# sources/distributed-fs/ceph-client/include/net/netprio_cgroup.h

Purpose: Provides cgroup net priority helpers for mapping tasks to socket priority indexes.

Important APIs/types/functions: With `CONFIG_CGROUP_NET_PRIO`, `struct netprio_map` stores RCU-freeable priority maps. `task_netprioidx` reads the task's net_prio css id under RCU, and `sock_update_netprioidx` copies the current task priority index into socket cgroup data unless in interrupt context. Without the feature, helpers return zero or no-op.

Control flow: Socket creation/update paths call `sock_update_netprioidx`; it reads the current task cgroup and updates socket cgroup metadata. Packet scheduling/classification can later use the priority index.

State and persistence: Runtime cgroup ids and RCU priority maps; no state is stored in this header.

Dependencies/integration: Depends on cgroup subsystem state, socket cgroup data, RCU, hardirq context checks, and net_prio cgroup config.

Risks/test signals: Test disabled stubs, RCU correctness, interrupt-context no-op, socket priority inheritance after task migration, cgroup deletion, and classifier/qdisc behavior.
