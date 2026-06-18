# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/MockS3ARemoteObject.java

Purpose: in-memory mock `S3ARemoteObject` for prefetch unit tests, with deterministic content and one-shot fault injection.

Important APIs/types/functions: package-private `MockS3ARemoteObject` extends `S3ARemoteObject`; constructors create fake read context, object attributes, callbacks, empty statistics, and change tracker. `openForRead(offset,size)` validates ranges, optionally throws one `IOException`, and returns an AWS `ResponseInputStream<GetObjectResponse>` over a `ByteArrayInputStream`. `close()` is a no-op. `byteAtOffset()` returns `offset % 128`. `createClient()` builds minimal `ObjectInputStreamCallbacks`.

Control flow: construction fills `contents` with predictable bytes. A test can set `throwExceptionOnOpen`; the first open clears the flag and fails, while later opens succeed.

State and persistence: keeps byte-array contents and fault flag in memory; no S3 or local filesystem access.

Dependencies/integration: AWS SDK response streams, Hadoop prefetch `Validate`, S3A fake factories, and `S3ARemoteObjectReader` tests.

Risks: callbacks return null for real object retrieval/submission, so this mock is only valid for code paths using overridden `openForRead`; range validation uses requested `size` and object size assumptions.

Test signals: consumers verify retry behavior, byte content by offset, EOF/range behavior, and close paths without external IO.
