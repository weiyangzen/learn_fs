# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClientSideEncryption.java

Purpose: abstract integration suite for S3 client-side encryption (CSE) behaviors common to CSE-KMS and custom keyring variants.

Important APIs/types/functions: extends `AbstractS3ATestBase`; test sizes include 0, 1, 255, and 4095 bytes plus big/small file constants. Tests validate encrypted writes, rename, directory listing lengths, multipart CSE reads/writes, behavior when encrypted and unencrypted filesystems read opposite content, V1 compatibility reads, and size derivation from encrypted metadata headers. `createConfiguration()` forces multipart threshold/part size to `MULTIPART_MIN_SIZE`. Abstract hooks `maybeSkipTest()` and `assertEncrypted()` are implemented by subclasses.

Control flow: common tests call `maybeSkipTest()`, write files with CSE-enabled FS, validate content and subclass encryption markers, and compare file lengths through `listStatus`, `listFiles`, and `getFileStatus`. Compatibility tests create separate CSE-disabled/enabled filesystems and assert expected read failures or successes. Header-size test writes an object directly with `UNENCRYPTED_CONTENT_LENGTH` metadata and checks status length.

State and persistence: writes encrypted/unencrypted S3 objects, uses extra `S3AFileSystem` instances, and performs direct `putObjectDirect`.

Dependencies and integration: AWS S3 encryption client behavior, S3A request factory, CSE compatibility config, audit spans, IOStatistics gauge for CSE enabled, and contract utilities.

Risks: CSE tests require encryption configuration, KMS/keyring permissions, and scale-test enablement for big-file multipart. Mixed encrypted/unencrypted behavior is sensitive to SDK compatibility mode and instruction-file expectations.

Test signals: broad abstract integration coverage for CSE correctness, listings, multipart, compatibility, and metadata-derived lengths.
