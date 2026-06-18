<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thermal/Kconfig

## Purpose

`drivers/thermal/Kconfig` defines the generic Linux thermal subsystem options, default governor selection, cooling-device support, optional diagnostics, and platform thermal driver choices. In this work item it is especially relevant for `AIROHA_THERMAL` and `AMLOGIC_THERMAL`.

## Important APIs, Types, and Functions

The top-level `THERMAL` menuconfig enables thermal zones, trip points, and cooling devices. Options include netlink, statistics, debugfs, emergency poweroff delay, hwmon exposure, device-tree helpers, emulation, governors (`fair_share`, `step_wise`, `bang_bang`, `user_space`, `power_allocator`), CPU/devfreq/PCIe cooling, and many platform drivers.

`AIROHA_THERMAL` is a tristate depending on `ARCH_AIROHA || COMPILE_TEST`, `MFD_SYSCON`, and `OF`. `AMLOGIC_THERMAL` is a tristate defaulting to `ARCH_MESON` and depending on `OF && ARCH_MESON`. The file also includes submenus for Mediatek, Intel, Broadcom, TI, Samsung, ST, Renesas, Tegra, and Qualcomm thermal drivers.

## Control Flow

Kconfig selection controls which thermal core components and platform drivers Kbuild compiles. Selecting a default governor selects the corresponding governor implementation. Enabling OF helpers allows platform drivers to register thermal zones from device tree. Platform symbols map to object files in `drivers/thermal/Makefile`.

## State and Persistence Behavior

Kconfig has no runtime state but determines compiled capabilities and defaults. Runtime thermal state is owned by the thermal core and platform drivers selected here.

## Dependencies and Integration Points

The file integrates the thermal subsystem with networking, hwmon, debugfs, OF, energy model, cpufreq, cpuidle, devfreq, PCIe, MFD/syscon, IIO, architecture symbols, and many platform subdirectories. It feeds directly into the Makefile's `obj-$(CONFIG_...)` selections.

## Risks and Edge Cases

Dependency choices can hide drivers from compile testing or accidentally prevent module builds on relevant platforms. `AMLOGIC_THERMAL` depends directly on `ARCH_MESON`, unlike many drivers that allow `COMPILE_TEST`, reducing broader build coverage. Emulation and emergency poweroff settings are powerful and risky on production systems. Default governor selection must ensure exactly one default and select required governor code.

## Test Signals

Config tests should validate default governor exclusivity, build matrix coverage for `THERMAL=y/m`, `AIROHA_THERMAL`, `AMLOGIC_THERMAL`, OF/hwmon/debugfs combinations, disabled dependency visibility, and generated Makefile object inclusion for selected platform symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/Kconfig -->
