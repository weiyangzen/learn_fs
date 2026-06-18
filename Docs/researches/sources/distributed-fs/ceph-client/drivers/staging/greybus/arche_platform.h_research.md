# sources/distributed-fs/ceph-client/drivers/staging/greybus/arche_platform.h

## Purpose

`arche_platform.h` shares Arche platform state definitions and APB child-driver entry points between the parent platform driver and APB control driver.

## Important APIs, Types, and Functions

It defines `enum arche_platform_state` with off, active, standby, and firmware-flashing states. It declares APB driver registration functions `arche_apb_init()`/`arche_apb_exit()` and operational functions `apb_ctrl_coldboot()`, `apb_ctrl_fw_flashing()`, `apb_ctrl_standby_boot()`, and `apb_ctrl_poweroff()`.

## Control Flow

The parent driver includes this header to register/unregister the APB platform driver and to invoke APB state changes through child device iteration. The APB driver includes it for the common enum and exported function prototypes.

## State and Persistence Behavior

No state is stored here. The enum values are the shared state vocabulary used by both driver data structures.

## Dependencies and Integration Points

The declarations require `struct device` to be available from included kernel headers in consumers. It is local to the Arche Greybus platform module.

## Risks and Edge Cases

The header does not include `<linux/device.h>`, relying on inclusion context. Enum changes must stay synchronized with sysfs string conversions in both C files.

## Test Signals

Build both Arche translation units with sparse/include-order checks and verify every enum state is represented in parent and child sysfs show/store code.
