# sources/distributed-fs/ceph-client/drivers/phy/xilinx/Kconfig

## Purpose
Defines Xilinx PHY Kconfig entries. In this tree it contains `PHY_XILINX_ZYNQMP`, the tristate option for the ZynqMP High Speed Gigabit Transceiver driver.

## APIs, Flow, And State
`CONFIG_PHY_XILINX_ZYNQMP` depends on `ARCH_ZYNQMP || COMPILE_TEST` and selects `GENERIC_PHY`. Kconfig state persists in `.config`; there is no runtime state. When enabled, the symbol drives the Xilinx PHY Makefile to include `phy-zynqmp.o` as built-in or module.

## Dependencies And Integration
Integrates with the PHY subsystem Kconfig, `drivers/phy/xilinx/Makefile`, and generic PHY infrastructure. `COMPILE_TEST` extends build coverage to non-ZynqMP architectures.

## Risks And Tests
Only `GENERIC_PHY` is selected; runtime needs such as OF, clocks, PM, and MMIO are assumed through broader config. Test `n/m/y`, native ZynqMP and compile-test builds, and that enabling the symbol compiles `phy-zynqmp.o`.
