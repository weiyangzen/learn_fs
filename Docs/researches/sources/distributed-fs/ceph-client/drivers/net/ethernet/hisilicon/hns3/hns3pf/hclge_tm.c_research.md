# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_tm.c

## Purpose
`hclge_tm.c` programs and queries HNS3 PF traffic management: priority-to-TC and DSCP-to-TC mapping, priority-group/priority/qset hierarchy, queue-to-qset and qset-to-priority mapping, shapers, DWRR weights, scheduler modes, flow control, MAC pause, PFC, qset backpressure, RSS/TC queue allocation updates, and debug getters for TM state.

## Important APIs And Functions
- `hclge_tm_schd_init()` initializes FC mode, validates scheduler mode constraints, initializes software scheduler state, initializes DSCP mapping defaults, and calls `hclge_tm_init_hw()`.
- `hclge_tm_init_hw()` validates TC-base or vNET-base scheduler mode, then runs `hclge_tm_schd_setup_hw()` and `hclge_pause_setup_hw()`.
- `hclge_tm_schd_setup_hw()` performs the hardware programming sequence: mapping, shapers, DWRR weights, scheduler modes, and TM flush disable.
- `hclge_shaper_para_calc()` converts Mbps rates into hardware IR_B/IR_U/IR_S parameters for port, PG, priority, or qset shapers.
- Mapping helpers include `hclge_up_to_tc_map()`, `hclge_dscp_to_tc_map()`, `hclge_tm_pg_to_pri_map()`, `hclge_tm_pri_q_qs_cfg()`, `hclge_vport_q_to_qs_map()`, and low-level command wrappers for PG-to-priority, qset-to-priority, and queue-to-qset links.
- Shaper and scheduler helpers configure port, PG, priority, VF/vNET, and qset shapers; DWRR weight helpers configure PG, priority, qset, and ETS TC weights.
- Flow-control helpers include `hclge_mac_pause_en_cfg()`, `hclge_pfc_pause_en_cfg()`, `hclge_pause_addr_cfg()`, `hclge_mac_pause_setup_hw()`, `hclge_pause_setup_hw()`, and `hclge_tm_bp_setup()`.
- Runtime update APIs include `hclge_tm_schd_info_update()`, `hclge_tm_prio_tc_info_update()`, `hclge_tm_pfc_info_update()`, `hclge_tm_vport_map_update()`, `hclge_tm_qs_shaper_cfg()`, and `hclge_reset_tc_config()`.
- Debug getters query qset/priority/PG/queue mapping, scheduler mode, weights, shaper parameters, node counts, and port shaper state from hardware.

## Control Flow
Software state is initialized first. `hclge_tm_pg_info_init()` creates one active priority group by default with full bandwidth; `hclge_tm_tc_info_init()` maps user priorities to TCs; `hclge_tm_vport_info_update()` recalculates PF/VF RSS size, queue counts, qset offsets, bandwidth, and per-TC queue offsets; `hclge_tm_pfc_info_update()` reconciles FC mode with PFC/DCB state.

Hardware setup then writes mappings and scheduler parameters in dependency order. User-priority and optional DSCP maps define TC selection. PG-to-priority, qset-to-priority, and queue-to-qset links build the hierarchy differently for TC-base and vNET-base modes. Port/PG/priority/qset shapers are calculated and written. DWRR weights and scheduler modes are programmed, with ETS TC weight command tolerated as unsupported on older firmware. Pause/PFC setup writes pause parameters and MAC pause bits, then DCB-capable devices get PFC and backpressure qset bitmaps.

## State And Persistence Behavior
The file mutates `hdev->tm_info`, `hdev->hw_tc_map`, `hdev->fc_mode_last_time`, PF RSS config, and each vport's `qs_offset`, `bw_limit`, `dwrr`, `kinfo.rss_size`, `kinfo.num_tqps`, and `kinfo.tc_info`. These are in-memory shadows of hardware scheduler state and must be replayed after resets. `hclge_reset_tc_config()` clears mqprio TC state, recomputes default scheduler state, and reinitializes RSS indirection. MAC/PFC packet stats are read from `hdev->mac_stats` offsets rather than command queries.

## Dependencies And Integration Points
The file depends on `hclge_cmd.h`, `hclge_main.h`, `hclge_tm.h`, HNAE3 queue/TC/private-info structures, firmware opcodes, DCB capability helpers, AE device specs (`max_tm_rate`), RSS common helpers, and PF MAC state. It integrates with ethtool/DCB/mqprio paths, PF/VF resource allocation, reset restore, pause/FEC/link handling, and debugfs diagnostics that call the getter functions.

## Risks And Edge Cases
- Shaper calculation rejects rates above firmware max and has several rounding paths; off-by-one errors can under/over-shape traffic.
- TC-base and vNET-base modes use different hierarchy semantics. Incorrect `tx_sch_mode`, `num_pg`, or qset offsets can map queues to the wrong scheduler node.
- VF handling deliberately limits VFs to one TC for simplicity; changing VF TC support would require broad updates.
- Backpressure bitmap programming depends on qset id bitfield layout and switches grouping when `num_tqps > HCLGE_TQP_MAX_SIZE_DEV_V2`.
- `hclge_tm_pri_vnet_base_shaper_qs_cfg()` currently calculates qset shaper parameters but does not send a qset shaper command in the visible code path; this may be intentional hardware behavior or a maintenance hazard.
- `hclge_pause_setup_hw()` suppresses PFC `-EOPNOTSUPP` only during init on GE MAC; later failures become hard errors.

## Test Signals
Validate default probe scheduler setup, mqprio create/destroy, DSCP mapping mode, DCB/PFC enable/disable, pause autoneg/manual modes, VF max TX rate/qset shaper changes, PF/VF queue allocation with multiple TCs, reset restore, GE MAC PFC unsupported path, large TQP backpressure grouping, debug getters matching programmed state, and traffic tests confirming TC/priority bandwidth behavior.
