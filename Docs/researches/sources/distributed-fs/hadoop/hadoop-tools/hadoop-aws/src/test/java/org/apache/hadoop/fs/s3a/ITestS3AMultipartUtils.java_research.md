# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AMultipartUtils.java

Purpose: Tests listing of pending multipart uploads, including iterator paging and optional prefix filtering.

Important APIs/types/functions: `MultipartUtils`, `S3AFileSystem.listUploads()`, `MultipartTestUtils.createPartUpload()`, `MultipartTestUtils.cleanupParts()`, `MultipartTestUtils.IdKey`, AWS SDK `MultipartUpload`, `Constants.MAX_PAGING_KEYS`, and `RemoteIterators.foreach()`.

Control flow: configuration disables FS caching and forces small list page size of two. Setup skips if multipart upload tests are unavailable. The test creates five pending uploads, lists by computed prefix and with null prefix, verifies all expected `(key, uploadId)` pairs are present, and cleans up uploads in `finally`.

State and persistence: creates live pending multipart uploads in S3 and must abort them in cleanup. Uses a set of expected upload IDs/keys.

Dependencies and integration points: S3 multipart upload APIs, S3A upload listing iterators, paging, audit spans, and test cleanup utilities.

Risks: leaked multipart uploads if cleanup fails; list output may include unrelated uploads, so matching must ignore extras; page size makes iterator bugs visible.

Test signals: verifies multipart upload listing returns all created uploads across pages and prefixes.
