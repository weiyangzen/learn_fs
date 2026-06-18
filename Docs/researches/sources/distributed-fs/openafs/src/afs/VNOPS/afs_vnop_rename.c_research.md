# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_rename.c

## Purpose
Implements rename across one or two AFS directories, including connected fileserver RPCs, disconnected replay logging, local directory cache surgery, target unlink accounting, and moved-directory parent handling.

## Important APIs, Types, and Functions
`afs_rename` is the vnode wrapper that creates the request and resolves fakestat for old and new parent directories. `afsrename` contains the main implementation. It uses `RXAFS_Rename`, `afs_dir_Lookup`, `afs_dir_Delete`, `afs_dir_Create`, `afs_LocalHero`, `afs_DisconAddDirty`, `afs_MakeShadowDir`, and `afs_dir_ChangeFid`.

## Control Flow and State
`afsrename` allocates output status buffers, validates name lengths, verifies old and new parents, rejects cross-volume renames, handles same-directory same-name as a no-op, locks parents in vnode-number order to reduce deadlock risk, obtains old and new directory dcaches, removes DNLC entries, and verifies dcache freshness. Connected mode performs `RXAFS_Rename` through `afs_Analyze`. Disconnected RW mode finds the moved file vcache, creates a parent shadow if needed, saves the old parent, and records `VDisconRename` plus `VDisconRenameSameDir` when applicable. After a successful operation, it locally deletes the source entry, deletes any existing target entry, creates the destination entry, updates link counts, handles overwritten target link-count/smush behavior, and invalidates or rewrites `..` for moved directories.

Connected renames are synchronously persisted by the fileserver. Directory dcache updates are kept only when server status and data-version expectations match; otherwise dcache entries are zapped. Disconnected renames persist intent in dirty flags and shadow metadata for later replay. Parent hints in `f.parent` and moved-directory cached `..` entries are updated or invalidated.

## Dependencies and Integration Points
Integrates with fakestat, vcache/dcache locking, DNLC, fileserver rename RPC, directory package operations, disconnected dirty replay infrastructure, callback invalidation, volume status bits, and remove semantics for overwritten targets.

## Risks and Test Signals
The local update block is fragile because success does not guarantee cached directories are current enough to edit safely. Cross-directory locking and dcache acquisition order are complex. Disconnected mode locks moved vcaches while holding directory locks. Same-directory target replacement must preserve correct link counts. If an RPC fails after partially executing on the server, both directories are marked stale.

Test same-name no-op, same-directory rename, cross-directory rename, cross-volume `EXDEV`, readonly parents, disconnected non-RW and RW rename, target overwrite, moved directories with `..`, cache-local update accepted/rejected by `afs_LocalHero`, missing target dcache, RPC retry/failure, and DNLC invalidation for both old and new names.
