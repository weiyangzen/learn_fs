# File Research: sources/cow-pools/openzfs/cmd/zfs/zfs_iter.c

`zfs_iter.c` implements the shared dataset traversal and sorting layer used by many `zfs` subcommands. Its public entry point, `zfs_for_each()`, accepts command-line dataset arguments, traversal flags, target ZFS types, optional sort columns, optional property lists, a depth limit, and a callback. It gathers matching handles into an AVL tree, sorts them, invokes the caller callback in stable order, and then closes all handles.

Core data structures:
- `zfs_node_t` stores a `zfs_handle_t *`, the active callback context, and an AVL node.
- `callback_data_t` stores the AVL tree, iterator flags, target types, sort columns, caller property list pointer, depth state, and a `cb_props_table` used to prune unneeded properties.
- `zfs_sort_column_t` is defined in the header and implemented here as a linked list with a tail pointer in `sc_last`.

Traversal behavior:
- `zfs_include_snapshots()` includes snapshots either when explicitly requested by type or when `ZFS_ITER_PROP_LISTSNAPS` is set and the pool `listsnapshots` property permits it.
- `zfs_callback()` adds matching filesystems, volumes, snapshots, or bookmarks to the AVL tree, expands/prunes requested properties, recurses into child filesystems, snapshots, and bookmarks according to flags and depth, and closes handles that were not retained in the tree.
- `zfs_for_each()` handles both implicit root traversal (`argc == 0`) and explicit arguments. With recursion enabled it broadens acceptable argument types so users can recurse from filesystems and, when appropriate, volumes.

Sorting behavior:
- `zfs_add_sort_column()` validates a built-in or user property name and appends it to the sort list.
- `zfs_free_sort_columns()` releases the linked sort list and any copied user property names.
- `zfs_compare()` is the fallback name comparator. It sorts datasets by base name, puts parent datasets before their snapshots, and orders snapshots by `createtxg` when available.
- `zfs_sort()` applies requested sort columns first. It supports user properties, string properties, and numeric properties; invalid properties for a row sort that row below valid rows. Equal rows fall back to `zfs_compare()`.

Fast-list optimization:
- `zfs_sort_only_by_fast()` and `zfs_list_only_by_fast()` return true only when requested sort/list properties can be populated from fast dataset stats: `name`, `guid`, `createtxg`, `numclones`, `inconsistent`, `redacted`, and `origin`.
- `zfs_main.c` uses these helpers to set `ZFS_ITER_SIMPLE` for `zfs list` when no slow property expansion is required.

Dependencies and integration:
- Depends on `libzfs` handle iteration APIs such as `zfs_iter_root()`, `zfs_iter_filesystems_v2()`, `zfs_iter_snapshots_v2()`, and `zfs_iter_bookmarks_v2()`.
- Uses AVL utilities from the OpenZFS userspace support environment.
- Uses `safe_malloc()` and global `g_zfs` from `zfs_util.h`/`zfs_main.c`.

Risks and maintenance notes:
- The iterator owns retained handles after insertion and closes them during AVL destruction; callers must not close handles passed to their callback unless explicitly documented elsewhere.
- Property pruning is an important performance and correctness contract: callers that pass a proplist must ensure later callbacks access only retained properties plus required implicit properties.
- Sort comparisons temporarily modify names by replacing `@` with NUL and restoring it; this assumes `zfs_get_name()` storage is writable in this context.
