# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-fsck.h

## Purpose
`pvfs2-fsck.h` declares the internal interfaces and handle-list structure for `pvfs2-fsck.c`. It is not a broad public API; it organizes the checker's parsing, traversal, repair, removal, and per-server handle-list operations.

## Important APIs, Types, And Functions
The header declares utility helpers (`parse_args`, `usage`, `get_type_str`), processing passes (`build_handlelist`, `traverse_directory_tree`, `match_dirdata`, `descend`, `verify_datafiles`, `find_sub_trees`, `fill_lost_and_found`, `cull_leftovers`), modification functions (`create_lost_and_found`, `create_dirent`, `remove_object`, `remove_directory_entry`), and `struct handlelist` with arrays for per-server handle pointers, capacities, and used counts. Static handle-list helpers cover initialize, add one/many handles, finish, find, remove, return, finalize, and optional debug print.

## Control Flow
`pvfs2-fsck.c` includes this header after defining `struct options`, so the static parser prototype refers to the implementation-local options type. The processing prototypes mirror the four-pass checker flow: build all handles, walk reachable tree, identify subtrees, fill lost+found, and cull leftovers.

## State And Persistence
The header defines no state directly, but `struct handlelist` is the central in-memory persistence mechanism for fsck's view of all handles and their consumption as objects are matched, salvaged, or removed.

## Dependencies And Integration Points
It depends on PVFS core types such as `PVFS_fs_id`, `PVFS_BMI_addr_t`, `PVFS_credential`, `PVFS_object_ref`, `PVFS_handle`, and `PVFS_ds_type`, supplied by prior includes in `pvfs2-fsck.c`. It is tightly coupled to that C file because many declarations are `static` and refer to local types.

## Risks And Test Signals
Risks include weak standalone includability, static prototypes in a header, tight coupling to definition order, and declaration drift from `pvfs2-fsck.c`. Compile coverage of `pvfs2-fsck.c` is the main signal; behavioral signals come from fsck tests that stress handle-list add/find/remove/return/finalize paths.
