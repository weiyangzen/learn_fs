# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mcu.h

## Purpose
`mcu.h` is the firmware ABI contract for `mcu.c`. It defines packed MCU RX/event records, command TLVs, enums, constants, and maximum message-size formulas used when constructing MT7996-family UNI and legacy MCU messages. It is intentionally hardware/firmware-facing: fields are endian-annotated, packed, and often mirror exact TLV payloads consumed or emitted by WM/WA firmware.

## Important APIs, Types, And Functions
The receive-side core is `mt7996_mcu_rxd`, which describes firmware event headers with EID, sequence, option, ext EID, and source/destination index. `mt7996_mcu_uni_event` carries generic UNI command result status. Event payload structures cover thermal notifications, countdown notifications, radar reports with pulse arrays, all-station rate/stat responses, and WED RRO BA session events.

Command payload types are grouped by subsystem. BSS TLVs include rate, RA, RLM channel, color, in-band discovery, beacon content/countdown/MBSSID, security, timing, MLD, protection, and MLD link operation. STA TLVs include HT, BA, EHT, security keys, RA, fixed RA, header translation, MLD setup, EHT MLD, and fixed-rate control. Other structures cover EEPROM update/access, background chain/offchannel scan, thermal control, VOW RX airtime, beamforming control, RRO settings, SER commands, RF register access, and txpower table control.

Important enums define UNI tags and command sub-actions: firmware logging, TWT agreement operations, WA parameter commands, MMPS modes, header translation TLVs, rate-control fields, beamforming actions, channel-switch tags, band config tags, RDD/efuse/VOW/MIB/power/TWT/RRO/SR/thermal/txpower/reg/SER/SDO tag IDs, and patch security modes. Size constants such as `MT7996_BSS_UPDATE_MAX_SIZE`, `MT7996_STA_UPDATE_MAX_SIZE`, `MT7996_MAX_BSS_OFFLOAD_SIZE`, and `MT7996_MAX_BEACON_SIZE` constrain skb allocation in `mcu.c`.

## Control Flow
This header has no executable control flow, but it shapes runtime control by defining how message builders append TLVs and how event handlers cast skb payloads. `mcu.c` allocates a command skb, writes a fixed header such as `bss_req_hdr` or `uni_header`, appends one or more structures from this header through `mt7996_mcu_add_uni_tlv()` or `mt76_connac_mcu_add_tlv()`, and sends the skb through mt76 MCU ops. Receive handlers pull `mt7996_mcu_rxd`, then inspect EID/tag values from this header to decide which packed payload to parse.

## State And Persistence
The header itself stores no state. It defines the wire representation for state that lives in firmware, hardware tables, and driver objects: BSS indices, WCID indices, EEPROM pages, RRO session IDs, thermal thresholds, radar pulse data, MLD IDs, RA state, beacon offload templates, and security key material. Because many structures contain flexible arrays or unions, caller-side length and tag validation is the real state-safety boundary.

## Dependencies And Integration Points
`mcu.h` includes `../mt76_connac_mcu.h`, so it extends shared Connac MCU definitions rather than replacing them. It is consumed primarily by `mcu.c`, but exported function declarations in `mt7996.h` expose many operations whose payloads are described here. It also depends on Linux/mac80211 constants such as `IEEE80211_NUM_ACS`, cipher IDs, HE/EHT capability shapes, and endian types.

## Risks
The main risk is ABI mismatch. Packed structure layout, reserved bytes, endian conversion, tag IDs, and maximum message sizes must match firmware exactly. Some structs expose flexible arrays and unioned payload interpretations; an incorrect tag or length can cause parser confusion or truncated copies. Size macros can become stale when new TLVs are added, producing allocation underruns in command builders. The header also carries key material layouts, including beacon protection modes, so cipher ID mistakes can break security behavior.

## Test Signals
Compile-time coverage should catch missing type/tag names and many size changes. Runtime signals include successful MCU command acknowledgements, valid all-station and thermal events, correct beacon/offload operation, successful EEPROM/efuse queries, WED RRO BA status processing, and stable behavior across MT7996, MT7992, and MT7990 variants. ABI regressions typically surface as firmware command failures, invalid status events, broken station setup, or command timeouts.
