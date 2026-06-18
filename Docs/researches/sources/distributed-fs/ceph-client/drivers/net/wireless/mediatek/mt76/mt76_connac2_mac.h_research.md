# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac2_mac.h

Purpose: Bitfield and enum contract for Connac2-generation MAC TX/RX descriptors, TX status, TX free events, RX vectors, HE radiotap decoding, and copy-engine TX metadata.

Important APIs and constants: Defines TX header formats, packet types, queue IDs, TX status formats, TX free masks, TXD DW0-DW8 fields, TX rate encoding, TXS fields, RXD normal/group fields, PRXV/CRXV rate vector fields, copy-engine parse lengths, CT info flags, MCU port queue IDs, port IDs, and fragment IDs.

Control flow and integration: `mt76_connac_mac.c` consumes these masks to write TXWI descriptors, parse TX status, decode RX rates/HE radiotap data, reverse mesh header translation, and free TXWI tokens. mt7615 USB/SDIO code also shares constants like `MT_CT_PARSE_LEN` and queue IDs for descriptor setup.

State and persistence: Describes hardware-visible descriptor and report state. No host state is stored.

Dependencies: Linux bitfield macros and mac80211 rate/descriptor semantics through including C files.

Risks: Constants are hardware ABI. Connac2 and Connac3 headers intentionally have similar names with different bit positions; mixing them corrupts descriptor parsing. Some fields are overloaded by bus or chip generation, requiring caller-side checks like `mt76_is_mmio()` and `is_connac2()`.

Test signals: TX descriptor correctness, TX status rate/stat updates, RX rate/radiotap decoding, mesh header translation, BA aggregation start, and traffic on Connac2 chips.
