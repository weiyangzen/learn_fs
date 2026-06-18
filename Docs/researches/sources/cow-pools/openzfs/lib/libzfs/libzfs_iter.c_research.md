# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_iter.c

## Scope

Implements libzfs dataset iteration for child filesystems, snapshots, bookmarks, clones, dependents, snapshot specs, sorted snapshots, and mounted child datasets.

## APIs And Behavior

- `zfs_iter_filesystems_v2()` and `zfs_iter_snapshots_v2()` use list-next ioctls with expandable nvlists and optional simple handles.
- `zfs_iter_bookmarks_v2()` requests bookmark-valid properties through `lzc_get_bookmarks()` and creates bookmark handles.
- `zfs_iter_snapshots_sorted_v2()` collects snapshots in an AVL tree sorted by `createtxg`.
- `zfs_iter_snapspec_v2()` parses comma-separated snapshot specs, including ranges with `%`, validates endpoints, and iterates matching snapshots.
- `zfs_iter_children_v2()` visits snapshots before child filesystems.
- `zfs_iter_dependents_v2()` recursively walks clone dependencies, child filesystems, and snapshots while detecting dependency cycles unless recursion is allowed.
- `zfs_iter_mounted()` walks `MNTTAB`, filters mounted ZFS child filesystems, skips snapshots and legacy mountpoints, and invokes the callback.

## State And Dependencies

Iteration builds handles from `zfs_cmd_t` responses using constructors from `libzfs_dataset.c`. It depends on ZFS dataset/snapshot list ioctls, libzfs_core bookmark APIs, clone property resolution, AVL trees, and mnttab parsing.

## Risks And Invariants

Callbacks receive handles and are expected to close or retain them according to libzfs iteration conventions. List iteration treats `ESRCH` and `ENOENT` as normal completion/removal races. Dependent traversal guards against clone cycles by comparing dataset GUIDs on an explicit stack.
