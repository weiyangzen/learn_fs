<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-common.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-common.c

## Purpose

`nfs-common.c` provides shared NFS server helpers for mapping between child xlators and ids, deriving xlators from mount paths, constructing and wiping `loc_t` objects from inodes, gfids, parents, and entries, hashing gfids, and maintaining NFS inode generation context. Source read: complete 449-line file.

## Important APIs, Types, and Functions

Exported helpers include `nfs_xlid_to_xlator`, `nfs_xlator_to_xlid`, `nfs_mntpath_to_xlator`, `nfs_loc_wipe`, `nfs_loc_copy`, `nfs_loc_fill`, `nfs_inode_loc_fill`, `nfs_gfid_loc_fill`, `nfs_root_loc_fill`, `nfs_entry_loc_fill`, `nfs_hash_gfid`, and `nfs_fix_generation`. `nfs_path_to_xlator` is a stub returning `NULL`. `nfs_parent_inode_loc_fill` is implemented here but not declared in `nfs-common.h`.

## Control Flow

Xlator helpers walk the `xlator_list_t` children list by index, pointer equality, or first mount-path component. Location helpers build up `loc_t` by referencing inode and parent objects, copying gfids, resolving inode paths, or synthesizing `<gfid:...>` paths when no path is known. `nfs_entry_loc_fill` first finds the parent by gfid, then tries to find or create the entry inode depending on `how`; it returns `-2` when it filled a loc for a missing entry and the caller should force lookup.

`nfs_fix_generation` checks for existing NFS inode context and updates the generation. If no context exists, it allocates one, initializes share list state, stores it in inode ctx, and sets generation from `nfs_state`.

## State and Persistence Behavior

This file does not persist state to disk. It manipulates references to inode-table objects and may allocate path strings and NFS inode contexts. Correct callers must wipe locs with `nfs_loc_wipe` and unref any inode references they own.

## Dependencies and Integration Points

It depends on rpcsvc/NFS XDR includes, Gluster dict/xlator/iobuf/iatt/inode APIs, `nfs-fops.h`, `nfs-mem-types.h`, and NFS message IDs. It is used heavily by MOUNT subdir resolution, NFSv3 filehandle resolution, and fop wrapper code.

## Risks and Edge Cases

`nfs_inode_loc_fill` uses `loc->gfid` in the synthetic fallback path, which requires callers to have initialized the loc gfid correctly. `nfs_entry_loc_fill` relies on inode ctx to decide whether hard resolution is needed; stale or missing ctx changes control flow. `nfs_hash_gfid` compresses a 128-bit gfid into 32 bits and can collide. The undeclared `nfs_parent_inode_loc_fill` may be intentionally private but can cause prototype drift.

## Test Signals

Tests should cover root loc fill, missing parent, missing entry with and without create mode, inode path failures, generation context creation/update, xlator list mapping, mount-path parsing with leading slashes and subdirs, and gfid hash root special casing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-common.c -->
