# sources/distributed-fs/ceph-client/drivers/scsi/qedi/Makefile

Purpose: this Makefile describes how the qedi kernel module is assembled from its source files.

Important definitions: `obj-$(CONFIG_QEDI) := qedi.o` creates the driver object when Kconfig enables it. `qedi-y` links `qedi_main.o`, `qedi_iscsi.o`, `qedi_fw.o`, `qedi_sysfs.o`, `qedi_dbg.o`, and `qedi_fw_api.o`. `qedi-$(CONFIG_DEBUG_FS)` conditionally adds `qedi_debugfs.o`.

Control flow and state: there is no runtime flow, but the object list determines which subsystems are always present and which are debugfs-gated. The unconditional objects provide PCI/lifecycle, iSCSI transport integration, firmware command/CQE handling, sysfs, logging, and firmware task-context builders.

Dependencies and integration points: the Makefile aligns with `Kconfig` and Linux kbuild conventions. It expects symbols declared in `qedi_gbl.h` to resolve across the listed objects and only includes debugfs file operations when `CONFIG_DEBUG_FS` is set.

Risks: omitting an object produces unresolved symbols or missing callbacks; adding `qedi_debugfs.o` unconditionally would break builds without debugfs support. The build list also means any new qedi source file must be explicitly added here.

Test signals: compile qedi with `CONFIG_QEDI=m/y` and `CONFIG_DEBUG_FS=y/n`; check that `qedi_debugfs.o` is present only when expected and that no unresolved symbols remain.
