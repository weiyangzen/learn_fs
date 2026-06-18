# sources/distributed-fs/ceph-client/drivers/misc/keba/Makefile

## Purpose
The Makefile maps KEBA Kconfig options to object files.

## Important APIs, types, and functions
`obj-$(CONFIG_KEBA_CP500) += cp500.o` builds the CP500 PCI system FPGA driver. `obj-$(CONFIG_KEBA_LAN9252) += lan9252.o` builds the LAN9252 SPI configuration driver.

## Control flow
Kbuild evaluates the two `obj-*` assignments during the kernel build. Depending on each tristate value, the object is omitted, built into the kernel, or built into a module.

## State and persistence
No runtime state exists. The build artifact state is fully controlled by Kconfig.

## Dependencies and integration points
The file integrates the KEBA subdirectory with the surrounding `drivers/misc` Kbuild hierarchy and relies on Kconfig to enforce subsystem dependencies.

## Risks
The main risk is object/Kconfig drift: renaming a config option or source file without updating this file would silently drop driver builds.

## Test signals
Build tests should verify that enabling `CONFIG_KEBA_CP500=m` produces `cp500.ko`, enabling `CONFIG_KEBA_LAN9252=m` produces `lan9252.ko`, and built-in configurations link both objects without missing symbols.
