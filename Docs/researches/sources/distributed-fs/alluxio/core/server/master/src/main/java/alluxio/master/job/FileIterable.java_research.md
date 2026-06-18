# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/FileIterable.java

## Purpose
`FileIterable` provides scheduler jobs with an iterable stream of `FileInfo` objects produced by `FileSystemMaster`. It supports full recursive listing or bounded partial listing and applies a caller-supplied filter, primarily for load jobs.

## Important APIs, types, and functions
The constructor captures `FileSystemMaster`, path, optional user, partial-listing flag, and filter. `iterator()` returns a new `FileIterator`. The inner iterator checks access, lists status through `listStatus`, supports `PARTIAL_LISTING_BATCH_SIZE = 100`, maintains `mStartAfter`, and tracks current-batch file and byte counts.

## Control flow
On construction the iterator sets `AuthenticatedClientUser`, checks access, then either fully lists recursively or begins partial listing. `hasNext()` and `next()` trigger another partial listing when the current iterator is exhausted. `partialListFileInfos` loops through list-status batches until it finds filtered results or reaches an empty batch, updating `startAfter` and disabling descendant-loaded checks after the first batch.

## State and persistence behavior
Iteration state is runtime-only: current batch list, current iterator, `startAfter`, and counters. No journal entries are produced. Full listing materializes the filtered list at once; partial listing bounds memory per batch.

## Dependencies and integration points
It depends on `FileSystemMaster`, list/check-access contexts, `AuthenticatedClientUser`, Alluxio exceptions converted to runtime exceptions, and wire `FileInfo`/block info. `LoadJobFactory` and `JournalLoadJobFactory` build it with `LoadJob.QUALIFIED_FILE_FILTER`.

## Risks
`checkAccess` sets the authenticated user but does not remove it in a finally block, unlike `listStatus`; this can leak thread-local user context. Partial listing updates `mStartAfter` to the last filtered file rather than always the last raw file when filtered results exist, which should be examined for skipped or repeated entries depending on list API semantics. Counters are reset to each batch, not cumulative.

## Test signals
Tests should cover access denied/not found conversion, full and partial listing, filters that skip many batches, empty results, user context cleanup, batch boundary `startAfter`, and file byte-count calculations for blocks without locations.
