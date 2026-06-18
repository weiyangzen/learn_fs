# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/UnderFileSystemTestUtils.java

Purpose: thread-safe utility class for UFS tests. The only behavior classifies UFS addresses as object storage paths.

Important APIs and control flow: `isObjectStorage(String ufsAddress)` returns true for prefixes `s3://`, `s3a://`, `gcs://`, `swift://`, or `oss://` using constants from `alluxio.Constants`. The constructor is private to prevent instantiation.

State, dependencies, integration, risks, tests: no state or persistence. Dependencies are just Alluxio URI header constants and the `UnderFileSystem` type in documentation. Integration point is test code that needs to branch behavior for object storage semantics, such as weaker directory/permission support. Risk: the list can become stale when new object-store schemes such as COS, COSN, ABFS, or ADL should be treated similarly by a given test.
