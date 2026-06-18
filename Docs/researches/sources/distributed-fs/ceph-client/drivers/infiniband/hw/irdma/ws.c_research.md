# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ws.c

## Purpose
`ws.c` manages the Intel irdma work-scheduler tree used to map RDMA VSI/user-priority traffic onto hardware scheduling nodes and LAN queue-set handles. It builds a three-level scheduler hierarchy: a device root, per-VSI parent nodes, and traffic-class leaf nodes shared by user priorities with the same traffic class.

## Important APIs, Types, And Functions
The public entry points are `irdma_ws_add()`, `irdma_ws_remove()`, and `irdma_ws_reset()`. Internally, `irdma_alloc_node()` initializes `struct irdma_ws_node` for root/VSI parents or TC leaves, allocating hardware node IDs for non-root nodes. `irdma_ws_cqp_cmd()` converts a software node into `struct irdma_ws_node_info` and posts `IRDMA_OP_WS_ADD_NODE`, `MODIFY_NODE`, or `DELETE_NODE` through `irdma_cqp_ws_node_cmd()`. `ws_find_node()` searches child lists by VSI or traffic class. `irdma_tc_in_use()` guards leaf removal by checking QP lists for the target and same-TC user priorities. `irdma_remove_leaf()` tears down TC, VSI, and root nodes when they become empty.

## Control Flow
`irdma_ws_add()` takes `vsi->dev->ws_mutex`, refuses changes while `tc_change_pending` is set, creates the root if missing, creates or reuses the VSI node, creates or reuses the TC leaf, registers the qset with LAN, enables the leaf with a MODIFY command, then marks every matching user priority valid and copies the RDMA/LAN queue handles. Error paths unwind leaf, VSI, and root nodes in reverse order. `irdma_ws_remove()` serializes on the same mutex, skips deletion if any same-TC QP list is still populated, and otherwise calls `irdma_remove_leaf()`. `irdma_ws_reset()` loops over all user priorities and removes each leaf under the scheduler mutex.

## State And Persistence
The in-memory tree is rooted at `vsi->dev->ws_tree_root` and each node is linked through `siblings` and `child_list_head`. Per-user-priority state in `vsi->qos[]` records `valid`, `traffic_class`, `rel_bw`, `qs_handle`, LAN qset handle, and L2 scheduler node ID. Hardware state is programmed through CQP commands and LAN callbacks; it is not persisted outside driver memory. Reset/removal clears `valid` for every priority sharing the removed traffic class.

## Dependencies And Integration Points
This file depends on irdma CQP scheduler commands, hardware node-id allocation, `struct irdma_sc_vsi`, per-priority QoS mutexes and QP lists, LAN qset registration callbacks, and RDMA core debug logging via `ibdev_dbg()`. It also relies on list APIs and the device-wide scheduler mutex to keep tree mutation serialized.

## Risks
`irdma_tc_in_use()` locks only `vsi->qos[user_pri].qos_mutex` while inspecting all same-TC `qplist` heads, so correctness depends on a broader convention that same-TC list updates are safe under that lock or the outer `ws_mutex`. The add path registers a LAN qset before enabling the leaf; failures after registration must keep LAN and RDMA scheduler state aligned. `irdma_ws_cqp_cmd()` maps any CQP failure to `-ENOMEM`, losing error specificity. Root node index zero is intentionally never freed, so node-index handling must preserve that root special case.

## Test Signals
Exercise first-add root creation, multiple VSIs, multiple user priorities sharing a traffic class, qset registration failure, CQP add/modify/delete failures, removal while QP lists are populated, complete tree teardown, `tc_change_pending` rejection, and repeated reset calls on partially populated trees.
