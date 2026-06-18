# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/core.h

## Purpose

`core.h` defines the shared ath10k object model and public core API used by bus, MAC, HTT, WMI, debug, coredump, spectral, testmode, thermal, and WoW code. It is the driver-wide contract for firmware components, peers, stations, virtual interfaces, scan state, crash state, debug state, capabilities, locks, completions, and exported lifecycle functions.

## Important APIs, Types, and Constants

The header provides register bit helpers (`MS`, `SM`, `WO`), core timeouts, channel limits, RSSI/noise defaults, management pending limits, keepalive constants, BDF SMBIOS constants, recovery limits, and bus string mapping through `ath10k_bus_str()`.

SKB metadata is defined by `struct ath10k_skb_cb`, `struct ath10k_skb_rxcb`, and helpers `ATH10K_SKB_CB()`/`ATH10K_SKB_RXCB()`. These impose compile-time size checks against mac80211 SKB control storage and hold DMA addresses, endpoint ids, txq/vif pointers, flags, airtime estimate, and cipher metadata.

Major subsystem structures include `struct ath10k_wmi`, `struct ath10k_fw_stats`, `struct ath10k_tpc_stats`, `struct ath10k_peer`, `struct ath10k_sta`, `struct ath10k_vif`, `struct ath10k_fw_crash_data`, `struct ath10k_debug`, `struct ath10k_fw_file`, `struct ath10k_fw_components`, and `struct ath10k_bus_params`. `struct ath10k` itself aggregates all driver state and ends with aligned `drv_priv[]` for bus-private data.

The exported API prototypes cover NAPI control, object create/destroy, firmware feature string formatting, firmware API parsing, start/stop/suspend/recovery, registration/unregistration, board file fetching, Device Tree variant checking, and board file release.

## Control Flow and State Model

The header encodes a lifecycle state machine in `enum ath10k_state`: OFF, ON, RESTARTING, RESTARTED, WEDGED, and UTF. Comments document how recovery moves through RESTARTING/RESTARTED and why WEDGED blocks commands to avoid recursive recovery. `enum ath10k_firmware_mode` distinguishes normal 802.11 operation from UTF/factory test mode.

Firmware feature bits (`enum ath10k_fw_features`) are the central compatibility mechanism. They describe WMI dialects, raw mode, MFP, peer flow control, BT coexistence parameters, non-BMI loading, channel-info behavior, peer fixed rate, IRAM recovery, and several quirks. Device flags (`enum ath10k_dev_flags`) represent runtime conditions such as CAC, core registration, crash flush, raw mode, disabled hardware crypto, BT coexistence, peer stats, and NAPI enabled.

Per-peer and per-station state is split by locking. Peer keys, PN tracking, and peer maps are protected by `data_lock`. Station rate, retry, RX duration, power-save, TID config, and optional debugfs TID counters are stored in `struct ath10k_sta`. Per-vif state tracks vdev identity, beacon buffers, power save, AP/STA specific fields, WMM params, delayed connection-loss work, bitrate masks, and per-TID overrides.

## Persistence Behavior

The header itself persists nothing, but it names all in-memory state that mirrors persistent or externally supplied inputs: firmware metadata, board data pointers, calibration files, SMBIOS/Device Tree board variants, nvmem/EEPROM-derived calibration mode, runtime feature bits, and module-global `ath10k_frame_mode`/`ath10k_coredump_mask`. Firmware and board data pointers are owned by `struct firmware` objects managed in `core.c`.

## Dependencies and Integration Points

`core.h` includes Linux completion, PCI, UUID/time/LED facilities and ath10k subsystem headers (`htt.h`, `htc.h`, `hw.h`, `targaddrs.h`, `wmi.h`, DFS, spectral, thermal, wow, swap). Because nearly every ath10k translation unit includes it, changes here affect ABI-like internal contracts across bus drivers, mac80211 operations, debugfs, coredump collection, and firmware protocol parsing.

Conditional fields are important integration points. `CONFIG_ATH10K_DEBUGFS` embeds debug and spectral state; `CONFIG_DEV_COREDUMP` embeds coredump storage; `CONFIG_MAC80211_DEBUGFS` adds station TID stats; `CONFIG_ATH10K_DEBUG` changes debug logging behavior through declarations in `debug.h`.

## Risks

The largest risk is shared-state contract drift. Reordering or resizing SKB control blocks can violate mac80211 storage assumptions. Adding fields to `struct ath10k` without clear locking annotations can introduce races. Changing enum values can break firmware feature interpretation, debug masks, or user-space crash-dump ABI. Conditional compilation paths must keep inline stubs and real implementations behaviorally compatible. Because `struct ath10k_fw_crash_data` is written by bus crash handlers and packaged by coredump code, its locking and lifetime are cross-file sensitive.

## Test Signals

Compile-time `BUILD_BUG_ON` checks for SKB CB sizing and feature-string table size are key signals. Runtime signals include lockdep coverage for `conf_mutex`, `data_lock`, and `dump_mutex`; successful creation/destruction with all optional configs on/off; recovery transitions without stuck completions; debugfs builds with and without `CONFIG_ATH10K_DEBUGFS`; and devcoredump builds with and without `CONFIG_DEV_COREDUMP`.
