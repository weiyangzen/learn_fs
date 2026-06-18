# sources/distributed-fs/ceph-client/drivers/scsi/qedi/Kconfig

Purpose: this Kconfig entry exposes the QLogic FastLinQ 41000-series iSCSI offload initiator driver as `CONFIG_QEDI`.

Important definitions: `config QEDI` is a tristate named "QLogic QEDI 25/40/100Gb iSCSI Initiator Driver Support". It depends on `PCI`, `SCSI`, `UIO`, and `QED`, and selects `SCSI_ISCSI_ATTRS`, `QED_LL2`, `QED_OOO`, `QED_ISCSI`, and `ISCSI_BOOT_SYSFS`.

Control flow and state: Kconfig does not execute at runtime. Its selected symbols shape compilation and ensure the driver has SCSI/iSCSI transport attributes, QED iSCSI/LL2/offload support, and iSCSI boot sysfs support available.

Dependencies and integration points: the entry integrates the qedi module into the kernel SCSI driver menu and couples it to QED common hardware support. `UIO` is required because qedi exposes user-space networking/control plumbing elsewhere in the driver.

Risks: missing dependencies or selects would produce compile failures or runtime feature holes, especially around QED LL2/iSCSI callbacks and iSCSI boot sysfs. Over-selecting can force support code into kernels that otherwise would not include it.

Test signals: `make menuconfig` should show the option only when dependencies are available; builds for `m`, `y`, and unset should respectively build `qedi.ko`, built-in qedi objects, or no qedi objects. Compile tests should confirm selected QED and iSCSI transport symbols satisfy all included headers and external references.
