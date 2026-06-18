# sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/Makefile

## Purpose
The Makefile binds `CONFIG_GP_PCI1XXXX` to the three source objects that implement the Microchip PCI1xxxx GP subsystem.

## Important APIs, Types, and Functions
The sole rule is `obj-$(CONFIG_GP_PCI1XXXX) := mchp_pci1xxxx_gp.o mchp_pci1xxxx_gpio.o mchp_pci1xxxx_otpe2p.o`.

## Control Flow
When enabled, Kbuild compiles and links the PCI parent, GPIO auxiliary driver, and OTP/EEPROM auxiliary driver.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates with Kbuild and matches the Kconfig symbol. The object order ensures all modules are part of the same enabled feature set.

## Risks
Any source file added to the subsystem must be listed here or it will not build. A mismatch with Kconfig would produce missing driver functionality.

## Test Signals
Signals are successful Kbuild compilation and presence of the PCI, GPIO auxiliary, and OTP/EEPROM auxiliary drivers in the resulting module or built-in image.
