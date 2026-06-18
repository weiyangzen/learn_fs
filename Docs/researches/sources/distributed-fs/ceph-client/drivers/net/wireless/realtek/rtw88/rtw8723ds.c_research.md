# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723ds.c

## Purpose
This is the SDIO module glue for Realtek RTL8723DS devices in rtw88. It matches both 1-antenna and 2-antenna SDIO IDs and delegates all behavior to common SDIO code using `rtw8723d_hw_spec`.

## Important APIs, Types, And Functions
`rtw_8723ds_id_table[]` has entries for `SDIO_DEVICE_ID_REALTEK_RTW8723DS_1ANT` and `SDIO_DEVICE_ID_REALTEK_RTW8723DS_2ANT`, both with `.driver_data = &rtw8723d_hw_spec`. `rtw_8723ds_driver` uses `rtw_sdio_probe`, `rtw_sdio_remove`, `rtw_sdio_shutdown`, and `rtw_sdio_pm_ops`, and is registered by `module_sdio_driver()`.

## Control Flow
On SDIO match, common `rtw_sdio_probe()` initializes the rtw88 device using the shared RTL8723D chip descriptor. Remove, shutdown, and PM callbacks are delegated to common SDIO helpers.

## State And Persistence
The file owns static ID/driver metadata only. Runtime device state, bus state, firmware state, and hardware programming are all owned by common rtw88 SDIO and RTL8723D chip code.

## Dependencies And Integration Points
It depends on Linux MMC/SDIO IDs, module support, `main.h`, `sdio.h`, and `rtw8723d.h`. It connects SDIO hardware IDs to the common rtw88 SDIO stack and RTL8723D chip implementation.

## Risks
The two antenna variants share the same chip descriptor, so antenna/RFE differences must be represented by efuse data and chip/coex code rather than this ID table. Missing IDs prevent autoload. SDIO PM and shutdown failures cannot be locally mitigated here.

## Test Signals
Signals include autoload for both 1ANT and 2ANT SDIO IDs, successful probe and firmware load, correct antenna/RFE behavior from efuse, suspend/resume via `rtw_sdio_pm_ops`, and clean removal/shutdown.
