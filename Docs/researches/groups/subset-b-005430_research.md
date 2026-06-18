# subset-b-005430 Research

Grouped source research for RTL8723BS staging driver include headers. Each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_intf.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_intf.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_intf.h` defines the driver-wide HAL facade: hardware variable identifiers, default-definition query identifiers, ODM variable selectors, RF-change causes, wake reasons, and wrappers that upper driver code calls without knowing the RTL8723BS SDIO implementation details. The source was reviewed as a complete 269-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `rtw_hal_init`, `rtw_hal_deinit`, `rtw_hal_stop`, `rtw_hal_set_hwreg`, `rtw_hal_get_hwreg`, `rtw_hal_xmit`, `rtw_hal_mgnt_xmit`, `rtw_hal_init_recv_priv`, `rtw_hal_update_ra_mask`, `rtw_hal_read_bbreg`, `rtw_hal_write_rfreg`, `rtw_hal_fill_h2c_cmd`, `SetHwReg8723BS`, `GetHwReg8723BS`, and the `HW_VAR_*`, `HAL_DEF_*`, and `HAL_ODM_*` enums.

## Control Flow

Callers route initialization, register access, channel changes, power-save H2C commands, C2H handling, and transmit/receive setup through the generic `rtw_hal_*` entry points; the RTL8723BS-specific implementation interprets the `HW_VAR_*` selector and updates MAC, BB, RF, firmware, or descriptor state.

## State and Persistence Behavior

The header owns no storage but standardizes mutable adapter state: efuse data, RF state, CAM entries, beacon timing, rate adaptation, MACID sleep, firmware power state, and queue configuration. Values persist in `struct adapter` fields, hardware registers, and firmware mailboxes.

## Dependencies and Integration Points

Depends on common Realtek types such as `struct adapter`, `struct xmit_frame`, `struct sta_info`, `enum channel_width`, bit macros, and the chip-specific 8723B HAL implementation. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

The selector enums are ABI-like contracts between generic code and chip HAL callbacks; reordering or mismatching payload sizes can silently program the wrong hardware variable. Power-save and CAM selectors are especially high risk because failures show as hangs, dropped traffic, or broken encryption.

## Test Signals

Build coverage for all rtl8723bs objects, suspend/resume and IPS/LPS smoke tests, association/disassociation with WPA/WPA2, C2H/H2C event logging, channel switching, and TX/RX traffic under rate-adaptation changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_intf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pg.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pg.h` declares efuse/EEPROM programming helpers and constants for parsing RTL8723B package data, MAC address, regulatory values, thermal meter, transmit power indexes, and Bluetooth coexistence efuse sections. The source was reviewed as a complete 69-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `EFUSE_ShadowMapUpdate`, `EFUSE_ShadowRead`, `EFUSE_ShadowWrite`, `Hal_EfuseParseIDCode`, `Hal_ReadPROMVersion`, `Hal_ReadPowerSavingMode`, `Hal_ReadTxPowerInfo8723B`, `Hal_ReadBoardType8723B`, `Hal_EfuseParseBTCoexistInfo`, and related `Hal_EfuseParse*` routines.

## Control Flow

During adapter bring-up, efuse content is loaded into a shadow map and parser helpers extract board and RF calibration values before PHY, MAC, power, and coexistence configuration use them.

## State and Persistence Behavior

The parsed values populate `eeprompriv`, HAL data, MAC address fields, per-rate power tables, channel plan, customer ID, and BT coexistence flags. The header itself does not persist data.

## Dependencies and Integration Points

Integrates with efuse access in `rtw_efuse.h`, chip configuration in `rtl8723b_hal.h`, and PHY power code in `hal_phy_cfg.h`. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Autoload failure paths must use sane defaults. Bad offset parsing corrupts transmit power limits, regulatory behavior, or MAC identity. BT coexistence fields can change RF scheduling behavior.

## Test Signals

Probe with valid and simulated autoload-fail efuse maps, verify MAC/channel plan/power table parsing, and run RF calibration plus BT coexistence smoke checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy.h` provides common PHY constants, RF path and RF type enums, register bit masks, and helper prototypes used by baseband/RF configuration code. The source was reviewed as a complete 73-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `enum rf_path`, `enum rf_type`, `MAX_RF_PATH`, `MAX_TX_COUNT`, `MAX_REGULATION_NUM`, `MAX_RFDEPENDCMD_CNT`, `MAX_POSTCMD_CNT`, and PHY helper declarations used by chip-specific PHY config files.

## Control Flow

No runtime flow is implemented here; it supplies vocabulary consumed by register programming routines that query and set BB/RF registers during initialization, channel changes, calibration, and power-index updates.

## State and Persistence Behavior

All state is external: RF path selection, per-rate power data, and channel/bandwidth configuration live in HAL data and hardware registers.

## Dependencies and Integration Points

Used by `hal_phy_cfg.h`, `rtl8723b_rf.h`, `rtw_rf.h`, and chip calibration/configuration implementation files. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

RF enum or limit mismatches can make loops skip paths or write beyond path-specific arrays. Constants must match the single-stream 2.4 GHz 8723B device.

## Test Signals

Compile-time include coverage, PHY init on real or emulated SDIO device, channel/bandwidth changes, and register trace comparison against known-good initialization tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_cfg.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_cfg.h` declares RTL8723B-specific PHY register access, MAC/BB/RF configuration, transmit-power calculation, channel switching, and bandwidth mode operations. The source was reviewed as a complete 63-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `PHY_QueryBBReg_8723B`, `PHY_SetBBReg_8723B`, `PHY_QueryRFReg_8723B`, `PHY_SetRFReg_8723B`, `PHY_BBConfig8723B`, `PHY_RFConfig8723B`, `PHY_MACConfig8723B`, `PHY_SetTxPowerIndex`, `PHY_GetTxPowerIndex`, `PHY_SetTxPowerLevel8723B`, `PHY_SwChnl8723B`, and `PHY_SetSwChnlBWMode8723B`.

## Control Flow

Initialization calls MAC, BB, and RF config routines; later MLME or regulatory changes call channel/bandwidth and power-index helpers that program BB/RF registers through masked read-modify-write accessors.

## State and Persistence Behavior

The persistent effects are hardware register values and HAL transmit-power tables derived from efuse, bandwidth, channel, and rate.

## Dependencies and Integration Points

Depends on `struct adapter`, `enum channel_width`, register bit helpers, efuse power info, and the 8723B PHY implementation. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Masked register writes are fragile; wrong masks or channel inputs can violate regulatory power limits or destabilize RF calibration. Loop and stall constants bound hardware polling behavior.

## Test Signals

PHY config success/failure checks, per-channel TX power validation, bandwidth transition tests, and BB/RF register trace diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_reg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_reg.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_reg.h` is a small register-include placeholder for the RTL8723B PHY layer, preserving the include boundary expected by the Realtek driver. The source was reviewed as a complete 17-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: Only the include guard `__INC_HAL8723BPHYREG_H__` is defined in this snapshot.

## Control Flow

There is no control flow. The file exists so code can include a stable PHY-register header even when register definitions are supplied elsewhere.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Included by PHY-related implementation files that expect a chip register namespace. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Low direct risk, but moving or deleting it can break include compatibility with copied vendor code.

## Test Signals

Compile coverage of all rtl8723bs PHY objects and include-order checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pwr_seq.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pwr_seq.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pwr_seq.h` encodes RTL8723B power transition tables as `WLAN_PWR_CFG` macro initializers for POFF, PDN, card-emulation, active, LPS, software LPS, suspend, and card-disabled states. The source was reviewed as a complete 226-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `RTL8723B_TRANS_CARDEMU_TO_ACT`, `RTL8723B_TRANS_ACT_TO_CARDEMU`, `RTL8723B_TRANS_CARDEMU_TO_SUS`, `RTL8723B_TRANS_SUS_TO_CARDEMU`, `RTL8723B_TRANS_CARDEMU_TO_PDN`, `RTL8723B_TRANS_ACT_TO_LPS`, `RTL8723B_TRANS_LPS_TO_ACT`, `RTL8723B_TRANS_ACT_TO_SWLPS`, `RTL8723B_TRANS_SWLPS_TO_ACT`, and `RTL8723B_TRANS_END` plus their step counts.

