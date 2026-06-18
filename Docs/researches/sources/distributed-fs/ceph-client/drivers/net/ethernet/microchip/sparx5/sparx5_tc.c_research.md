## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc.c

### Purpose
`sparx5_tc.c` is the TC offload dispatcher for Sparx5 netdevices. It connects Linux block, classifier, and qdisc setup callbacks to matchall, flower, MQPRIO, TBF, and ETS implementations.

### Important APIs, Types, And Functions
The exported function is `sparx5_port_setup_tc()`. Internal callbacks include `sparx5_tc_block_cb()`, ingress/egress wrappers, `sparx5_tc_setup_block()`, `sparx5_tc_get_layer_and_idx()`, and qdisc setup handlers for MQPRIO, TBF, and ETS. A static `sparx5_block_cb_list` tracks flow block callbacks.

### Control Flow
Block setup selects ingress or egress callback based on binder type and registers with `flow_block_cb_setup_simple()`. Classifier callbacks dispatch `TC_SETUP_CLSMATCHALL` to `sparx5_tc_matchall()` and `TC_SETUP_CLSFLOWER` to `sparx5_tc_flower()`. Qdisc handling maps root TBF to HSCH layer 2 and per-queue TBF to layer 0 using `SPX5_HSCH_L0_GET_IDX()`, delegates MQPRIO directly, and accepts ETS only at root with eight bands and reversed priority map.

### State, Persistence, And Dependencies
State is mostly in kernel TC flow block lists and netdev TC configuration; hardware state is programmed by downstream QoS and classifier files. Dependencies include Linux `pkt_cls`, `pkt_sched`, Sparx5 QoS helpers, and classifier implementations.

### Integration Points
Netdev ops call this through `ndo_setup_tc`. It is the central TC entry for qdiscs and clsact filters, tying Linux configuration to VCAP, mirror, PSFP, and HSCH programming.

### Risks
Unsupported binder types and qdisc commands return `-EOPNOTSUPP`, so user-visible TC features are intentionally narrow. ETS validation assumes a strict reversed priority map. Parent-to-layer mapping must match the hardware scheduling hierarchy.

### Test Signals
Test ingress/egress clsact block binding, matchall and flower dispatch, MQPRIO add/delete, root and queue TBF parent mapping, ETS invalid bands/priomap/weights, and unsupported command returns.
