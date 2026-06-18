# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/Makefile

Purpose: builds the qla4xxx iSCSI host adapter driver object list.

Important APIs/types: `qla4xxx-y` aggregates OS glue, init, mailbox, IOCB, ISR, NX/8xxx support, NVRAM, debug, attributes, BSG, and 83xx support objects. `obj-$(CONFIG_SCSI_QLA_ISCSI)` emits `qla4xxx.o`.

Control flow: no runtime flow; object ordering controls linked driver composition.

State and persistence: build artifact state only.

Dependencies and integration: integrates all qla4xxx implementation files behind the Kconfig symbol. The inclusion of `ql4_attr.o`, `ql4_bsg.o`, and `ql4_83xx.o` makes sysfs, BSG vendor commands, and 83xx reset paths part of every qla4xxx build.

Risks: omitting an object causes unresolved symbols or missing runtime features; adding chip-specific files unconditionally can expose compile dependencies across adapter families. Test signals are clean module build, modpost, and probe-time availability of sysfs/BSG/83xx ops.
