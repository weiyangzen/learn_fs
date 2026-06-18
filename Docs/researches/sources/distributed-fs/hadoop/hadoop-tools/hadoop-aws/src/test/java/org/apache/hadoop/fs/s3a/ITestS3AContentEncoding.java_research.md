# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AContentEncoding.java

Purpose: Verifies that configured S3 object content encoding metadata is applied to files and preserved across rename/copy paths, while directory markers do not get content encoding. It is gated by `KEY_CONTENT_ENCODING_ENABLED`.

Important APIs/types/functions: `Constants.CONTENT_ENCODING`, `HeaderProcessing.XA_CONTENT_ENCODING`, `decodeBytes()`, `S3AFileSystem.getXAttrs()`, `ContractTestUtils.touch()`, and `S3AFileSystem.rename()`. `createConfiguration()` removes base and bucket overrides, enables `gzip`, and skips when feature tests are disabled.

Control flow: create a directory, assert its decoded xattr encoding is null, touch a file, assert `gzip`, rename that file, and assert the destination still reports `gzip`. `AWSUnsupportedFeatureException` is converted into an assumption failure for object stores that reject the metadata.

State and persistence: persists only S3 object metadata/xattrs on test-created objects. There is no local persistent state beyond the inherited test filesystem.

Dependencies and integration points: S3A xattr projection of object headers, PUT metadata handling, rename/copy metadata propagation, and object-store support for `Content-Encoding`.

Risks: object stores can reject or normalize encodings; directory marker behavior is intentionally different from file metadata; rename is copy/delete on S3, so metadata propagation must stay explicit.

Test signals: catches lost content encoding on create or rename and accidental application of content encoding to directory markers.
