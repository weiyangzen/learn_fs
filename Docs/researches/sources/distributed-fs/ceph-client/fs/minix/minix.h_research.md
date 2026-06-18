<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/minix.h -->
# sources/distributed-fs/ceph-client/fs/minix/minix.h

## Purpose
`minix.h` is the private Minix filesystem header. It defines in-memory Minix inode and superblock state, version constants, accessors, function prototypes shared across Minix source files, bitmap endian abstractions, and error-reporting helpers.

## Important APIs, Types, and Functions
`struct minix_inode_info` embeds VFS `struct inode`, a union of V1 16-bit and V2/V3 32-bit zone arrays, and `struct mapping_metadata_bhs` for metadata buffer tracking. `struct minix_sb_info` stores mount-wide values decoded from the on-disk superblock: inode/zone counts, bitmap block counts, first data zone, directory entry size/name length, bitmap buffer arrays, superblock buffer, mount state, and version. `minix_sb()` and `minix_i()` are the central typed accessors. Prototypes cover inode lookup/allocation/free, block allocation/free/counting, raw inode access, directory entry manipulation, getattr, truncate, block mapping, fsync, and operation tables.

## Control Flow
Other Minix files include this header to coordinate version dispatch. `INODE_VERSION(inode)` reads `s_version` from the superblock info and drives V1 versus V2/V3 raw inode and block tree decisions. Directory and inode operation tables declared here are installed by `minix_set_inode()` and the directory code. `minix_blocks_needed()` is used during mount validation to confirm bitmap capacity.

## State and Persistence Behavior
The header describes the in-memory shadow of persistent Minix metadata. The zone arrays are copied from and back to raw inode zone fields. `s_imap` and `s_zmap` hold buffer heads for persistent inode and zone allocation bitmaps. `s_mount_state` mirrors the clean/error state for V1/V2 filesystems. Bitmap helper macros abstract the persistent bitmap bit order for native-endian, big-endian 16-bit indexed, and little-endian configurations.

## Dependencies and Integration Points
The header depends on core VFS types, folios/page cache types, and UAPI Minix on-disk structures from `<linux/minix_fs.h>`. It is shared by `inode.c`, directory/name lookup code, bitmap code, file/dir operation code, and both indirect tree implementations.

## Risks
Because this header defines compile-time bitmap semantics, incompatible endian configuration is rejected with `#error`. Any mismatch between `minix_inode_info` zone array sizes and raw inode update loops can corrupt in-memory or on-disk zones. The prototypes expose legacy Minix assumptions such as old device numbers and non-idmapped ownership semantics.

## Test Signals
Build coverage across endian configuration options is important. Runtime signals include correct inode/superblock accessors under KASAN/UBSAN, bitmap allocation on little- and big-endian images, V1/V2/V3 version dispatch, and metadata fsync behavior through `mapping_metadata_bhs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/minix.h -->
