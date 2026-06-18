<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalOperationCallbacks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalOperationCallbacks.java


## Purpose
Minimal stub for OperationCallbacks used by S3A operation helper unit tests.


## Important APIs, Types, and Functions
Implements createObjectAttributes overloads, createReadContext(), finishRename(), deleteObjectAtPath(), listFilesAndDirectoryMarkers(), copyFile(), removeKeys(), and listObjects().


## Control Flow
Most methods return null and mutating callbacks are no-ops. Tests can subclass or inject it where only selected callbacks are expected to be called.


## State and Persistence Behavior
No persistent or mutable state. Null returns are intentional tripwires for unimplemented paths.


## Dependencies and Integration Points
Depends on S3A status/read/object attribute types, AWS SDK copy/delete types, RemoteIterator, and MultiObjectDeleteException.


## Risks and Test Signals
Risk is silent no-op mutation callbacks masking a missing assertion if a test does not verify side effects. Interface implementation also acts as a signal for callback API drift.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalOperationCallbacks.java -->
