# sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/Makefile

## Purpose
`drivers/net/ethernet/micrel/Makefile` maps Micrel Kconfig symbols to the object files built by Kbuild for each supported Micrel Ethernet driver variant.

## Important APIs, Types, And Functions
This is Kbuild metadata. It declares `obj-$(CONFIG_KS8842) += ks8842.o`, `obj-$(CONFIG_KS8851) += ks8851_common.o ks8851_spi.o`, `obj-$(CONFIG_KS8851_MLL) += ks8851_common.o ks8851_par.o`, and `obj-$(CONFIG_KSZ884X_PCI) += ksz884x.o`.

## Control Flow
Kbuild evaluates each `obj-*` line from the kernel configuration. SPI and parallel KS8851 variants both include `ks8851_common.o` plus their bus-specific object. PCI and KS8842 variants build standalone driver objects.

## State And Persistence
The Makefile has no runtime state. Its persistent effect is build output: objects are linked built-in or as modules according to the tristate value of the corresponding Kconfig symbol.

## Dependencies And Integration Points
It integrates directly with `micrel/Kconfig` and the source files in the Micrel Ethernet driver directory. The shared common object for KS8851 variants must stay compatible with both SPI and parallel front ends.

## Risks
If Kconfig symbols change without updating this Makefile, selected drivers will not build. Shared object inclusion must avoid duplicate symbol problems when multiple variants are built in the same configuration.

## Test Signals
Build targeted configs for each Micrel symbol as built-in and module. Verify `ks8851_common.o` is included for both KS8851 variants and that resulting module names match Kconfig help expectations, especially `ksz884x` for `KSZ884X_PCI`.
