# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataTest.java

## Purpose
This PowerMock unit test covers user-facing `FileSystemMaster` metadata sync behavior for object-store mounts, fingerprint updates, owner/group propagation, alluxio-only deletes, and directory status lookups. It uses a custom `SyncAwareFileSystemMaster` to detect accidental sync calls in delete paths.

## Important APIs, Types, and Functions
- `completeFileWithOutOfDateHash()` verifies a completed through-written file keeps the complete-time content hash until a forced sync refreshes it from UFS fingerprint metadata.
- `setAttributeOwnerGroupOnMetadataUpdate()` ensures sync refreshes owner/group from updated `UfsFileStatus`.
- `listStatusWithSyncMetadataAndEmptyS3Owner()` verifies empty S3 owner/group values are replaced with mount parent owner/group when loading directories and files.
- `deleteAlluxioOnlyNoSync()` asserts recursive `alluxioOnly` delete avoids `syncMetadata`.
- `getStatusOnDirectory()` confirms `getFileInfo` on a directory does not recursively load children.
- `setupMockUfsS3Mount()` creates `/mnt/local` over a mocked `s3a://bucket/` UFS.
- `SyncAwareFileSystemMaster` overrides `syncMetadata` to record whether a sync happened.

## Control Flow
The fixture starts a metrics master, block master, and custom file system master with a mocked `UnderFileSystem` returned by static factory calls. Individual tests configure mock UFS status, fingerprint, existence, file/directory type, and listing responses. Operations then use `createFile`, `completeFile`, `listStatus`, `getFileInfo`, `delete`, and `mount` through the normal master API.

## State and Persistence Behavior
The tests use a UFS journal and temporary mount root. Restart behavior is not the focus here, but journal-backed service setup ensures operations follow production master initialization. Observable state includes inode fingerprints, owner/group fields, inode IDs, mocked UFS invocation counts, and a boolean flag proving whether `syncMetadata` was invoked.

## Dependencies and Integration Points
The class ties `DefaultFileSystemMaster` to `BlockMaster`, `MetricsMaster`, `JournalSystem`, mocked `UnderFileSystem`, S3 `Fingerprint`, `UfsFileStatus`, `UfsDirectoryStatus`, `MountContext`, `ListStatusContext`, `GetStatusContext`, and `DeleteContext`. It also uses `ManuallyScheduleHeartbeat` for persistence checker scheduler context.

## Risks
- Static factory mocking makes test order and cleanup important.
- Mocked object-store behavior may not capture all real S3 edge cases, especially fingerprint and owner/group defaults.
- Assertions around `getStatusOnDirectory` are negative Mockito verifications; additional legitimate UFS calls would require test updates.
- The alluxio-only delete guard relies on the custom subclass and could miss lower-level side effects outside `syncMetadata`.

## Test Signals
Key signals are fingerprint content hash changes after forced sync, owner/group equality, non-empty owner/group fallback for empty S3 metadata, invalid file IDs after alluxio-only delete, absence of sync invocation, and exact mocked `listStatus`/`getStatus` invocation counts for directory status calls.
