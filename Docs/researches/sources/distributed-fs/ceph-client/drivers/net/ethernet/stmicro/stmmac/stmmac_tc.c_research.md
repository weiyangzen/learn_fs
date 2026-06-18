# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_tc.c

Purpose: hardware traffic-control offloads for STMMAC, including flexible RX parser u32 filters, flower L3/L4 filters, packet routing filters, CBS, TAPRIO/EST, ETF/TBS, capability queries, MQPRIO, and FPE mapping.

Important APIs and functions: `tc_init()` allocates filter state from DMA capabilities. `tc_setup_cls_u32()` programs u32 RX parser entries through `stmmac_rxp_config()`. `tc_setup_cls()` manages flower replace/destroy for L3/L4, EthType routing, and VLAN-priority routing. `tc_setup_cbs()` maps CBS qdisc parameters into DWMAC queue mode and credit registers. `stmmac_calc_tas_basetime()` computes a future TAS base time. `tc_taprio_configure()` translates taprio gate lists into EST registers and FPE class maps. `tc_setup_etf()` toggles TBS. `tc_setup_dwmac510_mqprio()` maps traffic classes to TX queues and preemption classes.

Control flow: initialization creates arrays for parser entries, L3/L4 flows, and RFS routing entries. Netdev TC setup calls HWIF macros that land in this file. Classifier setup validates capabilities and RSS conflicts, stores cookies for delete, and writes hardware. Qdisc setup validates queue and hardware limits, updates platform queue config or `priv->est`, and programs hardware callbacks.

State and persistence: persistent state includes `priv->tc_entries`, `flow_entries`, `rfs_entries`, per-type counts, queue CBS mode/credits in platform data, EST state under `est_lock`, TBS flags, netdev TC mappings, and FPE preemption classes.

Dependencies and integration: Linux TC classifier/qdisc APIs, flow dissector/actions, STMMAC hardware callbacks for RX parser, L3/L4 filters, routing, DMA queue mode, CBS, EST, FPE, RSS state, and PTP time adjustment through shared TAS base-time calculation.

Risks and test signals: RSS disables flower filters. Masks are limited for VLAN priority and EthType. TAPRIO depends on hardware width/depth and PTP time; CBS rejects queue 0 and invalid rates. Test with `tc` offload commands, ethtool RX parser/L3/L4/TBS selftests, taprio stats, EST drop counters, and DWMAC510 MQPRIO/FPE mapping.
