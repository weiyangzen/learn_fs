## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_qos.c

### Purpose
`sparx5_qos.c` implements scheduling, shaping, DWRR, MQPRIO, TBF, ETS, PSFP initialization, and base-time calculation for Sparx5 QoS offload. It programs HSCH leak groups and scheduler elements used by TC qdiscs.

### Important APIs, Types, And Functions
Public functions include `sparx5_new_base_time()`, `sparx5_get_hsch_max_group_rate()`, `sparx5_qos_init()`, `sparx5_tc_mqprio_add/del()`, `sparx5_tc_tbf_add/del()`, and `sparx5_tc_ets_add/del()`. Internal leak-group operations maintain circular linked lists in hardware using `sparx5_lg_add()`, `sparx5_lg_del()`, and `sparx5_lg_conf_set()`. Shaper and DWRR programming are done by `sparx5_shaper_conf_set()` and `sparx5_dwrr_conf_set()`.

### Control Flow
QoS initialization derives leak group timing and resolution from `HSCH_SYS_CLK_PER`, disables all groups to mark them empty, initializes DCB, then initializes PSFP. TBF add converts bytes/s to kbit/s, selects a leak group by rate, validates min/max rate and burst, scales to hardware resolution and 4096-byte burst units, writes scheduler element mode/rate/burst, and links the element into the chosen group. ETS add validates bands in the TC layer, computes minimum weight, reverses priority bands to match hardware preference, converts weights to DWRR costs, and writes DWRR entries.

### State, Persistence, And Dependencies
Leak group metadata is cached in a static `layers[]` array, while active group membership persists in HSCH registers. Netdev TC state is reflected in Linux netdev TC queues. The file depends on PTP time for future base-time calculation, DCB initialization, PSFP initialization, generated HSCH registers, and qdisc offload structs.

### Integration Points
`sparx5_tc.c` dispatches MQPRIO, TBF, and ETS qdisc offloads here. `sparx5_psfp.c` uses `sparx5_new_base_time()` for stream gate basetimes. DCB support is initialized as part of QoS.

### Risks
Static `layers[]` is global, not per device, so multi-device assumptions should be reviewed. `sparx5_tc_tbf_del()` does not check failure from group lookup before using `group`. Leak group linked-list manipulation is hardware-state-dependent and uses warnings rather than graceful recovery for missing members. Base-time math assumes cycle time is nonzero.

### Test Signals
Test leak group init on each core clock, TBF add/delete across root and queue parents, rate/burst boundary rejection, moving a scheduler element between leak groups, MQPRIO exactly eight traffic classes, ETS strict/DWRR combinations and reverse priority mapping, and PSFP initialization side effects.
