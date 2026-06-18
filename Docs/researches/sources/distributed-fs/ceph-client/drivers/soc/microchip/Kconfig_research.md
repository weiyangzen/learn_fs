# sources/distributed-fs/ceph-client/drivers/soc/microchip/Kconfig

## Purpose
Defines build-time configuration for Microchip PolarFire SoC support drivers: GPIO IRQ muxing, the mailbox-backed system controller, and required syscon/MFD helpers.

## Important APIs, Types, And Functions
This is Kconfig only. It declares `POLARFIRE_SOC_IRQ_MUX`, `POLARFIRE_SOC_SYS_CTRL`, and `POLARFIRE_SOC_SYSCONS`.

## Control Flow
`POLARFIRE_SOC_IRQ_MUX` is a bool default-y option for `ARCH_MICROCHIP` that selects `REGMAP` and `REGMAP_MMIO`. `POLARFIRE_SOC_SYS_CTRL` is tristate and depends on `POLARFIRE_SOC_MAILBOX` and `MTD`. `POLARFIRE_SOC_SYSCONS` is a default-y bool for `ARCH_MICROCHIP` and selects `MFD_CORE`.

## State And Persistence
No runtime state. The selections determine which objects are compiled into the kernel or modules.

## Dependencies And Integration Points
Connects the Microchip SoC drivers to architecture selection, mailbox, MTD, regmap, MMIO regmap, and MFD infrastructure. It feeds the sibling Makefile object selection.

## Risks
Default-y syscon and IRQ mux options assume PolarFire SoC platforms need these early. Missing `POLARFIRE_SOC_MAILBOX` or `MTD` prevents the system controller driver from being built, which also blocks subdevice services that depend on it.

## Test Signals
Kconfig resolution should select `mpfs-irqmux.o`, `mpfs-control-scb.o`, `mpfs-mss-top-sysreg.o`, and optionally `mpfs-sys-controller.o` with the expected dependencies.