## Control Flow

The power-sequence executor iterates these tables, filters entries by chip cut/fab/interface, and performs register writes, polling, and delays to move the SDIO/USB/PCI-capable core between power states.

## State and Persistence Behavior

Persistent effects are MAC and SDIO local register values controlling LDOs, isolation, reset, suspend, GPIO wake, XTAL ownership, and RF shutdown.

## Dependencies and Integration Points

Depends on `HalPwrSeqCmd.h` for `WLAN_PWR_CFG`, command codes, masks, and delay constants; consumed by HAL power-on/off and IPS/LPS code. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

These are hardware sequencing contracts. Entry order, masks, and polling conditions must not drift from silicon documentation; errors can wedge the device, break wake, or leave power rails enabled.

## Test Signals

Cold probe, remove/reprobe, suspend/resume, IPS enter/leave, LPS enter/leave, wake-on-wireless scenarios, and register trace comparison to vendor sequence tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pwr_seq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_sdio.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_sdio.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_sdio.h` declares SDIO HAL helpers for queue-to-pipe mapping and transmit page accounting. The source was reviewed as a complete 18-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `ffaddr2deviceId`, `rtw_hal_sdio_max_txoqt_free_space`, `rtw_hal_sdio_query_tx_freepage`, `rtw_hal_sdio_update_tx_freepage`, `rtw_hal_set_sdio_tx_max_length`, and `rtw_hal_get_sdio_tx_max_length`.

## Control Flow

Transmit code queries free pages and queue limits before building SDIO transfer buffers, then updates accounting after reserving pages for a queue.

## State and Persistence Behavior

Uses SDIO device-object queue maps and HAL free-page counters; the header owns no storage.

## Dependencies and Integration Points

Integrates with `sdio_hal.h`, `sdio_ops.h`, `rtl8723b_xmit.h`, and the adapter's `dvobj_priv`. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Stale free-page accounting causes queue starvation or firmware buffer overrun. Queue index mapping must match firmware queue IDs.

## Test Signals

Saturated traffic across VO/VI/BE/BK queues, low-page conditions, and SDIO TX aggregation boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_sdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/ieee80211.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/ieee80211.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/ieee80211.h` collects driver-local IEEE 802.11 constants, WPA/RSN selectors, rates, information-element IDs, frame-layout helpers, hostapd private ioctl structures, channel descriptors, and IE parsing/building declarations. The source was reviewed as a complete 774-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct ieee_param`, `struct ieee_param_ex`, `struct sta_data`, `struct eapol`, `struct ieee80211_snap_hdr`, `struct rtw_ieee80211_channel`, `struct rtw_ieee80211_hdr`, `enum network_type`, WPA/RSN OUI arrays, rate masks, and helpers such as `rtw_get_ie`, `rtw_get_wpa_ie`, `rtw_parse_wpa_ie`, `rtw_parse_wpa2_ie`, `rtw_get_wps_ie`, `rtw_generate_ie`, and channel/rate conversion routines.

## Control Flow

Scan, join, AP, security, and cfg80211 paths use these definitions to parse beacon/probe/association IEs, determine network type and rates, build outgoing management IEs, and translate private hostapd control data.

## State and Persistence Behavior

No storage is owned, but the structures are copied through ioctl buffers, MLME network records, station records, and security setup paths.

## Dependencies and Integration Points

Includes Linux `ieee80211.h` and integrates with `wifi.h`, `rtw_mlme.h`, `rtw_security.h`, `ioctl_cfg80211.h`, and AP/hostapd support. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

IE parsing is length-sensitive and security-critical. Legacy private ioctl structures and flexible arrays must be bounded carefully. Rate and cipher constants must stay compatible with kernel cfg80211 expectations.

## Test Signals

Beacon/probe/association IE parser fuzzing, WPA/WPA2/WPS interoperability, hostapd private ioctl coverage, scan result parsing, and rateset validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/ieee80211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/ioctl_cfg80211.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/ioctl_cfg80211.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/ioctl_cfg80211.h` declares the cfg80211 integration layer that owns `wireless_dev` state, informs scan/connect/disconnect events, and bridges management-frame operations to the Linux wireless stack. The source was reviewed as a complete 58-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct rtw_wdev_priv`, `wiphy_to_adapter`, `wdev_to_ndev`, `rtw_wdev_alloc`, `rtw_wdev_free`, `rtw_wdev_unregister`, `rtw_cfg80211_init_wiphy`, `rtw_cfg80211_inform_bss`, `rtw_cfg80211_indicate_connect`, `rtw_cfg80211_indicate_disconnect`, `rtw_cfg80211_indicate_scan_done`, and management TX/RX wrapper macros.

## Control Flow

Driver MLME events call cfg80211 indication helpers; scan completion reports BSS entries, connection state changes update userspace, and action/management frames are passed to cfg80211 APIs.

## State and Persistence Behavior

`rtw_wdev_priv` stores the adapter backpointer, active scan request, monitor netdev, and power-management state around the kernel `wireless_dev`.

## Dependencies and Integration Points

Depends on Linux cfg80211/netdev types, `struct wlan_network`, `struct adapter`, and MLME event callbacks. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Incorrect scan-request lifetime or duplicate connect/disconnect indications can confuse cfg80211 and userspace. Kernel API wrapper macros must match the kernel version used by this source tree.

## Test Signals

iw scan/connect/disconnect flows, aborted scans, AP station association indications, remain-on-channel/action frame tests, and suspend with cfg80211 power management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/ioctl_cfg80211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_intf.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_intf.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_intf.h` declares OS-facing adapter lifecycle, netdev registration, driver thread startup/shutdown, timer cancellation, queue selection, IPS power transitions, and suspend/resume entry points. The source was reviewed as a complete 42-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `devobj_init`, `devobj_deinit`, `rtw_init_drv_sw`, `rtw_free_drv_sw`, `rtw_reset_drv_sw`, `rtw_dev_unload`, `rtw_start_drv_threads`, `rtw_stop_drv_threads`, `rtw_cancel_all_timer`, `rtw_init_netdev`, `rtw_unregister_netdevs`, `rtw_recv_select_queue`, `rtw_ips_pwr_up`, `rtw_ips_pwr_down`, `rtw_suspend_common`, `rtw_resume_common`, and `netdev_open`.

## Control Flow

Bus probe allocates the device object and adapter software, registers netdev/cfg80211 state, starts command/event/xmit threads, and unload/suspend paths reverse those steps while coordinating power transitions.

## State and Persistence Behavior

Manages the lifetime of `dvobj_priv`, `struct adapter`, netdev private state, driver timers, and worker threads, but the header itself is declarative.

## Dependencies and Integration Points

Tied to Linux netdev, SDIO bus probe/remove code, HAL init/deinit, command and transmit workers, and power-control helpers. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Lifecycle ordering is critical; netdev unregistration, timer cancellation, thread stop, and power-down must not race with RX/TX callbacks.

## Test Signals

