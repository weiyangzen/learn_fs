# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/BatchPathWaiter.java

Purpose: `BaseTask` implementation that lets callers wait until a specific path falls within a completed loaded range. It is used for single-listing and non-directory-recursive sync modes.

Important APIs and types: maintains `mLastCompleted`, a sorted list of `PathSequence` intervals, plus a sentinel `mNoneCompleted`. `waitForSync` blocks until completion or until a path is covered by the first completed interval. `nextCompleted` merges newly completed path ranges into the interval list.

Control flow: every processed `SyncProcessResult` with a loaded sequence is passed to `nextCompleted`. The method detects adjacent intervals on left and right and either inserts, extends, or merges ranges, then notifies waiters. Waiters return task success if the whole task completes before their path is individually covered.

State and persistence behavior: in-memory progress only. It gates client traversal while background sync continues but does not write metadata directly.

Dependencies and integration points: depends on `PathSequence`, `SyncProcessResult`, `AlluxioURI` ordering, and `BaseTask` lifecycle. It is selected by `BaseTask.create`.

Risks: correctness relies on `AlluxioURI.compareTo` matching the ordering used by UFS listings and inode iteration. Interval merge edge cases can cause waiters to block too long or proceed early. The sentinel object is compared by identity, so replacing it would break the initial-state check.

Test signals: tests should cover disjoint interval insertion, left/right/both-side merge, waiting for covered and uncovered paths, interrupted waits, and final completion behavior.
