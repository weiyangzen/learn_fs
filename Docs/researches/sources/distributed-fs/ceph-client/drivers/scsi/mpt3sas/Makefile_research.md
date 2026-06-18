# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/Makefile

Purpose: defines how the kernel build system links the MPT3SAS driver object when `CONFIG_SCSI_MPT3SAS` is enabled.

Important APIs/types/functions: the makefile adds `mpt3sas.o` to `obj-$(CONFIG_SCSI_MPT3SAS)` and composes that aggregate object from `mpt3sas_base.o`, `mpt3sas_config.o`, `mpt3sas_scsih.o`, `mpt3sas_transport.o`, `mpt3sas_ctl.o`, `mpt3sas_trigger_diag.o`, `mpt3sas_warpdrive.o`, and `mpt3sas_debugfs.o`.

Control flow: when the Kconfig symbol is `y`, these objects are built into the kernel; when `m`, they are linked into the `mpt3sas` module; when unset, none are built. Link order places base/config/SCSI host logic before transport, control, diagnostics, WarpDrive, and debugfs support inside the aggregate object.

State and persistence: this file has no runtime state. Its persistent effect is build-system metadata that determines which translation units are included in the final driver artifact.

Dependencies and integration points: integrates with the kernel kbuild object aggregation convention. It must stay aligned with exported symbols and initialization ordering across the MPT3SAS source files and with `drivers/scsi/mpt3sas/Kconfig`.

Risks: omitting a source object can produce missing symbols or silently remove functionality such as SAS transport, ioctl/control support, trigger diagnostics, WarpDrive handling, or debugfs observability. Adding objects without Kconfig/resource dependencies can introduce unwanted build requirements.

Test signals: build `CONFIG_SCSI_MPT3SAS=y` and `=m`, verify `mpt3sas_transport.o` and `mpt3sas_debugfs.o` are included, run `modpost` for unresolved symbols, and smoke-test module load/unload when built as a module.
