# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/quorum.c

## Purpose
`quorum.c` implements O2CB self-fencing decisions when heartbeat and network connectivity disagree. It prevents split-brain by fencing this node if it cannot communicate with a sufficient quorum of nodes that are still heartbeating.

## Important APIs, types, and functions
The global `o2quo_state` tracks heartbeating count/bitmap, connected count/bitmap, transition hold count/bitmap, pending decisions, and a work item. Public functions are `o2quo_init`, `o2quo_exit`, `o2quo_hb_up`, `o2quo_hb_down`, `o2quo_hb_still_up`, `o2quo_conn_up`, `o2quo_conn_err`, and `o2quo_disk_timeout`. `o2quo_fence_self` stops heartbeat regions and either panics or emergency-restarts according to nodemanager fence method.

## Control flow
Heartbeat up/down and network connection up/error events update bitmaps under a spinlock. Transition holds delay quorum decisions while a node is newly seen or connection fate is unresolved. When holds drain and a decision is pending, workqueue context runs `o2quo_make_decision`: odd-sized partitions require majority connectivity; even-sized half partitions require connectivity to the side containing the lowest active node. Disk heartbeat timeout fences immediately.

## State and persistence behavior
State is volatile in-memory cluster membership/connectivity. The only persistent side effect is indirect: fencing stops local writes by rebooting or panicking the machine. No state survives reboot.

## Dependencies and integration points
It depends on heartbeat callbacks, O2NET connection events, nodemanager fence configuration, workqueues, reboot/panic APIs, and masklog. Heartbeat write-timeout handling calls `o2quo_disk_timeout`.

## Risks and test signals
Risks include over-fencing during transient network races, stale hold counts blocking decisions, incorrect even-split lowest-node tie-breaks, null cluster state during fence, and heavy-handed local restart/panic. Test signals include two-node split, three-node majority/minority partitions, even half split with/without lowest active node, heartbeat-up before connection-up, connection-error while heartbeat remains up, hold drain scheduling, and disk timeout fencing.
