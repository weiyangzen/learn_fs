# sources/distributed-fs/ceph-client/include/linux/f2fs_fs.h

Purpose: F2FS on-disk format definitions shared by kernel code and tooling-like users: superblock, checkpoint, NAT/SIT, node, summary, journal, and directory-entry layouts.

Important APIs/types/functions: block/segment constants, sentinel block addresses, inode-number macros, stop-checkpoint and corruption enums, `struct f2fs_super_block`, checkpoint flags and `struct f2fs_checkpoint`, orphan blocks, node/inode/direct/indirect layouts, NAT/SIT structures and macros, summary/journal structures, dentry hash/slot constants, `struct f2fs_dir_entry`, and `struct f2fs_dentry_block`.

Control flow: mount/recovery code reads superblock and checkpoint packs, validates flags/checksums, reconstructs orphan/NAT/SIT/summary state, and interprets node/dentry blocks through these packed little-endian structures. Runtime allocation and recovery update persistent checkpoint, segment, NAT/SIT, and journal metadata.

State/persistence: nearly every structure here is persistent on-disk metadata. It tracks filesystem geometry, feature flags, checkpoint versions, valid block/inode counts, current segments, orphan inode lists, inode inline/compression attributes, NAT node-to-block mappings, SIT segment validity/age, and directory entries.

Dependencies/integration: page/block size assumptions, endian helpers, F2FS core mount/recovery/GC/directory code, compression, quota, encryption, project IDs, fsck compatibility.

Risks/test signals: risks are packed layout drift, page-size dependent geometry, endian mistakes, feature/checkpoint flag misinterpretation, flexible/zero-length placeholder misuse, corruption reason array bounds, and malformed directory slots. Test mount/fsck of varied F2FS images, crash recovery, orphan handling, compression/inline xattrs, NAT/SIT journal replay, large page sizes, and corrupt metadata fuzzing.
