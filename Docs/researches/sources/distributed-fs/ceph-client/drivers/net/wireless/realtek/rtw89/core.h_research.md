# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/core.h

## Purpose

`core.h` is the central internal contract for the Realtek `rtw89` mac80211 driver. It declares the driver-wide constants, hardware enums, descriptor formats, firmware/coexistence report layouts, device/vif/station state containers, bus and chip operation tables, inline dispatch helpers, and core function prototypes used by the PCI/USB/HCI, MAC, PHY, firmware, power-save, scan, MLO/MCC, Bluetooth coexistence, regulatory, and debug paths.

The file is not a standalone implementation unit. Its primary purpose is to keep shared driver state and call boundaries consistent across the `rtw89` source tree while hiding chip- and bus-specific behavior behind `struct rtw89_chip_ops` and `struct rtw89_hci_ops`.

## Major Types and APIs

- Hardware identity and channel/rate enums: `rtw89_core_chip_id`, `rtw89_chip_gen`, `rtw89_hci_type`, `rtw89_band`, `rtw89_bandwidth`, `rtw89_rf_path`, `rtw89_hw_rate`, `rtw89_rate_section`, `rtw89_nss`, regulation and 6 GHz power enums, and MLO/DBCC mode enums provide the canonical values consumed by MAC/PHY/FW code.
- Descriptor and packet metadata: `rtw89_tx_desc_info`, TX descriptor body/info variants, RX descriptor variants, `rtw89_rx_desc_info`, and `rtw89_rx_phy_ppdu` define the parsed and generated TX/RX metadata passed between HCI DMA/USB code and core RX/TX handling.
- Per-role state: `rtw89_vif`, `rtw89_vif_link`, `rtw89_sta`, and `rtw89_sta_link` extend mac80211 objects with driver state such as MAC ID, port, BSSID/addr CAM entries, rate-adaptation state, RSSI/EVM/SNR EWMA data, TID aggregation state, link maps, and MLO transition tracking.
- Device state: `struct rtw89_dev` is the root object. It owns mac80211 handles, bus/chip pointers, HAL/channel state, firmware state, HCI state, efuse data, CAM allocation maps, TX queues and waits, C2H queues, SER recovery state, RF calibration state, TX power/SAR/TAS/regulatory data, Bluetooth coexistence state, WoWLAN state, NAPI, debugfs, and HCI-private trailing storage.
- Operation tables: `struct rtw89_hci_ops` abstracts bus operations such as TX write, start/stop, register access, interrupts, DMA control, reset, recovery hooks, and resource reclamation. `struct rtw89_chip_ops` abstracts chip-specific PHY/MAC/RF operations, descriptor conversion, channel setup, efuse reads, RF calibration, TX power, coexistence programming, CAM H2C commands, and scheduler control.
- Firmware and command state: `rtw89_fw_info`, `rtw89_fw_suit`, feature bitmaps, wait objects, H2C/C2H counters, secure boot metadata, firmware element tables, and `rtw89_fw_suit_get()` centralize runtime firmware capabilities and loaded image metadata.
- Bluetooth coexistence contracts: the large `rtw89_btc_*` family defines host-side coexistence state, firmware report formats, TDMA/slot policies, AFH maps, BT/Wi-Fi role descriptions, counters, error maps, and versioned report unions. These structures are packed when they cross the firmware boundary.
- Regulatory and power state: `rtw89_regulatory_info`, `rtw89_sar_info`, ACPI SAR table structures, antenna-gain state, TAS history, TX power by-rate/limit tables, RFE parameter sets, and helpers such as `rtw89_regd_get()` model persistent power constraints derived from firmware tables, efuse, country code, ACPI, and runtime regulatory changes.
- Inline helpers: wrappers dispatch through HCI/chip ops, convert mac80211 private objects, manage RCU link lookups, read/write registers with masks, select active PHYs, complete TX waits, allocate RX SKBs with radiotap headroom, and convert bands/bandwidths/RU allocation values.
- Exported core prototypes: the bottom of the header declares core TX/RX, NAPI, station/vif link lifecycle, initialization/register/unregister, channel setup, BA CAM management, scan/ROC, wait conditions, power/start/stop, P2P PS, 6 GHz recalculation, MLO switch, and dynamic-management disable APIs.

## Control Flow

Typical TX flow starts with mac80211 invoking driver ops, core code filling `rtw89_core_tx_request` and `rtw89_tx_desc_info`, then `rtw89_hci_tx_write()` dispatching to bus-specific HCI. `rtw89_core_tx_kick_off()` or `rtw89_core_tx_kick_off_and_wait()` triggers transmission; waitable TX uses `rtw89_tx_wait_info`, an RCU pointer in `rtw89_tx_skb_data`, and completion from TX report status.

RX flow is the inverse: HCI code obtains descriptors and payloads, chip-specific `query_rxdesc` parses descriptor variants into `rtw89_rx_desc_info`, and `rtw89_core_rx()` consumes SKBs. Monitor-mode allocations reserve `RTW89_RADIOTAP_ROOM`; PHY/PPDU metadata can be converted into mac80211 rate/RSSI/status fields through chip callbacks.

Device bring-up uses allocation and registration APIs, HCI `start`, chip pre/post init, firmware metadata/feature checks, CAM bitmap initialization, efuse/phycap/RFE setup, channel setup, and workqueue/NAPI activation. Shutdown and recovery reverse those pieces, with explicit SER state and HCI recovery hooks. `rtw89_hci_reset()` is notable because the HCI reset callback must complete pending TX waits before the core clears completed wait entries.

