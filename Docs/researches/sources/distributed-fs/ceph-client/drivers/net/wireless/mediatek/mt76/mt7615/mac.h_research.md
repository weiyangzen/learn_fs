# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mac.h

Purpose: descriptor and MAC bitfield definitions for MT7615-family RXD, RXV, TXD, TXS, DFS radar structures, and WTBL address calculation.

Important APIs/types/macros: defines RX descriptor fields (`MT_RXD*`), RX vector fields (`MT_RXV*`), TX header/packet/port enums, TX descriptor fields (`MT_TXD*`), TX rate fields, TX status fields (`MT_TXS*`), DFS pulse/pattern/spec structs, and `mt7615_mac_wtbl_addr()`.

Control flow: declarative only. The macros are consumed heavily by `mac.c` for parsing hardware RX/TX status and writing TX descriptors, and by `mcu.c` when constructing beacon offload descriptors.

State and persistence: describes volatile packet descriptors and firmware/hardware status formats. DFS structs are in-memory templates passed to MCU radar-threshold commands.

Dependencies and integration: assumes Linux bit macros and `struct mt7615_dev` from included compilation context. WTBL address helper uses `MT_WTBL_BASE(dev)` and `MT_WTBL_ENTRY_SIZE` from register headers.

Risks: descriptor bitfields are hardware ABI. Wrong bit definitions can corrupt TX metadata, misreport RX status, or mis-handle encryption and aggregation. The USB TXD size path in `mac.c` also uses these fields, so changes affect non-MMIO transports.

Test signals: correct RX rate/RSSI/decryption flags, TX descriptor queue selection, TX status retry parsing, DFS pattern commands with expected payload sizes, and WTBL address calculations matching hardware table dumps.
