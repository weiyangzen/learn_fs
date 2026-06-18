<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/lcommon_cl.c -->
# sources/distributed-fs/lustre-release/lustre/llite/lcommon_cl.c

## Purpose

`lcommon_cl.c` contains common llite client-layer object helpers: propagating setattr operations to OST/CL objects, creating or updating CL objects when inode metadata arrives, safely tearing down CL objects during inode eviction, and deriving stable inode number/generation values from Lustre FIDs.

## Important APIs, Types, And Functions

- `cl_setattr_ost(struct inode *inode, const struct iattr *attr, enum op_xvalid xvalid, unsigned int attr_flags)`: sends CL setattr operations to OST-side objects, including truncate/fallocate-style metadata, flags, owner/group/project identity, and designated mirror from `ATTR_FILE`.
- `cl_file_inode_init(struct inode *inode, struct lustre_md *md)`: creates a new `cl_object` for a regular inode when metadata includes a valid FID, or updates an existing object's layout configuration.
- `cl_inode_fini(struct inode *inode)`: kills and drops the inode's CL object during eviction, using an emergency environment under memory pressure.
- `cl_fid_build_ino(const struct lu_fid *fid, int api32)`: maps a FID to a 32-bit or 64-bit inode number depending on platform/API constraints.
- `cl_fid_build_gen(const struct lu_fid *fid)`: derives inode generation, using IGIF generation when applicable and high flattened-FID bits otherwise.
- `cl_object_put_last()`: private helper that waits until only the inode-owned CL object reference remains before dropping it.
- `cl_inode_fini_env`, `cl_inode_fini_refcheck`, and `cl_inode_fini_guard`: emergency CL environment and serialization for eviction under allocation failure.

## Control Flow

`cl_file_inode_init()` is called when llite has new metadata. It ignores non-regular files and metadata without `OBD_MD_FLID`. For new inodes with no `lli_clob`, it requires the inode to still have `I_NEW`, marks the object config as `LOC_F_NEW`, and calls `cl_object_find()` directly against the top client device. Existing `lli_clob` objects receive `cl_conf_set()` with the new layout; `-EBUSY` is ignored because later I/O will handle layout reconfiguration.

`cl_setattr_ost()` obtains a CL environment, fills `io->u.ci_setattr` with times, size, valid flags, xvalid flags, parent FID, and truncate credentials when `ATTR_SIZE` is present. If a file is supplied, `ll_io_set_mirror()` and the VVP file descriptor are installed so ftruncate honors group locks and mirror selection. The `CIT_SETATTR` CLIO runs and restarts while `ci_need_restart` is set.

`cl_inode_fini()` is called after the inode cache is evicting its slave CL object. It tries to allocate a normal CL environment, but if that fails it locks `cl_inode_fini_guard` and uses the preallocated emergency environment. It kills the object, waits in `cl_object_put_last()` for external references to drain, drops the final reference, clears `lli_clob`, and releases the chosen environment.

## State And Persistence Behavior

The file manages in-memory CL object lifetime and layout configuration. `cl_setattr_ost()` causes persistent OST-side changes through the CL stack when it truncates or updates object attributes/flags. `cl_file_inode_init()` stores the CL object pointer in `ll_inode_info::lli_clob`; `cl_inode_fini()` clears it. FID-to-inode-number helpers are deterministic mappings and do not mutate state.

## Dependencies And Integration Points

This file depends on CL object/site/device APIs, VVP environment helpers, llite inode metadata, Lustre FID helpers, Linux inode state, and quota/user namespace conversion helpers. It is used by `file.c` for truncate, fallocate, encrypted flag propagation, project/ext flags, and CL object teardown. It integrates with layout configuration through `cl_conf_set()` and object creation through `cl_object_find()`.

## Risks And Edge Cases

- `cl_file_inode_init()` treats a non-new inode without `lli_clob` as `-EIO`; callers must only create CL objects during safe inode initialization.
- Ignoring `-EBUSY` from layout config relies on later I/O handling stale or contested layout state.
- `cl_object_put_last()` waits for references to drop; a leaked reference or blocked AST path can hang inode eviction.
- Emergency environment use is serialized and assumes `cl_inode_fini_env` has been initialized elsewhere.
- `cl_setattr_ost()` restarts while `ci_need_restart` is set and must keep file/mirror/group-lock context consistent across retries.
- FID flattening to 32-bit inode numbers can collide by design; generation handling is the mitigation.

## Test Signals

Tests should exercise new regular inode CL object creation, existing layout update including `-EBUSY`, non-regular/no-FID no-op behavior, unexpected non-new inode failure, truncate setattr with UID/GID/project propagation, file-backed ftruncate honoring group locks/designated mirrors, restart after layout change, inode eviction under normal and emergency environment paths, and 32-bit inode/generation mapping for IGIF and non-IGIF FIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/lcommon_cl.c -->