Module load/unload loops, netdev open/stop, suspend/resume, IPS transitions, and race testing with traffic during removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_intf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_service.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_service.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_service.h` provides common OS abstraction macros and small service declarations used by Realtek code: status values, bit constants, queue initialization, netif receive/free wrappers, rounding helpers, buffer update/free, and a circular buffer type. The source was reviewed as a complete 109-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `_SUCCESS`, `_FAIL`, `RTW_RX_HANDLED`, `BIT0` through `BIT36`, `RTW_STATUS_CODE`, `_kfree`, `_rtw_netif_rx`, `_rtw_init_queue`, `rtw_free_netdev`, `rtw_buf_free`, `rtw_buf_update`, `struct rtw_cbuf`, `rtw_cbuf_full`, `rtw_cbuf_empty`, `rtw_cbuf_push`, `rtw_cbuf_pop`, and `rtw_cbuf_alloc`.

## Control Flow

Other modules use these wrappers for queue setup, buffer replacement, netdev RX submission, and small producer/consumer event queues.

## State and Persistence Behavior

`struct rtw_cbuf` stores ring-buffer read/write indices and caller-owned pointers; queues and buffers live in caller-owned driver structures.

## Dependencies and Integration Points

Includes `osdep_service_linux.h` for Linux-specific implementation glue and feeds nearly every rtl8723bs include file. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

The 64-bit-style `BIT32+` constants need correct type handling. Circular-buffer push/pop users must serialize access externally when shared across contexts.

## Test Signals

Compile on the target kernel, queue/cbuf unit coverage if available, C2H event queue stress, and netif RX smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_service_linux.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_service_linux.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_service_linux.h` maps Realtek OS abstraction to Linux kernel primitives including network queues, timers, sleep/delay, endian helpers, netdev private storage, and etherdev allocation. The source was reviewed as a complete 121-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `_set_timer`, `_cancel_timer_ex`, `rtw_netif_wake_queue`, `rtw_netif_start_queue`, `rtw_netif_stop_queue`, `rtw_signal_process`, `struct rtw_netdev_priv_indicator`, `rtw_netdev_priv`, `rtw_alloc_etherdev_with_old_priv`, and `rtw_alloc_etherdev`.

## Control Flow

Driver lifecycle and data paths call these inline wrappers whenever they need Linux netdev queue state, timers, or netdev-private adapter lookup.

## State and Persistence Behavior

Stores the adapter pointer in `netdev_priv` through `struct rtw_netdev_priv_indicator`; timer state is managed by Linux `timer_list` instances.

## Dependencies and Integration Points

Depends on Linux netdevice, timer, delay, list, endian, and signal APIs. It is included indirectly through `osdep_service.h`. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Kernel API compatibility matters because timer and netdev APIs change across releases. Netdev private layout must be consistent for every allocation path.

## Test Signals

Build against the intended kernel tree, netdev queue transition tests, timer cancellation during unload, and netdev private pointer validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/osdep_service_linux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8192c_recv.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8192c_recv.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8192c_recv.h` declares shared receive PHY-status processing structures inherited from the rtl8192c family for translating PHY status into signal metrics. The source was reviewed as a complete 37-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct phy_stat`, `struct phy_cck_rx_status`, `struct odm_phy_info`, and `rtl8192c_query_rx_phy_status`.

## Control Flow

RX descriptor handling passes raw PHY status, packet attributes, and station info into `rtl8192c_query_rx_phy_status` to update RSSI, signal quality, and per-station/link metrics.

## State and Persistence Behavior

Updates caller-owned `rx_pkt_attrib`, station state, and ODM/link statistics; no storage is declared here.

## Dependencies and Integration Points

Used by RTL8723B receive code and dynamic management code that still shares 8192C PHY-status decoding conventions. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

PHY status layouts are hardware-specific. Reusing rtl8192c helpers for rtl8723b requires field compatibility, especially CCK signal interpretation.

## Test Signals

RX PHY-status decode tests with CCK/OFDM/HT frames, RSSI sanity checks, and traffic tests across signal strengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8192c_recv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_cmd.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_cmd.h` defines RTL8723B firmware H2C command IDs, power-mode parameter structs, reserved-page layout, Bluetooth coexistence commands, and firmware media/status helpers. The source was reviewed as a complete 182-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `enum h2c_cmd_8723B`, `struct cmd_msg_parm`, `struct setpwrmode_parm`, `struct H2C_8723B_BTMP_OPER`, `struct RSVDPAGE_LOC`, `rtl8723b_set_FwPwrMode_cmd`, `rtl8723b_set_FwJoinBssRpt_cmd`, `rtl8723b_set_rssi_cmd`, `rtl8723b_Add_RateATid`, `rtl8723b_set_FwMediaStatusRpt_cmd`, and reserved-page download helpers.

## Control Flow

MLME, power-control, rate-adaptation, and BT coexistence paths package small H2C messages and send them through the HAL command mailbox to firmware.

## State and Persistence Behavior

Firmware-visible state includes power mode, join status, reserved-page addresses, RSSI/rate masks, media status, and BT MP operation state.

## Dependencies and Integration Points

Depends on `rtw_cmd.h`, `hal_intf.h`, power control state, firmware download code, and reserved-page beacon construction. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

H2C payload length and field layout must match firmware. Reserved-page offsets are easy to corrupt and can break PS-Poll, null data, or WoWLAN-like firmware behavior.

## Test Signals

Trace H2C bytes, connect/disconnect, LPS transitions, reserved-page download, rate mask updates, and BT coexistence command smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_dm.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_dm.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_dm.h` declares RTL8723B dynamic management hooks for initializing ODM, watchdog processing, low-power watchdog work, antenna selection, and dynamic transmit-power tracking. The source was reviewed as a complete 33-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `rtl8723b_init_dm_priv`, `rtl8723b_deinit_dm_priv`, `rtl8723b_InitHalDm`, `rtl8723b_HalDmWatchDog`, `rtl8723b_HalDmWatchDog_in_LPS`, `rtl8723b_hal_dm_in_lps`, `AntDivBeforeLink8723B`, and `odm_DIGbyRSSI_LPS`.

## Control Flow

After HAL initialization, ODM state is initialized; periodic watchdog and low-power watchdog paths adjust gain, antenna, and rate-related dynamic behavior based on link and signal state.

## State and Persistence Behavior

Updates HAL/ODM private state, antenna selection, DIG thresholds, and dynamic TX power settings kept in adapter/HAL structures.

## Dependencies and Integration Points

Integrates with PHY, HAL, MLME link state, power-control LPS paths, and station RSSI tracking. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Watchdog work can race with suspend, LPS, or disconnect. Bad RSSI/DIG decisions can reduce throughput or link stability.

## Test Signals

Link under changing RSSI, LPS watchdog exercise, antenna diversity before/after association, and watchdog during suspend/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_hal.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_hal.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_hal.h` is the central RTL8723B HAL header, defining firmware metadata, reserved-page constants, EFUSE sizes, HAL private data fields, chip init/deinit hooks, register access, interrupt control, C2H handlers, and BT firmware download declarations. The source was reviewed as a complete 243-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct rt_firmware`, `struct hal_com_data`, `struct hal_spec_t`, `rtl8723b_FirmwareDownload`, `rtl8723b_InitAntenna_Selection`, `rtl8723b_init_default_value`, `rtl8723b_InitBeaconParameters`, `rtl8723b_SetHalODMVar`, `SetHwReg8723B`, `GetHwReg8723B`, `rtl8723b_set_hal_ops`, `rtl8723bs_set_hal_ops`, `c2h_handler_8723b`, and EFUSE/reserved-page constants.

## Control Flow

Probe-time code allocates and fills HAL data, downloads firmware, initializes MAC/BB/RF/DM, sets SDIO-specific ops, and later services register operations, interrupts, and firmware C2H notifications.

## State and Persistence Behavior

Defines the main HAL state carrier: firmware version/signature, RF type/path, channel/bandwidth, antenna selection, efuse maps, transmit power tables, reserved-page offsets, interrupt masks, and BT coexistence fields.

## Dependencies and Integration Points

