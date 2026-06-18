# sources/distributed-fs/ceph-client/drivers/ufs/host/Makefile

## Purpose
Maps UFS host Kconfig symbols to object files. It composes shared DesignWare glue with Synopsys G210 and AMD Versal2 drivers and builds each vendor platform module when its configuration symbol is enabled.

## Important APIs and build objects
The file uses standard kernel `obj-$(CONFIG_...) += ...` assignments. Notable composite entries are `SCSI_UFS_DWC_TC_PCI` and `SCSI_UFS_DWC_TC_PLATFORM`, which include `ufshcd-dwc.o` and `tc-dwc-g210.o`, and `SCSI_UFS_AMD_VERSAL2`, which includes `ufs-amd-versal2.o ufshcd-dwc.o`. Single-object entries include `cdns-pltfrm.o`, `ufs-exynos.o`, `ufs-hisi.o`, `ufs-mediatek.o`, and `ti-j721e-ufs.o`.

## Control flow and state
There is no runtime state. Build flow is entirely declarative: selected Kconfig symbols produce built-in or module objects, and object ordering matters for linked modules that need exported helper functions.

## Dependencies and integration points
The file is tightly coupled to Kconfig symbols and source filenames in the same directory. It also exposes the expectation that common DWC helper code can be linked into multiple driver modules.

## Risks and test signals
Risks include stale object names, missing shared objects for drivers that call helper symbols, and accidental multiple-definition issues when shared helpers are included in built-in combinations. Test signals are kernel builds for each symbol as `y` and `m`, plus `modpost` checks for exported Synopsys helper symbols and DWC helper references.
