## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_cle.h

Purpose: describes the classifier engine register layout, DRAM encodings, parser node formats, RSS constants, and CLE operation export.

Important APIs, types, and functions: defines indirect access registers (`INDADDR`, `INDCMD`, `DATA_RAM0`), parser pointers, default class-result registers, RSS control, command timeouts, packet RAM size, DRAM register count, node and branch field positions, jump modes, parser/node/operation enums, DRAM and command types, RSS hash type, protocol type/version, DB pointer indexes, sideband fields, IDT fields, and data structures for branches, decision nodes, key nodes, DB pointers, parser trees, and `struct xgene_enet_cle`.

Control flow, state, and dependencies: included by `xgene_enet_main.h` and implemented by `xgene_enet_cle.c`. It carries no live state except the structures embedded in `xgene_enet_pdata`.

Integration points: `xgene_cle3in_ops` is consumed by `xgene_enet_setup_ops` for XGMII; ring/buffer pool IDs from the main driver feed DB pointer and RSS IDT construction.

Risks: packed bitfield constants are hardware ABI. Small changes can invalidate parser trees, default routing, or RSS queue selection. The data structures contain pointers to temporary setup arrays in init paths, so use after setup must not assume permanent storage beyond programmed hardware.

Test signals: compile CLE users, initialize XGMII hardware, verify default packet acceptance, packet drops for unsupported paths if expected, and RSS queue distribution.