Includes or coordinates with `hal_intf.h`, `hal_phy_cfg.h`, `rtl8723b_cmd.h`, `rtl8723b_dm.h`, `rtl8723b_spec.h`, `rtw_efuse.h`, and SDIO HAL/ops. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

This is a high-blast-radius contract. Field layout changes affect many implementation files, and firmware/efuse size constants must match silicon and firmware images.

## Test Signals

Full driver probe, firmware download/version reporting, efuse parsing, interrupt enable/disable, C2H event handling, channel/rate/power tests, and unload/reload loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_hal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_recv.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_recv.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_recv.h` declares RTL8723B receive descriptor parsing, PHY status conversion, and RX buffer/frame handlers. The source was reviewed as a complete 95-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct rxreport_8723b`, `rtl8723b_query_rx_desc_status`, `rtl8723b_process_phy_info`, `rtl8723b_query_rx_phy_status`, `rtl8723bs_init_recv_priv`, `rtl8723bs_free_recv_priv`, `rtl8723bs_recv_hdl`, and `rtl8723bs_recv_tasklet`.

## Control Flow

SDIO RX code reads packets into buffers, parses 8723B RX descriptors into `rx_pkt_attrib`, optionally decodes PHY info, and dispatches completed frames to the common receive path/tasklet.

## State and Persistence Behavior

Updates receive buffer queues, frame attributes, per-station RSSI/link quality, and adapter receive counters.

## Dependencies and Integration Points

Depends on `rtw_recv.h`, `rtl8723b_xmit.h` descriptor bit macros, `rtl8192c_recv.h` PHY status helpers, and SDIO receive operations. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Descriptor bit offsets and buffer alignment are critical. Bad packet length, shift, or driver-info parsing can cause memory corruption or dropped frames.

## Test Signals

RX descriptor decode coverage, fragmented/aggregated frame receive, PHY status RSSI sanity, tasklet under load, and malformed descriptor rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_recv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_rf.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_rf.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_rf.h` declares RTL8723B RF front-end configuration entry points. The source was reviewed as a complete 17-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `PHY_RF6052_Config8723B` and `PHY_RF6052SetBandwidth8723B`.

## Control Flow

PHY initialization configures the RF6052 path; channel/bandwidth changes call the bandwidth helper to keep RF and BB settings aligned.

## State and Persistence Behavior

Persistent effects are RF register values and HAL bandwidth state.

## Dependencies and Integration Points

Used by `hal_phy_cfg.h` implementation and RF register access helpers. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

RF register programming must match the device path count and channel width; mistakes produce weak or absent RF output.

## Test Signals

RF init success, channel/bandwidth switches, throughput at 20/40 MHz where supported, and register trace comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_rf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_spec.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_spec.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_spec.h` defines RTL8723B register addresses, queue IDs, page sizes, interrupt masks, firmware command registers, security CAM layout, and SDIO local register constants. The source was reviewed as a complete 237-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `TX_TOTAL_PAGE_NUMBER_8723B`, queue page-boundary constants, `REG_*` aliases, `IMR_*` interrupt bits, `REG_HMEBOX_*`, `REG_HIMR0_8723B`, `REG_HISR0_8723B`, SDIO local offsets, and CAM/security register definitions.

## Control Flow

HAL, SDIO, transmit, receive, interrupt, firmware mailbox, and security code use these constants to read/write the correct MAC, BB, system, and SDIO local registers.

## State and Persistence Behavior

The header defines addresses only; state lives in hardware registers and firmware mailboxes.

## Dependencies and Integration Points

Consumed by almost all RTL8723B-specific `.c` files and descriptor/power/SDIO helpers. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Register aliases are silicon contracts. Incorrect constants can damage unrelated hardware state, mask interrupts, break firmware commands, or corrupt security CAM programming.

## Test Signals

Probe/interrupt smoke tests, H2C/C2H mailbox exercise, TX/RX queue operation, security association, and register dump comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_spec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_xmit.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_xmit.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_xmit.h` defines RTL8723B transmit and receive descriptor bit layouts, descriptor accessor macros, queue-select values, hardware rate IDs, and SDIO transmit entry points. The source was reviewed as a complete 421-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct txdesc_8723b`, `SET_TX_DESC_*_8723B`, `GET_RX_STATUS_DESC_*_8723B`, `DESC8723B_RATE*`, `RX_HAL_IS_CCK_RATE_8723B`, `rtl8723b_update_txdesc`, `rtl8723b_fill_fake_txdesc`, `rtl8723bs_hal_xmit`, `rtl8723bs_mgnt_xmit`, `rtl8723bs_hal_xmitframe_enqueue`, `rtl8723bs_xmit_buf_handler`, `BWMapping_8723B`, and `SCMapping_8723B`.

## Control Flow

Common xmit code fills `xmit_frame` attributes; the 8723B transmit path translates them into little-endian descriptors, queues SDIO buffers, and a transmit thread drains pending buffers to the device.

## State and Persistence Behavior

Descriptor memory, transmit buffers, SDIO TX sequence fields, aggregation metadata, retry/rate settings, queue selection, and ownership bits are mutable hardware-facing state.

## Dependencies and Integration Points

Depends on endian bit helpers, `rtw_xmit.h`, `rtw_recv.h`, SDIO TX ops, HAL rate/bandwidth state, and security settings. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Descriptor packing errors are high risk: own/length/offset/rate/security bits control DMA/FIFO behavior. Endianness and unaligned access must be correct on all supported architectures.

## Test Signals

TX descriptor byte-level checks, management/data/null frame transmission, aggregation and queue stress, encrypted traffic, and SDIO TX thread shutdown under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_xmit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ap.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ap.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ap.h` declares AP-mode helpers for beacon updates, station association/disassociation handling, client expiration, and AP initialization/free. The source was reviewed as a complete 39-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `init_mlme_ap_info`, `free_mlme_ap_info`, `rtw_indicate_sta_assoc_event`, `rtw_indicate_sta_disassoc_event`, `rtw_sta_flush`, `expire_timeout_chk`, `update_beacon`, `add_RATid`, and `rtw_ap_inform_ch_switch`.

## Control Flow

When operating as AP, MLME and station events call these helpers to maintain station state, refresh beacon IEs, notify cfg80211/hostapd, and update rate-adaptation entries.

## State and Persistence Behavior

Touches AP MLME state, station tables, beacon contents, TIM/WMM/ERP/HT IEs, and rate masks.

## Dependencies and Integration Points

Integrates with `sta_info.h`, `rtw_mlme.h`, `rtw_mlme_ext.h`, `ieee80211.h`, and cfg80211 AP notifications. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Beacon updates and station table changes must be serialized. Incorrect TIM or association indication behavior breaks power-save clients and userspace AP control.

## Test Signals

AP bring-up, client association/disassociation, beacon IE changes, inactivity expiration, channel switch indication, and multi-client traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_btcoex.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_btcoex.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_btcoex.h` declares Bluetooth coexistence hooks for binding adapter state, initialization, IPS/LPS notifications, scan/connect/media status notifications, and display/debug helpers. The source was reviewed as a complete 28-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `rtw_btcoex_Initialize`, `rtw_btcoex_PowerOnSetting`, `rtw_btcoex_InitHwConfig`, `rtw_btcoex_IpsNotify`, `rtw_btcoex_LpsNotify`, `rtw_btcoex_ScanNotify`, `rtw_btcoex_ConnectNotify`, `rtw_btcoex_MediaStatusNotify`, and `rtw_btcoex_HaltNotify`.

## Control Flow

Power, scan, association, and link-state paths notify the coexistence module so firmware/HAL policy can adjust RF sharing between Wi-Fi and Bluetooth.

## State and Persistence Behavior

Updates coexistence private state, firmware coexistence commands, and possibly antenna/RF scheduling settings.

## Dependencies and Integration Points

