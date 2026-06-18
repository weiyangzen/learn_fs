<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lis3lv02d.h -->
# sources/distributed-fs/ceph-client/include/linux/lis3lv02d.h

## Purpose
This header defines platform data and board-level constants for ST LIS3LV02D-family accelerometer drivers. It lets board code describe axis wiring, interrupt routing, click/wakeup capabilities, power hooks, and optional block-read behavior without embedding those details in the transport driver.

## Important APIs, Types, and Functions
The central type is `struct lis3lv02d_platform_data`, which carries click flags, wakeup flags, IRQ routing, duration/threshold values, axis maps, default control register values, and platform callbacks such as setup, release, power-on, and power-off. Macros such as `LIS3_CLICK_SINGLE_X`, `LIS3_IRQ1_*`, `LIS3_WAKEUP_*`, `LIS3_HIPASS_*`, `LIS3_DEV_X`, and `LIS3_INV_DEV_X` encode hardware features and board orientation.

## Control Flow
There is no executable control flow in the header. Driver probe code consumes the platform-data structure, maps logical axes to device axes, configures interrupts and filter bits, and invokes board callbacks around device setup and power transitions.

## State and Persistence Behavior
The header owns no persistent state. State is provided by board data and becomes runtime driver configuration. Incorrect axis or IRQ constants persist only through compiled board files and can affect every boot.

## Dependencies and Integration Points
It integrates with LIS3 platform, SPI, or I2C accelerometer drivers and board files that still use platform data rather than firmware properties. It depends on integer bit fields matching the hardware register programming expected by the driver.

## Risks and Test Signals
Risks include inverted axes, missing wake events, wrong interrupt polarity, and broken suspend/resume power sequencing. Test signals are accelerometer input events, orientation sanity checks, click/wakeup interrupt delivery, and suspend/resume cycles with power callbacks enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lis3lv02d.h -->
