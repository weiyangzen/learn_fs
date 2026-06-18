## sources/distributed-fs/openafs/src/libacl/prs_fs.h

Purpose: `prs_fs.h` defines AFS directory/file ACL rights bit masks used by filesystem ACL tools, tests, and server-side ACL checks.

Important constants: base rights are `PRSFS_READ`, `PRSFS_WRITE`, `PRSFS_INSERT`, `PRSFS_LOOKUP`, `PRSFS_DELETE`, `PRSFS_LOCK`, and `PRSFS_ADMINISTER`. User-reserved high bits `PRSFS_USR0` through `PRSFS_USR7` occupy `0x01000000` through `0x80000000`.

State and persistence: rights masks are part of ACL persisted and transmitted state.

Dependencies and integration points: used by ACL tests and filesystem command code to translate symbolic rights like read/write/all into masks.

Risks: high user bits overlap the sign bit for `PRSFS_USR7` when interpreted as signed `int`; callers should treat rights as masks, not signed numeric values.

Test signals: `libacl/test/acltest.c` uses these constants in its `Convert` and `PRights` helpers.
