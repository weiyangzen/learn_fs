# File Research: sources/block-storage/parted/libparted/fs/f2fs/f2fs.h

Defines the f2fs superblock prefix needed for probing. Constants include `F2FS_MAGIC`, maximum volume-name length, and superblock sector offset `0x02`.

`struct f2fs_super_block` is packed and includes the magic, version, sector/block geometry logs, segment/section/zone counts, checkpoint/SIT/NAT/SSA/main block addresses, root/node/meta inode numbers, UUID, and UTF-16 volume name. The probe currently only reads `magic`, but the structure documents the adjacent on-disk fields and keeps alignment stable for future checks.

The header has a conventional include guard and no function declarations.
