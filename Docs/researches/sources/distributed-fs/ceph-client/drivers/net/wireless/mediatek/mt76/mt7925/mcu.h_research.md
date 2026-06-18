# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mcu.h

Purpose: MT7925 firmware ABI header. It defines MCU event IDs, packed command/event/TLV structures, firmware constants, cipher mapping, testmode payloads, scan/BSS/STA/power/offload structures, and exported MCU function prototypes.

Important APIs/types/functions: key structs include `mt7925_mcu_rxd`, `mt7925_mcu_uni_event`, `mt7925_txpwr_req/event`, scan TLVs, `bss_req_hdr`, `bss_rate_tlv`, `bss_mld_tlv`, `bss_eht_tlv`, `sta_rec_ba_uni`, `sta_rec_eht`, `sta_rec_sec_uni`, `sta_rec_hdr_trans`, `sta_rec_mld`, `sta_rec_eht_mld`, power-limit TLVs, ARP/NS/WoW TLVs, ROC TLV, and testmode command payloads. `mt7925_mcu_get_cipher()` maps Linux WLAN cipher suites to connac3 firmware cipher IDs.

Control flow: the header does not execute logic beyond the inline cipher mapping, but its structure definitions drive how `mcu.c` serializes commands and interprets events. Size macros `MT7925_STA_UPDATE_MAX_SIZE` and `MT7925_BSS_UPDATE_MAX_SIZE` determine skb allocation capacity for composite firmware messages.

State/persistence: no runtime state is stored in the header. It defines the serialized state exchanged with firmware for EEPROM, rate power, scan, BSS, STA, security keys, MLO, PM/offload, ROC, and testmode.

Dependencies/integration: includes `mt76_connac_mcu.h` and relies on Linux wireless cipher constants and mt76/connac shared TLV definitions. Prototypes are consumed by `main.c`, `mac.c`, `init.c`, `debugfs.c`, and bus-specific MT7925 drivers.

Risks: packed ABI structs must match firmware exactly; changing field sizes/order or allocation-size macros can break command parsing. Inline cipher mapping returning `CONNAC3_CIPHER_NONE` controls software fallback paths. Max scan/BSS/STA sizes must stay large enough as TLVs evolve.

Test signals: compile ABI users with sparse/packed warnings, install every supported cipher, exercise EHT/MLO STA and BSS records, scan with max SSID/BSSID/channel data, WoW patterns, ROC requests, and firmware response parsing against real firmware.
