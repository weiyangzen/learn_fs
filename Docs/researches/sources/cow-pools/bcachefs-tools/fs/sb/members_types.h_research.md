# File Research: sources/cow-pools/bcachefs-tools/fs/sb/members_types.h

Defines `struct bch_member_cpu`, the runtime endian-converted member cache. It stores bucket geometry, group/state, discard/data/durability flags, initialization state, resize and rotational flags, validity, and btree allocation bitmap data.

Used after superblock parsing to avoid repeated endian/bitfield extraction.
