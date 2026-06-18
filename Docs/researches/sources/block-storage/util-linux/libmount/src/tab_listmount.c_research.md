# File Research: sources/block-storage/util-linux/libmount/src/tab_listmount.c

This file integrates the Linux `listmount()`/`statmount()`-era APIs into `libmnt_table`. When `HAVE_STATMOUNT_API` is not available, all exported functions return `-ENOSYS`. When available, `struct libmnt_listmnt` tracks root mount id, namespace id, last id from the previous syscall, step size, an id buffer, enabled/done status, and traversal direction.

`table_init_listmount()` checks kernel support with `has_listmount()`, allocates `struct libmnt_listmnt` and its id buffer in one block, defaults the root id to `LSMT_ROOT`, preserves old settings when reallocating for a different step size, and reports `-ENOSYS` for unsupported kernels. Public setters configure root id, namespace id, and batch size.

`mnt_table_enable_listmount()` toggles on-demand fetching for `mnt_table_next_fs()` and returns the old status. `mnt_table_want_listmount()` is the private predicate used by `tab.c`. `mnt_table_reset_listmount()` clears fetch state after the table is reset and requires an empty table.

`lsmnt_to_table()` converts returned mount ids into placeholder kernel `libmnt_fs` entries, setting `MNT_FS_KERNEL`, unique mount id, and optional namespace id, then inserting them before or after a saved position depending on traversal direction. The detailed mount data is expected to be filled later via statmount fetching.

`mnt_table_next_lsmnt()` backs lazy iteration. It disables on-demand fetching during the syscall, avoids mixing forward and reverse ordering by fetching all remaining data when direction changes, calls `ul_listmount()`, marks done when fewer than a full batch is returned, inserts new ids, and restores the enabled state. `mnt_table_fetch_listmount()` eagerly resets the table and reads all mount ids, temporarily disabling on-demand statmount and listmount, then marks the listmount state done.
