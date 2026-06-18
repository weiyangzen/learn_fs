# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/nodemanager.c

## Purpose
`nodemanager.c` implements the O2CB configfs cluster model and module lifecycle. It lets userspace create one cluster, define nodes with number/IP/port/local status, tune network timeouts and fence method, attach the heartbeat default group, and initialize/shutdown heartbeat, TCP, quorum callbacks, configfs, and sysfs.

## Important APIs, types, and functions
Exports include `o2nm_single_cluster`, `o2nm_get_node_by_num`, `o2nm_get_node_by_ip`, `o2nm_configured_node_map`, `o2nm_node_get`, `o2nm_node_put`, `o2nm_this_node`, `o2nm_depend_item`, `o2nm_undepend_item`, `o2nm_depend_this_node`, and `o2nm_undepend_this_node`. Configfs handlers manage node attributes (`num`, `ipv4_port`, `ipv4_address`, `local`) and cluster attributes (`idle_timeout_ms`, `keepalive_delay_ms`, `reconnect_delay_ms`, `fence_method`). Module init/exit are `init_o2nm` and `exit_o2nm`.

## Control flow
Module init initializes heartbeat, O2NET, heartbeat callbacks, configfs subsystem `cluster`, and `/sys/fs/o2cb`. Creating a cluster allocates cluster, node group, and heartbeat group; only one cluster is allowed. Creating a node allocates a config item; userspace must set address and port before node number, then can mark one node local, which starts listening. Dropping nodes disconnects network state, stops local listening if applicable, removes IP tree and bitmap entries, and releases the item. Dropping the cluster removes default groups and clears `o2nm_single_cluster`.

## State and persistence behavior
State is runtime configfs state: the single cluster pointer, node array, configured-node bitmap, IP rbtree, local-node flag, network timeout values, reconnect delay, and fence method. None is persisted by the kernel; userspace cluster tooling must recreate it after boot.

## Dependencies and integration points
It depends on configfs, rbtree, O2NET TCP helpers, heartbeat configfs allocation, O2CB sysfs, and masklog. Heartbeat and networking use nodemanager lookups and configfs dependency pins to keep local nodes/regions alive while active.

## Risks and test signals
Risks include singleton cluster assumptions, attribute ordering surprises, races between node deletion and heartbeat/network users, inability to change network timeouts after peers connect, duplicate IP/node numbers, local-node transitions, and fence-method misconfiguration. Test signals include configfs create/drop cycles, invalid attribute values, duplicate nodes/IPs, local listener start/stop, connected peer timeout-change rejection, module init unwind failures, and configfs dependency behavior under active heartbeat.
