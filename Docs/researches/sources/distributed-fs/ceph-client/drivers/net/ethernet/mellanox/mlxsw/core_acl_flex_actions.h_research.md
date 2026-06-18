# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_actions.h

## Purpose
`core_acl_flex_actions.h` declares the ACL flexible-action builder interface. It lets higher-level ACL code create an AFA context, build action blocks, commit and query them, look up drop cookies, and append supported hardware actions without knowing the byte layout implemented in `core_acl_flex_actions.c`.

## Important APIs, Types, And Functions
- Opaque `struct mlxsw_afa` and `struct mlxsw_afa_block` hide global action state and per-rule action-chain state.
- `struct mlxsw_afa_ops` is the hardware integration contract. It provides KVDL set add/delete/activity, forwarding-entry add/delete, counter allocation/free, mirror add/delete, policer add/delete, sampler add/delete, and `dummy_first_set`.
- Lifecycle APIs are `mlxsw_afa_create()`, `mlxsw_afa_destroy()`, `mlxsw_afa_block_create()`, `mlxsw_afa_block_destroy()`, and `mlxsw_afa_block_commit()`.
- Accessors expose encoded first/current sets, first KVDL index, and action-set activity.
- Control APIs end a block with continue, jump to ACL group, or terminate.
- Append APIs cover drop with optional `flow_action_cookie`, trap, trap-and-forward, mirror, forwarding, VLAN modification, QoS rewrites, counters, FID set, ignore, multicast router action, SIP/DIP rewrite, L4 port rewrite, policer, and sampler.

## Control Flow
Callers instantiate `mlxsw_afa` with device callbacks, create a block per ACL rule, append actions in order, set the terminal behavior, commit the block so sets are shared/KVDL-backed as needed, use `mlxsw_afa_block_first_set()` or KVDL index when programming the rule, and destroy the block when the rule is removed.

## State And Persistence Behavior
The header indicates ownership but not representation. Blocks own temporary and hardware-backed resources until destroyed. The AFA context owns deduplication tables and allocator state. Cookie lookup returns a pointer valid only under RCU read-side protection, as documented by the implementation.

## Dependencies And Integration Points
The header depends on Linux types, netdevice, and flow offload. It exposes netlink extack propagation so append failures can be reported to tc/flow-offload users. The ops table connects this generic builder to Spectrum KVDL, counters, span/mirror, policer, and psample implementations.

## Risks And Edge Cases
- Operation callbacks must be internally consistent; a successful add must be matched by the corresponding delete on resource release.
- Append functions may allocate resources before encoding. Callers must destroy blocks even after partial failures to release anything already attached.
- `dummy_first_set` changes the structure of committed blocks and is significant for users that query the first KVDL index or activity.
- `mlxsw_afa_block_append_police()` always writes through `p_policer_index`; callers must pass a valid pointer.

## Test Signals
Compile-time users should cover all append prototypes. Runtime tests should verify callback pairing, extack propagation, block commit before rule programming, activity retrieval, cookie lookup for trapped drops, and cleanup after failed append sequences.
