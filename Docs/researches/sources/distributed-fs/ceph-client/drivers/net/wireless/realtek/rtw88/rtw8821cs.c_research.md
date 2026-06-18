<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821cs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821cs.c

## Purpose

This file is the SDIO bus binding module for Realtek RTW8821CS devices. It maps the SDIO vendor/device ID to `rtw8821c_hw_spec` and registers the shared `rtw88` SDIO probe, remove, shutdown, and power-management callbacks.

## Important APIs, Types, and Functions

- `rtw_8821cs_id_table[]`: SDIO ID table containing `SDIO_VENDOR_ID_REALTEK` and `SDIO_DEVICE_ID_REALTEK_RTW8821CS`, with `.driver_data = (kernel_ulong_t)&rtw8821c_hw_spec`.
- `MODULE_DEVICE_TABLE(sdio, rtw_8821cs_id_table)`: emits SDIO module aliases for autoload.
- `rtw_8821cs_driver`: `struct sdio_driver` with `.probe = rtw_sdio_probe`, `.remove = rtw_sdio_remove`, `.shutdown = rtw_sdio_shutdown`, `.id_table = rtw_8821cs_id_table`, and `.drv.pm = &rtw_sdio_pm_ops`.
- `module_sdio_driver(rtw_8821cs_driver)`: standard module registration wrapper.

## Control Flow

At module initialization, the SDIO driver is registered. The MMC/SDIO core matches Realtek RTW8821CS functions against `rtw_8821cs_id_table`, then calls `rtw_sdio_probe`. The shared SDIO probe consumes the chip spec from `driver_data` and initializes the common `rtw88` stack for 8821C: efuse parsing, firmware load, table application, queues, interrupts, and mac80211 registration.

On device removal or system shutdown, control goes to the shared SDIO helpers. Suspend/resume hooks are provided through `rtw_sdio_pm_ops` in the embedded `.drv` field.

## State and Persistence Behavior

The file stores only static ID and driver structures. It does not keep per-device runtime state. Runtime state lives in the SDIO function/device objects and common `rtw_dev` allocation created by `rtw_sdio_probe`. Persistent effects are module alias metadata and registration with the SDIO core.

## Dependencies and Integration Points

- Linux MMC/SDIO framework: `<linux/mmc/sdio_func.h>`, `<linux/mmc/sdio_ids.h>`, `struct sdio_driver`.
- `sdio.h`: shared `rtw88` SDIO bus implementation.
- `main.h` and `rtw8821c.h`: core types and chip spec declaration.
- `rtw8821c.c` and `rtw8821c_table.c`: chip behavior, firmware name, table pointers, and efuse parser used after probe.

## Risks

- Missing or incorrect SDIO ID prevents automatic binding on embedded/mobile platforms.
- Wrong chip-spec driver data would misconfigure firmware, efuse parsing, and hardware table loading.
- SDIO power sequencing and host quirks are delegated entirely to shared code; this binding has no local quirk table for boards that require special handling.
- Device-tree or ACPI integration issues may appear outside this file even when the SDIO ID is correct.

## Test Signals

- `modinfo` should expose an SDIO alias for the Realtek RTW8821CS device ID.
- Probe testing on an SDIO 8821CS board should reach `rtw_sdio_probe`, load the 8821C firmware, and register a wireless PHY.
- Runtime PM and system suspend/resume are important because SDIO devices are often power-gated by platform firmware.
- Basic association/throughput tests across 2.4 GHz and 5 GHz confirm the common 8821C chip path works through the SDIO transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821cs.c -->
