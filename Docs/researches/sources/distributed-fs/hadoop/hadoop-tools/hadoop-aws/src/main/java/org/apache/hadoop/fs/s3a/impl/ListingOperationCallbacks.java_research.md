<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ListingOperationCallbacks.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ListingOperationCallbacks.java

## Purpose

`ListingOperationCallbacks` defines the filesystem callbacks needed by S3A listing implementations.

## Important APIs, Types, and Functions

It declares async list initiation and continuation, located-status conversion, list-request construction, default block-size lookup, S3 object size lookup, and max-key retrieval.

## Control Flow

Listing code uses `createListObjectsRequest()` to build an audited request, submits it through `listObjectsAsync()`, follows pages through `continueListObjectsAsync()`, and converts returned S3 objects/statuses through the remaining callbacks.

## State and Persistence Behavior

The interface has no state. Implementations may update metrics through `DurationTrackerFactory` and audit spans.

## Dependencies and Integration Points

It connects listing code with AWS S3 list request/result abstractions, S3A status objects, block location synthesis, CSE-aware object size calculation, and max listing page size configuration.

## Risks and Edge Cases

Failures surface asynchronously from returned futures. Object size may require metadata or CSE calculations and can throw IOException. Audit spans must be passed into async requests.

## Test Signals

Mock callback tests should cover initial and continued listings, future failure propagation, status-to-located-status conversion, max-key configuration, default block-size lookup, and encrypted object size handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ListingOperationCallbacks.java -->
