# sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/AlluxioFuseOpenUtilsTest.java

Purpose: unit test for access-mode decoding in `AlluxioFuseOpenUtils`.

Important APIs and flow: three tests feed representative flags with high-order bits set and assert `READ_ONLY`, `WRITE_ONLY`, or `READ_WRITE` based on the low access-mode bits.

State, dependencies, risks, and signals: no state beyond local arrays. It depends on JUnit assertions. It signals that only the `O_ACCMODE` low bits should drive access action. Coverage does not include `containsTruncate`, `containsCreate`, invalid access modes, or platform-specific flag variants.
