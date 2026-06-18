# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ALocatedFileStatus.java

## Purpose
`S3ALocatedFileStatus` adapts an `S3AFileStatus` into a Hadoop `LocatedFileStatus` while preserving S3-specific metadata: ETag, version id, and empty-directory tristate.

## Important APIs, Types, and Functions
The constructor accepts an `S3AFileStatus` and block locations. Public APIs are deprecated `getETag()`, `getEtag()`, `getVersionId()`, `toS3AFileStatus()`, `equals()`, `hashCode()`, and `toString()`.

## Control Flow and State
Construction delegates base file metadata to `LocatedFileStatus`, copies S3 metadata from the input status, and stores empty-directory state. `toS3AFileStatus()` reconstructs an S3A status from the located status fields plus preserved S3 metadata. Equality/hash behavior intentionally delegates to the base path-based implementation.

## State and Persistence Behavior
Instances are immutable after construction aside from superclass behavior. They are serializable through `LocatedFileStatus` conventions and carry only copied metadata, not live S3 state.

## Dependencies and Integration Points
The class depends on Hadoop `LocatedFileStatus`, `BlockLocation`, `EtagSource`, `S3AFileStatus`, and `Tristate`. It is used by listing/open status paths that need both block-location API compatibility and object version/change-detection metadata.

## Risks and Test Signals
Risks include losing S3 metadata when converting between status types, callers using deprecated `getETag()`, and path-only equality surprising code that expects version-sensitive comparison. Tests should verify ETag/version preservation, directory tristate preservation, conversion back to `S3AFileStatus`, and compatibility with list located status APIs.
