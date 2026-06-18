## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_sgmac.c

Purpose: implements SGMII MAC/port operations for the original X-Gene driver.

Important APIs, types, and functions: the file provides CSR, clock/reset, ring-interface, diagnostic, and MCX register accessors; ECC init; drop counter reads; ring-interface association; internal MII/TBI reads and writes; SGMAC reset/address/speed/frame-size/autoneg configuration; RX/TX enable/disable; flow-control; CLE bypass; port clear/shutdown; and delayed link-state polling. It exports `xgene_sgmac_ops` and `xgene_sgport_ops`.

Control flow, state, and persistence: selected for `PHY_INTERFACE_MODE_SGMII`. During hardware init the port reset and MAC init configure clocks, ECC, ring association, MAC address, SGMII settings, and autoneg. If no external MDIO driver attaches, delayed work polls internal SGMII link state and updates carrier and MAC speed.

Dependencies and integration points: depends on `xgene_enet_sgmac.h`, shared main private data, ring IDs, CLE bypass path, PHYLIB speed constants, and operation-table calls from `xgene_enet_main.c`.

Risks: internal MII operations are bounded by busy polling and can misread link state if timing changes. Link polling and MAC enable/disable must coordinate with open/close delayed work. CLE bypass must program correct destination and buffer pool IDs.

Test signals: SGMII probe, internal/external PHY modes, autoneg completion, 10/100/1000 speed transitions, pause control, delayed link polling, and traffic after link flap.