Channel and multi-role flow centers on `rtw89_hal.chanctx[]`, `rtw89_entity_mgnt`, per-link `chanctx_idx`, MCC/MLO structures, scan state, and helpers such as `rtw89_chandef_get()`, `rtw89_chan_get()`, `rtw89_scan_chan_get()`, `rtw89_get_active_phy_bitmap()`, and `rtw89_for_each_active_bb`. The active PHY set depends on DBCC and MLO DBCC mode.

## State and Persistence Behavior

Most state is in-memory kernel driver state with lifetimes tied to the `ieee80211_hw`, vifs, stations, firmware image, and bus device. There is no filesystem persistence in this header. Persistent hardware-origin data enters through efuse/phycap (`rtw89_efuse`, `rtw89_phy_efuse_gain`, RFE type, country code, trim data), firmware image metadata, ACPI SAR tables, DMI quirks, and regulatory configuration.

Long-lived runtime state includes bitmaps for MAC IDs, ports, packet offloads, CAM entries, firmware features, flags, quirks, per-link associations by MAC ID, TX/RX statistics, thermal/CFO/TSSI/RFK calibration state, coexistence counters and policies, WoWLAN parameters, and beacon/traffic monitoring history. Many fields are updated by work items and firmware events rather than direct synchronous calls.

Concurrency is explicit in several state containers: spinlocks guard BA lists, RPWM, TX report SKB arrays, and SER message queues; RCU protects association pointers, TX wait pointers, and mac80211 link configuration snapshots; completions are used for firmware/offload waits, power-save waits, MCC/MLO waits, RFK waits, and waitable TX. Several helpers assert wiphy locking for RF access and TX-wait cleanup.

## Dependencies and Integration Points

The header depends on Linux kernel and mac80211 APIs: `linux/average.h`, `bitfield.h`, `dmi.h`, `firmware.h`, `iopoll.h`, `workqueue.h`, `net/mac80211.h`, RCU, completions, SKBs, NAPI, workqueues, bitmaps, and cfg80211/nl80211 structures.

Internal integration points are broad:

- HCI-specific code supplies `rtw89_hci_ops` for PCI/USB/SDIO style behavior and register access.
- Chip files supply `rtw89_chip_info`, `rtw89_chip_variant`, `rtw89_chip_ops`, firmware definitions, PHY/RF tables, DLE/HFC quota tables, IMR tables, EDCCA/DIG/NHM register definitions, and coexistence parameters.
- MAC/PHY/FW modules consume descriptor structures, H2C/C2H wait state, firmware feature flags, RFK/BB helper wrappers, and channel/regulatory/TX power data.
- mac80211 integration uses `rtw89_ops`, private `drv_priv` conversions for `ieee80211_vif`, `ieee80211_sta`, and `ieee80211_txq`, and link-aware RCU lookups for MLO.
- WoWLAN, P2P/ROC, scan offload, MCC, MLO, SER, BTC, regulatory/SAR/TAS, and debugfs modules all store their root state in `rtw89_dev`.

## Risks and Edge Cases

- Operation-table assumptions are sharp: many wrappers call function pointers unconditionally, while some tolerate missing callbacks. New chip/HCI ports must fill required ops consistently or crashes will occur.
- Packed firmware report structures are ABI-like. Field ordering, endian annotations, version unions, and sizes must match firmware exactly; changes can silently corrupt coexistence, scan, or report parsing.
- Link and station helpers rely on RCU and fallback default links when exact MLO link data is missing. Incorrect locking or stale link IDs can lead to wrong BSS/STA state, especially during MLO transitions.
- Register mask helpers use `__ffs(mask)` and assume nonzero masks; a zero mask would be invalid. `rtw89_write32_mask()` warns on unaligned 32-bit addresses, but 8/16-bit helpers depend on callers choosing valid addresses and masks.
- CAM and MAC-ID resources are bitmap-backed and finite. Leaks or double releases can break security CAM, BA CAM, packet offload, or station association state.
- TX waits combine RCU, completions, SKB ownership, and HCI reset requirements. Failing to complete pending waits during reset can leave waiters stuck or leak SKBs.
- Regulatory/TX power state combines country, 6 GHz TPE, SAR, antenna gain, RFE, efuse, ACPI, and firmware tables. Bugs can become compliance issues, not just connectivity defects.
- Coexistence state has many versioned layouts and counters; mismatched `rtw89_btc_ver` feature negotiation can cause invalid H2C/C2H interpretation.
- DBCC/MLO active PHY selection is mode-sensitive. Wrong mode handling can update the wrong BB context, RF path, channel context, or power table.

## Test Signals

Useful validation signals include successful compilation of all `rtw89` chip/HCI variants against this header, sparse/lockdep/RCU checks for the inline helpers, and runtime coverage of probe, firmware download, start/stop, suspend/resume, WoWLAN, SER recovery, and device unplug.

Functional tests should exercise TX/RX on PCI and USB variants, monitor mode radiotap RX allocation, waitable management/H2C TX completion and timeout paths, BA setup/teardown, station add/assoc/disassoc/remove, scan start/complete, ROC, P2P NoA/PS updates, channel changes across 2.4/5/6 GHz, DBCC/MCC/MLO modes, and 6 GHz regulatory recalculation.

Hardware-oriented signals include correct efuse/phycap parsing, RFK/DACK/IQK/DPK completion reports, thermal/TSSI/CFO tracking, EDCCA/DIG/noise monitor behavior, TX power table loading, SAR/TAS enforcement, antenna gain handling, RF kill state, HCI flow-control quotas, DMA idle polling, and interrupt recovery.

Coexistence test signals should cover BT profile changes, AFH map updates, TDMA slot report parsing, BT/Wi-Fi role-info H2C layouts across versioned firmware, coexistence counters, mailbox errors, report length/version mismatches, and policy updates under scan, 2.4 GHz traffic, DBCC, MLO, and WoWLAN.
