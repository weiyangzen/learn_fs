# sources/distributed-fs/ceph-client/drivers/scsi/iscsi_boot_sysfs.c

Purpose: provides a reusable sysfs library for exporting firmware/iBFT iSCSI boot information under firmware ksets, with target, ethernet, initiator, and ACPI table attribute groups.

Important APIs and functions: exported constructors include `iscsi_boot_create_kset()`, `iscsi_boot_create_host_kset()`, `iscsi_boot_create_target()`, `iscsi_boot_create_ethernet()`, `iscsi_boot_create_initiator()`, and `iscsi_boot_create_acpitbl()`. `iscsi_boot_destroy_kset()` tears down all child kobjects. `struct iscsi_boot_attr` binds sysfs attribute name/mode to an `ISCSI_BOOT_*` type and caller-provided `show` handler. Visibility callbacks delegate each attribute to driver-provided `is_visible()`.

Control flow: a caller creates a kset, then child kobjects through `iscsi_boot_create_kobj()`. That helper allocates `iscsi_boot_kobj`, initializes and adds the kobject, stores data/show/visibility/release callbacks, creates the group, emits `KOBJ_ADD`, and appends to `kobj_list`. Reads go through `iscsi_boot_show_attribute()`, require `CAP_SYS_ADMIN`, and call the provider’s `show(data, type, buf)`. Destroy walks the list safely, removes groups, drops kobject refs, unregisters the kset, and frees the wrapper.

State and persistence: sysfs objects persist while the module/driver keeps krefs; provider data is released via callback from `iscsi_boot_kobj_release()`. No durable state is written, but exported attributes expose boot configuration to user space.

Dependencies and integration: integrates with Linux kobjects/sysfs, `firmware_kobj`, iSCSI boot enum definitions, module exports, and drivers such as iBFT or NIC firmware providers.

Risks and test signals: access control matters because CHAP secrets are represented as readable attributes to admin-only callers. Error paths intentionally null `release` after group creation failure to avoid freeing data the caller still owns. Tests should cover hidden attributes, permission denial for non-admin, create/destroy cycles, failed allocation/group creation, and absence of use-after-free during concurrent sysfs reads.
