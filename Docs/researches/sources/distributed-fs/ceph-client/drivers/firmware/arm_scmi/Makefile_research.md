# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/Makefile

## Purpose
Composes SCMI bus, core driver, protocols, transports, vendor extensions, and power-control client objects for kbuild.

## APIs, Types, And Functions
`scmi-core.o` contains `bus.o`. `scmi-module.o` contains the main driver, notifications, optional quirks/raw mode, optional shmem/msg transport helpers, and protocol implementations (`base.o`, `clock.o`, `perf.o`, `power.o`, `reset.o`, `sensors.o`, `system.o`, `voltage.o`, `powercap.o`, `pinctrl.o`). `scmi_power_control.o` is built under `CONFIG_ARM_SCMI_POWER_CONTROL`.

## Control Flow
kbuild descends into `transports/` and `vendors/imx/` when `CONFIG_ARM_SCMI_PROTOCOL` is set, then links bus/core and module objects according to configuration.

## State, Persistence, And Dependencies
No runtime state is in the Makefile. Build outputs depend on SCMI Kconfig symbols, transport selections, and optional debug/quirk/raw features.

## Integration Points
This file determines which SCMI protocol implementations are present for client drivers and which transport support code is linked into the SCMI module.

## Risks And Test Signals
Risks are missing protocol objects, optional object mismatches with Kconfig, and build failures when transport helpers are selected in unusual combinations. `allmodconfig`, `allyesconfig`, and minimal transport-specific builds are the test signals.