Used by HAL, MLME, power-control, and RTL8723B command code; depends on adapter/HAL coexistence data. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Notification order matters around power transitions. Missing notifications can cause poor Wi-Fi or BT throughput and connection instability.

## Test Signals

Wi-Fi scan/connect while BT active, IPS/LPS transitions with BT, coexistence debug output, and throughput coexistence smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_btcoex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_byteorder.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_byteorder.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_byteorder.h` keeps the Realtek byteorder include boundary for endian conversion helpers. The source was reviewed as a complete 16-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: Only the include guard is active in this snapshot; endian helper macros are supplied by Linux/common headers elsewhere.

## Control Flow

No runtime flow.

## State and Persistence Behavior

No state.

## Dependencies and Integration Points

Included by legacy Realtek code that expects a byteorder header. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Low direct risk; removing it can break vendor-code include compatibility.

## Test Signals

Compile coverage on little-endian and any cross-build targets represented by the source tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_cmd.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_cmd.h` defines the driver's asynchronous command/event framework, H2C command object layout, command thread state, C2H event headers, command codes, parameter structs, command submission APIs, and callback dispatch table types. The source was reviewed as a complete 715-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct cmd_obj`, `struct cmd_priv`, `struct evt_priv`, `struct submit_ctx`, `struct c2h_evt_hdr`, command parameter structs such as `joinbss_parm`, `disconnect_parm`, `sitesurvey_parm`, `setkey_parm`, `drvextra_cmd_parm`, `addBaReq_parm`, `RunInThread_param`, command IDs generated by `GEN_CMD_CODE`, `rtw_enqueue_cmd`, `rtw_dequeue_cmd`, `rtw_cmd_thread`, `rtw_sitesurvey_cmd`, `rtw_joinbss_cmd`, `rtw_disassoc_cmd`, `rtw_setopmode_cmd`, `rtw_lps_ctrl_wk_cmd`, `rtw_c2h_wk_cmd`, and command callbacks.

## Control Flow

Public request helpers allocate/fill command objects, enqueue them on `cmd_queue`, wake `rtw_cmd_thread`, invoke handlers in MLME/HAL context, and optionally complete submit contexts or callbacks after firmware/driver work finishes.

## State and Persistence Behavior

`cmd_priv` owns command queue, completions, thread termination state, allocated command buffers, and submit context. `evt_priv` owns C2H work and event ring buffering.

## Dependencies and Integration Points

Depends on Linux completions, `osdep_service.h` queues, MLME/security/RF structs, C2H handling, and RTL8723B firmware command wrappers. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Command lifetime and callback ownership are race-prone. Parameter structs are copied across thread/firmware boundaries, so size mismatches or missing completion handling can deadlock or leak.

## Test Signals

Command-thread lifecycle, scan/join/disconnect commands, key setting, LPS command work, C2H event queue stress, and unload while commands are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_eeprom.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_eeprom.h` defines EEPROM/efuse constants, customer IDs, channel-plan defaults, and the `eeprom_priv` structure that stores parsed autoload and calibration information. The source was reviewed as a complete 118-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct eeprom_priv`, `EEPROM_*` offsets/sizes, `EEPROM_Default_*` values, `enum RT_CUSTOMER_ID`, and helpers/fields for MAC address, channel plan, thermal meter, TX power, regulatory, and Bluetooth coexistence data.

## Control Flow

HAL probe reads efuse/EEPROM shadow data, populates `eeprom_priv`, and later PHY, regulatory, MAC-address, and coexistence code consume the parsed fields.

## State and Persistence Behavior

`eeprom_priv` is persistent per adapter for the device lifetime and is the software copy of nonvolatile board configuration.

## Dependencies and Integration Points

Connected to `hal_pg.h`, `rtw_efuse.h`, `rtl8723b_hal.h`, PHY power configuration, and regulatory/cfg80211 setup. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Defaults on autoload failure must be conservative. Wrong power/channel/customer parsing can violate regulatory rules or break board-specific RF behavior.

## Test Signals

Efuse read with real hardware, autoload-failure fallback, MAC/channel/power table validation, and customer/channel-plan variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_efuse.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_efuse.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_efuse.h` declares low-level efuse access constants and helpers for reading, writing, shadow-map synchronization, power switching, and packetized efuse layout handling. The source was reviewed as a complete 80-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `EFUSE_MAP_SIZE`, `EFUSE_MAX_SIZE`, `EFUSE_MAX_SECTION`, `Efuse_GetCurrentSize`, `rtw_efuse_access`, `rtw_efuse_map_read`, `rtw_efuse_map_write`, `rtw_BT_efuse_map_read`, `efuse_OneByteRead`, `efuse_OneByteWrite`, `Efuse_PowerSwitch`, and shadow read/write/update helpers.

## Control Flow

Probe and maintenance paths enable efuse power, read raw or logical maps, parse section/word enable packets, and copy results into EEPROM/HAL structures.

## State and Persistence Behavior

The physical efuse is nonvolatile hardware state; shadow maps and parsed fields live in adapter/HAL memory.

## Dependencies and Integration Points

Used by `hal_pg.h`, `rtw_eeprom.h`, HAL initialization, and BT coexistence efuse parsing. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Write paths can permanently alter efuse. Boundary checks must prevent reads past efuse size and handle malformed sections. Power switching around efuse access is hardware-sensitive.

## Test Signals

Read-only efuse dump, map read bounds tests, autoload failure simulation, and write-path tests only on expendable hardware or mocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_efuse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_event.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_event.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_event.h` defines event IDs, event buffer layout, and small event payload structs used for firmware/driver MLME notifications. The source was reviewed as a complete 96-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `enum rtw_event` style event IDs, `struct surveydone_event`, `struct joinbss_event`, `struct stassoc_event`, `struct stadel_event`, and event callback table declarations.

## Control Flow

Firmware or command handlers produce event buffers; MLME event callbacks decode them and update scan, join, station, and power-management state.

## State and Persistence Behavior

Event payloads transiently carry network and station information into MLME state machines.

## Dependencies and Integration Points

Integrated with `rtw_cmd.h`, `rtw_mlme.h`, `rtw_mlme_ext.h`, and C2H/event worker code. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Event sizes must match command/event dispatch tables. Bad event ordering can leave MLME state linked or scanning incorrectly.

## Test Signals

Survey done, join result, station association/deletion, C2H event dispatch, and malformed/short event handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ht.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ht.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ht.h` declares 802.11n HT capability state, AMPDU/AMSDU settings, bandwidth/channel offset helpers, and HT IE manipulation routines. The source was reviewed as a complete 83-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct ht_priv`, `struct ht_caps_element`, `rtw_set_ht_cap`, `rtw_ht_use_default_setting`, `rtw_restructure_ht_ie`, `rtw_update_ht_cap`, `rtw_issue_addbareq_cmd`, and bandwidth/short-GI related fields.

## Control Flow

During scan/join/AP setup, HT IEs are parsed or generated, adapter HT defaults are applied, and aggregation setup can issue ADDBA commands once a link supports HT.

## State and Persistence Behavior

`ht_priv` persists per adapter/station and records HT enablement, AMPDU density/factor, bandwidth mode, short GI, STBC/LDPC, and MCS capabilities.

## Dependencies and Integration Points

Used by `rtw_mlme.h`, `sta_info.h`, `rtw_recv.h`, `rtw_xmit.h`, and PHY bandwidth/rate-control code. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

HT capability negotiation affects descriptor bandwidth/rate bits and reorder buffering; mismatched IEs can break interoperability or aggregation.

## Test Signals

