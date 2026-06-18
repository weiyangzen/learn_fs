## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_hw.c

Purpose: implements X-Gene1 ring programming, GMAC register access, reset/clock/MAC setup, MDIO/PHY integration, error parsing, flow control, and the GMAC port/ring operation tables.

Important APIs, types, and functions: ring helpers write ring state, type, recombination buffer settings, ring IDs, interrupt mode, command counts, and queue length. `xgene_enet_parse_error` maps ingress hardware error codes to netdev stats. Indirect MAC/stat access helpers `xgene_enet_wr_mac`, `xgene_enet_rd_mac`, and `xgene_enet_rd_stat` serialize register operations. GMAC functions set MAC address, initialize ECC/clock, set RGMII speed/delays, frame size, pause thresholds, TX/RX enablement, CLE bypass, and shutdown. `xgene_ring_mgr_init`, `xgene_enet_reset`, MDIO config, PHY connect/disconnect, and the exported `xgene_gmac_ops`, `xgene_gport_ops`, and `xgene_ring1_ops` are core integration points.

Control flow, state, and persistence: `xgene_enet_setup_ops` selects these ops for RGMII and X-Gene1 ring mode. Probe maps CSR bases, then `port_ops->reset`, ring creation, buffer pool setup, `port_ops->cle_bypass`, and `mac_ops->init` program hardware. PHY link changes call adjust-link logic to update speed and flow control. Ring configuration persists in hardware until clear/delete.

Dependencies and integration points: depends on main private data, register constants in `xgene_enet_hw.h`, PHYLIB/MDIO_XGENE, ACPI/OF PHY lookup, clock APIs, and port/ring allocation in `xgene_enet_main.c`.

Risks: indirect MAC access has timeout loops; failures can leave stale register values. Ring programming differs from X-Gene2, so selecting the wrong `ring_ops` corrupts queue ownership. RGMII delay validation and clock assumptions are platform-sensitive. MDIO setup has multiple firmware paths, so ACPI/DT coverage is important.

Test signals: RGMII probe, MDIO bus registration, PHY connect and link adjustment, ring allocation and interrupt delivery, pause control, statistics reads, reset/shutdown, and descriptor error injection for all ingress error codes.
