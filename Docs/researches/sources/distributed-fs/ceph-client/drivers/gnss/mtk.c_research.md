# sources/distributed-fs/ceph-client/drivers/gnss/mtk.c

## Purpose
`mtk.c` is the Mediatek serial GNSS receiver driver. It uses the generic GNSS serial helper and supplies regulator-based power control for Mediatek-compatible modules.

## Important APIs, Types, and Functions
Private state is `struct mtk_data` with `vcc` and optional `vbackup` regulators. Power callbacks are `mtk_set_active()`, `mtk_set_standby()`, and `mtk_set_power()`, installed through `struct gnss_serial_ops`. Probe and remove are `mtk_probe()` and `mtk_remove()`.

## Control Flow
Probe allocates a generic serial GNSS device with room for `mtk_data`, sets GNSS type `GNSS_TYPE_MTK`, gets mandatory `vcc` and optional `vbackup`, enables backup power if present, and registers the serial GNSS device. The generic serial helper handles serdev open, baud rate, runtime PM, read insertion, and write_raw. Remove deregisters, disables backup power, and frees the serial wrapper.

## State and Persistence
Runtime state is the regulator handles and GNSS serial object. Backup regulator state persists only while the driver is bound. There is no stored configuration.

## Dependencies and Integration Points
The driver depends on serdev, regulator framework, GNSS serial helper, and OF compatible `globaltop,pa6h`.

## Risks and Test Signals
Power sequencing is minimal: `vcc` is toggled for active/standby and `vbackup` remains enabled for bind lifetime. Tests should cover missing optional backup regulator, regulator enable failure, runtime suspend/resume through `gnss_serial_pm_ops`, registration failure cleanup, and serial read/write through the generic helper.
