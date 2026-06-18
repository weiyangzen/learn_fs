<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_flow.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_flow.c

## Purpose
`spectrum_flow.c` bridges Linux TC block offload plumbing to Spectrum ACL flower and matchall/mall offload handlers. It creates and tracks per-block driver state, binds shared TC blocks to Spectrum ports on ingress or egress, dispatches classifier commands, and tears down flow-block state when TC releases the block callback.

## Important APIs, Types, and Functions
Public functions are `mlxsw_sp_flow_block_create()`, `mlxsw_sp_flow_block_destroy()`, and `mlxsw_sp_setup_tc_block_clsact()`. Important helpers include flow-block binding lookup, bind/unbind, mall callback dispatch, flower callback dispatch, the common `mlxsw_sp_flow_block_cb()`, and `mlxsw_sp_tc_block_release()`. A static global `mlxsw_sp_block_cb_list` is used as the TC driver block list.

## Control Flow
On `FLOW_BLOCK_BIND`, the code looks up an existing `flow_block_cb` for the TC block and Spectrum instance. If none exists, it allocates a new `mlxsw_sp_flow_block`, allocates a TC callback wrapper, and marks it for registration. It increments the callback refcount, validates ingress/egress blocker rule counts, binds mall state to the port, allocates a binding record, optionally binds existing ACL rulesets to the new port binding, updates ingress or egress binding counts, stores the block pointer in the port, and registers the callback in TC and the global driver list if this was the first binding. On `FLOW_BLOCK_UNBIND`, it clears the port pointer, removes the binding, unbinds rulesets and mall state, decrements the TC callback refcount, and removes/frees the callback when the last binding goes away.

## State and Persistence Behavior
State is in allocated `mlxsw_sp_flow_block` objects, their binding lists, mall state, ruleset status, ingress/egress binding counts, blocker rule counts, TC `flow_block_cb` refcounts, and per-port ingress/egress flow-block pointers. It persists only while TC blocks are bound. Hardware ACL/mall state is owned by called flower/mall helpers.

## Dependencies and Integration Points
The file integrates with Linux TC block offload APIs, `flow_block_cb` reference management, clsact ingress/egress setup, Spectrum ACL rulesets, flower offload functions, and matchall/mall handlers. Extack messages are used to explain unsupported bind directions when blocker rules exist.

## Risks and Edge Cases
Shared blocks can bind to multiple ports and directions, so refcounting and binding-count accounting must stay exact. Unsupported rules tracked by ingress/egress blocker counts prevent later binding in that direction. Bind failure after callback incref must correctly free an unregistered callback when appropriate. Unbind tolerates missing callbacks but ignores unbind errors except for refcount removal. Destroy warns if bindings still exist.

## Test Signals
Signals include TC flower replace/destroy/stats/template commands, matchall mirror/police actions through mall handlers, shared block binding to multiple ports, ingress and egress clsact binding and unbinding, extack messages for blocked directions, and no leaked `flow_block_cb` or WARNs after qdisc removal and port teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_flow.c -->
