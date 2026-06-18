# sources/distributed-fs/ceph-client/drivers/scsi/qedf/Makefile

## Purpose
This Makefile defines the QEDF driver object composition for the kernel build.

## Important APIs, types, and functions
`obj-$(CONFIG_QEDF) := qedf.o` builds the aggregate object when the Kconfig symbol is enabled. `qedf-y` lists the core objects: debug, main, I/O, FIP, attributes, ELS, SCSI firmware helpers, and FCoE firmware helpers. `qedf-$(CONFIG_DEBUG_FS)` conditionally adds debugfs support.

## Control flow
The build assembles one `qedf.o` from the listed objects. Debugfs code is included only when both QEDF is built and `CONFIG_DEBUG_FS` is enabled.

## State and persistence behavior
There is no runtime state. The file influences generated build artifacts and module contents.

## Dependencies and integration points
It connects the firmware-helper files in this work item, `drv_scsi_fw_funcs.o` and `drv_fcoe_fw_funcs.o`, into the broader QEDF module. It also makes debugfs support an optional build-time integration point.

## Risks and test signals
Risks are omitted objects causing unresolved symbols, stale object names after source moves, or debugfs-only code accidentally required by non-debug builds. Test signals are clean `CONFIG_QEDF=m/y` builds with and without `CONFIG_DEBUG_FS`.
