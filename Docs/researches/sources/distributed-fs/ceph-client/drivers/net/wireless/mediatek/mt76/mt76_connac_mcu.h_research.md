# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac_mcu.h

Purpose: this header is the shared Connac MCU ABI contract. It defines command encoding macros, firmware/patch metadata layouts, MCU TX/RX descriptors, BSS/STA/WTBL TLV structures, scan/offload/WoWLAN payloads, capability bits, event IDs, cipher mappings, and prototypes for the helpers implemented in `mt76_connac_mcu.c`.

Important types and APIs: key structures include `mt76_connac2_mcu_txd`, `mt76_connac2_mcu_uni_txd`, `mt76_connac2_mcu_rxd`, `mt76_connac2_patch_hdr`, `mt76_connac2_patch_sec`, `mt76_connac2_fw_trailer`, `mt76_connac2_fw_region`, generic `struct tlv`, `sta_req_hdr`, `wtbl_req_hdr`, many `sta_rec_*` and `wtbl_*` TLVs, `mt76_connac_bss_basic_tlv`, scan request/done structures, GTK/ARP/suspend/WoWLAN TLVs, and `mt76_sta_cmd_info`. Inline helpers include `mt76_connac_mcu_get_cipher`, `mt76_connac_mcu_gen_dl_mode`, `mt76_connac_mcu_get_wlan_idx`, and `mt76_connac_mcu_add_tlv`.

Control flow role: this file does not execute control flow directly beyond small inline encoders. It shapes control flow by defining how command IDs are constructed with `MCU_CMD`, `MCU_EXT_CMD`, `MCU_UNI_CMD`, `MCU_CE_CMD`, and query/WA/WM variants. The helpers in the C file then inspect these bit fields to choose descriptor format, query/set flags, and destination indexes.

State and persistence behavior: all structures are transient command/event payloads, but they encode persistent firmware state such as station connection state, BSS activation, WTBL entries, BA windows, security keys, channel context, WoWLAN triggers, rate-power SKU tables, and firmware download state. The inline WLAN index split is state-compatible behavior: non-v1 devices use low/high portions while v1 devices use the legacy low byte only.

Dependencies and integration: the header depends on `mt76_connac.h`, kernel bitfield/endian helpers, mac80211/cfg80211 constants, and mt76 core types. It is included by Connac chip drivers and the shared implementation, so any layout change affects firmware interoperability across multiple chips.

Risks: packed structure size and alignment are critical. The `static_assert` around `mt76_connac2_mcu_rxd` guards a flexible-array layout hazard. Command/event numeric IDs must remain synchronized with firmware. Several comments document subtle firmware semantics, such as unified command option bits, WoWLAN trigger bits, and rekey modes. Incorrect cipher mapping or download-mode generation can silently break security or firmware boot.

Test signals: compile-time `static_assert` and `BUILD_BUG_ON` checks catch some layout issues. Runtime validation comes from firmware command acknowledgements, event parsing, successful STA/BSS/WTBL programming, scan/WoWLAN behavior, and security interop with every advertised cipher. ABI changes should be tested against all Connac generations represented by callers.
