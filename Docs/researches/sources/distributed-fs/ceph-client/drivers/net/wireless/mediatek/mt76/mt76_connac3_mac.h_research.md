# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac3_mac.h

Purpose: Bitfield and enum contract for Connac3-generation MAC descriptors, RX descriptors, RX vectors, TX status/free reports, and EHT/HE radiotap source fields.

Important APIs and constants: Defines queue IDs, copy-engine parse lengths, RXD DW0-DW4 fields, group fields, PRXV fields, CRXV HE/EHT fields, TX header/packet/port/management/fragment enums, CT flags, TXD DW0-DW9 fields, TXP buffer/token fields, TX rate encoding, TXFREE fields, and TXS fields.

Control flow and integration: `mt76_connac3_mac.c` uses RX vector masks for HE/EHT radiotap decoding. Connac3 driver TX/RX paths use TXD, TXP, TXFREE, and TXS constants to build descriptors and parse hardware reports.

State and persistence: Describes DMA-visible descriptors and RX/TX hardware reports only.

Dependencies: Kernel bitfield macros and mac80211 PHY/radiotap semantics through consuming files.

Risks: Connac3 masks differ from Connac2, including wider WLAN IDs, RX band indexes, TX rate/NSS fields, and EHT fields. Copying Connac2 logic without adjusting bit positions is a high-risk regression. Some mask definitions are easy to misread, so tests should validate actual decoded captures.

Test signals: Connac3 TX/RX traffic, TX status and free event parsing, monitor-mode HE/EHT radiotap output, aggregation behavior, and descriptor validation under multiple bandwidth/NSS modes.
