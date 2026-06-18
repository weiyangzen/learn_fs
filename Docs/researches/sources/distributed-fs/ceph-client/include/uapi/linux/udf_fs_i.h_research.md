# sources/distributed-fs/ceph-client/include/uapi/linux/udf_fs_i.h

Purpose: Exposes UDF filesystem-specific ioctl numbers for extended attributes, volume identification, and block relocation.

Important APIs/types/functions: `UDF_GETEASIZE` returns extended attribute size, `UDF_GETEABLOCK` reads EA block data, `UDF_GETVOLIDENT` reads the volume identifier, and `UDF_RELOCATE_BLOCKS` performs block relocation via `_IOWR('l', 0x43, long)`.

Control flow: Userspace issues ioctls against a UDF file or filesystem handle; the filesystem driver copies requested metadata or updates the relocation argument.

State and persistence behavior: Query ioctls are read-only. Relocation may alter on-disk block placement and is persistent if supported.

Dependencies and integration points: Integrates with the UDF filesystem driver and Linux ioctl numbering for filesystem-private range `'l', 0x40-0x7f`.

Risks: Pointer-typed ioctls must validate user buffers. Relocation is sensitive to filesystem consistency and media behavior.

Test signals: Mount UDF images, verify EA size/block and volume ID retrieval, fuzz invalid pointers/lengths, and test relocation on disposable images with fsck verification.
