# File Research: sources/cow-pools/openzfs/cmd/zfs/zfs_iter.h

`zfs_iter.h` declares the shared iteration and sorting interface for the `zfs` command binary.

Primary exported type:
- `zfs_sort_column_t` is a linked-list node describing one sort key. It stores the built-in property enum, optional user property string, reverse-sort flag, next pointer, and a tail pointer used for append efficiency.

Exported functions:
- `zfs_for_each()` is the generic traversal API used by subcommands that operate over datasets, snapshots, volumes, and bookmarks.
- `zfs_add_sort_column()` parses and appends one sort column.
- `zfs_free_sort_columns()` releases sort column state.
- `zfs_sort_only_by_fast()` and `zfs_list_only_by_fast()` let callers detect whether list/sort operations can use fast dataset stats without full property expansion.

Integration notes:
- This header is included by `zfs_main.c` for list/get/set/inherit/upgrade/userspace/holds/key operations and by `zfs_iter.c` for its own implementation.
- It depends on OpenZFS public types such as `zfs_prop_t`, `zfs_type_t`, `zprop_list_t`, `zfs_iter_f`, and `boolean_t`, supplied through the broader `zfs` command include chain.

Risks and maintenance notes:
- The header exposes only traversal primitives, not the internal AVL/node state, which keeps callers decoupled from sorting internals.
- Adding new fast-list properties requires updating both declarations’ implementation in `zfs_iter.c`, and callers such as `zfs_do_list()` will then automatically benefit.
