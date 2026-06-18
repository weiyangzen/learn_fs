# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/BackupManager.java

## Purpose
`BackupManager` creates gzip backups from all master journal entries and restores master state from such backups.

## Important APIs, Types, And Functions
`backup(OutputStream, AtomicLong)` streams journal entries from every registered master to a gzip output stream using reader/writer tasks and a bounded queue. `initFromBackup(InputStream)` reads gzip-delimited journal entries, maps each entry to its owning master via `JournalEntryAssociation`, and applies/journals batches through per-master `JournalContext`s. `safeWaitTasks` coordinates worker failures and cancellation.

## Control Flow, State, Dependencies, Risks, And Tests
Backup registers gauges for last backup/restore counts and durations. Backup writes a termination sentinel sequence number and finishes, not closes, the caller-owned stream. Restore schedules progress logging, drains batches, opens contexts for all masters, applies entries, then closes contexts to flush. Persistent behavior is serialized gzip journal entries and restored master journal/state. Dependencies include `MasterRegistry`, `JournalEntryStreamReader`, gzip streams, metrics, executor services, and `JournalUtils`. Risks include partial backups if a writer fails late, unbounded per-drain list size, sentinel collision assumptions, restore fatality on unrecognized entries, and context creation for all masters per batch. Tests should cover backup/restore round trips, failure cancellation, corrupted/truncated input, master association, metrics, and queue backpressure.
