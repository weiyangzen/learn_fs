# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dquot_buf.c

## Purpose
`xfs_dquot_buf.c` verifies, repairs, and converts on-disk quota records and implements quota inode loading/creation for both legacy superblock quota inode pointers and metadata-directory quota files. It protects quota buffers during read/write/readahead and maps quota health failures to filesystem sickness flags.

## Important APIs, Types, and Functions
Important functions include `xfs_calc_dquots_per_chunk`, `xfs_dquot_verify`, `xfs_dqblk_verify`, `xfs_dqblk_repair`, buffer verifier callbacks for `xfs_dquot_buf_ops` and `xfs_dquot_buf_ra_ops`, timestamp conversion helpers `xfs_dquot_from_disk_ts` and `xfs_dquot_to_disk_ts`, `xfs_dqinode_sick_mask`, `xfs_dqinode_load`, `xfs_dqinode_metadir_create`, userspace-only `xfs_dqinode_metadir_link`, `xfs_dqinode_mkdir_parent`, and `xfs_dqinode_load_parent`.

## Control Flow
`xfs_dquot_verify` validates the embedded `struct xfs_disk_dquot`: magic, version, quota type mask and record type, bigtime compatibility, id consistency when an expected id is provided, and soft-limit timer invariants for nonzero ids. `xfs_dqblk_verify` adds v5 UUID verification around the full `struct xfs_dqblk`. `xfs_dqblk_repair` zeroes a quota record, fills magic/version/type/id, and updates UUID/CRC on CRC-enabled filesystems.

Read verification first checks CRCs for every dquot in the buffer if metadata CRCs are enabled, using either `mp->m_quotainfo->qi_dqperchunk` or a manual chunk calculation during log recovery. It then verifies each dquot with monotonically increasing ids starting at the first record's id. Readahead verification suppresses detailed reporting and marks the buffer not done on failure so a later real read will report through normal verifier paths. Write verification checks structure only because dquot CRCs are refreshed when dquots are flushed into the buffer.

Quota inode loading branches on metadir support. Without metadir, it selects the superblock quota inode field for user/group/project quota, rejects `NULLFSINO`, and calls `xfs_trans_metafile_iget`. With metadir, it resolves a path under `/quota` via `xfs_metadir_load`. Loaded quota inodes must use extents or btree data forks and project id zero; failures mark the corresponding quota sick mask. Metadir create/link helpers wrap metadata directory updates, log inode core, commit, and finish inode setup.

## State and Persistence
Persistent state includes arrays of `struct xfs_dqblk` in quota files, each containing a disk dquot, UUID, and CRC on modern filesystems. Quota inode state may live in legacy superblock inode fields or metadir entries under `quota`. The file itself does not mutate quota counters except repair initialization and metadir inode creation/linking; it verifies and logs metadata inode creation through transaction helpers.

## Dependencies and Integration Points
Dependencies include quota type definitions, mount quota info, CRC helpers, buffer verifier APIs, bigtime conversion, metadata inode lookup, metadir operations, health reporting, and transaction logging. It integrates with log recovery by supporting verification before quota info is initialized.

## Risks and Test Signals
Risks include false corruption reports during quotaoff/log recovery, accepting quota records with invalid timers, mishandling bigtime flags on filesystems without bigtime, and loading a non-quota inode as a quota file. Test signals include quotaon/quotacheck after crash recovery, CRC corruption injection, metadir quota creation/load, legacy quota inode loading, user/group/project type coverage, bigtime quota timers, and readahead verifier behavior.
