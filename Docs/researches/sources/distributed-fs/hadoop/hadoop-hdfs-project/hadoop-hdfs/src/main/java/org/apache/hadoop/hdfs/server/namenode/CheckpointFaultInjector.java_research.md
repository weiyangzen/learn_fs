# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CheckpointFaultInjector.java

## Purpose
`CheckpointFaultInjector` is a test hook class for injecting failures or altered file-transfer behavior during checkpoint and image-transfer flows.

## Important APIs and Types
It exposes a mutable singleton via `getInstance` and `set`. Hook methods include `beforeGetImageSetsHeaders`, `afterSecondaryCallsRollEditLog`, `duringMerge`, `afterSecondaryUploadsNewImage`, `aboutToSendFile`, `afterMD5Rename`, `beforeEditsRename`, and `duringUploadInProgess`. Boolean hooks `shouldSendShortFile` and `shouldCorruptAByte` control transfer corruption scenarios.

## Control Flow
Production behavior is no-op and returns false for corruption/short-send decisions. Tests replace `instance` with subclasses to throw exceptions, block, corrupt, or shorten files at well-defined checkpoint phases.

## State and Persistence
Only the static singleton is stateful. It is not persisted and must be reset by tests to avoid cross-test contamination.

## Dependencies and Integration
Used by checkpoint/image transfer code such as `TransferFsImage` and edit/image rename paths. Dependencies are limited to `File` and checked exceptions.

## Risks and Test Signals
The singleton is globally mutable and not synchronized; tests running concurrently can interfere. The method name `duringUploadInProgess` is misspelled, so callers and tests must match that exact API. Test suites should reset the singleton in teardown and cover short file, corrupted byte, MD5 rename, and upload interruption paths.
