# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/Kconfig

Purpose: declares the `BE2ISCSI` kernel configuration option for the Emulex/Broadcom BladeEngine 2/OneConnect 10Gbps iSCSI offload driver.

Important APIs/types/functions: `config BE2ISCSI` is a tristate option labeled `Emulex 10Gbps iSCSI - BladeEngine 2`. It depends on `PCI`, `SCSI`, and `NET`, and selects `SCSI_ISCSI_ATTRS`, `ISCSI_BOOT_SYSFS`, and `IRQ_POLL`.

Control flow: there is no runtime flow. Kconfig decides whether the driver is built in, built as `be2iscsi.ko`, or omitted. Selected symbols ensure the transport attributes, iSCSI boot sysfs support, and IRQ polling infrastructure are present.

State and persistence: state is the generated kernel configuration only. The choice persists in `.config` and controls build outputs.

Dependencies and integration: integrates the driver into the SCSI configuration tree and expresses required subsystems for code in `be_main.c`, `be_cmds.c`, `be_mgmt.c`, and `be_iscsi.c`.

Risks and test signals: missing or stale selects would show up as unresolved symbols or disabled sysfs/transport features. Build tests should cover `BE2ISCSI=m`, `BE2ISCSI=y`, and dependency-disabled configurations such as `NET=n` or `PCI=n`.
