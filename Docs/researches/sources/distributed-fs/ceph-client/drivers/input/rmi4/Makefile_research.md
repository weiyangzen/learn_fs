<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/Makefile

## Purpose
`drivers/input/rmi4/Makefile` maps RMI4 Kconfig symbols to object files and composes the `rmi_core` module.

## Important APIs, Types, and Functions
The main build target is `rmi_core.o`, made from `rmi_bus.o`, `rmi_driver.o`, and `rmi_f01.o`. Conditional additions include `rmi_2d_sensor.o` and function handlers `rmi_f03.o`, `rmi_f11.o`, `rmi_f12.o`, `rmi_f1a.o`, `rmi_f21.o`, `rmi_f30.o`, `rmi_f34.o`, `rmi_f34v7.o`, `rmi_f3a.o`, `rmi_f54.o`, and `rmi_f55.o`. Transport modules are `rmi_i2c.o`, `rmi_spi.o`, and `rmi_smbus.o`.

## Control Flow
The file is build-system logic only. It ensures F01 and bus/physical-driver code are always included with `RMI4_CORE`, while optional function and transport objects follow configuration.

## State and Persistence
Build outputs and module composition are determined by Kconfig state. There is no runtime state.

## Dependencies and Integration Points
The Makefile is paired with `Kconfig` and the Linux kbuild system. Function handler declarations in `rmi_driver.h` assume objects are only linked when their Kconfig symbols are enabled.

## Risks and Edge Cases
Missing an object from `rmi_core-y` would cause unresolved handler references or missing runtime support despite Kconfig visibility. F34 includes both base and v7 code as a pair.

## Test Signals
Run kernel builds with representative RMI4 configurations, especially `RMI4_CORE=m`, transports as modules, F11/F12 selecting `RMI4_2D_SENSOR`, and F34/F54 optional features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/Makefile -->
