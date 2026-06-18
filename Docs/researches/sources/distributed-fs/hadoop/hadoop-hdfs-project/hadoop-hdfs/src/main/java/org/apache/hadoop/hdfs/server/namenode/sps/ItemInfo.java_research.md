# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/ItemInfo.java

## Purpose

`ItemInfo` is the small value object SPS uses to track a file needing storage policy satisfaction and the original start path that caused it to be queued.

## Important APIs, Types, And Functions

It stores `startPathId`, `fileId`, and `retryCount`. Constructors initialize retry count to zero or a supplied value. Accessors are `getStartPath`, `getFile`, `isDir`, `getRetryCount`, and `increRetryCount`.

## Control Flow

Directory scans create `ItemInfo` for child files with `startPathId` set to the directory request and `fileId` set to the child file. File-level SPS requests use the same ID for both. Attempted-item retry paths construct new `ItemInfo` objects with incremented retry counts before requeueing them for policy recheck.

## State And Persistence Behavior

`ItemInfo` is transient in-memory queue state and is not serialized. The durable association with a user SPS request is held externally by SPS hints/xAttrs for the start path.

## Dependencies And Integration Points

It is used by `BlockStorageMovementNeeded`, `BlockStorageMovementAttemptedItems`, and `SPSService` queue APIs. It has no dependencies beyond Hadoop annotations.

## Risks And Edge Cases

`isDir` means "the item came from a directory start path", not that `fileId` itself is a directory. Fields are mutable only through retry increment, so callers creating retry objects must preserve the correct start/file IDs. There is no equality/hash implementation, so queue de-duplication cannot rely on object equality.

## Test Signals

Tests should verify constructor defaults, retry incrementing, `isDir` for file and directory-origin items, and retry requeue behavior preserving IDs.
