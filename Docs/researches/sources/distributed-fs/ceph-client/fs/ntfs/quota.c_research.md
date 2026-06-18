# sources/distributed-fs/ceph-client/fs/ntfs/quota.c

## Purpose
`quota.c` marks NTFS quota metadata out of date so Windows can rescan quota entries after Linux-side changes.

## Important API
The only exported function is `ntfs_mark_quotas_out_of_date(struct ntfs_volume *vol)`.

## Control Flow and State
The function exits early if the volume is already marked quota-out-of-date. Otherwise it requires open quota inodes, locks `vol->quota_q_ino`, opens its `I30` index, looks up `QUOTA_DEFAULTS_ID`, validates the entry size and `QUOTA_VERSION`, and checks quota flags. If tracking is enabled/requested or pending deletes exist, it sets `QUOTA_FLAG_OUT_OF_DATE` in the quota defaults entry and marks the index entry dirty. It then sets the in-memory volume flag `NVolSetQuotaOutOfDate()` to avoid repeated attempts.

## Dependencies and Integration
This code depends on quota layout structures from NTFS layout headers, index context APIs, volume flags, inode locking, and NTFS logging. It is intended for volume-level metadata consistency rather than normal VFS quota enforcement.

## Risks
If quota inodes are not open, the function returns false. It does not mark the containing MFT record dirty directly, relying on index dirty handling. Unsupported quota versions, missing defaults entries, or short entries prevent marking and may leave Windows quota state stale.

## Test Signals
Test volumes with quota tracking enabled, disabled, pending deletes, missing quota inodes, missing defaults entry, unsupported versions, and repeated calls after the in-memory out-of-date flag is set. Verify the defaults index entry is dirtied only when flags change.
