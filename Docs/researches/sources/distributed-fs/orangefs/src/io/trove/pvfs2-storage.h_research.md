# sources/distributed-fs/orangefs/src/io/trove/pvfs2-storage.h

## Purpose
`pvfs2-storage.h` defines storage-facing PVFS/TROVE attribute types and conversion macros used by the job and TROVE layers.

## Important APIs, types, and macros
`PVFS_coll_getinfo_options` currently defines `PVFS_COLLECTION_STATFS`. `PVFS_vtag` is an opaque version tag placeholder, with a dummy field on Windows. `PVFS_ds_attributes` is the storage-layer dataspace attribute format: common type, fs id, handle, uid, gid, mode, ctime, mtime, atime, plus a union for metafile, datafile, or dirdata-specific attributes.

Macros include `PVFS_ds_init_time()` for initializing all three times to `time(NULL)`, `PVFS_ds_attr_to_object_attr()` for copying storage attributes into user/server object attributes, `PVFS_object_attr_to_ds_attr()` for the reverse direction, and `PVFS_object_attr_overwrite_setable()` for applying settable object-attribute mask fields.

## Control flow
The file has no functions, but macro control flow matters. `PVFS_object_attr_overwrite_setable()` conditionally updates owner, group, permissions, atime, mtime, ctime, object type, and metafile distribution fields according to mask bits; unset explicit atime/mtime values are replaced with current time/versioned current time.

## State and persistence behavior
`PVFS_ds_attributes` describes the form TROVE stores for dataspaces, distinct from wire/user-facing `PVFS_object_attr`. Comments note historical storage format differences that would require migration utilities when layouts change. Time macros call `time(NULL)`, so repeated macro arguments should not be expressions with side effects.

## Dependencies and integration points
The header depends on PVFS internal/types headers and `<time.h>`. It is included by `job.h` so job status and TROVE wrappers can refer to storage attributes and vtags. TROVE code uses these structures to persist and translate object metadata.

## Risks
The conversion macros assume metafile union fields when copying distribution data, so callers must use them with compatible object types and masks. Macro arguments are evaluated many times, which is risky for nontrivial expressions. Adding fields to storage or object attributes requires updating both conversion directions and considering on-disk migration.

## Test signals
Tests should cover round-trip conversion for metadata attributes, selective overwrite masks for uid/gid/perms/time/type/dist/dfiles, time-setting behavior for explicit and implicit atime/mtime, and ABI/layout expectations for stored `PVFS_ds_attributes`.
