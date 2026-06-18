# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_version.h

Purpose: centralizes QEDI driver version constants used for module metadata, UIO version reporting, QED slowpath driver identity, and probe logging.

Important APIs/types/functions: `QEDI_MODULE_VERSION` is `"8.37.0.20"`. Numeric components are `QEDI_DRIVER_MAJOR_VER`, `QEDI_DRIVER_MINOR_VER`, `QEDI_DRIVER_REV_VER`, and `QEDI_DRIVER_ENG_VER`, set to `8`, `37`, `0`, and `20`.

Control flow: this header has no executable flow. `qedi_main.c` passes the numeric version fields to `qedi_ops->common->slowpath_start()`, uses the string for `uio_info.version`, logs it at probe, and publishes it via `MODULE_VERSION()`.

State and persistence behavior: no runtime state is stored. Version values are compile-time constants and therefore persist only as built module metadata and driver-identification values passed to firmware/management interfaces.

Dependencies and integration points: consumed by QEDI source files through local includes. It should stay synchronized with any package, firmware compatibility, or management tooling expectations for this driver.

Risks and test signals: the string and numeric components can drift if one is updated without the other. Test signals are mostly build and metadata checks: verify module version output, UIO version field, QED slowpath parameters, and probe log formatting after any version bump.
