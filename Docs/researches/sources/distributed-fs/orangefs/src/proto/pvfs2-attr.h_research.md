<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/pvfs2-attr.h -->
# sources/distributed-fs/orangefs/src/proto/pvfs2-attr.h

## Purpose
Defines OrangeFS object attribute masks, object-specific attribute structures, and protocol encode/decode logic for `PVFS_object_attr`. It is the central protocol contract for common metadata, metafile distribution/datafile lists, datafile sizes, symlink targets, directory hints, distributed-directory metadata, and capabilities.

## Important APIs, Types, and Functions
Defines common masks (`PVFS_ATTR_COMMON_*`), object-specific masks (`PVFS_ATTR_META_*`, `PVFS_ATTR_DATA_SIZE`, `PVFS_ATTR_SYMLNK_TARGET`, `PVFS_ATTR_DIR_*`, `PVFS_ATTR_DISTDIR_ATTR`, `PVFS_ATTR_CAPABILITY`), and `PVFS_STATIC_ATTR_MASK`. Important structs include `PVFS_metafile_hint`, `PVFS_metafile_attr`, `PVFS_datafile_attr`, `PVFS_dirhint_server_list`, `PVFS_dirhint_layout`, `PVFS_directory_hint`, `PVFS_directory_attr`, `PVFS_symlink_attr`, and `PVFS_object_attr`. Under `__PINT_REQPROTO_ENCODE_FUNCS_C`, it defines encoders/decoders for distribution fields, dfile arrays, mirror dfile arrays, directory attrs, and full object attrs. It also defines extra-size constants used by max-size calculations.

## Control Flow
`encode_PVFS_object_attr` writes common owner/group/perms/time/mask/type fields, conditionally writes capability, conditionally writes metafile stuffed size for stuffed metafiles, then conditionally writes distribution, dfile arrays and hints, mirror dfile arrays, datafile size, symlink target, distributed-directory bitmap/handles, and directory attributes based on mask bits and object type. Decode mirrors the same mask-driven order and allocates arrays for distributions, dfile handles, mirror handles, distributed-directory bitmaps, and dirdata handles.

## State and Persistence
The header defines in-memory representations of object metadata and their wire representation. Attribute data is persisted by OrangeFS servers; this header controls how client/server messages carry that state. Decode allocations become transient ownership that higher-level release paths must free.

## Dependencies and Integration Points
Depends on internal PVFS types, storage types, distribution descriptors, security/capability definitions, and the encode macro framework. It is included by request protocol stubs and used heavily by create/getattr/setattr/listattr/tree operations and the bytefield encoder's release logic.

## Risks
The mask-driven wire format is highly order-sensitive. Any new mask or field requires protocol version updates, max-size updates, release-path updates, and compatibility tests. Decode trusts counts such as `dfile_count`, `mirror_copies_count`, bitmap size, and server count before allocating. `PVFS_STATIC_ATTR_MASK` defines fields that should not change after creation, so setter code must respect it outside this header. Extra-size constants must remain conservative for `PINT-le-bytefield.c` preallocation.

## Test Signals
Round-trip `PVFS_object_attr` for metafile, datafile, directory, symlink, stuffed/unstuffed, mirrored, distributed-directory, and capability combinations; fuzz masks with inconsistent object types; memory-check release of all decoded nested allocations; validate max encoded sizes at protocol limits; and require protocol-version review for every field or mask change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/pvfs2-attr.h -->
