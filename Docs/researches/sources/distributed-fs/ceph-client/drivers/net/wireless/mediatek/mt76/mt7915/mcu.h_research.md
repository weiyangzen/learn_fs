# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mcu.h

## Purpose

`mcu.h` defines MT7915-family firmware command payloads, event payloads, command constants, TLV structures, enum values, and size limits used by `mcu.c` and related driver files. It is a firmware ABI header: the packed layouts describe how Linux-side state is serialized for the WM/WA MCU and how firmware notifications are decoded.

## Important APIs, Types, and Definitions

- Thermal and event payloads: `mt7915_mcu_thermal_ctrl`, `mt7915_mcu_thermal_notify`, `mt7915_mcu_csa_notify`, `mt7915_mcu_bcc_notify`, and `mt7915_mcu_rdd_report`.
- Radar/background scan structure: `mt7915_mcu_background_chain_ctrl`, including serving and monitor channel fields, scan mode, band index, and monitor scan type.
- Spatial reuse and EEPROM payloads: `mt7915_mcu_sr_ctrl`, `mt7915_mcu_eeprom`, and `mt7915_mcu_eeprom_info`.
- Query/response payloads: `mt7915_mcu_phy_rx_info`, `mt7915_mcu_mib`, `mt7915_mcu_txpower_sku`, `mt7915_mcu_tx`, and `mt7915_mcu_muru_stats`.
- BSS TLV structures: BMC rate, RA, HW AMSDU, BSS color, HE, beacon wrapper, beacon countdown, MBSSID, beacon content, in-band discovery, and protection TLVs.
- Command enums cover ATE parameters, channel MIB offsets, firmware log source, TWT agreement operations, WA parameter operations, RED controls, MMPS modes, beacon sub-TLVs, rate parameters, txpower feature IDs, OBSS SPR operations, thermal protection actions, TXBF actions, MURU settings, MURU stats commands, and SER actions.
- Size macros such as `MT7915_MAX_BEACON_SIZE`, `MT7915_BEACON_UPDATE_SIZE`, `MT7915_MAX_BSS_OFFLOAD_SIZE`, and `MT7915_BSS_UPDATE_MAX_SIZE` bound SKB allocations in `mcu.c`.

## Control Flow Role

This header does not execute control flow directly. Its values drive the command-building branches in `mcu.c`. For example:

- `THERMAL_PROTECT_*` constants select which firmware thermal operation a packed `mt7915_mcu_thermal_ctrl` represents.
- `BSS_INFO_BCN_*` values select nested beacon-offload sub-TLVs.
- `RATE_PARAM_*` values select fixed-rate, GI, HE-LTF, MMPS, automatic, or SPE update behavior.
- `TX_POWER_LIMIT_*` values select SKU enable, rate/path power tables, power queries, and frame power limits.
- `SPR_*` values select spatial reuse enablement, dynamic PD behavior, SIG-A restrictions, SRG bitmaps, and OBSS PD parameters.
- `SER_*` values encode firmware recovery actions and system assert triggers.

## State and Persistence Behavior

All structures in this file represent transient firmware messages or replies. They do not store driver state by themselves, but the layouts govern how runtime state from `mt7915_dev`, `mt7915_phy`, `mt7915_vif`, and `mt7915_sta` is persisted into firmware tables. Many structures are marked `__packed`, and some beacon TLVs are also `__aligned(4)`, so alignment is part of the ABI.

The most state-sensitive layouts are radar reports with arrays of pulses, channel MIB counters, MURU clear-on-read statistics, BSS update TLVs, beacon offload sub-TLVs, and txpower tables. Changes to these definitions affect runtime hardware behavior across resets only after firmware is reprogrammed; they are not saved by the kernel.

## Dependencies and Integration Points

`mcu.h` includes `../mt76_connac_mcu.h`, so it extends the common connac MCU API with MT7915-specific structures. It depends on constants from mac80211/mt76 headers such as `IEEE80211_NUM_ACS`, `CMD_HE_MCS_BW_NUM`, `MT7915_SKU_RATE_NUM`, and common BSS/STA request headers. `mcu.c` is the main consumer, but `main.c`, debugfs, DFS, and EEPROM code use the exported command helpers whose payloads are defined here.

## Risks and Edge Cases

- Packed firmware ABI structures are easy to break by adding fields, changing enum values, or using host-endian fields where firmware expects little-endian.
- Several enums use sparse firmware-assigned values, for example rate parameters, WA parameter IDs, txpower format IDs, SPR actions, and SER actions. Renumbering is not safe.
- Size macros must remain consistent with TLV builders in `mcu.c`; underestimating sizes causes SKB tail overrun risk, and overestimating can hide layout regressions.
- Radar report pulse arrays are large and firmware-owned; decoders must validate context before trusting the radar index.
- `struct edca` mixes 8-bit and little-endian fields; queue, CW, and TXOP conversion must stay in the sender.

## Test Signals

Header changes should be validated by building the driver with sparse/endian checking, exercising firmware commands that use every modified structure, checking firmware acceptance of BSS/STA/beacon updates, verifying txpower and thermal commands with real firmware replies, and ensuring `sizeof()`-based allocation macros still cover emitted TLVs. Runtime signs of mismatch include MCU command timeouts, firmware asserts, invalid radar events, wrong EDCA behavior, missing beacons, rejected station records, and broken power limits.
