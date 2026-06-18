## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_xgmac.c

Purpose: implements 10G XGMAC/AXGMAC operations and port control for the original X-Gene driver.

Important APIs, types, and functions: provides direct and indirect CSR/PCS/AXG access, ECC init, drop counter reads, ring-interface association, XGMAC and PCS reset, MAC address programming, MSS register programming for TSO, frame size, link status, pause/flow control, MAC init, RX/TX enable/disable, full reset, XG CLE bypass, clear/shutdown, optional GPIO/SFP readiness lookup, and delayed link-state handling. Exports `xgene_xgmac_ops` and `xgene_xgport_ops`.

Control flow, state, and persistence: selected for XGMII/default high-speed mode. Probe enables TSO/RX checksum and initializes MSS locks. Hardware init configures rings and CLE for RSS, then MAC init programs 10G-specific registers. If no PHY is present, delayed link work checks hardware link and optional SFP GPIO state and updates carrier.

Dependencies and integration points: depends on `xgene_enet_xgmac.h`, resource bases set in main, CLE setup for XGMII, TSO MSS setup from TX path, GPIO descriptors, and ethtool pause/drop-counter callbacks.

Risks: indirect PCS/AXG register access uses polling and can fail silently if status bits change. SFP GPIO readiness can keep carrier down. MSS register refcounts in main must match completions. XG CLE bypass differs from classifier mode and must route to correct rings.

Test signals: 10G link bring-up, SFP ready/not-ready transitions, TSO traffic with multiple MSS values, RSS/CLE operation, pause frames, jumbo frames, reset/shutdown, and link work cancellation during close/remove.
