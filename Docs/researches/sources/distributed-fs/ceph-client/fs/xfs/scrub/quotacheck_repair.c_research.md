# sources/distributed-fs/ceph-client/fs/xfs/scrub/quotacheck_repair.c

## Purpose
`quotacheck_repair.c` commits quota counters recomputed by live quotacheck to the actual dquots and manages quota CHKD flags so crash recovery can fall back to mount-time quotacheck if repair is interrupted.

## Important APIs, Types, And Functions
`xrep_quotacheck` is the repair entry point. `xqcheck_commit_dquot` adjusts one dquot from observed `xqcheck_dquot` data. `xqcheck_commit_dqtype` commits all known and observed dquots for one type. `xqcheck_chkd_flags` computes which quota CHKD flags correspond to currently running quota types.

## Control Flow
Repair first clears the CHKD flags for all active quota types and commits, making the filesystem conservatively require quotacheck if a crash occurs mid-repair. It then commits user, group, and project counters where corresponding observation arrays exist. For each quota type it first iterates dquots known to the quota file, then walks the observation array to create or repair dquots that were observed but not previously scanned. Each dquot commit allocates a scrub transaction, joins and locks the dquot, reads the observed counters, adjusts count and reserved fields by deltas, marks the observation repaired, logs dirty dquots, adjusts timers, and commits.

After all dquots are repaired, it allocates a final transaction, restores CHKD flags, and commits.

## State And Persistence Behavior
Persistent changes include dquot counts, reservations, timers, dirty dquot log items, newly allocated dquots for observed ids, and superblock quota CHKD flags. The repair uses the volatile `xqcheck` arrays from scrub as authoritative input.

## Dependencies And Integration Points
It depends on quota manager dquot lookup/allocation, transaction commit/cancel helpers, `quotacheck.h`, tracepoints, and superblock qflag update helpers. It is the repair companion to `quotacheck.c`.

## Risks And Edge Cases
If the live scan was aborted, commits return `-ECANCELED`. A crash after CHKD flags are cleared but before final restoration intentionally leaves mount-time quotacheck as the recovery path. Observed dquot ids absent from the quota file may allocate quota blocks. Negative deltas adjust reservations and counts together, so underflow-sensitive data should be tested.

## Test Signals
Tests should cover interrupted repair with CHKD flags cleared, creating missing observed dquots, count increases and decreases, timer adjustment for nonzero ids, all enabled quota-type combinations, and aborted/incomplete scan repair rejection.
