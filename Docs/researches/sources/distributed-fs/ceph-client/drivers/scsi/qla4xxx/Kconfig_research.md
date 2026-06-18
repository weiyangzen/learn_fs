# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/Kconfig

Purpose: declares the `SCSI_QLA_ISCSI` tristate for QLogic ISP4XXX, ISP82XX, and ISP83XX iSCSI host adapters.

Important APIs/types: the option depends on `PCI`, `SCSI`, and `NET`, and selects `SCSI_ISCSI_ATTRS` plus `ISCSI_BOOT_SYSFS`. Help text identifies supported 40xx, 8022, and 8032 families.

Control flow: no runtime logic; it controls whether the qla4xxx module and its transport/sysfs integration are built.

State and persistence: build configuration only. It influences kernel/module availability and generated config state.

Dependencies and integration: ties this driver to PCI probing, SCSI midlayer, networking, iSCSI transport attributes, and iSCSI boot sysfs.

Risks: missing selected transport features would break attribute/boot paths; family help text must stay in sync with PCI IDs and source support. Test signals are Kconfig dependency resolution, module build under `m` and `y`, and boot sysfs/iSCSI attribute registration.
