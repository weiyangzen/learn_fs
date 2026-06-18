# sources/distributed-fs/ceph-client/drivers/ptp/Kconfig Research

## Purpose
`drivers/ptp/Kconfig` defines build-time configuration for the Linux PTP hardware clock framework and a collection of PHC drivers. It controls whether the common character-device framework is built and which hardware, virtual, PHY, FPGA, and platform clocks can register with it.

## Important APIs, Types, And Functions
The primary symbol is `PTP_1588_CLOCK`, a tristate depending on `NET` and `POSIX_TIMERS`, selecting `PPS` and `NET_PTP_CLASSIFY`. `PTP_1588_CLOCK_OPTIONAL` lets drivers optionally compile against dummy helpers when PTP is off or modular. This group covers symbols for `PTP_1588_CLOCK_DTE`, `PTP_1588_CLOCK_IDT82P33`, `PTP_1588_CLOCK_IDTCM`, `PTP_1588_CLOCK_FC3W`, and `PTP_DFL_TOD`, plus the surrounding choices that show how the PTP menu is organized.

## Control Flow
Kconfig has no runtime flow. At configuration time, dependencies restrict visibility and selection. At build time, these symbols drive the PTP Makefile and determine which objects are included as built-ins or modules.

## State And Persistence
The selected symbols persist in the kernel `.config`. The runtime effect is whether `/dev/ptp*` support and hardware-specific PHC drivers are available.

## Dependencies And Integration Points
The framework requires networking and POSIX timers. Specific drivers add dependencies: DTE requires Broadcom-related architecture or compile-test plus MMIO; IDT/ClockMatrix/FemtoClock drivers require I2C through their MFD/regmap stack and PTP; DFL TOD requires FPGA DFL and PTP. Other entries integrate with PHYLIB, PCI, ACPI, MTD, common clock, and virtual-machine timing features.

## Risks
Incorrect dependencies can produce link failures, unusable built-in/module combinations, or hidden drivers. `PTP_1588_CLOCK_OPTIONAL` is particularly important for drivers that can compile with dummy PTP helpers. Defaults such as `default ETHERNET` and architecture-specific defaults affect kernel footprint.

## Test Signals
Validation includes `olddefconfig` and randconfig coverage, module/built-in combinations for optional PTP users, dependency checks for I2C/MFD-based drivers, and build tests for `COMPILE_TEST` paths.
