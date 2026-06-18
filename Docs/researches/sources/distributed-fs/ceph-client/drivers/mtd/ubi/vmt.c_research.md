# sources/distributed-fs/ceph-client/drivers/mtd/ubi/vmt.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/vmt.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/vmt.c

Purpose: this file implements UBI volume management after a device is attached: create, remove, resize, rename, add existing volumes to the device model, free volumes on detach, expose per-volume sysfs attributes, and self-check volume state against the volume table.

Important APIs, types, and functions: main entry points are `ubi_create_volume()`, `ubi_remove_volume()`, `ubi_resize_volume()`, `ubi_rename_volumes()`, `ubi_add_volume()`, and `ubi_free_volume()`. Support code includes `vol_attribute_show()`, `vol_release()`, `find_volume_fwnode()`, `self_check_volume()`, and `self_check_volumes()`. Volume devices expose attributes such as `reserved_ebs`, `type`, `name`, `corrupted`, `alignment`, `usable_eb_size`, `data_bytes`, and `upd_marker`.

Control flow: creation validates available IDs/names under `volumes_lock`, computes usable LEB size and reserved PEBs, reserves accounting, flushes old erase work for that volume ID, creates an EBA table, initializes dynamic/static size fields, publishes the volume in `ubi->volumes[]`, registers cdev/device nodes, writes the volume table record, sends `UBI_VOLUME_ADDED`, and self-checks. Removal requires exclusive open, marks the volume dead to block new refs, sends shutdown notification, clears the volume-table record unless suppressed, unmaps all LEBs, deletes device nodes, returns PEB accounting, updates bad-block reserve, sends removed notification, and self-checks. Resize swaps EBA tables and updates accounting before committing the volume-table size, flushing when shrinking. Rename first updates the volume table for the whole batch, then updates RAM names or removes selected volumes.

State and persistence behavior: persistent metadata changes are volume table records written via `ubi_change_vtbl_record()` and physical unmaps through EBA/WL. Runtime state includes cdev/device registration, sysfs visibility, `is_dead`, reference counts, EBA table pointers, name/size/type fields, and global PEB accounting. `find_volume_fwnode()` attaches firmware nodes from a parent `volumes` child by `volname` or `volid`, enabling integrations such as NVMEM.

Dependencies and integration points: it integrates with Linux device/cdev/sysfs infrastructure, UBI volume notifier calls, EBA table allocation/replacement/unmap, WL flush, bad-block reserve accounting, volume table updates, firmware node APIs, and debug self-checks.

Risks: publish ordering matters: the volume is added to `ubi->volumes[]` before sysfs/cdev exposure, and removal uses `is_dead` to avoid races with sysfs reads. Resize rollback is complex because EBA tables and PEB accounting are changed before the volume table commit. Removing with `no_vtbl` is used after a batch volume-table rename/remove and must not double-clear records. `find_volume_fwnode()` matching by name uses `strncmp()` with volume name length, so ambiguous prefixes deserve review.

Test signals: create auto-ID and explicit-ID volumes; reject duplicate names and insufficient PEBs; verify sysfs attributes during concurrent removal; remove busy versus exclusive volumes; resize grow/shrink including static too-small rejection and shrink flush; batch rename/remove crash behavior; notifier ordering for shutdown/removed/resized/renamed; firmware-node association; and debug self-checks comparing RAM volume fields to vtbl records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/vmt.c -->
