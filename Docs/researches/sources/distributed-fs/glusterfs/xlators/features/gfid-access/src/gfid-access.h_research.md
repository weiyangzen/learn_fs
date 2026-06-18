# sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/gfid-access.h

## Purpose
Defines constants, payload structures, private state, local frame state, and validation macros for the `gfid-access` translator.

## Important APIs, Types, and Functions
- `GF_FUSE_AUX_GFID_NEWFILE` and `GF_FUSE_AUX_GFID_HEAL` name the control xattrs consumed by `ga_setxattr()`.
- `GF_GFID_DIR` and `GF_AUX_GFID` define the virtual `.gfid` namespace identity.
- `GFID_ACCESS_ENTRY_OP_CHECK` rejects entry creation/removal under `/.gfid` and direct operations on the virtual directory.
- `GFID_ACCESS_INODE_OP_CHECK` rejects inode fops against `.gfid` itself.
- `ga_newfile_args_t` and `ga_heal_args_t` model decoded auxiliary request payloads.
- `ga_private_t` carries cached stat buffers and mem pools; `ga_local_t` carries copied-frame state for async helper creates.

## Control Flow
The macros are used as early guards in `gfid-access.c` fop handlers. The packed structs guide parser layout: uid, gid, GFID string, mode, basename, and type-specific mkdir/symlink/mknod fields for new-file creation; GFID plus basename for heal.

## State and Persistence
Header-defined state is memory-only. `ga_private_t` survives for the translator lifetime; `ga_local_t` exists per helper operation; decoded argument structs come from mem pools.

## Dependencies and Integration Points
Includes GlusterFS logging, dict, defaults, and translator-specific memory accounting definitions. The macros rely on `__is_root_gfid()` from GlusterFS and `__is_gfid_access_dir()` from the C file.

## Risks and Edge Cases
The macro calls `__is_gfid_access_dir()` before a prototype in this header, so its implementation must remain visible in the C translation unit before macro use matters. Packed structs document wire layout but the parser manually walks blobs, so drift between struct and parser would break auxiliary clients.

## Test Signals
Compile coverage should catch macro/function visibility issues. Behavior tests should assert `ENOTSUP` for `/.gfid` itself and `EPERM` for mutation below virtual GFID entries.