Join APs with/without HT, 20/40 MHz operation, ADDBA setup/teardown, short-GI rates, and interoperability with legacy B/G clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ht.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_io.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_io.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_io.h` defines the generic IO abstraction around `intf_hdl`, synchronous/asynchronous memory/register operations, and bus-specific IO operation callbacks. The source was reviewed as a complete 74-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct intf_hdl`, `struct _io_ops`, `rtw_read8`, `rtw_read16`, `rtw_read32`, `rtw_write8`, `rtw_write16`, `rtw_write32`, `rtw_read_mem`, `rtw_write_mem`, `rtw_write_port`, `rtw_read_port`, `rtw_init_io_priv`, and `register_intf_hdl`.

## Control Flow

HAL and data-path code call generic IO helpers; the interface handle dispatches to SDIO-specific operations from `sdio_ops.h`/`sdio_ops_linux.h`.

## State and Persistence Behavior

`intf_hdl` binds adapter/dvobj context to the selected IO callback table; hardware state changes through the actual bus operations.

## Dependencies and Integration Points

Connected to SDIO ops, HAL register access, transmit/receive port IO, and Linux SDIO bus glue. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Wrong callback registration or address translation affects every register and FIFO access. Error propagation must be observed by callers.

## Test Signals

Register read/write smoke, memory and port IO, SDIO error injection, and probe/unload IO handle lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ioctl_set.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ioctl_set.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ioctl_set.h` declares high-level setters used by ioctl/cfg80211 paths to request authentication, WEP keys, scans, infrastructure mode, SSID/BSSID joins, and current-rate queries. The source was reviewed as a complete 28-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `rtw_set_802_11_authentication_mode`, `rtw_set_802_11_add_wep`, `rtw_set_802_11_disassociate`, `rtw_set_802_11_bssid_list_scan`, `rtw_set_802_11_infrastructure_mode`, `rtw_set_802_11_ssid`, `rtw_set_802_11_connect`, `rtw_validate_bssid`, `rtw_validate_ssid`, `rtw_do_join`, and `rtw_get_cur_max_rate`.

## Control Flow

Userspace requests are validated, translated into MLME/security state changes, and often enqueue commands through `rtw_cmd.h` to scan, join, set keys, or disconnect.

## State and Persistence Behavior

Mutates MLME association targets, security mode/key material, requested infrastructure mode, and scan state.

## Dependencies and Integration Points

Depends on NDIS-style structs, `rtw_mlme.h`, `rtw_security.h`, `rtw_cmd.h`, and cfg80211/ioctl front ends. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Input validation is security-sensitive. SSID/BSSID length checks and WEP key bounds must be enforced before state mutation.

## Test Signals

Invalid SSID/BSSID inputs, WEP/WPA configuration, scan/connect/disconnect through iw/wpa_supplicant, and current-rate reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ioctl_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme.h` defines the core MLME state machine data: Wi-Fi state flags, scan/join timeouts, scanned-network queues, current network, roam state, timers, link detection, and many scan/join/connect/disconnect APIs. The source was reviewed as a complete 398-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct mlme_priv`, `struct sitesurvey_ctrl`, `struct rt_link_detect_t`, `struct hostapd_priv`, Wi-Fi state macros such as `WIFI_ASOC_STATE` and `WIFI_UNDER_LINKING`, `rtw_init_mlme_priv`, `rtw_free_mlme_priv`, `rtw_joinbss_event_callback`, `rtw_survey_event_callback`, `rtw_indicate_connect`, `rtw_indicate_disconnect`, `rtw_scan_abort`, `check_fwstate`, `set_fwstate`, `rtw_update_scanned_network`, `rtw_restruct_sec_ie`, and roaming helpers.

## Control Flow

Scan commands populate scanned queues, join selection chooses a target, join/connect events update firmware state and cfg80211, timers handle scan/join timeouts, and roaming helpers select better candidates when configured.

## State and Persistence Behavior

`mlme_priv` is long-lived adapter state containing locks, free/scanned BSS queues, current network, association SSID/BSSID, timers, WMM/HT/security IEs, scan deny flags, link metrics, and roam counters.

## Dependencies and Integration Points

Integrated with `rtw_cmd.h`, `rtw_event.h`, `rtw_security.h`, `rtw_ht.h`, `sta_info.h`, `ioctl_cfg80211.h`, and AP/hostapd support. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

MLME state flags are shared across timers, command thread, RX management handling, and cfg80211 notifications. Races can produce stuck scanning/linking states or double indications.

## Test Signals

Scan timeout, successful and failed join, roaming, disconnect during scan/join, AP/IBSS paths, security IE restructuring, and cfg80211 notification sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme_ext.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme_ext.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme_ext.h` defines the extended MLME engine: management-frame construction/parsing helpers, channel plans, command handlers, action frame handling, site-survey state, link timers, operation mode, and C2H event headers. The source was reviewed as a complete 717-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct mlme_ext_priv`, `struct mlme_ext_info`, `struct ss_res`, `struct rt_channel_plan`, `struct action_handler`, `struct xmit_frame`, management helpers such as `issue_beacon`, `issue_probereq`, `issue_auth`, `issue_assocreq`, `issue_deauth`, `issue_nulldata`, `send_beacon`, IE helpers such as `rtw_set_fixed_ie`, `rtw_set_ie`, `rtw_get_wpa2_cipher_suite`, handlers such as `join_cmd_hdl`, `disconnect_hdl`, `sitesurvey_cmd_hdl`, `setkey_hdl`, `mlme_evt_hdl`, and C2H event callback declarations.

## Control Flow

The command thread invokes extended MLME handlers to scan channels, join/create BSS, set keys, issue management frames, process received management frames, maintain beacon timing, and handle action/ADDBA/TDLS-style control.

## State and Persistence Behavior

Extended MLME state persists channel plan, current channel/bandwidth/offset, survey result counters, sequence numbers, authentication/association status, beacon timing, link timers, and management-frame retry/timeout state.

## Dependencies and Integration Points

Deeply connected to `wifi.h`, `ieee80211.h`, `rtw_cmd.h`, `rtw_mlme.h`, `rtw_xmit.h`, `rtw_recv.h`, `sta_info.h`, `rtw_security.h`, `rtw_rf.h`, and HAL channel/power APIs. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Large management-frame surface with many length-sensitive IEs. Channel plan and timer mistakes can break regulatory behavior, association, or scanning. Handler table sizes must match command payloads.

## Test Signals

Management-frame encode/decode, scan across channel plans, auth/assoc timeout/retry, AP beaconing, ADDBA/action handling, malformed management frames, and channel switch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_pwrctrl.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_pwrctrl.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_pwrctrl.h` defines power-control state for IPS/LPS, RF power states, power-deny reasons, task-alive accounting, RPWM/CPWM firmware handshake, timers, and public power-management APIs. The source was reviewed as a complete 254-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct pwrctrl_priv`, `enum rt_rf_power_state`, `enum ps_deny_reason`, `rtw_init_pwrctrl_priv`, `rtw_register_task_alive`, `rtw_register_tx_alive`, `rtw_register_cmd_alive`, `cpwm_int_hdl`, `ips_enter`, `ips_leave`, `LPS_Enter`, `LPS_Leave`, `rtw_set_ps_mode`, `rtw_set_rpwm`, `_rtw_pwr_wakeup`, `rtw_pm_set_ips`, `rtw_pm_set_lps`, `rtw_ps_deny`, and `rtw_ps_deny_cancel`.

## Control Flow

Traffic, command, and power-management paths register active tasks, deny or allow power save, enter/leave IPS or LPS, and use RPWM/CPWM plus timers to synchronize host/firmware power states.

## State and Persistence Behavior

`pwrctrl_priv` persists locks, requested/current power modes, firmware power state, RPWM/CPWM values, timers/work items, IPS/LPS mode settings, RF power state, deny masks, and adapter backpointer.

## Dependencies and Integration Points

Integrated with HAL power sequences, firmware H2C power commands, command/transmit alive tracking, MLME link state, and Linux PM suspend/resume. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Power state races are high risk. Incorrect deny-mask handling or RPWM/CPWM timeout behavior can sleep while traffic is active or keep the device awake indefinitely.

## Test Signals

IPS/LPS enter-leave loops, traffic-triggered LPS leave, suspend/resume, command/xmit alive registration balance, and power-state timer timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_pwrctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_qos.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_qos.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_qos.h` defines the small WMM/QoS private state carried by MLME code. The source was reviewed as a complete 19-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct qos_priv` with QoS option and AC parameter fields.

## Control Flow

MLME IE parsing and association setup populate QoS/WMM state; transmit queue selection and beacon/association IE generation consume it.

## State and Persistence Behavior

`qos_priv` persists per adapter within `mlme_priv`.

## Dependencies and Integration Points

Used by `rtw_mlme.h`, AP beacon code, and xmit queue selection. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Incorrect WMM state can map traffic to wrong access categories or advertise bad AP parameters.

## Test Signals

Association with WMM APs, AP beacon WMM IE generation, and traffic queue mapping checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_qos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_recv.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_recv.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_recv.h` defines the common receive pipeline structures: RX packet attributes, PHY info, receive buffers, receive frames, reorder control, per-station receive state, receive queues, and RX helper APIs. The source was reviewed as a complete 457-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct recv_reorder_ctrl`, `struct stainfo_rxcache`, `struct signal_stat`, `struct phy_info`, `struct rx_pkt_attrib`, `struct recv_stat`, `struct recv_priv`, `struct sta_recv_priv`, `struct recv_buf`, `struct recv_frame_hdr`, `union recv_frame`, `rtw_alloc_recvframe`, `rtw_free_recvframe`, `rtw_enqueue_recvframe`, `rtw_dequeue_recvbuf`, `rtw_reordering_ctrl_timeout_handler`, `_rtw_init_recv_priv`, `_rtw_free_recv_priv`, `rtw_recv_entry`, and `mgt_dispatcher`.

## Control Flow

Bus-specific receive code fills buffers and frames, descriptor parsing fills attributes, security/defrag/reorder logic handles the frame, management frames are dispatched to MLME, and data frames are delivered to netdev.

## State and Persistence Behavior

`recv_priv` owns free/pending frame queues, skb queues, receive buffer queues, tasklets, counters, and signal statistics. Station receive state owns reorder/defrag queues and sequence caches.

## Dependencies and Integration Points

Depends on `ieee80211.h`, `wifi.h`, `sta_info.h`, `rtw_security.h`, `rtl8723b_recv.h`, Linux skb/tasklet primitives, and netdev delivery. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

RX path is exposed to untrusted frames. Length, fragment, reorder, and decryption handling must be robust to malformed or replayed packets. Queue lifetime races matter during unload.

## Test Signals

RX fuzz/malformed frames, A-MPDU reorder timeout, fragmentation/defragmentation, software decrypt pending queue, management dispatch, and unload under RX load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_recv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_rf.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_rf.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_rf.h` defines RF/channel constants, regulatory classes, channel widths, extension channel offsets, and wireless mode masks for the 2.4 GHz RTL8723BS device. The source was reviewed as a complete 100-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct regulatory_class`, `enum channel_width`, `enum extchnl_offset`, `MAX_CHANNEL_NUM_2G`, `NUM_REGULATORYS`, `HAL_PRIME_CHNL_OFFSET_*`, wireless mode constants, and rate/channel helper declarations.

## Control Flow

MLME channel planning, PHY channel switching, cfg80211 regulatory setup, and rate/bandwidth negotiation use these constants.

## State and Persistence Behavior

No storage here; adapter/HAL/MLME structs store selected channel, bandwidth, offset, and regulatory plan.

## Dependencies and Integration Points

Used by `hal_phy_cfg.h`, `rtw_mlme_ext.h`, `rtw_cmd.h`, `rtw_xmit.h`, and cfg80211 regulatory code. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Regulatory and bandwidth constants must be correct for 2.4 GHz-only hardware. Channel width mismatch affects PHY register programming and advertised capabilities.

## Test Signals

Channel plan validation, cfg80211 regulatory domain smoke, 20/40 MHz association, and channel switch operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_rf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_security.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_security.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_security.h` defines security algorithms, authentication modes, key storage, PMKID cache, IV/PN helpers, MIC state, and software crypto entry points for WEP, TKIP, AES/CCMP, and BIP verification. The source was reviewed as a complete 272-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct security_priv`, `struct rt_pmkid_list`, `struct mic_data`, `security_type_str`, `GET_ENCRY_ALGO`, `SET_ICE_IV_LEN`, `GET_TKIP_PN`, `omac1_aes_128`, `rtw_secmicsetkey`, `rtw_secgetmic`, `rtw_aes_encrypt`, `rtw_tkip_encrypt`, `rtw_wep_encrypt`, `rtw_aes_decrypt`, `rtw_tkip_decrypt`, `rtw_wep_decrypt`, `rtw_BIP_verify`, and `rtw_handle_tkip_countermeasure`.

## Control Flow

Configuration paths populate auth/cipher/key state; TX/RX paths choose the active algorithm, build/parse IVs, perform software crypto where needed, verify MIC/BIP, and handle TKIP countermeasures.

## State and Persistence Behavior

`security_priv` persists keys, key IDs, cipher/auth modes, PMKID cache, WPS/association IEs, TKIP PN counters, ARC4 contexts, and join-time security BSS data.

## Dependencies and Integration Points

Includes Linux `crypto/arc4.h`; integrates with MLME, ioctl/cfg80211, command key setting, transmit descriptors, and receive decrypt paths. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Security code is high risk: key bounds, PN/replay handling, MIC failure behavior, and IE lengths must be correct. Legacy WEP/TKIP support expands attack surface.

## Test Signals

WEP/TKIP/CCMP association, software encrypt/decrypt known vectors, replay/MIC failure handling, PMKID cache behavior, malformed security IE parsing, and BIP verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_security.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_version.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_version.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_version.h` records the vendor driver version string used for diagnostics and build identification. The source was reviewed as a complete 3-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `DRIVERVERSION` set to `v4.3.5.5_12290.20140916_BTCOEX20140507-4E40`.

