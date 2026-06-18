# sources/distributed-fs/ceph-client/include/linux/mmc/sdio_ids.h

## Purpose
`mmc/sdio_ids.h` is the central SDIO class/vendor/device ID registry used by SDIO function drivers for device matching. It defines standard SDIO function interface classes and known vendor/device identifiers.

## Important APIs, Types, And Functions
The file defines standard classes such as `SDIO_CLASS_NONE`, UART, Bluetooth type A/B, GPS, camera, PHS, WLAN, ATA, and Bluetooth AMP. Vendor/device IDs cover STE, Intel, C-Guys, TI, Atheros/Qualcomm, Broadcom/Cypress, Marvell, MediaTek, Microchip WILC, NXP, Realtek, Siano, RSI, and TI WL1251 devices. There are no functions or structs.

## Control Flow And State
There is no runtime state. SDIO drivers reference these constants in `struct sdio_device_id` tables, usually through `SDIO_DEVICE()` or `SDIO_DEVICE_CLASS()` from `sdio_func.h`. The bus match layer compares enumerated function class/vendor/device values against those tables during probe.

## Dependencies And Integration Points
The header is standalone and integrates with module device tables, SDIO bus matching, SDIO function drivers, udev/module autoloading metadata, and probe dispatch.

## Risks And Test Signals
Risks include duplicate or incorrect IDs, unsorted additions that increase maintenance cost, device IDs assigned to the wrong vendor, and missing IDs that prevent module autoload or probe. Test signals include modalias generation, SDIO device matching, driver autoload tests, probe on real hardware, and review against vendor specifications or existing driver tables.
