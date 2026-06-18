# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_idmap.c

## Purpose
`nodemap_idmap.c` implements the in-memory UID, GID, and PROJID mapping tables used by nodemaps. Each `struct lu_idmap` is represented once but linked into two rbtrees so lookup is efficient in both client-to-filesystem and filesystem-to-client directions.

## Important APIs, types, and functions
The core type is `struct lu_idmap`, with `id_client`, `id_fs`, `id_client_to_fs`, and `id_fs_to_client`. Public helpers are `idmap_create()`, `idmap_insert()`, `idmap_delete()`, `idmap_search()`, `idmap_delete_tree()`, and `idmap_copy_tree()`.

`idmap_insert()` selects one forward and one backward root from the nodemap according to `NODEMAP_UID`, `NODEMAP_GID`, or `NODEMAP_PROJID`. It searches both roots before insertion, returns `NULL` on clean insert, `ERR_PTR(-EEXIST)` when both sides already match, a conflicting existing map when only one side matches, or `ERR_PTR(-EINVAL)` for invalid ID type.

## Control flow and behavior
Creation allocates and initializes both rb nodes. Insert walks forward by `id_client` and backward by `id_fs`; it only links into both trees when neither side exists. A partial conflict is returned so the handler can delete the old persistent index and retry. Search chooses the correct tree for direction/type and performs a normal integer rbtree walk. Delete erases both nodes and frees the object.

`idmap_delete_tree()` and `idmap_copy_tree()` traverse representative roots with `rbtree_postorder_for_each_entry_safe()`. They visit one tree per ID class because each object appears in both directional trees. Copy is used for initial inheritance into sub-nodemaps.

## State and persistence
This file is memory-only and does not call `nodemap_idx_*()`. Callers must hold `nm_idmap_lock` for normal mutation/lookup safety. Persistence is handled by the handler around calls into this file.

## Dependencies and integration points
Dependencies are Linux rbtrees, Lustre allocation helpers, and `nodemap_internal.h`. The handler uses these helpers for add/delete/map/destruction/inheritance; member comparison uses the rbtrees to decide whether lock revocation is required.

## Risks and edge cases
`idmap_search()` dereferences `root` after enum selection, so invalid type/direction combinations would crash. `idmap_delete_tree()` frees through copied roots and is appropriate for teardown, not reusable clearing. `idmap_copy_tree()` appears to free `idmap` rather than `idmap_new` on insertion failure, which could corrupt the source tree if the failure path is reachable.

## Test signals
Cover one-to-one inserts, duplicate and partial-conflict inserts, lookup in both directions for all ID types, deletion from both trees, invalid enum misuse, delete-tree teardown under leak checking, and copy failure injection.
