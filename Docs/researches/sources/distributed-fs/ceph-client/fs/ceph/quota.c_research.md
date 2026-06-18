<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/quota.c -->
# sources/distributed-fs/ceph-client/fs/ceph/quota.c

## Purpose
`quota.c` implements client-side CephFS quota awareness. It receives quota updates from the MDS, tracks whether quota realms exist, locates quota realm inodes even when they are outside the visible mount subtree, checks max-files and max-bytes limits before creates/writes, compares quota realms for rename/link decisions, and adjusts `statfs` output when the mounted root is governed by a byte quota.

## Important APIs, types, and functions
Public functions are `ceph_adjust_quota_realms_count`, `ceph_handle_quota`, `ceph_cleanup_quotarealms_inodes`, `ceph_quota_is_same_realm`, `ceph_quota_is_max_files_exceeded`, `ceph_quota_is_max_bytes_exceeded`, `ceph_quota_is_max_bytes_approaching`, and `ceph_quota_update_statfs`.

Important internal helpers include `ceph_has_realms_with_quotas`, `find_quotarealm_inode`, `lookup_quotarealm_inode`, `get_quota_realm`, and `check_quota_exceeded`. The file uses `struct ceph_quotarealm_inode` nodes stored in `mdsc->quotarealms_inodes` to cache lookup results and recent lookup failures.

## Control flow
Quota update messages enter through `ceph_handle_quota`. The handler validates message length, finds the target inode by vino, and updates recursive byte/file/subdirectory counts plus max byte/file quotas under the inode's Ceph lock. It uses MDS stopping blockers so teardown does not race the message handler.

Quota checks first call `ceph_has_realms_with_quotas` to avoid expensive snaprealm walks when there are no known quotas and the mount root is the real CephFS root. If quotas may exist, `check_quota_exceeded` walks from the inode's snap realm toward the root under `snap_rwsem`, obtains the realm inode either from `realm->inode` or by temporarily dropping the rwsem and performing an MDS lookup, then checks the requested operation against recursive values and max limits. Max-byte "approaching" returns true when a write would consume more than one sixteenth of remaining quota space, allowing writeback/reporting paths to refresh quota state early.

`get_quota_realm` performs a similar snaprealm walk but returns the first realm with a requested quota type, or the root realm. Because hidden realm inode lookup may drop `snap_rwsem`, callers can request retry or receive `-EAGAIN` and restart atomic multi-realm comparisons. `ceph_quota_is_same_realm` uses that behavior to compare two inodes' quota realms safely. `ceph_quota_update_statfs` finds the root quota realm and rewrites block counts/free counts using quota bytes, including special handling for quotas smaller than the normal block size.

## State and persistence behavior
Quota values are cached in `ceph_inode_info` fields such as recursive bytes/files/subdirs and max bytes/files. `mdsc->quotarealms_count` tracks known quota-bearing realms. `mdsc->quotarealms_inodes` caches hidden quota realm inodes and lookup failure timeouts until unmount; cleanup iputs cached inodes and frees nodes. This is runtime cache state only. Authoritative quota state lives on the MDS and is pushed or fetched as needed.

## Dependencies and integration points
The quota code depends on the MDS client, snap realm locking and reference helpers, inode lookup/getattr helpers, Ceph inode quota helpers (`__ceph_update_quota`, `__ceph_has_quota`), VFS inode and statfs APIs, jiffies timeouts, rbtrees, and MDS stopping blockers. It integrates with create/write paths for limit checks, rename/link logic through realm comparison, statfs reporting, and `mds_client.c` dispatch of `CEPH_MSG_CLIENT_QUOTA`.

## Risks and test signals
Risks include deadlocks or races while dropping and reacquiring `snap_rwsem`, stale hidden realm inode lookup failures due to the fixed 60-second timeout, false negatives when `i_snap_realm` is temporarily null after cap loss, quota overshoot from concurrent clients, overflow in `rvalue + delta`, incorrect statfs scaling for very small quotas, and realm comparison restarts that leak snap realm references. Test signals include quota update messages for visible and hidden inodes, creates at and above max-files, extending/truncating writes around max-bytes, approaching-threshold behavior, renames across quota realms, statfs under root quota smaller than 4 MB and 4 KB, missing realm inode lookup with retry, snap realm parent traversal, unmount cleanup of cached realm inodes, and reserved/stray inode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/quota.c -->
