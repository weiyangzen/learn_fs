<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/PrefetchConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/PrefetchConstants.java

## Purpose
Centralizes prefetch implementation constants, currently the timeout used while acquiring cache-entry write locks during eviction and close.

## Important APIs, Types, And Functions
Defines package-private `PREFETCH_WRITE_LOCK_TIMEOUT = 5` and `PREFETCH_WRITE_LOCK_TIMEOUT_UNIT = TimeUnit.SECONDS`.

## Control Flow
No runtime control flow beyond class initialization. Constructor is private to prevent instantiation.

## State And Persistence
Contains only static constants. No mutable state or persistence.

## Dependencies And Integration Points
`SingleFilePerBlockCache` uses these constants when trying to acquire per-entry write locks before deleting cache files.

## Risks
The constants are package-private and fixed. If cache file deletion regularly blocks longer than five seconds, eviction/close logs errors and leaves files behind rather than waiting.

## Test Signals
Simulate held read locks in `SingleFilePerBlockCache` and verify eviction/close respects the configured five-second timeout path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/PrefetchConstants.java -->
