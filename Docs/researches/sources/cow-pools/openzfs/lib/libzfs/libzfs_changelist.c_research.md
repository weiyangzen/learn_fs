# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_changelist.c

This file implements libzfs changelists: ordered sets of datasets that need pre/post handling when properties such as `mountpoint`, `sharenfs`, `sharesmb`, `name`, `zoned`, `canmount`, or `volsize` change.

Primary purpose:
- Before a property change, gather affected datasets and remember whether they were mounted/shared/zoned.
- Prefix phase unmounts or unshares as needed.
- Postfix phase remounts and reshares according to new properties and previous state.

Important structures:
- `prop_changenode_t`: stores a dataset handle, prior shared/mounted/zoned state, whether postfix work is needed, and AVL node.
- `prop_changelist`: stores real and effective properties, companion share property, AVL tree, mount/gather flags, and whether any child is zoned.

Main workflow:
1. `changelist_gather()`
2. `changelist_prefix()`
3. caller changes property
4. `changelist_postfix()`
5. `changelist_free()`

Prefix behavior:
- `changelist_prefix()` acts only for `mountpoint` and `sharesmb`.
- It returns immediately if `CL_GATHER_DONT_UNMOUNT` is set.
- For mountpoint changes it unmounts affected filesystems.
- For SMB share changes it unshares SMB resources and commits SMB share updates.
- If an unmount fails, remaining nodes are marked as not needing postfix and already-processed nodes are restored through `changelist_postfix()`.
- Zoned children are skipped from the global zone.

Postfix behavior:
- `changelist_postfix()` returns immediately for `CL_GATHER_DONT_UNMOUNT`.
- For mountpoint changes it removes the old mountpoint for the last node.
- It walks the AVL in reverse order so parents are mounted before children.
- It refreshes properties, skips volumes, checks `sharenfs`, `sharesmb`, key availability, mounted state, and `canmount`.
- It remounts datasets that were mounted before, were legacy/none mountpoints, or need sharing and can be mounted.
- It shares or unshares NFS and SMB according to current properties and previous shared state.
- It commits share changes once after walking the list.
- It only propagates share option syntax errors; service-not-running style share failures are tolerated.

Gather behavior:
- `changelist_gather()` chooses AVL ordering:
  - by dataset name when the existing mountpoint is `legacy` or `none`;
  - by mountpoint otherwise, to handle mount hierarchies that differ from dataset hierarchy.
- Property mapping:
  - rename (`ZFS_PROP_NAME`) is treated as a mountpoint-affecting operation and gathers all dependents;
  - `ZFS_PROP_ZONED` gathers all children;
  - `ZFS_PROP_CANMOUNT` and `ZFS_PROP_VOLSIZE` are treated as mountpoint related.
- For `sharenfs`, it also watches `sharesmb`; for `sharesmb`, it also watches `sharenfs`.
- It can gather mounted descendants from mnttab with `CL_GATHER_ITER_MOUNTED`.
- It always reopens and adds the target dataset itself after child/dependent gathering.
- It records legacy/none mountpoint state to guide postfix remount behavior.

Other operations:
- `changelist_rename()` updates stored dataset names after a rename and removes previous mountpoints.
- `changelist_unshare()` unshares all nodes for the requested protocol list and commits each protocol.
- `changelist_haszonedchild()` exposes whether gather found any zoned child.
- `changelist_remove()` removes and closes one named dataset from a gathered list.
- `changelist_free()` closes all dataset handles and destroys the AVL tree.

Notable helper logic:
- `isa_child_of()` treats `dataset`, `dataset/...`, and `dataset@...` as descendants.
- `change_one()` adds datasets that inherit the watched property, are included by all-children/all-dependents modes, or inherit companion share properties.
- For mountpoint changes, child iteration includes snapshots/clones only where the gather mode requires it.

Dependencies:
- libzfs dataset iteration, mount, unmount, share, unshare, property, and handle APIs.
- AVL ordering from `sys/avl.h`.
- Zone awareness via `getzoneid()` and `GLOBAL_ZONEID`.