## Control Flow

No runtime flow beyond code that prints or exposes the version string.

## State and Persistence Behavior

Compile-time metadata only.

## Dependencies and Integration Points

May be included by module/version reporting code. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Low behavioral risk; stale version metadata can confuse support or compatibility triage.

## Test Signals

Build and module information/version output checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_wifi_regd.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_wifi_regd.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_wifi_regd.h` declares cfg80211 regulatory helper initialization for the Realtek driver. The source was reviewed as a complete 17-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `rtw_regd_init`.

## Control Flow

Wiphy setup calls `rtw_regd_init` to attach regulatory behavior based on adapter/eeprom channel plan before userspace uses cfg80211.

## State and Persistence Behavior

Regulatory state is stored in cfg80211/wiphy and adapter channel-plan fields.

## Dependencies and Integration Points

Depends on cfg80211 setup, `rtw_eeprom.h` channel plan, and `rtw_rf.h` channel constants. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Incorrect regulatory initialization can advertise disallowed channels or block valid ones.

## Test Signals

iw regulatory output, channel list validation by country/domain, and scan availability across channel plans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_wifi_regd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_xmit.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_xmit.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_xmit.h` defines the common transmit pipeline: packet attributes, transmit frame/buffer queues, per-station transmit state, management frame allocation, queue mapping, aggregation accounting, and xmit APIs. The source was reviewed as a complete 491-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct pkt_attrib`, `struct xmit_priv`, `struct xmit_frame`, `struct xmit_buf`, `struct hw_xmit`, `struct tx_servq`, `struct sta_xmit_priv`, `rtw_alloc_xmitframe`, `rtw_free_xmitframe`, `rtw_alloc_xmitbuf`, `rtw_free_xmitbuf`, `rtw_xmit_classifier`, `rtw_xmitframe_enqueue`, `rtw_xmit`, `rtw_make_wlanhdr`, `rtw_xmitframe_coalesce`, `rtw_mgntframe_coalesce`, `dump_xframe`, `rtw_count_tx_stats`, and management frame allocation helpers.

## Control Flow

Netdev TX and MLME management paths create frames, fill attributes and 802.11 headers, classify by station/TID/AC, enqueue service queues, coalesce payloads, fill chip descriptors, and submit through HAL/SDIO.

## State and Persistence Behavior

`xmit_priv` owns frame and buffer pools, pending queues, hardware queue state, semaphores/tasklets, counters, and aggregation limits. Per-station transmit state tracks TID queues and sequence numbers.

## Dependencies and Integration Points

Uses `wifi.h`, `sta_info.h`, `rtw_security.h`, `rtw_qos.h`, `rtl8723b_xmit.h`, netdev skbs, and HAL transmit callbacks. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

TX path mixes untrusted skb data, security headers, and hardware descriptors. Queue lifetime, sequence numbers, aggregation sizes, and key/IV lengths must be correct.

## Test Signals

Data and management TX, encrypted traffic, WMM queue mapping, aggregation limits, netdev stop/wake, xmit thread shutdown, and packet coalescing length checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_xmit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_hal.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_hal.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_hal.h` declares SDIO-specific HAL operation setup for RTL8723BS. The source was reviewed as a complete 14-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `rtl8723bs_set_hal_ops`.

