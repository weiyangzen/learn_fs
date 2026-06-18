# sources/distributed-fs/ceph-client/drivers/scsi/scsi_devinfo.c

Purpose: maintains SCSI device quirk information, historically known as the blacklist/whitelist. It combines a large built-in table of vendor/model patterns with boot/module parameters, optional `/proc/scsi/device_info` updates, and keyed lists for subsystems that need their own devinfo namespace.

Important APIs/types/functions: `struct scsi_dev_info_list` stores padded vendor/model keys, `blist_flags_t flags`, and a compatibility-match flag. `struct scsi_dev_info_list_table` groups entries by key. `scsi_init_devinfo()` creates the global list, parses `scsi_dev_flags`, imports `scsi_static_device_list[]`, and creates the proc entry when configured. `scsi_get_device_flags_keyed()` returns matching flags, device-specific defaults, or global defaults. Exported mutators include `scsi_dev_info_list_add_keyed()`, `scsi_dev_info_add_list()`, and `scsi_dev_info_remove_list()`.

Control flow: initialization creates the global table, applies dynamic parameter entries first, then appends static compatible entries. Lookup trims leading/trailing spaces for compatible entries, matches vendor exactly, and treats model as a prefix; non-compatible entries are exact padded matches and are inserted at the head so runtime entries override older ones. The proc reader walks all tables with a two-list cursor; the proc writer copies a page-sized userspace string, parses `vendor:model:flags` entries, and adds non-compatible overrides.

State and persistence: runtime state lives in global linked lists, `scsi_default_dev_flags`, and the module parameter buffer. It is not durable across boot, but static entries are rebuilt on each init and user-provided module/proc entries persist for the lifetime of the module/core instance.

Dependencies and integration: scan code calls `scsi_get_device_flags*()` while creating `struct scsi_device`, and later SCSI paths consume `sdev->sdev_bflags` for LUN scanning, VPD, retry, queue, locking, DIF, and ULD attachment behavior. The file depends on procfs, module parameters, kernel lists, and SCSI devinfo flag definitions.

Risks: quirk matching is global and order-sensitive; a broad compatible prefix can alter discovery or I/O behavior for unrelated devices. Runtime list mutation is not visibly protected by a lock in this file, so callers must rely on init-time/proc-time usage patterns. This source snapshot also shows duplicated lines in the matching/write-adjacent code, which is a compile-time risk if present in the active tree.

Test signals: compile with and without `CONFIG_SCSI_PROC_FS`; boot with `scsi_dev_flags=` overrides; read and write `/proc/scsi/device_info`; scan devices that exercise compatible prefixes, exact runtime overrides, wildcard-like model strings from the static table, keyed list add/remove, and unsupported `__BLIST_UNUSED_MASK` rejection.
