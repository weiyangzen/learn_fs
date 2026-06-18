# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2_core.c

Purpose: Implements MAC-side callbacks for Synopsys XGMAC2 and XLGMAC cores. It programs MAC enablement, link capabilities, MTL queue routing/scheduling, filtering, RSS, EEE/LPI, Wake-on-LAN, safety features, flexible RX parser, PPS, L3/L4 filters, ARP offload, and setup of `mac_device_info`.

Important APIs and flow: `dwxgmac210_ops` and `dwxlgmac2_ops` are the exported `stmmac_ops` tables. Setup functions initialize `mac->pcsr`, link speed masks, MDIO register layout, multicast/unicast filter capacity, VLAN count, and XGMAC/XLGMAC advertised speeds. Runtime callbacks include `core_init`, `irq_modify`, `set_mac`, `rx_ipc`, queue priority/routing functions, `rss_configure`, `config_l3_filter`, `config_l4_filter`, `flex_pps_config`, and `rxp_config`.

Control flow and state: Most operations are read-modify-write MMIO updates. Interrupt enable changes are serialized by `hw->irq_ctrl_lock`. RSS writes use the indirect address/data register and poll the busy bit. RX parser reprogramming temporarily disables RX and the parser, orders entries by priority, handles fragment entries, writes the all-pass entry last, then restores RX state. Safety IRQ handlers read, clear, log, and accumulate error counters in `stmmac_safety_stats`.

Dependencies and integration: Uses `stmmac.h` private state, `stmmac_fpe.h` for preemption class mapping, `stmmac_ptp.h`, VLAN helpers, XGMAC/XLGMAC register definitions, netdev multicast/unicast lists, CRC/hash helpers, and `readl_poll_timeout`.

Risks and test signals: High-risk paths are indirect filter/RSS polling timeouts, priority mapping conflicts, RX parser reconfiguration while traffic is active, safety counter offsets, and PPS period conversion. Test queue routing, multicast hash and perfect filter overflow, RSS key/table programming, L3/L4 filter enable/disable including IPv6 SA/DA exclusivity, EEE forced mode rejection of timer mode, FPE class mapping, and XGMAC versus XLGMAC speed setup.
