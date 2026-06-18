# File Research: sources/block-storage/util-linux/libmount/src/tab_diff.c

This file implements `libmnt_tabdiff`, a small diff engine for comparing two mount tables and reporting mount, unmount, remount, and move operations. A diff entry holds an operation code plus referenced old and new `libmnt_fs` pointers.

`mnt_new_tabdiff()` initializes active and unused lists. `mnt_free_tabdiff()` frees all active entries and unrefs held filesystems. `tabdiff_reset()` recycles active entries into an unused list, clears operation state, unrefs old/new fs pointers, and resets the change count. Reusing unused entries reduces allocation churn when a diff object is reused repeatedly.

`tabdiff_add_entry()` obtains an unused or newly allocated entry, references the supplied old/new filesystems, stores the operation, and appends to the active change list. `mnt_tabdiff_next_change()` iterates over recorded changes with a libmount iterator and optionally returns old fs, new fs, and operation.

`mnt_diff_tables()` is the main algorithm. Empty-to-nonempty produces all mounts; nonempty-to-empty produces all unmounts. Otherwise, it scans the new table and uses `mnt_table_find_pair(old_tab, source, target)` to detect new mounts. Existing pairs with changed VFS or FS option strings become remounts. It then scans the old table for pairs missing in the new table. If a missing old entry has a corresponding new mount change with the same source and mount id, the change is converted to `MNT_TABDIFF_MOVE`; otherwise it records an unmount.

Limitations are intentional: matching is source/target-pair oriented and option changes are string comparisons of VFS and FS option strings when both sides exist. The test program prints a human-readable diff between two table files.
