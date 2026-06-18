<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timb_gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/timb_gpio.h

## Purpose
defines platform data for the Timberdale GPIO block.

## Important APIs, Types, and Functions
The file is 26 lines and exports these visible symbol families: types/enums `timbgpio_platform_data`; macros/constants none; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Platform code provides GPIO count, base, and IRQ base information through `timbgpio_platform_data`; the GPIO driver consumes it during probe.

## State and Persistence Behavior
No runtime state is declared here; the values become driver initialization data.

## Dependencies and Integration Points
It integrates with the GPIO subsystem and Timberdale MFD/platform-device registration. Direct includes are none.

## Risks and Edge Cases
Incorrect base or IRQ numbering can collide with other GPIO controllers or misroute interrupts.

## Test Signals
Build/probe Timberdale GPIO, request lines, toggle GPIOs, and verify IRQ mapping for interrupt-capable pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timb_gpio.h -->
