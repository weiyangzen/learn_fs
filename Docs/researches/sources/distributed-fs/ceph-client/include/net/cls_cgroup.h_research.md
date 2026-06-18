# sources/distributed-fs/ceph-client/include/net/cls_cgroup.h

Read `sources/distributed-fs/ceph-client/include/net/cls_cgroup.h` completely for this pass (88 lines, 2086 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/cls_cgroup.h_research.md`.

Purpose: defines the net_cls cgroup classifier interface used by traffic control to obtain class IDs from the current task or from a socket's cgroup data.

Important APIs/types/functions: when `CONFIG_CGROUP_NET_CLASSID` is enabled, `struct cgroup_cls_state` embeds `cgroup_subsys_state` plus a `classid`. `task_cls_state()` returns a task's classifier state. Inline helpers `task_cls_classid()`, `sock_update_classid()`, `__task_get_classid()`, and `task_get_classid()` retrieve or snapshot class IDs. With the config disabled, `sock_update_classid()` is a no-op and `task_get_classid()` returns zero.

Control flow: socket creation/update paths call `sock_update_classid()` to copy the current task's classid into `sock_cgroup_data`. TC classifier paths call `task_get_classid()`: in process context it reads the current task's classid; in softirq context it avoids using `current` and instead tries to recover a full socket from the skb and read the socket's saved classid.

State and persistence: the classid is stored in cgroup subsystem state and optionally copied into socket cgroup data. No additional persistence exists in this header; values change as tasks move cgroups or sockets are updated.

Dependencies and integration points: depends on Linux cgroup, hardirq/softirq state, RCU, sockets, inet sockets, skb-to-socket helpers, and TC classifier code. It bridges cgroup net_cls policy to qdisc/classifier decisions.

Risks: context detection matters: using `current` in softirq would misclassify packets. RCU protection is required around task CSS access. Sockets that are absent or not full sockets fall back to classid zero in softirq paths. The feature disappears at compile time when `CONFIG_CGROUP_NET_CLASSID` is disabled.

Test signals: compile both config variants; move tasks between net_cls cgroups and verify classid lookup; create sockets and confirm `sock_cgroup_data` snapshots; send packets from process and softirq-like paths; validate zero fallback for interrupt context, missing sockets, and disabled config.
