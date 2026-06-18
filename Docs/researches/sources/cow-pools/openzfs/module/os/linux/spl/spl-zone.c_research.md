# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-zone.c

## Purpose

Implements Linux user-namespace-backed equivalents of Solaris zone dataset visibility and delegation. It supports namespace-specific dataset delegation and UID-owned dataset delegation for rootless container use.

## Main State

- `zone_datasets_lock`: protects all delegation lists.
- `zone_datasets`: list of user-namespace-specific delegations.
- `zone_uid_datasets`: list of UID-owned delegations.
- `zone_get_zoned_uid_fn`: callback registered by ZFS to resolve the `zoned_uid` property and delegation root.

## Data Structures

- `zone_datasets_t`: namespace reference plus datasets delegated to that namespace.
- `zone_dataset_t`: variable-length dataset name node.
- `zone_uid_datasets_t`: owner UID plus datasets delegated to that UID.

## Namespace Handling

When `CONFIG_USER_NS` is enabled, `user_ns_get()` validates a file descriptor as an nsfs user namespace file, extracts its `struct user_namespace`, and returns errors that let higher layers distinguish invalid namespace references. Namespace zone IDs are derived from `user_ns->ns.inum`.

Without user namespace support, attach/detach APIs return `ENXIO`, and global-zone checks treat all callers as global.

## Delegation APIs

- `zone_dataset_attach()`: root-only attach of dataset to a user namespace.
- `zone_dataset_attach_uid()`: root-only attach of dataset to an owning UID.
- `zone_dataset_detach()`: remove namespace delegation and release namespace ref when empty.
- `zone_dataset_detach_uid()`: remove UID delegation and prune empty UID entry.
- `zone_register_zoned_uid_callback()` / `zone_unregister_zoned_uid_callback()`: ZFS property callback lifecycle.

## Authorization And Visibility

- `zone_dataset_admin_check()`: authorizes operations under `zoned_uid` delegation. It checks non-global zone status, callback availability, delegation root, namespace owner UID, operation-specific capability, and extra constraints for destroy, rename, and clone.
- `zone_dataset_visible()`: checks if a dataset should be visible/writable to the current zone. Global zone gets full write visibility. Non-global callers are checked first against namespace delegation and then UID delegation.
- `zone_dataset_check_list()`: implements parent/root/child matching. Parents are visible read-only; delegated roots and descendants are writable.

## Utility APIs

- `global_zoneid()`
- `crgetzoneid()`
- `inglobalzone()`
- `spl_zone_init()`
- `spl_zone_fini()`

## Notes

Dataset names are rejected if empty or beginning with `/`; a trailing slash is ignored. Namespace delegation holds a namespace reference to avoid namespace ID reuse while delegation is active.
