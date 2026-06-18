# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/main.h

## Purpose
`main.h` is the central contract for the `rtw88` driver. It defines shared constants, enums, data structures, chip-operation callbacks, per-device state, per-vif/per-station private state, firmware state, coexistence state, PHY/dynamic-mechanism state, efuse/HAL state, power-save state, and core API prototypes. Nearly every implementation file in this subset includes it, and HCI-private data is embedded at the end of `struct rtw_dev`.

## Important APIs, Types, and Functions
- Core capability enums: HCI type, band, bandwidth, secondary-channel offset, network type, RF type/path, BB path, rate section, wireless set, chip type, TX/RX queue type, firmware type, descriptor rates, regulatory domain, flags, ports, WoW flags, and capability quirks.
- Power and packet descriptors: `struct rtw_tx_pkt_info`, `struct rtw_rx_pkt_stat`, `struct rtw_lps_conf`, `struct rtw_sec_desc`, `struct rtw_tx_report`, `struct rtw_sta_info`, and `struct rtw_vif`.
- Hardware abstraction: `struct rtw_chip_ops` and `struct rtw_chip_info` describe chip-specific hooks, table pointers, firmware names, FIFO layout, RF/BB parameters, power sequences, coexistence parameters, scan/WoW limits, and feature support.
- PHY/power state: `struct rtw_dm_info`, `struct rtw_efuse`, `struct rtw_hal`, `struct rtw_sar`, power-by-rate and power-limit arrays, DPK/IQK/GAPK/CFO state, and path-diversity state.
- Device root: `struct rtw_dev`, containing mac80211 handle, device handle, HCI ops/type, chip pointer, HAL/fifo/fw/efuse/security/stat/regd/BF/DM/coex state, locks, work items, queues, flags, ID bitmaps, WoW state, LED state, and flexible HCI-private storage.
- Inline helpers: vif/txq container conversions, efuse grant wrappers, WCPU checks, LDPC/STBC checks, MAC ID allocation/release, firmware crash hook, and band conversion.
- Exported prototypes for core lifecycle, channel setup, station/vif handling, firmware recovery/dump, port switching, beacon control, AMPDU factor, and scan notifications.

## Control Flow
The header establishes how the driver is assembled rather than executing logic itself. Transport drivers allocate `sizeof(struct rtw_dev) + private_hci_size`, then access `rtwdev->priv` through the flexible `priv[]` tail. Core code calls chip operations from `rtw_chip_ops` for power, MAC, PHY, RF, calibration, beamforming, coexistence, and LED behavior. Table-loading macros produce `struct rtw_table` instances consumed by PHY parsers. mac80211 private areas use `hw->sta_data_size`, `hw->vif_data_size`, and `hw->txq_data_size` to store `rtw_sta_info`, `rtw_vif`, and `rtw_txq`.

## State and Persistence Behavior
`main.h` defines all long-lived in-memory state for a device. `rtw_fw_state` persists firmware pointers and parsed feature/version fields until deinit. `rtw_efuse` persists factory/calibration values and hardware capabilities read from efuse and firmware feature reports. `rtw_hal` persists current channel/bandwidth/RF topology, RCR, TX power tables, SAR source, and chip-version fields. `rtw_dm_info` persists dynamic PHY metrics across watchdog intervals. `rtw_lps_conf` persists active/LPS/deep-LPS settings and backup policy flags. Bitmaps (`hw_port`, `mac_id_map`, CAM map, TX queue flags) are the persistent allocation state used by callbacks.

## Dependencies and Integration Points
The header includes mac80211, firmware, vmalloc, EWMA, bit operations, field helpers, I/O polling, interrupt, and workqueue APIs. It includes local `util.h` before later including `hci.h`, which relies on `struct rtw_dev`. It is consumed by core, PCI, PHY, PS, firmware, TX/RX, security, coexistence, efuse, regulatory, WoW, and chip-specific files. `struct rtw_chip_info` is the main integration point for per-chip modules: they provide tables, register descriptions, feature flags, and operation callbacks.

## Risks
- Layout stability matters: `struct rtw_dev` ends with flexible `priv[]`; transport private structures depend on correct allocation and alignment.
- Many fields are shared between interrupt, workqueue, mac80211 callback, and mutex-protected contexts. The header itself does not enforce locking, so readers must follow conventions from implementation files.
- Large multidimensional TX power arrays are indexed by regulatory domain, bandwidth, rate section, channel, path, and descriptor rate. Bad enum bounds or mismatched table sizes can corrupt behavior.
- Packed bitfield structs for efuse/power/PHY conditions depend on endianness guards; new fields or compiler assumptions can break table interpretation.
- `rtw_chip_ops` has many optional hooks. Call sites must check for NULL where appropriate; some hooks, such as power tracking or false-alarm statistics, are assumed present by core PHY logic.

## Test Signals
- Build coverage across all chip variants and HCI backends, catching structure/prototype drift.
- Probe with multiple chip infos validating `rtw_dev` private storage and `rtw_chip_ops` callback availability.
- Runtime association, AP, scan, WoW, coexistence, LPS, and firmware-recovery paths validating shared state transitions.
- KASAN/lockdep runs for struct lifetime, workqueue cancellation, and mixed interrupt/workqueue access.
- Regulatory and TX power tests confirming array bounds and table parser compatibility with `rtw_hal` definitions.
