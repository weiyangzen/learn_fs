# sources/distributed-fs/ceph-client/fs/ocfs2/filecheck.h

Purpose: defines the OCFS2 online file-check sysfs API data model, status codes, queue sizing limits, and lifecycle declarations.

Important APIs and types: declares filecheck error constants from `OCFS2_FILECHECK_ERR_SUCCESS` through `OCFS2_FILECHECK_ERR_UNSUPPORTED`, queue limits `OCFS2_FILECHECK_MAXSIZE` and `OCFS2_FILECHECK_MINSIZE`, operation types `OCFS2_FILECHECK_TYPE_CHK`, `OCFS2_FILECHECK_TYPE_FIX`, and `OCFS2_FILECHECK_TYPE_SET`, `struct ocfs2_filecheck`, `struct ocfs2_filecheck_sysfs_entry`, `ocfs2_filecheck_create_sysfs`, and `ocfs2_filecheck_remove_sysfs`.

Control flow: no active control flow. The enums drive `filecheck.c` parsing and status rendering for `check`, `fix`, and `set` sysfs files.

State and persistence behavior: `struct ocfs2_filecheck` holds transient queue/list state protected by a spinlock. `struct ocfs2_filecheck_sysfs_entry` embeds the kobject and completion used to coordinate sysfs lifetime with superblock teardown.

Dependencies and integration points: includes Linux list/types support and is consumed by OCFS2 superblock lifecycle and `filecheck.c`. Error codes are intentionally distinct from normal negative errno so they can describe domain-specific filecheck outcomes.

Risks: error enum ordering must match the string table in `filecheck.c`. Queue limits are part of sysfs behavior and tests may depend on them. Teardown requires all entries to be complete before freeing.

Test signals: compile coverage, enum-to-string mapping, queue max/min behavior, sysfs kobject lifetime, and all defined status codes surfaced through check/fix result output.
