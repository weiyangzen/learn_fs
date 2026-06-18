# sources/distributed-fs/ceph-client/fs/ocfs2/heartbeat.c

Purpose: maintains OCFS2 node maps and handles cluster node-down notifications by triggering recovery for failed peers.

Important APIs and functions: public functions are `ocfs2_init_node_maps`, `ocfs2_do_node_down`, `ocfs2_node_map_set_bit`, `ocfs2_node_map_clear_bit`, and `ocfs2_node_map_test_bit`. Internal `ocfs2_node_map_init` initializes a bitmap map to `OCFS2_NODE_MAP_MAX_NODES`.

Control flow: superblock setup initializes `node_map_lock` and the orphan-directory recovery map. The cluster stack calls `ocfs2_do_node_down` with a failed node number; the function rejects self-death with `BUG_ON`, ignores events before a cluster connection exists, and otherwise starts `ocfs2_recovery_thread`. Node-map helpers set, clear, and test bits under the superblock spinlock, with a legacy special case that ignores bit `-1` for set/clear.

State and persistence behavior: node maps are in-memory bitmaps tracking mounted or recovering nodes; no persistent disk state is written here. Recovery triggered by node-down events may later affect journal/orphan cleanup through other modules.

Dependencies and integration points: depends on OCFS2 superblock state, cluster heartbeat callbacks registered by `dlmglue.c`, journal recovery, inode/allocation headers, bitmap operations, and tracing.

Risks: bit bounds are enforced with `BUG_ON`/`BUG`, so invalid node numbers can crash the kernel. Ignoring `-1` in set/clear but not in test reflects legacy caller behavior and should not be broadened silently. Node-down events before `osb->cconn` are intentionally ignored because slot checks after cluster setup catch existing deaths.

Test signals: mount initialization of node maps, node-down callback for remote nodes, rejection of local node number, recovery thread invocation, set/clear/test under concurrent callers, out-of-range node-number assertions in debug testing, and early node-down before cluster connection.
