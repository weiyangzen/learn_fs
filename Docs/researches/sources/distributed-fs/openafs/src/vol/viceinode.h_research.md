# sources/distributed-fs/openafs/src/vol/viceinode.h

## Purpose

`viceinode.h` defines the parameter layout OpenAFS uses to encode fileserver inode metadata. It is a compact contract between the volume package, salvager/fsck-style tools, and platform-specific inode/namei implementations.

## Important Types and Constants

`struct InodeParams` describes ordinary vnode data inodes with `volumeId`, `vnodeNumber`, `vnodeUniquifier`, and `inodeDataVersion`. `struct SpecialInodeParams` describes volume special inodes with `volumeId`, `vnodeNumber` set to `INODESPECIAL`, parent id, and type; field order differs under `AFS_3DISPARES`.

`struct ViceInodeInfo` is the fsck output record: inode number, byte count, link count, and a union exposing raw parameters or the ordinary/special interpretations. `INODESPECIAL` is platform-dependent, and special inode type ids include `VI_VOLINFO`, `VI_SMALLINDEX`, `VI_LARGEINDEX`, `VI_ACL`, `VI_MOUNTTABLE`, and `VI_LINKTABLE`.

## State and Persistence Behavior

These structures describe persisted inode identity. Ordinary inodes are tied to a volume/vnode/unique/data-version tuple; special inodes represent the volume info file, vnode index files, ACL/mount/link tables, and other metadata. The values are interpreted by salvage, volume inspection, and inode-handle code rather than manipulated here.

## Dependencies and Integration Points

The header assumes OpenAFS typedefs such as `VolumeId`, `VnodeId`, `Unique`, `FileVersion`, `Inode`, `afs_fsize_t`, and `bit32` are already available through volume headers. It is included by volume cache and scanner code even when those files do not directly use the structs, because inode identity is part of volume package context.

## Risks and Test Signals

The largest risk is ABI and on-disk compatibility. Reordering special inode fields, changing `INODESPECIAL`, or changing special type numbering can break fsck/salvage interpretation. Tests should decode known fsck records for both ordinary and special inodes, including `AFS_3DISPARES` builds, and verify special type ids match `vutil.h` expectations.
