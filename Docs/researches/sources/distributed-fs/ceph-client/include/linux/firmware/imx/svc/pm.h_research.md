# sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/pm.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/pm.h` defines i.MX SCU Power Management service function IDs and constants. The source was read as a complete 85-line file for this report.

## Important APIs, Types, and Functions

It defines `enum imx_sc_pm_func` for system/partition/resource power modes, low-power requests, CPU resume address, clock rate/enable/parent, reset, boot/reboot, and CPU start. It also defines clock selector constants, power mode constants, and clock-parent constants.

## Control Flow

There are no functions in this header. SCU PM service shims use these function IDs and constants when building PM RPC messages to firmware.

## State and Persistence Behavior

The header owns no state. Firmware applies power, clock, reset, and boot state changes.

## Dependencies and Integration Points

It includes `sci.h` and integrates with i.MX SCFW PM service, clock drivers, power domain drivers, CPU boot/resume, and reset/reboot paths.

## Risks and Edge Cases

ID mismatches can power off or clock the wrong resource. Some clock constants intentionally alias per-resource meanings. Firmware policy may reject operations despite valid IDs.

## Test Signals

SCU PM RPC encoding tests, clock/power-domain integration tests, suspend/resume tests, reset/reboot tests, and firmware rejection-path tests.
