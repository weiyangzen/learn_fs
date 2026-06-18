# sources/distributed-fs/ceph-client/fs/quota/quotaio_v1.h

Purpose: Defines the old VFS quota on-disk record layout and default grace-time constants used by `quota_v1.c`.

Important APIs, types, and functions: Defines `MAX_IQ_TIME`, `MAX_DQ_TIME`, `struct v1_disk_dqblk`, and the offset macro `v1_dqoff(UID)`.

Control flow: The macro computes direct array offsets for v1 quota records. `quota_v1.c` reads and writes records at those offsets and interprets id zero as the source of default grace times.

State and persistence: The disk structure stores 32-bit block limits, current blocks, inode limits, inode usage, and `unsigned long` block/inode grace timers. The `unsigned long` fields make the old format architecture-sensitive.

Dependencies and integration points: Included by `quota_v1.c`; depends only on Linux integer types. It represents the persistent ABI for old external quota files.

Risks and test signals: Risks include on-disk incompatibility across 32-bit and 64-bit systems and direct offset overflow for large ids. Test old quota files created by legacy tools, cross-architecture behavior, and exact record offset calculations.
