# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/Kconfig

Purpose: declares the kernel configuration option for the ATTO ExpressSAS RAID adapter driver.

Important APIs/types/functions: defines `config SCSI_ESAS2R` as a tristate option named "ATTO Technology's ExpressSAS RAID adapter driver". It depends on `PCI` and `SCSI` and describes support for ATTO ExpressSAS R6xx SAS/SATA RAID controllers.

Control flow: no runtime control flow. At configuration time, enabling this option as built-in or module controls whether the ESAS2R object list in the local Makefile is built and linked into the kernel or module tree.

State and persistence behavior: the only persistent state is the selected kernel configuration value in the build configuration. It does not create runtime state.

Dependencies and integration points: integrates with the SCSI driver Kconfig hierarchy and the local `Makefile` through `CONFIG_SCSI_ESAS2R`. The dependency gates prevent building this PCI SCSI host driver without the PCI bus and SCSI core.

Risks and test signals: risks are limited to dependency accuracy and discoverability. Test signals include `oldconfig/menuconfig` visibility with PCI+SCSI enabled, hidden/disabled behavior when either dependency is missing, module and built-in builds, and successful inclusion of `esas2r.o` when `CONFIG_SCSI_ESAS2R=m` or `y`.
