# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/Makefile

## Purpose
This Makefile defines the LiquidIO module composition for shared core code, PF driver code, and VF driver code.

## Important APIs, Types, And Functions
The build targets are `liquidio-core.o`, `liquidio.o`, and `liquidio_vf.o`. `liquidio-core-y` includes hardware-independent and chip-specific support such as `octeon_device.o`, `cn66xx_device.o`, `cn68xx_device.o`, `cn23xx_pf_device.o`, `cn23xx_vf_device.o`, mailbox, memory ops, DROQ, and NIC support. `liquidio-y` adds PF entry points and console/VF representor code; `liquidio_vf-y` adds the VF entry point.

## Control Flow
Kbuild first builds the selected core library object for `CONFIG_LIQUIDIO_CORE`, then links PF or VF front-end modules when `CONFIG_LIQUIDIO` or `CONFIG_LIQUIDIO_VF` are enabled.

## State And Persistence
No runtime state is defined here. It controls which object files are linked into each module.

## Dependencies And Integration Points
It is driven by Cavium Kconfig symbols. Both PF and VF support depend on the same core object, so shared chip setup code can be linked for either module.

## Risks
PF and VF chip-specific files are part of `liquidio-core.o`; exported symbols and function tables must avoid assuming that both PF and VF front ends are active. Build failures in any core object affect both PF and VF configurations.

## Test Signals
Build PF-only, VF-only, both, built-in, and module configurations. Confirm `liquidio` contains PF entry objects and `liquidio_vf` contains only VF entry objects plus shared core.
