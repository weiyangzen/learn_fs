# sources/distributed-fs/ceph-client/fs/quota/quota_tree.h

Purpose: Defines the on-disk header used at the start of VFS v2 quota data blocks and the block offset of the quota tree root.

Important APIs, types, and functions: Declares `struct qt_disk_dqdbheader` with little-endian `dqdh_next_free`, `dqdh_prev_free`, `dqdh_entries`, and padding fields. Defines `QT_TREEOFF` as block 1.

Control flow: This header is consumed by `quota_tree.c` when interpreting blocks that contain quota entries. Data blocks use the header to participate in the list of blocks with free entries and to count valid entry slots.

State and persistence: The structure is persisted inside quota files. It is intentionally padded to 16 bytes, which aligns the following quota entries and fixes the usable entry count for the historical v2 block layout.

Dependencies and integration points: Included by `quota_tree.c` and `quota_v2.c`. It depends only on basic Linux types and quota definitions.

Risks and test signals: Risks are ABI/layout changes and endian mistakes, since on-disk quota files depend on exact field sizes. Test by validating quota files written on one endian/word-size environment can be read with expected free-list and entry counts.
