# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_zone.c

## Scope

FreeBSD jail-backed implementation of ZFS zone dataset visibility and hostid helpers. It stores the list of datasets delegated to each jail using jail OSD storage.

## Main Interfaces

- `zone_dataset_attach()` adds a dataset to a jail after `PRIV_ZFS_JAIL` authorization.
- `zone_dataset_detach()` removes a delegated dataset from a jail.
- `zone_dataset_visible()` checks whether the current process can see a dataset and whether it is writable.
- `zone_get_hostid()` returns the current jail hostid.
- `zone_sysinit()` / `zone_sysuninit()` register and deregister the jail OSD slot.

## State And Control Flow

Each jail stores a `zone_dataset_head` list in `zone_slot`; each entry is a variable-sized `zone_dataset_t` containing the delegated dataset name. Attach allocates before taking prison locks, rejects duplicates, creates the OSD list lazily, and inserts the dataset. Detach finds the jail/list/name, removes the entry, and deletes the OSD slot when the list becomes empty.

Visibility is global-zone permissive. In a jail, it first checks whether the requested dataset is equal to or under a delegated dataset, which is visible and writable. It then checks whether the requested dataset is a parent of a delegated dataset, which is visible but read-only.

## Dependencies

Uses FreeBSD jails/prisons, OSD jail storage, privilege checks, allprison locking, and SPL policy wrappers.

## Correctness Notes

The prefix checks distinguish dataset separators `/`, snapshot separator `@`, exact names, and trailing slash parent forms. The OSD destructor frees every delegated dataset entry when a jail is destroyed.
