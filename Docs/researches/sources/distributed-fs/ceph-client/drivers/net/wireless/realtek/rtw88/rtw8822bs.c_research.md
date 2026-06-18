# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822bs.c

## Purpose

`rtw8822bs.c` is the SDIO module binding for RTL8822BS. It matches the Realtek SDIO vendor/device ID, points the shared SDIO transport at `rtw8822b_hw_spec`, and registers a `struct sdio_driver` with standard rtw88 SDIO callbacks.

## Important APIs and Types

- `rtw_8822bs_id_table[]`: `struct sdio_device_id` table matching `SDIO_VENDOR_ID_REALTEK` and `SDIO_DEVICE_ID_REALTEK_RTW8822BS`.
- `MODULE_DEVICE_TABLE(sdio, rtw_8822bs_id_table)`: exposes SDIO modalias information.
- `rtw_8822bs_driver`: `struct sdio_driver` with:
  - `.probe = rtw_sdio_probe`
  - `.remove = rtw_sdio_remove`
  - `.shutdown = rtw_sdio_shutdown`
  - `.drv.pm = &rtw_sdio_pm_ops`
  - `.id_table = rtw_8822bs_id_table`
- `module_sdio_driver(rtw_8822bs_driver)` supplies module registration boilerplate.

## Control Flow and Integration

The MMC/SDIO core calls `rtw_sdio_probe()` when the function ID matches. The generic rtw88 SDIO path reads `.driver_data`, initializes the bus-specific I/O layer, then uses RTL8822B chip operations for firmware loading, efuse parsing, PHY/MAC setup, and mac80211 registration. Removal and shutdown are delegated to the same SDIO infrastructure.

## State and Persistence

This file contains only static ID and driver registration state. Runtime device state lives in the SDIO core function object, rtw88 transport structures, and RTL8822B chip/DM state. Power-management persistence is handled by `rtw_sdio_pm_ops`.

## Dependencies

It depends on Linux MMC/SDIO IDs, `main.h`, `sdio.h`, and `rtw8822b.h`. It is tightly coupled to the shared SDIO transport and to the correctness of the `rtw8822b_hw_spec` pointer stored in `.driver_data`.

## Risks

- Bad device ID coverage prevents autoload or matching for RTL8822BS modules.
- SDIO power sequencing and wake behavior are completely delegated; regressions in the shared transport will surface here without local mitigation.
- SDIO I/O can be sensitive to host-controller quirks; this binding has no quirk table of its own.

## Test Signals

- Build/modalias output should include the Realtek RTL8822BS SDIO ID.
- Hardware boot logs should show `rtw_sdio_probe()` selecting `rtw8822b_hw_spec`.
- Suspend/resume, card removal, and shutdown tests are the primary behavior signals for this module.