## Control Flow

During bus-specific probe, SDIO code installs chip HAL callbacks so generic `rtw_hal_*` calls dispatch to RTL8723BS SDIO implementations.

## State and Persistence Behavior

Mutates adapter HAL operation tables during initialization.

## Dependencies and Integration Points

Integrates with `rtl8723b_hal.h`, `hal_intf.h`, SDIO bus probe, and `sdio_ops.h`. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

If operations are not installed before generic HAL calls, initialization or TX/RX paths will dereference missing callbacks.

## Test Signals

Probe path ordering, HAL init/deinit through SDIO, and all generic HAL operations after ops installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_hal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops.h` declares SDIO register, FIFO, and initialization operations at the Realtek IO abstraction layer. The source was reviewed as a complete 34-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `sdio_init`, `sdio_deinit`, `sdio_read8`, `sdio_read16`, `sdio_read32`, `sdio_write8`, `sdio_write16`, `sdio_write32`, `sdio_read_mem`, `sdio_write_mem`, `sdio_read_port`, `sdio_write_port`, `sdio_set_intf_ops`, and address translation helpers.

## Control Flow

IO abstraction and HAL code call SDIO operations to access MAC/SDIO local registers and data ports; initialization binds these operations into `intf_hdl`.

## State and Persistence Behavior

The operations affect hardware registers/FIFOs and SDIO device-object state, but this header owns no storage.

## Dependencies and Integration Points

Backed by Linux SDIO implementations in `sdio_ops_linux.h` and used by `rtw_io.h`, `hal_sdio.h`, transmit, receive, and interrupt handling. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Address translation and port lengths must match SDIO block size and hardware alignment. Error pointers must propagate to callers.

## Test Signals

SDIO register read/write, block/byte mode transfer, RX/TX port operations, interrupt path, and probe/remove loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops_linux.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops_linux.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops_linux.h` declares the Linux SDIO bus backend for CMD52/CMD53-style byte, word, dword, memory, and port access. The source was reviewed as a complete 30-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `sd_cmd52_read`, `sd_cmd52_write`, `sd_read8`, `sd_read32`, `sd_read`, `sd_write8`, `sd_write32`, `_sd_write`, `sd_write`, and `rtw_sdio_set_irq_thd`.

## Control Flow

Generic SDIO ops dispatch here to perform Linux kernel SDIO transfers and manage the SDIO interrupt thread handle.

## State and Persistence Behavior

Uses Linux `sdio_func`/interface state behind `intf_hdl` and stores the IRQ thread handle in `dvobj_priv`.

## Dependencies and Integration Points

Depends on Linux MMC/SDIO APIs, `struct intf_hdl`, and `struct dvobj_priv`. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Bus transfer failures, alignment, and host-claiming rules are critical. IRQ thread handle lifetime must track device removal.

## Test Signals

CMD52/CMD53 transfer tests, SDIO interrupt registration/removal, transfer error injection, and suspend/resume with IRQ enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops_linux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sta_info.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sta_info.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sta_info.h` defines station table state for associated peers, including ACLs, per-station transmit/receive state, security keys, QoS/HT state, timers, power-save queues, statistics, and station allocation APIs. The source was reviewed as a complete 330-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct rtw_wlan_acl_node`, `struct wlan_acl_pool`, `struct rssi_sta`, `struct stainfo_stats`, `struct sta_info`, `struct sta_priv`, packet counter macros, `_rtw_init_sta_priv`, `rtw_alloc_stainfo`, `rtw_free_stainfo`, `rtw_get_stainfo`, `rtw_init_bcmc_stainfo`, `rtw_get_bcmc_stainfo`, and `rtw_access_ctrl`.

## Control Flow

AP/client MLME paths allocate station entries on association or peer discovery, attach TX/RX/security/HT state, update counters during data flow, and free entries on disassociation or adapter teardown.

## State and Persistence Behavior

`sta_priv` owns the station pool, free queue, hash table, auth/asoc lists, sleep/wakeup queues, AID map, and ACL pool. Each `sta_info` owns per-peer keys, sequence/cache state, timers, and traffic stats.

## Dependencies and Integration Points

Connected to `rtw_xmit.h`, `rtw_recv.h`, `rtw_security.h`, `rtw_ht.h`, `rtw_mlme.h`, AP support, and rate adaptation. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Station lifetime races with RX/TX, timers, and AP events can cause use-after-free. Hash/AID/ACL bounds are fixed-size and must be respected.

## Test Signals

Multi-client AP association/disassociation, station lookup/free under traffic, BCMC station setup, ACL allow/deny, power-save queue handling, and timer cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sta_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/wifi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/wifi.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/wifi.h` defines 802.11 frame control constants, management/data frame structs, address and sequence helper macros, reason/status codes, IE IDs, WMM constants, and frame header manipulation helpers. The source was reviewed as a complete 464-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct rtw_ieee80211_hdr`, `struct rtw_ieee80211_hdr_3addr`, `struct wlan_bssid_ex`, `SetFrameSubType`, `GetFrameSubType`, `GetToDs`, `GetFrDs`, `GetAddr1Ptr`, `GetAddr2Ptr`, `GetAddr3Ptr`, `GetSequence`, `SetSeqNum`, `GetPrivacy`, `SetPrivacy`, frame type/subtype constants, and IE constants such as `_SSID_IE_`, `_SUPPORTEDRATES_IE_`, `_RSN_IE_`, and WMM definitions.

## Control Flow

Management and data TX/RX paths use these macros to construct headers, inspect received frames, parse addresses, manipulate sequence numbers, and recognize IEs/subtypes.

## State and Persistence Behavior

No global storage; helpers mutate or read caller-owned frame buffers and MLME network descriptors.

## Dependencies and Integration Points

Used throughout MLME, MLME extension, receive, transmit, AP, security, and IEEE80211 IE helper code. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Frame header helpers operate on raw packet bytes. Bounds must be enforced before use, and endian assumptions must match 802.11 little-endian fields.

## Test Signals

Management/data frame encode/decode, subtype/address extraction, privacy/sequence bit manipulation, malformed short frame handling, and AP/client interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/wifi.h -->
