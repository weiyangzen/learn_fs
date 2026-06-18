<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_sysfs.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_sysfs.c

Purpose: this file exposes bnx2i per-host sysfs tuning attributes for send queue size and command-cell/history queue size. It is tied into `bnx2i_host_template.shost_groups` through `bnx2i_dev_groups`.

Important APIs, types, and functions: `bnx2i_dev_to_hba()` maps a sysfs `struct device` to the driver HBA via `class_to_shost()` and `iscsi_host_priv()`. `bnx2i_show_sq_info()` and `bnx2i_set_sq_info()` implement the `sq_size` attribute. `bnx2i_show_ccell_info()` and `bnx2i_set_ccell_info()` implement `num_ccell`. The exported symbol is the `const struct attribute_group *bnx2i_dev_groups[]` array referenced by the host template.

Control flow: reads format the current HBA values as hex. Writes parse a hex integer with `sscanf()`, reject changes while `hba->ofld_conns_active` is nonzero, and update the in-memory HBA configuration only when values are in range. SQ writes also require power-of-two sizing and choose maximums based on whether the device is a 57710-class adapter or a 570x-class adapter. CCELL writes enforce `BNX2I_CCELLS_MIN` to `BNX2I_CCELLS_MAX`.

State and persistence behavior: settings are runtime HBA fields, not persistent across driver reloads or device reprobe. They influence later connection/session queue resource sizing, but writes are blocked once offloaded connections are active. No lock is taken around the field updates; correctness relies on the active-connection guard and sysfs serialization.

Dependencies and integration points: this file depends on `bnx2i.h`, SCSI host class mapping, libiscsi host private storage, and constants from the bnx2i driver. It integrates with the main iSCSI file through `bnx2i_dev_groups`.

Risks: invalid input silently leaves the old value while still returning `count`, which can surprise management tools. Busy rejection returns `0` rather than `-EBUSY`, which is a weak sysfs signal. Lack of explicit locking is acceptable only if no connection setup can race between the busy check and assignment.

Test signals: verify attribute presence under the bnx2i host, hex read formatting, accepted and rejected SQ sizes, non-power-of-two rejection, 570x versus 57710 max enforcement, CCELL bounds, and busy write behavior with an active offloaded session.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_sysfs.c -->
