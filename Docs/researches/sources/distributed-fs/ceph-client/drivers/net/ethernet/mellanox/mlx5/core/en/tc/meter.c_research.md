# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/meter.c

Purpose: Implements mlx5e TC flow meter resources using ASO flow meter objects, flow counters, meter handle refcounting, rate/burst encoding, and stats aggregation.

Important APIs: `mlx5e_flow_meters_init()`/`cleanup()`, `mlx5e_tc_meter_get()`, `put()`, `replace()`, `update()`, `modify()`, `get_stats()`, `get_namespace()`, and `mlx5e_flow_meter_get_base_id()`.

Control flow: Initialization checks flow-meter ASO capability and post-action availability, allocates a PD and ASO SQ, and initializes lists/hash. Meter allocation creates action/drop counters and, for rate meters, allocates a slot from a partial ASO object or creates a new object. `modify()` converts BPS/PPS rate and burst to hardware mantissa/exponent fields, builds an ASO WQE, posts it under `aso_lock`, and polls completion. `replace()` gets or allocates a handle under `sync_lock` then updates params. `put()` decrements refcount and frees counters/ASO slot/object at zero.

State and persistence: `mlx5e_flow_meters` owns namespace, ASO, locks, PDN, hash table, partial/full ASO object lists, device, and post_act. Meter handles own counters, ASO object slot, params, refcount, and hash node. ASO objects persist until all slots are free.

Dependencies and integration: Uses mlx5 ASO, general object commands, flow counters, post-action subsystem, TC police parser, QoS caps, and kernel bitmap/list/hash utilities.

Risks: Rate conversion truncates to closest representable hardware value and rejects zero or oversized CIR/CBS. PPS mode scales rate/burst. Cleanup does not walk the hash/list to free live meters, so users must release all handles first. Refcount is plain int protected by `sync_lock`. Tests should cover BPS/PPS/MTU allocation, ASO slot reuse and full/partial list transitions, max burst clamp, invalid rate/burst, ASO command failure, replace update path, stats aggregation, and cleanup with no live meters.
