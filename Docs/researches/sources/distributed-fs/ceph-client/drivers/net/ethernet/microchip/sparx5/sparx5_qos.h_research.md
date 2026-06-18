## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_qos.h

### Purpose
`sparx5_qos.h` defines scheduler-layer constants, hardware shaper limits, leak-group metadata, DWRR state, and the public TC/QoS offload function prototypes.

### Important APIs, Types, And Functions
The header defines three HSCH layers, scheduler element counts, `SPX5_HSCH_L0_GET_IDX()`, four leak groups, scheduler modes, rate/burst hardware limits, and `SPX5_DWRR_COST_MAX`. Structs include `sparx5_shaper`, `sparx5_lg`, `sparx5_layer`, and `sparx5_dwrr`. It declares QoS init and TC mqprio/tbf/ets add/delete functions plus `sparx5_get_hsch_max_group_rate()`.

### Control Flow
No runtime control flow exists in the header. The L0 index macro maps a port and queue to a hardware scheduler element with 64 elements per port and eight queues.

### State, Persistence, And Dependencies
The header itself has no state. Its structs define the in-memory metadata used by `sparx5_qos.c`, and constants must match HSCH hardware limits.

### Integration Points
Included by `sparx5_qos.c` and `sparx5_tc.c`. It is the interface between Linux qdisc offload handling and hardware scheduler programming.

### Risks
Hardware limits are compiled in; mismatches with chip variants can cause accepted TC configs to fail or be misprogrammed. The L0 index formula is central to queue shaping correctness.

### Test Signals
Compile-time coverage plus qdisc tests that validate root and queue parent mapping, rate/burst limit enforcement, and DWRR cost array dimensions.
