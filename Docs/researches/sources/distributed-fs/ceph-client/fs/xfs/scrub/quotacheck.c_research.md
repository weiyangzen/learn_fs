# sources/distributed-fs/ceph-client/fs/xfs/scrub/quotacheck.c

## Purpose
`quotacheck.c` implements live quota counter scrub. It recomputes user, group, and project quota usage by scanning every inode, tracks live quota transaction deltas, and compares the observed counters against incore dquots and quota CHKD flags.

## Important APIs, Types, And Functions
`xchk_setup_quotacheck` allocates `struct xqcheck` and enables quota fsgates. `xchk_quotacheck` runs setup, collection, and comparison. Live transaction tracking uses `struct xqcheck_dqtrx`, `struct xqcheck_dqacct`, `xqcheck_get_dqtrx`, `xqcheck_mod_live_ino_dqtrx`, and `xqcheck_apply_live_dqtrx`. Collection uses `xqcheck_collect_inode` and `xqcheck_collect_counts`; comparison uses `xqcheck_compare_dquot`, `xqcheck_compare_dqtype`, and `xqcheck_walk_observations`.

## Control Flow
Setup creates `xfarray` counter tables for each enabled quota type, initializes an rhashtable keyed by transaction id, starts an inode scan, and installs quota transaction hooks. The mod hook records per-transaction dquot deltas only for quota types being checked and only for inodes already scanned. The apply hook applies committed deltas to shadow counts and frees shadow transaction records when all dquot updates have applied.

Collection cancels the ordinary transaction and scans inodes under an empty transaction. Metadata and quota inodes are skipped. Regular files take IOLOCK and MMAPLOCK; realtime files read data fork extents so data and realtime blocks can be separated. The inode's user/group/project ids update the corresponding shadow dquot counters.

Comparison first checks that the CHKD flag is set for each quota type. It iterates existing dquots and compares inode, data block, and realtime block counts. Then it walks all observed shadow dquots to catch ids that should exist but are missing from the quota file.

## State And Persistence Behavior
Scrub is read-only but uses extensive volatile state: shadow dquot arrays, an iscan cursor, a mutex, quota hooks, and a transaction-id rhashtable. Hook or storage errors abort the iscan and mark scrub incomplete to prevent repair from using partial counts.

## Dependencies And Integration Points
It depends on quota transaction hook infrastructure, inode scanning, block counting, dquot iteration, xfarray, rhashtable, and `quotacheck.h`. Repair in `quotacheck_repair.c` reuses the live observation data.

## Risks And Edge Cases
Missing live deltas would create false corruption, so hook ordering installs the apply hook before the mod hook and removes hooks in reverse-safe order. Sparse-array `EFBIG`, allocation failure, busy inode scans, and hook errors all mark incomplete. Delayed allocation deltas are included with block deltas during commit shadowing. Quota files and metadata directory inodes are intentionally excluded from usage.

## Test Signals
Tests should include live writes, truncates, ownership changes, delayed allocation conversion, realtime files, quota CHKD flag cleared, missing dquots for observed ids, all combinations of enabled quota types, and injected hook allocation failures.
