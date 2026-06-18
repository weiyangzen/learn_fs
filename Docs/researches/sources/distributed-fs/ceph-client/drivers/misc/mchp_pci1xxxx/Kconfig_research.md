# sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_GP_PCI1XXXX`, the Microchip PCI1xxxx PCIe GPIO expander plus OTP/EEPROM manager driver.

## Important APIs, Types, and Functions
The symbol is `GP_PCI1XXXX`, tristate. It depends on `PCI`, `GPIOLIB`, and `NVMEM_SYSFS`, and selects `GPIOLIB_IRQCHIP` and `AUXILIARY_BUS`.

## Control Flow
Selecting the symbol builds the PCI parent driver and both auxiliary child drivers for GPIO and OTP/EEPROM support. The help text describes PCI1xxxx as a PCIe Gen3 switch endpoint exposing GPIO and OTP/EEPROM registers.

## State and Persistence
No runtime state is defined here; it controls build-time inclusion.

## Dependencies and Integration Points
Integrates the subsystem with the kernel configuration system and guarantees required GPIO IRQ and auxiliary bus infrastructure.

## Risks
`NVMEM_SYSFS` exposes EEPROM/OTP access through sysfs once the runtime driver registers nvmem devices. Disabling any dependency prevents the subsystem from building.

## Test Signals
Signals are correct Kconfig dependency resolution, module or built-in build of all three objects, and availability of auxiliary bus and GPIO IRQ helpers when enabled.
