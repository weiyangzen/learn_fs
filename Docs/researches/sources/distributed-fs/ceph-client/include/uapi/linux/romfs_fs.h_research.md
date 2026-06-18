<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/romfs_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/romfs_fs.h

Purpose: describes the on-disk ROMFS filesystem superblock and inode layouts plus constants used by kernel and tooling that parse or create ROMFS images.

Important APIs, types, and functions: `ROMBSIZE`, `ROMBSBITS`, and `ROMBMASK` map ROMFS block alignment to Linux block size definitions. `ROMFS_MAGIC`, `ROMSB_WORD0`, and `ROMSB_WORD1` identify the `-rom1fs-` magic words in big-endian form. `struct romfs_super_block` contains magic words, image size, checksum, and a flexible volume name. `struct romfs_inode` contains next inode pointer/type bits, device/spec data, file size, checksum, and a flexible name. `ROMFH_*` constants encode inode type and execute flag in the low bits of `next`; `ROMFH_SIZE`, `ROMFH_PAD`, and `ROMFH_MASK` define 16-byte alignment.

Control flow: the ROMFS mount/parser path reads the superblock, validates magic and checksum, walks inode records using the aligned `next` field, decodes the low type bits with `ROMFH_TYPE`, and interprets `spec`/`size` according to hardlink, directory, regular, symlink, block, char, socket, or FIFO type.

State and persistence behavior: all represented state is persistent image data. The header has no functions and no runtime state. The flexible array members mean callers must treat the fixed struct as a prefix and bounds-check volume/file names against image size and alignment.

Dependencies and integration points: depends on `linux/types.h` for big-endian integer types and `linux/fs.h` for block-size constants. It integrates with the ROMFS filesystem driver and image creation/inspection tools that need exact disk-format compatibility.

Risks and edge cases: name and inode records are variable length and alignment-sensitive. Endianness must be honored; `__mk4` builds big-endian constants. The low bits of `next` carry type flags, so code must mask before following offsets. Corrupt checksums, unterminated names, and offsets outside image size are the main parser risks.

Test signals: mount known-good ROMFS images, fuzz superblock/inode lengths and checksums, validate big-endian decoding on little-endian hosts, test every `ROMFH_*` type, and compare mkromfs output with kernel mount traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/romfs_fs.h -->
