# sources/distributed-fs/ceph-client/fs/quota/quota_v1.c

Purpose: Registers and implements the old flat-file VFS quota format (`QFMT_VFS_OLD`) where quota records are stored as an array indexed directly by uid or gid.

Important APIs, types, and functions: Defines `v1_stoqb()`, `v1_qbtos()`, `v1_disk2mem_dqblk()`, `v1_mem2disk_dqblk()`, `v1_read_dqblk()`, `v1_commit_dqblk()`, `v1_check_quota_file()`, `v1_read_file_info()`, `v1_write_file_info()`, `v1_format_ops`, and module init/exit registration.

Control flow: Format checking verifies file size is a multiple of the old record size and rejects files that appear to contain newer v2 magics. Reads zero-fill a disk record, read the id-indexed slot, convert fields into `mem_dqblk`, and mark all-zero limits as fake. Commits convert memory fields back to disk, preserve root grace-time storage semantics for user/group root records, and write the indexed slot. File info reads and writes grace times from id 0.

State and persistence: Persistent records are `struct v1_disk_dqblk` slots at `v1_dqoff(id)`. Limits are stored in 1 KiB quota blocks and inode counts as 32-bit values; grace times are stored in the root record. There is no tree allocator or per-record release path.

Dependencies and integration points: Uses generic dquot core format registration, filesystem quota read/write callbacks, `dqio_sem`, `dq_data_lock`, and `quotaio_v1.h`. It supports user and group quotas only in the old format.

Risks and test signals: Risks include 32-bit limit overflow, word-size-dependent on-disk time fields, accidentally enabling old format on v2 files, and root grace-time compatibility. Test old quota files, bad file sizes, v2 magic rejection, root id grace changes, and large limits near `0xffffffff`.
