## sources/distributed-fs/ceph-client/include/linux/can/platform/flexcan.h

**Purpose:** This header defines minimal platform data for FlexCAN devices that are not fully described by firmware.

**Important APIs/types/functions:** `struct flexcan_platform_data` carries `clock_frequency` and `clk_src`.

**Control flow, state, persistence:** There is no code. The driver consumes this data during probe to select clock source/frequency for bit timing. Hardware state persists in FlexCAN registers managed by the driver.

**Dependencies/integration:** Used by platform-board code and the FlexCAN driver, alongside device tree/ACPI paths.

**Risks and test signals:** Risks are stale board data, wrong clock source, and timing drift. Test signals include probe with platform data, configured bitrate verification, CAN loopback/traffic tests, and comparison with firmware-described boards.
