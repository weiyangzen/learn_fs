# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AStorageClass.java

Purpose: Parameterized storage-class tests across disk and array fast-upload buffers. It verifies storage class metadata on create/copy/rename for default, reduced redundancy, Glacier, invalid, and empty values.

Important APIs/types/functions: `Constants.STORAGE_CLASS`, `STORAGE_CLASS_REDUCED_REDUNDANCY`, `STORAGE_CLASS_GLACIER`, `FAST_UPLOAD_BUFFER`, `FAST_UPLOAD_BUFFER_DISK`, `FAST_UPLOAD_BUFFER_ARRAY`, `HeaderProcessing.XA_STORAGE_CLASS`, `decodeBytes()`, `S3AContract`, and `FileSystem.rename()`.

Control flow: constructor selects buffer type. Configuration skips unless storage-class tests are enabled, disables FS caching, removes relevant overrides, and sets fast-upload buffer. Each test creates a contract filesystem, makes a directory, asserts directory markers have no storage class, touches a file, checks expected xattr storage class, and renames/copies where appropriate. Glacier expects `AccessDeniedException`/`InvalidObjectState` on rename because archived objects cannot be read directly.

State and persistence: writes S3 directory markers and objects with varied storage class. No local state beyond parameter.

Dependencies and integration points: S3 object storage-class metadata, S3A PUT/copy header propagation, xattr header projection, fast-upload buffer implementations, and archive-object read semantics.

Risks: reduced redundancy or Glacier support may vary by store/region; invalid storage class is expected to degrade to no metadata rather than fail; directories intentionally differ from files.

Test signals: catches lost storage class on create or rename and verifies archive class failures are surfaced as expected.
