# sources/distributed-fs/ceph-client/drivers/phy/xilinx/Makefile

## Purpose
Maps the Xilinx PHY Kconfig symbol to its kbuild object.

## APIs, Flow, And State
The single rule is `obj-$(CONFIG_PHY_XILINX_ZYNQMP) += phy-zynqmp.o`. kbuild expands it according to the symbol value, building the object into the kernel, as a module, or not at all. There is no runtime state.

## Dependencies And Integration
Integrates with `drivers/phy/xilinx/Kconfig`, the parent PHY Makefile, and `phy-zynqmp.c`.

## Risks And Tests
Future Xilinx drivers require matching Kconfig and Makefile updates; symbol/object drift would break builds or omit drivers. Test `CONFIG_PHY_XILINX_ZYNQMP=y`, `=m`, and disabled builds.
