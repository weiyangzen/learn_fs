# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723cs.c

## Purpose
This is the SDIO module glue for Realtek RTL8723CS-class devices in rtw88. In this tree, RTL8723CS binds to the RTL8703B chip implementation by passing `rtw8703b_hw_spec` as SDIO driver data.

## Important APIs, Types, And Functions
The `rtw_8723cs_id_table[]` matches `SDIO_VENDOR_ID_REALTEK` and `SDIO_DEVICE_ID_REALTEK_RTW8723CS`, with `.driver_data = &rtw8703b_hw_spec`. `rtw_8723cs_driver` wires the Linux SDIO driver callbacks to common rtw88 SDIO helpers: `rtw_sdio_probe`, `rtw_sdio_remove`, `rtw_sdio_shutdown`, and `rtw_sdio_pm_ops`. `module_sdio_driver()` registers the module.

## Control Flow
When the SDIO core matches the device ID, it invokes `rtw_sdio_probe()`. The common probe extracts the chip info from driver data and uses the 8703B operations and tables for firmware loading, power sequencing, MAC/PHY setup, and runtime operation. Removal, shutdown, and power management are delegated completely to common SDIO code.

## State And Persistence
This file stores only static module metadata and device ID data. Runtime device state is owned by the SDIO core and common rtw88 structures allocated by `rtw_sdio_probe()`. Persistent hardware behavior is defined by the referenced `rtw8703b_hw_spec`, not by this glue file.

## Dependencies And Integration Points
The file depends on Linux MMC/SDIO IDs and module APIs, `main.h`, `sdio.h`, and `rtw8703b.h`. It is an integration point between the kernel SDIO bus match table and the rtw88 RTL8703B chip implementation.

## Risks
The key risk is identity mismatch: this module labels the device as 8723CS while using 8703B hardware data, so the assumption that the SDIO 8723CS target is compatible with `rtw8703b_hw_spec` must remain valid. Missing or wrong SDIO IDs prevent autoload. Any common SDIO PM or shutdown bug affects this module because it has no local recovery logic.

## Test Signals
Signals include module autoload via the SDIO modalias, successful `rtw_sdio_probe()`, firmware load for the 8703B spec, interface creation, suspend/resume through `rtw_sdio_pm_ops`, and clean remove/shutdown on 8723CS hardware.
