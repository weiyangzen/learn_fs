# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/Kconfig

Purpose: declares the kernel configuration interface for the MPT3SAS driver family. It exposes the main `SCSI_MPT3SAS` tristate option, tunable maximum scatter-gather entry counts for SAS 2.0 and SAS 3.0 devices, and a legacy `SCSI_MPT2SAS` compatibility symbol that selects the unified MPT3SAS driver.

Important APIs/types/functions: this is Kconfig metadata, not executable C. `config SCSI_MPT3SAS` depends on `PCI && SCSI` and selects `SCSI_SAS_ATTRS`, `RAID_ATTRS`, and `IRQ_POLL`. `config SCSI_MPT2SAS_MAX_SGE` and `config SCSI_MPT3SAS_MAX_SGE` are integer symbols with default `128` and range `16 256`. `config SCSI_MPT2SAS` is a dummy legacy tristate that defaults to `n`, depends on `PCI && SCSI`, and selects `SCSI_MPT3SAS`.

Control flow: build configuration flows from user or defconfig selection. Enabling `SCSI_MPT3SAS` makes the driver eligible for module or built-in compilation and automatically enables SAS transport attributes, RAID attributes, and IRQ polling support. The max-SGE symbols become available only when PCI, SCSI, and MPT3SAS are enabled. Selecting the legacy MPT2SAS option redirects users to the MPT3SAS implementation by selecting the unified driver.

State and persistence: selected Kconfig symbols persist in the kernel `.config` and influence compile-time constants and object inclusion. There is no runtime state in this file.

Dependencies and integration points: integrates with the kernel Kconfig system and the SCSI subsystem's build graph. The selected helper symbols are required by code that exposes SAS transport attributes, RAID class attributes, and IRQ polling behavior. The SGE options are consumed by the MPT3SAS driver sources at compile time to size I/O scatter-gather handling.

Risks: changing dependencies or selected symbols can silently break builds where the driver expects SAS, RAID, or IRQ polling infrastructure. Reducing max-SGE below workload expectations can increase I/O splitting, while increasing it can increase per-controller memory use. The legacy MPT2SAS symbol must remain a compatibility alias rather than building a separate driver.

Test signals: run Kconfig coverage for built-in, module, and disabled combinations; verify old configs containing `CONFIG_SCSI_MPT2SAS` still enable `CONFIG_SCSI_MPT3SAS`; validate boundary values `16`, `128`, and `256` for both max-SGE symbols; and compile with `PCI` or `SCSI` disabled to confirm options disappear cleanly.
