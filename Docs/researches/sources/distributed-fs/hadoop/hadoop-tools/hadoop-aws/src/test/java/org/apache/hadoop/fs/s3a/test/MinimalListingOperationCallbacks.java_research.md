<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalListingOperationCallbacks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalListingOperationCallbacks.java


## Purpose
Minimal stub implementation of ListingOperationCallbacks for tests that need an object satisfying the interface without real S3/listing behavior.


## Important APIs, Types, and Functions
Implements listObjectsAsync(), continueListObjectsAsync(), toLocatedFileStatus(), createListObjectsRequest(), getDefaultBlockSize(), getObjectSize(), and getMaxKeys().


## Control Flow
All methods return null or zero; no control flow performs IO. It is intended as a base for subclassing or for tests where only construction/type compatibility matters.


## State and Persistence Behavior
No state is stored. Returning null futures/statuses will fail fast if a test accidentally exercises real listing behavior.


## Dependencies and Integration Points
Depends on S3A listing model types, AWS S3Object, DurationTrackerFactory, and AuditSpan.


## Risks and Test Signals
Risk is misuse in tests expecting functional callbacks. Signal is mostly compile-time interface coverage when ListingOperationCallbacks evolves.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalListingOperationCallbacks.java -->
