# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_sysfs.c

Purpose: provides QEDI SCSI-host sysfs attributes for link state and link speed. It is intentionally small and is wired into `qedi_host_template.shost_groups` through `qedi_shost_groups`.

Important APIs/types/functions: `qedi_dev_to_hba()` converts a sysfs `struct device` to `struct Scsi_Host` with `class_to_shost()` and then to `struct qedi_ctx` with `iscsi_host_priv()`. `port_state_show()` reports `Online` when `qedi->link_state` is `QEDI_LINK_UP`, otherwise `Linkdown`. `speed_show()` calls `qedi_ops->common->get_link()` and prints `if_link.speed / 1000` as Gbit. `DEVICE_ATTR_RO(port_state)` and `DEVICE_ATTR_RO(speed)` define read-only attributes. `qedi_shost_attr_group` and exported `qedi_shost_groups[]` package the attributes for SCSI host registration.

Control flow: after the QEDI host is registered, SCSI core creates the shost attribute group. A sysfs read of `port_state` uses the cached atomic link state that `qedi_link_update()` maintains in `qedi_main.c`. A sysfs read of `speed` queries QED common ops synchronously for current link output and formats speed. There are no write paths, allocation paths, or long-lived state transitions in this file.

State and persistence behavior: no state is stored in this file. It observes `qedi->link_state`, `qedi->cdev`, and QED link output. Output is transient and reflects current runtime link state; it is not persisted.

Dependencies and integration points: includes `qedi.h`, `qedi_gbl.h`, `qedi_iscsi.h`, and `qedi_dbg.h`. The group is referenced from `qedi_host_template` in `qedi_iscsi.c`. The speed attribute depends on global `qedi_ops` and a live QED common device.

Risks and test signals: `speed_show()` assumes `qedi_ops`, `qedi_ops->common`, and `qedi->cdev` are valid while sysfs reads are possible; remove ordering through `iscsi_host_remove()` should prevent use after teardown. `sprintf()` is used instead of `sysfs_emit()`, matching older style but worth modernizing if touching this area. Test signals should read both attributes with link up/down, during remove stress, after recovery, and with firmware returning zero or unusual link speeds.
