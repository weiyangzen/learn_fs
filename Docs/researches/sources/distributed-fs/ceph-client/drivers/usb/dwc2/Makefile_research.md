<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/Makefile

## Purpose
The DWC2 Makefile maps Kconfig selections to object composition. It builds the common `dwc2.o` module from core, interrupt, platform, role-switch, and parameter code, conditionally adds host, gadget, and debugfs components, and builds optional PCI glue as `dwc2_pci.o`.

## Important APIs, types, and functions
The significant build variables are `ccflags-$(CONFIG_USB_DWC2_DEBUG) += -DDEBUG`, `ccflags-$(CONFIG_USB_DWC2_VERBOSE) += -DVERBOSE_DEBUG`, `obj-$(CONFIG_USB_DWC2) += dwc2.o`, and `dwc2-y := core.o core_intr.o platform.o drd.o params.o`. Host mode adds `hcd.o`, `hcd_intr.o`, `hcd_queue.o`, and `hcd_ddma.o`. Peripheral or dual-role mode adds `gadget.o`. Any debugfs-enabled build adds `debugfs.o`. `USB_DWC2_PCI` builds `pci.o` into `dwc2_pci.o`.

## Control flow
Build composition follows Kconfig: common files are always part of the DWC2 core, host files are linked only when host or dual-role mode is enabled, gadget files only when peripheral or dual-role mode is enabled, and debugfs only when the kernel has debugfs support. The PCI glue module is separate from the core module.

## State and persistence behavior
The Makefile stores no runtime state, but it determines which runtime state fields and functions from `core.h` are backed by implementations versus inline stubs. It also controls whether debug statements are compiled and whether debugfs registration symbols resolve to real code.

## Dependencies and integration points
It connects Kconfig to the Linux kbuild system and to the source-level `IS_ENABLED` boundaries in `core.h`, `debug.h`, and implementation files. The note documents the historical move of the old `s3c-hsotg` peripheral driver into `gadget.c` and clarifies module names for host, peripheral, dual-role, PCI, and platform cases.

## Risks
Conditional object omissions can create unresolved symbols if header stubs and implementation boundaries diverge. The `ifneq ($(filter y,...))` checks add host/gadget objects only for built-in boolean mode symbols, so module/built-in combinations must match Kconfig constraints. Enabling `VERBOSE_DEBUG` can increase logging volume substantially.

## Test signals
Build tests should inspect object membership for host-only, gadget-only, dual-role, debugfs-disabled, debugfs-enabled, and PCI-enabled configurations. Link tests should verify that `dwc2.o`, `dwc2_platform.ko`, and `dwc2_pci.ko` resolve all mode-specific symbols in their supported configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/Makefile -->
