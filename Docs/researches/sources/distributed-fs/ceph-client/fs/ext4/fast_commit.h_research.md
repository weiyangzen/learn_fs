# sources/distributed-fs/ceph-client/fs/ext4/fast_commit.h

## Purpose
`fast_commit.h` defines the shared on-disk and kernel-private data contracts for ext4 fast commits. The header explicitly notes that the kernel copy and the e2fsprogs/libext2fs copy must remain byte-identical, making this file part of both kernel recovery behavior and userspace filesystem tooling compatibility.

## Important APIs, types, and functions
The wire-format definitions are `EXT4_FC_TAG_ADD_RANGE`, `DEL_RANGE`, `CREAT`, `LINK`, `UNLINK`, `INODE`, `PAD`, `TAIL`, and `HEAD`; `EXT4_FC_SUPPORTED_FEATURES`; and TLV payload structures `struct ext4_fc_tl`, `ext4_fc_head`, `ext4_fc_add_range`, `ext4_fc_del_range`, `ext4_fc_dentry_info`, `ext4_fc_inode`, and `ext4_fc_tail`. Kernel-only state includes `struct ext4_fc_dentry_update`, `struct ext4_fc_stats`, `struct ext4_fc_alloc_region`, and `struct ext4_fc_replay_state`. The header also defines status codes, ineligibility reason codes, `EXT4_FC_REPLAY_REALLOC_INCREMENT`, `region_last()`, and `tag2str()`.

## Control flow
The commit path in `fast_commit.c` serializes the TLV payloads defined here, and the replay path validates and decodes them. Dentry payloads store parent inode, target inode, and variable-length name bytes. Inode payloads store inode number plus raw inode bytes. Range payloads describe either an extent-shaped add or logical deletion interval. TAIL payloads close atomic commit units by carrying tid and CRC.

## State and persistence behavior
All non-`__KERNEL__` structures are persistent ABI. Field sizes, endian annotations, tag values, and payload lengths must not drift from e2fsprogs. Kernel-only replay arrays dynamically track excluded physical regions and modified inodes so recovery can avoid accidental block reuse and later repair allocation bitmaps.

## Dependencies and integration points
This header is included by ext4 kernel fast commit code and mirrored into e2fsprogs. It depends on ext4 scalar types, list heads, and name snapshots under `__KERNEL__`, and on the broader fsmap owner namespace for no direct part.

## Risks and test signals
Risks are ABI drift between kernel and userspace, endian/packing mistakes, accepting unsupported feature bits, ineligibility reason/table mismatches, and assuming a fixed inode payload size despite extra inode fields. Test signals include byte-for-byte comparison with e2fsprogs, replay of every TLV type, fuzzed TLV lengths, unknown tag handling, unsupported feature handling, and debug output that exercises `tag2str()`.
