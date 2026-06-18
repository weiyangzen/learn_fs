# sources/distributed-fs/ceph-client/fs/befs/super.c

Purpose: loads and validates the BeFS superblock from disk into host-endian in-memory state.

Important APIs/types/functions: `befs_load_sb` and `befs_check_sb`.

Control flow: load detects little- or big-endian format from `fs_byte_order`, converts magic, block geometry, allocation group fields, journal positions, and root/indices addresses. Check verifies magic values, supported block sizes, page-size compatibility, block-shift consistency, logs an allocation-group consistency warning, and rejects dirty/journal-not-empty filesystems.

State and persistence: populates `befs_sb_info` from persistent `befs_super_block`. No disk mutation occurs.

Dependencies and integration: called during `befs_fill_super()` after reading the candidate disk superblock; relies on endian helpers after byte order selection.

Risks: byte order must be detected before conversion. Dirty filesystem rejection prevents replay-less read of potentially inconsistent metadata.

Test signals: little/big-endian images; invalid magic/block size/block shift; dirty journal images should fail mount.
