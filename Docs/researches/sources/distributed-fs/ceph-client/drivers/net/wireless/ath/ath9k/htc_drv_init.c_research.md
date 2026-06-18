# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_init.c

## Purpose

`htc_drv_init.c` is the probe, initialization, and teardown lane for the ath9k HTC USB driver. It binds an `htc_target` supplied by the USB HIF layer to a mac80211 `ieee80211_hw`, creates the WMI control channel, connects all HTC service endpoints, adapts shared ath9k register access to firmware-mediated WMI commands, initializes the common ath9k hardware core, registers the device with mac80211, and unwinds all of that on disconnect or initialization failure.

## Important APIs, Types, and Functions

The externally visible lifecycle functions are `ath9k_htc_probe_device()`, `ath9k_htc_disconnect_device()`, `ath9k_htc_suspend()`, `ath9k_htc_resume()`, and the module `ath9k_htc_init()`/`ath9k_htc_exit()` pair. `ath9k_htc_probe_device()` allocates `ieee80211_hw`, waits for target readiness, initializes WMI, connects services, initializes hardware and mac80211 state, then stores `htc_handle->drv_priv`. `ath9k_htc_disconnect_device()` sets `AH_UNPLUGGED` on hot unplug, unregisters/deinitializes mac80211 and hardware state, stops WMI, deallocates USB URBs, destroys WMI, and frees `ieee80211_hw`.

The service setup path is `ath9k_init_htc_services()`, with `ath9k_htc_connect_svc()` as a small helper for beacon, CAB, UAPSD, management, and four data AC services. WMI control uses `ath9k_wmi_connect()`. Endpoint IDs are saved in `priv->wmi_cmd_ep`, `beacon_ep`, `cab_ep`, `uapsd_ep`, `mgmt_ep`, and `data_*_ep`.

The register access adapter is a key API boundary. `ath9k_regread()`, `ath9k_multi_regread()`, `ath9k_regwrite()`, `ath9k_regwrite_multi()`, `ath9k_reg_rmw()`, and their buffer/flush helpers implement `struct ath_ops` over WMI commands such as `WMI_REG_READ_CMDID`, `WMI_REG_WRITE_CMDID`, and `WMI_REG_RMW_CMDID`. `ath_usb_eeprom_read()` reads EEPROM through remote registers, and `ath9k_usb_bus_ops` exposes USB bus callbacks to the shared hardware layer.

`ath9k_init_priv()` allocates and wires `struct ath_hw`, assigns register ops, bus ops, power-save ops, tasklets, delayed work, timers, locks, cache-line sizing, `ath9k_hw_init()`, queue setup, common channels/rates/crypto, miscellaneous defaults, and BT coexistence init. `ath9k_set_hw_capab()` translates hardware capabilities into mac80211/wiphy flags, interface combinations, bands, antenna masks, headroom, and extended features. `ath9k_init_device()` layers firmware version validation, regulatory init, TX/RX init, `ieee80211_register_hw()`, debugfs, LEDs, rfkill polling, and hardware name reporting.

## Control Flow

The normal probe sequence is: allocate mac80211 hardware, populate `priv`, wait for firmware `target_wait`, create WMI, connect WMI and HTC data services, set HTC credits according to USB device family, run `htc_init()`, initialize `ath_hw`, validate firmware version, register regulatory and mac80211 state, initialize TX/RX queues, then publish `priv->initialized` after a memory barrier so WMI event processing can safely proceed.

Error paths are layered in reverse order. Failures after WMI setup stop/destroy WMI and deallocate USB URBs. Failures after hardware init call `ath9k_deinit_priv()`. Failures after mac80211 registration unregister hardware before cleaning RX/TX. This file deliberately avoids setting the global `htc_handle->drv_priv` until initialization succeeds.

Suspend only asks the hardware core to enter `ATH9K_PM_FULL_SLEEP`. Resume waits for target readiness again, reconnects HTC services with the stored device IDs, and reconfigures LEDs.

## State and Persistence Behavior

Persistent driver state is mostly in `struct ath9k_htc_priv`, `struct htc_target`, and `struct ath_hw`. This file initializes `priv->ah`, `priv->wmi`, endpoint IDs, firmware version fields, `fw_flags`, `initialized`, WMI register batching counters, queue maps, locks, work items, tasklets, timers, beacon slots, spectral defaults, and `common` fields such as `macaddr`, `bssidmask`, `debug_mask`, `btcoex_enabled`, and `op_flags`.

The register write and RMW batching paths are stateful: `mwrite_cnt` and `m_rmw_cnt` gate whether writes are buffered; `multi_write_idx` and `multi_rmw_idx` are protected by mutexes and flushed on explicit flush or full buffer. Firmware versions older than 1.4 set `HTC_FWFLAG_NO_RMW`, causing `ath9k_reg_rmw()` to fall back to read-modify-write on the host.

## Dependencies and Integration Points

This file depends on `htc.h` for the HTC/WMI/private driver contract, the USB HIF layer for `ath9k_hif_usb_init()`, URB cleanup, and target readiness, mac80211/cfg80211 for device allocation and registration, the shared ath9k hardware core for `ath9k_hw_init()` and capability handling, common ath helpers for regulatory/crypto/rates, and optional debugfs/LED/rfkill/PM features.

## Risks

Remote register access is latency-sensitive and can fail independently of the host call site; most failures are logged but not always propagated once initialization is past the command boundary. The multi-register read helper uses fixed arrays of 8 elements, so callers must respect that implicit limit. Initialization ordering is tight: WMI tasklets are only safe after `priv->initialized`, and RX endpoint processing is separately gated by RX initialization. Cleanup must remain paired with the exact stage reached, especially on USB hot-unplug where `AH_UNPLUGGED` suppresses some warnings in lower layers. Firmware version and RMW capability mismatches can change register semantics across the whole hardware core.

## Test Signals

Useful test signals include successful module load/unload, USB probe and hot-unplug while traffic is active, firmware-ready timeout behavior, firmware version rejection, WMI service endpoint assignment logs, register read/write failure logs, `ieee80211_register_hw()` success, interface creation after probe, suspend/resume service reconnection, and no leaked URBs/SKBs across failed initialization stages.
