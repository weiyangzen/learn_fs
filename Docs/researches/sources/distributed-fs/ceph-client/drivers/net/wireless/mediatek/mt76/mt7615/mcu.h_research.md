# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mcu.h

Purpose: Defines MT7615/MT7663 MCU wire formats, firmware state constants, regulatory/test power SKU indexes, radar report layouts, remain-on-channel TLVs, and DBDC type identifiers. It is a protocol contract header used by transport-specific MCU implementations and by higher-level mt7615 control code.

Important APIs, types, and constants: `struct mt7615_mcu_txd` and `struct mt7615_uni_txd` describe legacy and unified MCU command descriptors, including command IDs, sequence numbers, packet type, source/destination index, and ACK/set/query options. `struct mt7615_mcu_rxd` is the common MCU event header. `struct mt7615_mcu_csa_notify`, `struct mt7615_mcu_rdd_report`, and `struct mt7615_roc_tlv` model channel-switch, radar-detection, and remain-on-channel payloads. `MT_SKU_*` indexes map EEPROM/rate families into firmware TX power tables. `FW_STATE_PWR_ON` and `FW_STATE_N9_RDY` are used by USB/SDIO/PCI firmware bring-up polling.

Control flow and integration: This file has no executable code, but its packed/aligned structures are serialized directly into skb command buffers by `mt7615_mcu_fill_msg()`, `mt7663u_mcu_send_message()`, and `mt7663s_mcu_send_message()`. Transport code relies on `sizeof(struct mt7615_mcu_txd)` for MCU headroom, so layout drift changes DMA-visible packet framing. Radar and ROC structures are consumed by MCU event and command paths outside this subset.

State and persistence: The header defines transient host/firmware command state only. Persistent data is in firmware, EEPROM, and device registers; this file preserves host-side binary interpretation.

Dependencies: Includes `../mt76_connac_mcu.h` for command macros and shared MCU definitions; depends on Linux endian and packing conventions through included mt76 headers.

Risks: Any field size, packing, alignment, endian annotation, SKU order, or enum value change can break firmware ABI. The large radar report arrays are fixed-format hardware reports and should not be resized without matching firmware. `set_query` is documented as firmware-don't-care in one descriptor but remains part of the ABI.

Test signals: Build coverage catches type/layout references. Runtime signals include successful firmware load, MCU command replies, DFS/radar reports, CSA notifications, ROC grants, and testmode TX power command success.
