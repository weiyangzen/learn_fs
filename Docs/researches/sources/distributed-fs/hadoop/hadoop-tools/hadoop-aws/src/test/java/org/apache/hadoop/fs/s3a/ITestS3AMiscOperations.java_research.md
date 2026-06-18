# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AMiscOperations.java

Purpose: Miscellaneous S3A behavior tests for non-recursive create, direct PUT validation, ETag checksums, uninitialized filesystem calls, and path qualification slash fixups.

Important APIs/types/functions: `createNonRecursive()`, `RequestFactoryImpl`, `PutObjectOptions`, `S3AFileSystem.putObjectDirect()`, `S3ADataBlocks.BlockUploadData`, `Constants.ETAG_CHECKSUM_ENABLED`, `EtagChecksum`, `HeaderProcessing.XA_ETAG`, `CommonPathCapabilities.FS_CHECKSUMS`, and `S3AFileSystem.makeQualified()`.

Control flow: setup enables checksums and configuration removes encryption overrides. Tests write non-recursively, attempt invalid direct PUT with content length -1 and assert no object is created, toggle checksums off/on, compare checksums across empty/non-empty/overwritten files, reject negative checksum lengths, check past-EOF length returns same checksum, call `toString()`/`getIOStatistics()` on uninitialized filesystems, and verify trailing slash handling for paths, double slashes, and root.

State and persistence: creates small S3 objects and toggles checksum config on the live filesystem config. No persistent local state.

Dependencies and integration points: S3A upload request factory, audit spans, checksum capability/xattr projection, path URI qualification, and encryption-independent checksum behavior.

Risks: mutating checksum config on the filesystem assumes option is not cached; direct PUT test depends on validation before upload; URI/path slash behavior is subtle and can break with Hadoop Path changes.

Test signals: catches checksum regressions, invalid upload validation holes, and path normalization bugs.
