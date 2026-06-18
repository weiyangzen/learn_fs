# sources/distributed-fs/ceph-client/fs/quota/quota_v2.c

Purpose: Registers and implements VFS quota formats v2r0 (`QFMT_VFS_V0`) and v2r1 (`QFMT_VFS_V1`) on top of the shared quota tree storage engine.

Important APIs, types, and functions: Defines qtree format operations for v2r0 and v2r1, header parsing `v2_read_header()`, validation `v2_check_quota_file()`, info load/store `v2_read_file_info()` and `v2_write_file_info()`, disk/memory conversion for `v2r0_disk_dqblk` and `v2r1_disk_dqblk`, dquot operations `v2_read_dquot()`, `v2_write_dquot()`, `v2_release_dquot()`, `v2_get_next_id()`, and registration for both format ids.

Control flow: Quota-on validates magic and version, reads `v2_disk_dqinfo`, allocates `qtree_mem_dqinfo`, sets limits according to version width, chooses record size and conversion ops, and sanity-checks block counts and free-list heads against quota file size. Reads/writes/release/enumeration delegate to `quota_tree.c` under `dqio_sem`; writes take exclusive I/O locking only if a new entry must be allocated.

State and persistence: Persistent state includes v2 header, info header, qtree metadata, and little-endian dquot entries. v2r0 stores 32-bit inode and block limits plus 64-bit current space; v2r1 expands most counters and limits to 64 bits. Both encode all-zero disk records by setting `dqb_itime` to one so unused slots can still be detected.

Dependencies and integration points: Integrates with generic dquot core through `quota_format_ops`, uses `quota_tree` for storage, `quotaio_v2.h` for ABI structs, filesystem quota read/write, `dqio_sem`, and id mapping through init user namespace ids.

Risks and test signals: Risks include accepting corrupt tree metadata, version/format mismatch, all-zero entry escape mistakes, limit truncation in v2r0, and free-list corruption. Test v0 and v1 quota files, project quota magics, corrupted block counters, get-next-id scans, new dquot allocation, zero-limit records, and 64-bit limits.
