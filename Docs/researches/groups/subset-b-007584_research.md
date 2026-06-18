# Research report: subset-b-007584

This grouped report covers Hadoop S3A integration tests under `sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a`. Each section is source-tree-aligned and is intended to be split into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AConfiguration.java

Purpose: Integration coverage for S3A configuration plumbing, especially endpoint selection, proxy validation, credential-provider resolution, AWS SDK client options, buffer directories, user identity propagation, and custom signer registration. It extends `AbstractHadoopTestBase` rather than the normal S3A base so each test can construct deliberately different `Configuration` and `S3AFileSystem` instances.

Important APIs/types/functions: `S3ATestUtils.createTestFileSystem()`, `S3AUtils.getAWSAccessKeys()`, `ProviderUtils.excludeIncompatibleCredentialProviders()`, `CredentialProviderFactory`, `LocalDirAllocator`, `S3AInternals`, AWS SDK `S3Client`, `StsClient`, `SdkClientConfiguration`, `SdkClientOption`, and nested `CustomS3Signer`/`CustomSTSSigner`. Helpers `useFailFastConfiguration()`, `expectFSCreateFailure()`, `provisionAccessKeys()`, `getField()`, and `skipIfCrossRegionClient()` set up failure-fast clients, validate exception surfaces, seed JCEKS credentials, and introspect SDK internals.

Control flow: tests build fresh configs, unset bucket overrides where needed, then initialize an S3A filesystem or SDK client and assert either successful propagation or expected initialization failure. Proxy tests deliberately point at localhost port 1 and validate `ConnectException` or proxy username/password `IllegalArgumentException`. Credential-provider tests seed a temporary local JCEKS and check provider values override or combine with config values. SDK option tests inspect path-style access, user-agent prefix, and request timeout through reflected `clientConfiguration`. Signer tests register custom S3/STS signer names, trigger `headBucket()` and `getSessionToken()`, and assert both signers were invoked.

State and persistence: the class uses mutable fields `conf` and `fs`, a JUnit `@TempDir` for local credential stores, local temp directories for buffer allocation, and static flags in signer classes. It mutates `AWSClientConfig` minimum operation duration and resets it in `finally`; it also clears `LocalDirAllocator` contexts around buffer-dir tests to avoid shared static allocator state.

Dependencies and integration points: live S3 bucket configuration, AWS SDK v2 S3/STS clients, Hadoop credential providers, UGI, S3A bucket-specific option propagation, and S3A internal store temp-file allocation. Several tests skip or special-case cross-region clients, S3 encryption clients, AP ARNs, and AWS redirects.

Risks: reflection against AWS SDK fields is brittle across SDK upgrades; signer static flags can leak if tests are reused in-process; path-style tests depend on bucket region and ARN behavior; temporary JCEKS/provider path handling can regress silently if provider filtering changes; buffer allocator tests rely on static cleanup to avoid order sensitivity.

Test signals: validates configuration failure modes, credential precedence, path-style SDK config, user-agent composition, timeout mapping, idempotent close/refcounts, bucket option propagation, temp buffer round-robin, UGI owner/group, and service-specific signer overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AContentEncoding.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AContentEncoding.java

Purpose: Verifies that configured S3 object content encoding metadata is applied to files and preserved across rename/copy paths, while directory markers do not get content encoding. It is gated by `KEY_CONTENT_ENCODING_ENABLED`.

Important APIs/types/functions: `Constants.CONTENT_ENCODING`, `HeaderProcessing.XA_CONTENT_ENCODING`, `decodeBytes()`, `S3AFileSystem.getXAttrs()`, `ContractTestUtils.touch()`, and `S3AFileSystem.rename()`. `createConfiguration()` removes base and bucket overrides, enables `gzip`, and skips when feature tests are disabled.

Control flow: create a directory, assert its decoded xattr encoding is null, touch a file, assert `gzip`, rename that file, and assert the destination still reports `gzip`. `AWSUnsupportedFeatureException` is converted into an assumption failure for object stores that reject the metadata.

State and persistence: persists only S3 object metadata/xattrs on test-created objects. There is no local persistent state beyond the inherited test filesystem.

Dependencies and integration points: S3A xattr projection of object headers, PUT metadata handling, rename/copy metadata propagation, and object-store support for `Content-Encoding`.

Risks: object stores can reject or normalize encodings; directory marker behavior is intentionally different from file metadata; rename is copy/delete on S3, so metadata propagation must stay explicit.

Test signals: catches lost content encoding on create or rename and accidental application of content encoding to directory markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AContentEncoding.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AContractGetFileStatusV1List.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AContractGetFileStatusV1List.java

Purpose: Runs the standard contract get-file-status suite against S3A while forcing the legacy List Objects V1 API. It ensures status resolution still works with older listing semantics and small paging.

Important APIs/types/functions: extends `AbstractContractGetFileStatusTest`, creates `S3AContract`, sets `Constants.LIST_VERSION` to `1`, and sets `Constants.MAX_PAGING_KEYS` to `2`. It uses `disableFilesystemCaching()`, `skipIfNotEnabled(KEY_LIST_V1_ENABLED)`, and `skipIfS3ExpressBucket()`.

Control flow: the inherited contract tests create files/directories and call `getFileStatus`; this class only specializes configuration and logs filesystem details during teardown.

State and persistence: test data is inherited from the contract suite and written to the live S3A test path. Filesystem caching is disabled to keep the configured V1 client isolated.

Dependencies and integration points: Hadoop contract tests, S3A contract binding, List Objects V1 compatibility, paging code, and S3 Express skip logic.

Risks: V1 listing can be unsupported or undesirable on newer stores; small page size raises iterator/pagination sensitivity; inherited tests can mask S3-specific assumptions unless configuration is isolated.

Test signals: proves `getFileStatus` contract behavior when the backing list API is V1 and listings span multiple pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AContractGetFileStatusV1List.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ACopyFromLocalFile.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ACopyFromLocalFile.java

Purpose: Parameterized contract coverage for `copyFromLocalFile()` with optimized copy enabled and disabled. It verifies option propagation and rejects non-local sources or destinations where the API contract requires local input.

Important APIs/types/functions: extends `AbstractContractCopyFromLocalTest`, uses `S3AContract`, toggles `Constants.OPTIMIZED_COPY_FROM_LOCAL`, and checks `FileSystem.hasPathCapability()`. Test helpers from the base class create temp files/directories and perform local-to-S3 copies.

Control flow: constructor receives the enabled flag. `createConfiguration()` removes bucket overrides, sets the optimized flag, and disables FS caching. Tests assert path capability equals the parameter, reject S3-to-S3 or destination-as-source misuse with `IllegalArgumentException`, and validate a local path without a `file:` scheme copies to S3.

State and persistence: writes temporary local files through the inherited contract base and remote S3 objects at method paths. No long-lived state.

Dependencies and integration points: Hadoop copy-from-local contract, S3A optimized upload path, local filesystem URI parsing, and path capability reporting.

Risks: optimized and non-optimized paths must remain semantically equivalent; scheme-less local paths are easy to misclassify; filesystem cache would hide per-parameter configuration without explicit disabling.

Test signals: catches option propagation regressions, local-source validation gaps, and behavior divergence between optimized and standard copy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ACopyFromLocalFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ADSSEEncryptionWithDefaultS3Settings.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ADSSEEncryptionWithDefaultS3Settings.java

Purpose: Tests bucket-default DSSE-KMS encryption behavior where S3 bucket settings, not explicit S3A write settings, encrypt objects. It extends `AbstractTestS3AEncryption` but intentionally returns `S3AEncryptionMethods.NONE` to avoid overriding bucket defaults.

Important APIs/types/functions: `patchConfigurationEncryptionSettings()`, `assertEncrypted()`, `skipIfBucketNotKmsEncrypted()`, `EncryptionTestUtils.assertEncrypted()`, `EncryptionSecrets`, `ContractTestUtils.writeDataset()`, and `FileSystem.newInstance()` with `DSSE_KMS`.

Control flow: setup skips unless encryption is configured. The normal base-class propagation and direct encryption tests are disabled because the focus is existing bucket defaults. Rename tests first touch a probe object to confirm the bucket reports `aws:kms:dsse`; then files written under default settings are renamed through a DSSE-KMS-configured filesystem and verified for content and encryption metadata.

State and persistence: creates probe objects, data files, and target directories in S3, deleting probes in `finally`. Uses a second filesystem instance for rename behavior under explicit DSSE-KMS.

Dependencies and integration points: live bucket default encryption, configured KMS key in test configuration, S3 object metadata, S3A encryption-secret propagation, and copy/rename semantics.

Risks: highly environment-dependent; disabled inherited tests reduce generic signal; bucket default encryption must match the configured KMS key or assertions skip/fail; rename changes encryption via copy operation.

Test signals: verifies S3A can work with DSSE-KMS bucket defaults and that rename through an explicitly encrypted filesystem produces objects with the expected DSSE-KMS key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ADSSEEncryptionWithDefaultS3Settings.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ADelayedFNF.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ADelayedFNF.java

Purpose: Exercises the case where a file is successfully opened but deleted before the first read, so the failure appears lazily from the stream. It checks S3A translates that delayed object-missing condition into `FileNotFoundException`.

Important APIs/types/functions: `FSDataInputStream`, `ChangeDetectionPolicy`, `Source.VersionId`, `ContractTestUtils.createFile()`, `assertDeleted()`, and `LambdaTestUtils.intercept()`. Configuration lowers retry limits and removes change-detection overrides.

Control flow: create a small object, open it, delete it, then call `read()` and expect `FileNotFoundException`. The test assumes out when object versioning/change detection by version ID means the old opened object can still be resolved.

State and persistence: writes and deletes one S3 object. Retry settings are shortened for fast failure.

Dependencies and integration points: S3A input stream lazy GET behavior, change detection policy, retry policy, and exception translation.

Risks: bucket versioning changes semantics; retry settings affect latency and observed exception timing; prefetch or stream implementation changes may move failure earlier.

Test signals: catches regressions where delayed missing-object reads return EOF, AWS exceptions, or retry excessively instead of a Hadoop `FileNotFoundException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ADelayedFNF.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ADeleteOnExit.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ADeleteOnExit.java

Purpose: Validates Hadoop `deleteOnExit()` behavior for S3A across nonexistent paths, existing files, paths registered before creation, and recursive directory cleanup.

Important APIs/types/functions: `FileSystem.deleteOnExit()`, `S3AFileSystem.initialize()`, `ContractTestUtils.createFile()`, `dataset()`, and inherited `assertPathExists()`/`assertPathDoesNotExist()`.

Control flow: creates a separate `S3AFileSystem` instance, builds test paths, registers missing and future paths with delete-on-exit, writes files and a subdirectory, closes the separate filesystem, then verifies all registered paths were removed through the base filesystem.

State and persistence: uses a distinct filesystem object with its own delete-on-exit set; remote S3 objects/directories are persisted until close triggers cleanup.

Dependencies and integration points: Hadoop `FileSystem` close lifecycle, S3A recursive delete, and delete-on-exit path set ordering.

Risks: delete-on-exit state is per-filesystem instance; object-store eventual/listing behavior can affect recursive directory verification; failure to close would leave test data.

Test signals: ensures registered cleanup executes on close even when paths were missing at registration time or are directories containing later-created files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ADeleteOnExit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEmptyDirectory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEmptyDirectory.java

Purpose: Checks that S3A directory status reports definitive `Tristate.TRUE` or `Tristate.FALSE` as children are added or removed.

Important APIs/types/functions: `S3AFileStatus.isEmptyDirectory()`, `S3AFileSystem.innerGetFileStatus()`, `StatusProbeEnum.ALL`, `AuditSpan`, `mkdirs()`, `assertDeleted()`, and `ContractTestUtils.touch()`.

Control flow: one test creates a nested child under a parent, verifies parent is non-empty, deletes the child, and verifies empty. The other creates an empty directory, verifies empty, touches a file beneath it, and verifies non-empty.

State and persistence: remote S3 directory markers and child objects are created/deleted. `innerGetFileStatus(..., true, ALL)` requests definitive emptiness rather than unknown.

Dependencies and integration points: S3A status probing, directory marker handling, list-based emptiness checks, and audit-span wrapping.

Risks: directory marker retention policies and list consistency affect emptiness; using internal APIs means changes to probe semantics can break the test.

Test signals: catches stale or unknown empty-directory state after child creation/deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEmptyDirectory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionAlgorithmValidation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionAlgorithmValidation.java

Purpose: Disabled integration tests for invalid encryption configuration validation. The suite verifies S3A fails initialization for unknown algorithms, missing/blank SSE-C keys, and SSE-S3 configured with a key.

Important APIs/types/functions: `Constants.S3_ENCRYPTION_ALGORITHM`, `Constants.S3_ENCRYPTION_KEY`, `S3AEncryptionMethods.SSE_C`, `S3AEncryptionMethods.SSE_S3`, `S3AUtils.SSE_C_NO_KEY_ERROR`, `S3AUtils.SSE_S3_WITH_KEY_ERROR`, `S3AContract`, and `LambdaTestUtils.intercept()`.

Control flow: each test creates a modified configuration, initializes an `S3AContract`, extracts the filesystem, and expects initialization or validation to throw a specific exception/message. `mkdirs()` is overridden as a no-op so setup does not fail before the validation under test.

State and persistence: no intended S3 writes; failures occur during configuration/initialization. The class-level `@Disabled` means it contributes no regular CI signal unless explicitly enabled.

Dependencies and integration points: S3A encryption option parsing, contract initialization, and legacy/new encryption config names.

Risks: disabled status can let validation behavior drift; expected exception types/messages are brittle; setting Hadoop config value to null has framework-specific semantics.

Test signals: when enabled, provides negative coverage for encryption misconfiguration before any data is written.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionAlgorithmValidation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionDSSEKMSUserDefinedKey.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionDSSEKMSUserDefinedKey.java

Purpose: Concrete `AbstractTestS3AEncryption` subclass for DSSE-KMS with a user-defined KMS key from test configuration.

Important APIs/types/functions: `S3AUtils.getS3EncryptionKey()`, `S3ATestUtils.skipIfEncryptionNotSet()`, `S3ATestUtils.getTestBucketName()`, `Constants.S3_ENCRYPTION_KEY`, and `S3AEncryptionMethods.DSSE_KMS`.

Control flow: `createConfiguration()` probes a fresh configuration for the bucket KMS key, skips/assumes if DSSE-KMS or key is unavailable, then delegates to the base configuration and injects the key. `getSSEAlgorithm()` selects `DSSE_KMS`; inherited base tests perform create/read/rename/encryption assertions.

State and persistence: inherited encryption tests write encrypted objects to S3. No extra local state.

Dependencies and integration points: live AWS KMS key, bucket auth-keys configuration, S3A encryption secrets, and base encryption test framework.

Risks: missing or wrong KMS key skips or fails; KMS permissions and bucket region matter; the class has little direct logic and depends on inherited test coverage.

Test signals: confirms configured DSSE-KMS writes and base encryption operations work with an explicit key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionDSSEKMSUserDefinedKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEC.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEC.java

Purpose: Parameterized SSE-C integration suite, run with analytics accelerator enabled and disabled, focusing on wrong-key behavior for reads, metadata/status, rename, delete, checksum, and listing.

Important APIs/types/functions: extends `AbstractTestS3AEncryption`; uses `S3AEncryptionMethods.SSE_C`, `Constants.S3_ENCRYPTION_KEY`, `ETAG_CHECKSUM_ENABLED`, `S3AContract`, `ContractTestUtils.verifyFileContents()`, `listFiles()`, `listStatus()`, `getFileChecksum()`, and helper `createNewFileSystemWithSSECKey()`.

Control flow: configuration removes encryption overrides, sets SSE-C key A, enables etag checksums, and optionally enables analytics accelerator. Setup skips root-style tests and non-AWS-hosted stores. Tests write with key A, then create `fsKeyB` with a different key and assert AWS 403 translated to `AccessDeniedException` for decrypting reads, file metadata, file delete, and checksum. Directory listing/status and recursive directory deletion are expected to work even with wrong or no key because LIST does not require object decryption.

State and persistence: maintains `fsKeyB` as a secondary filesystem closed in teardown; writes encrypted objects and directories. Test constants are fixed base64 SSE-C keys.

Dependencies and integration points: AWS SSE-C semantics, S3A encryption headers on read/write/copy/delete, list-before-head optimizations, ETag checksum behavior, analytics accelerator path, and contract-created alternate filesystems.

Risks: live AWS-only behavior; alternate object stores may differ; 403 message matching is brittle; directory marker/list optimizations are subtle and can change status behavior; analytics accelerator can alter stream path.

Test signals: strong coverage for SSE-C access boundaries and for S3A logic that must avoid unnecessary HEAD/decrypt operations on directories while still failing correctly for encrypted files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEKMSDefaultKey.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEKMSDefaultKey.java

Purpose: Tests SSE-KMS when S3/AWS uses the account/region default KMS key because no explicit key is provided.

Important APIs/types/functions: extends `AbstractTestS3AEncryption`, sets `Constants.S3_ENCRYPTION_KEY` to empty, returns `SSE_KMS`, uses `HeadObjectResponse`, `EncryptionTestUtils.AWS_KMS_SSE_ALGORITHM`, and `validateEncryptionFileAttributes()`.

Control flow: inherited encryption tests write/read encrypted objects. This class overrides `assertEncrypted()` to check server-side encryption is AWS KMS and that `ssekmsKeyId()` contains a KMS ARN rather than matching an exact configured key. The explicit file-attributes test writes data, verifies content, and validates encryption attributes with `Optional.empty()`.

State and persistence: writes S3 objects encrypted with the service/default key; no local state.

Dependencies and integration points: AWS default KMS behavior, S3 object metadata, and S3A file-attribute/xattr projection.

Risks: default key ARN format and availability are account/region dependent; exact key comparison is impossible by design; permissions to use default KMS key must exist.

Test signals: catches missing SSE-KMS headers and incorrect file-attribute reporting when no explicit KMS key is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEKMSDefaultKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEKMSUserDefinedKey.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEKMSUserDefinedKey.java

Purpose: Concrete base encryption test for SSE-KMS with an explicit user-defined key.

Important APIs/types/functions: `S3AUtils.getS3EncryptionKey()`, `S3ATestUtils.getTestBucketName()`, `Constants.S3_ENCRYPTION_ALGORITHM`, `Constants.S3_ENCRYPTION_KEY`, and `S3AEncryptionMethods.SSE_KMS`.

Control flow: `createConfiguration()` reads the configured KMS key and verifies the base test configuration says `SSE_KMS`; otherwise it skips. It then delegates to the base configuration and writes `S3_ENCRYPTION_KEY`. `getSSEAlgorithm()` returns `SSE_KMS` so inherited base tests do the actual encrypted operations.

State and persistence: inherited tests create encrypted S3 objects; no extra state.

Dependencies and integration points: auth-keys KMS configuration, S3A encryption option propagation, KMS permissions, and inherited encryption contract.

Risks: environment-gated; wrong algorithm or blank key skips; KMS policy/region mismatch can fail during live writes.

Test signals: verifies explicit SSE-KMS key use in the common base encryption scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEKMSUserDefinedKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEKMSWithEncryptionContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEKMSWithEncryptionContext.java

Purpose: Tests KMS encryption with an S3/KMS encryption context for either SSE-KMS or DSSE-KMS. Since S3 HEAD does not reveal the encryption context, the test relies on KMS/IAM policy setup to make missing/wrong context observable.

Important APIs/types/functions: `S3AEncryption.getS3EncryptionContext()`, `S3AUtils.getEncryptionAlgorithm()`, `S3AUtils.getS3EncryptionKey()`, `Constants.S3_ENCRYPTION_CONTEXT`, `Constants.S3_ENCRYPTION_KEY`, and `ImmutableSet` of `SSE_KMS`/`DSSE_KMS`.

Control flow: configuration reads bucket-specific key, context, and algorithm; assumes the algorithm is KMS-based; skips if context is blank; removes overrides; sets key and context in the base configuration. `getSSEAlgorithm()` returns the discovered algorithm so inherited encryption tests execute with the selected KMS method.

State and persistence: inherited encrypted objects in S3; no local state. The `encryptionAlgorithm` field is set during configuration creation.

Dependencies and integration points: KMS encryption-context policy, S3A request header construction, bucket-specific encryption configuration, and base encryption tests.

Risks: correctness is only fully observable when external KMS policy denies decrypt without the expected context; otherwise it mainly verifies request construction does not fail. Field initialization depends on `createConfiguration()` running before `getSSEAlgorithm()` use.

Test signals: provides environment-gated coverage that encryption context is passed through for KMS-backed S3A writes and reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEKMSWithEncryptionContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSES3.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSES3.java

Purpose: Concrete base encryption test for SSE-S3.

Important APIs/types/functions: `AbstractTestS3AEncryption`, `S3ATestUtils.disableFilesystemCaching()`, `Constants.S3_ENCRYPTION_KEY`, and `S3AEncryptionMethods.SSE_S3`.

Control flow: configuration delegates to the base class, disables filesystem caching, and sets the encryption key to an empty string because SSE-S3 must not have a key but the value cannot be null. The inherited base suite performs write/read/rename and metadata assertions for the selected algorithm.

State and persistence: creates SSE-S3 encrypted S3 objects through inherited tests. No local state.

Dependencies and integration points: S3A encryption config validation and AWS SSE-S3 server-side encryption metadata.

Risks: most behavior lives in the base class; a null/blank key distinction is important; filesystem cache disabling is necessary to avoid contamination by other encryption tests.

Test signals: confirms SSE-S3 can be configured and used without a customer key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSES3.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionWithDefaultS3Settings.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionWithDefaultS3Settings.java

Purpose: Tests existing S3 bucket default SSE-KMS settings without S3A explicitly setting encryption on initial writes. It verifies bucket-default encrypted objects and rename behavior when a second filesystem explicitly uses SSE-KMS.

Important APIs/types/functions: `patchConfigurationEncryptionSettings()`, `assertEncrypted()`, `skipIfBucketNotKmsEncrypted()`, `validateEncryptionFileAttributes()`, `EncryptionSecrets`, `FileSystem.newInstance()`, `S3AEncryptionMethods.NONE`, and `S3AEncryptionMethods.SSE_KMS`.

Control flow: setup skips unless encryption is configured. Base propagation/direct encryption tests are disabled. File-attribute and rename tests first create a probe object and inspect metadata to ensure the bucket default is `aws:kms`; then they write content, verify it, and assert encryption metadata and KMS key. Rename test uses a new filesystem configured with SSE-KMS to copy/rename the source into a target directory and verify the renamed file's encryption.

State and persistence: creates probe, source, and target objects/directories in S3; probe cleanup is in `finally`. No local persistent state.

Dependencies and integration points: bucket default encryption, S3 metadata, configured KMS key, S3A copy/rename encryption behavior, and encryption-file-attribute reporting.

Risks: environment-dependent and skip-heavy; inherited base tests are disabled by design; bucket default must match auth-keys KMS key; rename behavior can vary with copy implementation.

Test signals: validates compatibility with server-side bucket default SSE-KMS and S3A's ability to preserve/apply encryption during rename/copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionWithDefaultS3Settings.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEndpointRegion.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEndpointRegion.java

Purpose: Validates endpoint, region, FIPS, VPC endpoint, central endpoint, requester-pays, and cross-region behavior in `DefaultS3ClientFactory` and S3A filesystem initialization.

Important APIs/types/functions: `DefaultS3ClientFactory`, `S3ClientFactory.S3ClientCreationParameters`, AWS SDK `ExecutionInterceptor`, `AwsExecutionAttribute`, `S3Client.headBucket()`, `S3AFileSystem.initialize()`, `getBucketMetadata()`, `Constants.ENDPOINT`, `AWS_REGION`, `FIPS_ENDPOINT`, `AWS_S3_CROSS_REGION_ACCESS_ENABLED`, `ALLOW_REQUESTER_PAYS`, and helper `createS3Client()`.

Control flow: pure client-construction tests create an S3 client with an interceptor that inspects SDK execution attributes just before the first request and then throws a synthetic `AwsServiceException` to avoid network IO. Live filesystem tests initialize new filesystems with missing region, unknown bucket, central endpoint, FIPS, requester-pays, and cross-region settings, then assert expected failures or run CRUD through `assertOpsUsingNewFs()`.

State and persistence: `newFS` is closed in teardown; `EXPECTED_MESSAGE` is an `AtomicReference` for assertion context; CRUD tests write/delete a method-path object. Configuration is cloned and base/bucket overrides removed aggressively.

Dependencies and integration points: AWS SDK endpoint resolution, FIPS endpoint rules, region parsing, S3A bucket metadata, public requester-pays dataset, cross-region redirect handling, S3 Express/AWS-hosted assumptions, and S3A filesystem CRUD.

Risks: endpoint/region rules are AWS SDK sensitive; public datasets and requester-pays settings can change; FIPS only works for certain regions; cross-region tests skip in unsupported regions; typo `endpointOveridden` is in assertion text only.

Test signals: strong coverage that configured endpoints and regions produce expected SDK attributes and that central/cross-region access works or fails according to configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEndpointRegion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFSMainOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFSMainOperations.java

Purpose: Runs Hadoop `FSMainOperationsBaseTest` against S3A, with S3-specific exclusions and overwrite behavior adjusted for create-performance mode.

Important APIs/types/functions: `FSMainOperationsBaseTest`, `S3AContract`, `S3ATestUtils.createTestPath()`, `setPerformanceFlags()`, and `isCreatePerformanceEnabled()`.

Control flow: constructor passes a stable S3A base path. `createFileSystem()` creates and initializes an `S3AContract`. Tests for unreadable dirs and raw local copy are disabled because S3A lacks POSIX permissions or setup is broken. Block write/read/delete tests call the superclass. `testOverwrite()` runs the superclass and swallows the assertion only when create-performance mode is enabled.

State and persistence: inherited tests create remote objects under `/ITestS3AFSMainOperations`. The `contract` field owns the test filesystem instance.

Dependencies and integration points: Hadoop main filesystem operation contract, S3A contract implementation, and create-performance feature behavior.

Risks: superclass assumptions may not match object-store semantics; create-performance mode changes overwrite semantics enough to require conditional handling; disabled tests reduce permission coverage.

Test signals: broad compatibility signal for common FileSystem operations on S3A.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFSMainOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFailureHandling.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFailureHandling.java

Purpose: Integration tests for S3A failure handling, primarily multi-object delete behavior, paging, missing keys, and access-denied exception translation.

Important APIs/types/functions: `S3AFileSystem.removeKeys()`, AWS SDK `ObjectIdentifier` and `S3Error`, `MultiObjectDeleteException`, `StoreStatisticNames.OBJECT_BULK_DELETE_REQUEST`, `PublicDatasetTestUtils.requireDefaultExternalData()`, `RemoteIterators.toList()`, and `mappingRemoteIterator()`.

Control flow: configuration disables FS caching and enables multi-delete. Tests remove missing keys, create many files and delete them through batched bulk delete while checking request counters, delete a mix of existing/missing keys, and attempt to delete external read-only/public data to verify `MultiObjectDeleteException` and single-delete `AccessDeniedException` translation.

State and persistence: creates up to 1005 S3 objects for paging when bulk delete is enabled; external-data tests operate on configured public/read-only objects. Audit spans wrap low-level delete calls.

Dependencies and integration points: S3 multi-delete API, S3A bulk delete paging, IOStatistics counters, public external data configuration, and exception translation.

Risks: external data configuration affects endpoint overrides; bulk delete enabled/disabled changes expected request count; access-denied behavior depends on public dataset permissions; large object count makes test cost/time higher.

Test signals: catches regressions in missing-key tolerance, delete paging, bulk-delete metrics, and AWS-to-Hadoop exception mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFailureHandling.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFileOperationCost.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFileOperationCost.java

Purpose: Defines metrics-level cost contracts for common S3A file operations. It verifies exact or expected S3 operation counts for status, list, glob, copy-from-local, and directory probes.

Important APIs/types/functions: extends `AbstractS3ACostTest`; uses `verifyMetrics()`, `verify()`, `verifyInnerGetFileStatus()`, `interceptGetFileStatusFNFE()`, `isDir()`, `isFile()`, `StatusProbeEnum`, `PerformanceFlagEnum.Create`, and operation-cost constants such as `GET_FILE_STATUS_ON_FILE`, `LIST_STATUS_LIST_OP`, `FILE_STATUS_DIR_PROBE`, and `NO_IO`.

Control flow: setup enables create performance flag. Each test creates a known file/directory state, invokes one API (`listLocatedStatus`, `listFiles`, `listStatus`, `getFileStatus`, `globStatus`, `copyFromLocalFile`, or internal `s3GetFileStatus`), then checks IOStatistics deltas against expected operation-cost expressions. Directory probe tests explicitly exercise HEAD-only, LIST-only, no-probe, and trailing-slash key paths.

State and persistence: writes small S3 objects/directories and one local temp file for copy-from-local. Metrics are sampled around each operation by the cost-test base.

Dependencies and integration points: S3A status probing implementation, list iterators, globber, local-to-S3 upload path, IOStatistics, and performance flag handling.

Risks: these are intentionally brittle against implementation changes in probe strategy or counter naming; exact request counts can change with new optimizations; trailing-slash internal calls depend on key mapping details.

Test signals: high-value guardrail for S3 request-cost regressions and accidental extra HEAD/LIST/PUT operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFileOperationCost.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFileSystemContract.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFileSystemContract.java

Purpose: Live S3A implementation of Hadoop `FileSystemContractBaseTest`, with S3-specific rename and overwrite expectations.

Important APIs/types/functions: `FileSystemContractBaseTest`, `S3ATestUtils.createTestFileSystem()`, `setPerformanceFlags()`, `TestName`, `rename()`, `createFile()`, and `LambdaTestUtils.intercept()`.

Control flow: `setUp()` names the test thread, creates a test filesystem, and computes a qualified base path. Several inherited tests are skipped or adapted: mkdirs umask unsupported, rename into nonexistent directories does not fail on S3A, rename directory onto existing dir is validated for nested children, directory-to-file and file-to-file rename expect `FileAlreadyExistsException`, and missing-source rename expects `FileNotFoundException`.

State and persistence: remote test data under `s3afilesystemcontract`; base class manages cleanup. Method name extension aids logging/thread naming.

Dependencies and integration points: Hadoop FS contract, S3A rename/copy/delete semantics, and create-performance mode.

Risks: object-store rename is non-atomic copy/delete and differs from POSIX; superclass behavior can conflict with S3A semantics; overwrite handling conditionally tolerates create-performance differences.

Test signals: broad compatibility coverage for classic filesystem contract behavior that S3A chooses to support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFileSystemContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFileSystemIsolatedClassloader.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFileSystemIsolatedClassloader.java

Purpose: Verifies S3A extension class loading honors `Constants.AWS_S3_CLASSLOADER_ISOLATION`, including default isolation, explicit isolation, disabled isolation, and direct reflection utility behavior.

Important APIs/types/functions: nested `CustomCredentialsProvider`, nested `CustomClassLoader`, `S3AFileSystem.initialize()`, `S3AUtils.getInstanceFromReflection()`, `AWSCredentialProviderList.shareCredentials()`, `InstantiationIOException`, and `Constants.AWS_CREDENTIALS_PROVIDER`.

Control flow: helper `assertInNewFilesystem()` installs a custom context classloader that can load `custom.class.name`, prepares test configuration, applies overrides, creates a new S3A filesystem, and runs assertions before restoring the old context classloader. Default and isolation=true expect the filesystem config classloader to be the S3A classloader and fail to load the custom provider. isolation=false expects the context classloader to be used and the custom provider to appear in the credential provider list.

State and persistence: mutates the current thread context classloader in a `try/finally`; creates short-lived filesystem instances. No S3 data is intentionally written beyond initialization side effects.

Dependencies and integration points: Hadoop configuration classloader, S3A extension loading, AWS credentials provider reflection, and HADOOP-17372/HADOOP-18993/HADOOP-19833 classloader behavior.

Risks: thread context classloader must always be restored; provider returns null credentials so tests depend on initialization path not requiring actual use; classloader behavior is subtle and easy to regress with refactors.

Test signals: catches isolation leaks and ensures applications can opt out to load providers from their own classpath.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFileSystemIsolatedClassloader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AIOStatisticsContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AIOStatisticsContext.java

Purpose: Tests thread-level `IOStatisticsContext` aggregation for S3A input streams, output streams, listing operations, context sharing, and task-pool execution.

Important APIs/types/functions: `IOStatisticsContext`, `IOStatisticsContextIntegration.enableIOStatisticsContext()`, `getCurrentIOStatisticsContext()`, `getThreadSpecificIOStatisticsContext()`, `setThreadIOStatisticsContext()`, `StreamCapabilities.IOSTATISTICS_CONTEXT`, `HadoopExecutors`, `SubjectInheritingThread`, `TaskPool`, and counters `STREAM_READ_BYTES`, `STREAM_WRITE_BYTES`, `OBJECT_LIST_REQUEST`.

Control flow: configuration disables prefetching and forces classic streams for deterministic stream statistics. Tests run read/write workloads in multiple executor threads, reset contexts, assert per-thread byte counters, verify context IDs and thread IDs, share a context into a worker thread, set null context to force a new context, and verify list operations update the current context both directly and through `TaskPool`.

State and persistence: maintains an executor per test, worker exceptions through inherited future-exception fields, and global/thread-local IO statistics contexts. Writes small S3 objects for read/write tests.

Dependencies and integration points: S3A stream capabilities, block output stream, classic input stream, listing iterators, Hadoop task-pool context propagation, and thread-local statistics implementation.

Risks: thread scheduling and context inheritance can be order-sensitive; prefetching is disabled because it would alter counters; context is global/thread-local and can leak between tests if not reset.

Test signals: verifies both stream-level and filesystem/listing statistics are attributed to the correct thread or explicitly shared context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AIOStatisticsContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AInputStreamLeakage.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AInputStreamLeakage.java

Purpose: Verifies S3A input stream leak detection through finalization/GC logging and `STREAM_LEAKS` statistics.

Important APIs/types/functions: `FSDataInputStream`, `ObjectInputStream`, `S3AInputStream`, `StreamStatisticNames.STREAM_LEAKS`, `GenericTestUtils.LogCapturer`, `WeakReference`, `System.gc()`, `System.runFinalization()`, and `IOStatistics`.

Control flow: setup assumes the filesystem advertises `STREAM_LEAKS`. The test creates a file, opens a stream without try-with-resources, reads one byte, captures a weak reference to the wrapped stream, records leak counter, captures root logs, nulls the strong reference, forces GC/finalization, waits briefly, then asserts log output includes the leak message, path, thread, and test stack. It also asserts the leak counter increased, exactly by one for the classic stream.

State and persistence: creates one S3 object; intentionally relies on GC/finalizer behavior and root logger capture. Cleanup closes the stream only if it was not nulled.

Dependencies and integration points: S3A stream finalizer/leak-detection implementation, IOStatistics counters, logging content, and JVM GC/finalization behavior.

Risks: GC/finalizer timing is inherently flaky; log-message text is brittle; prefetch streams may increment leak counters more than once due to nested streams.

Test signals: catches removal or weakening of leak logging/statistics for unclosed input streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AInputStreamLeakage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AMetrics.java

Purpose: Tests S3A instrumentation registry and stream-statistics merging into filesystem metrics.

Important APIs/types/functions: `S3AInstrumentation`, `MutableCounterLong`, `Statistic.FILES_CREATED`, `Statistic.STREAM_READ_BYTES`, `ContractTestUtils.touch()`, `ContractTestUtils.createFile()`, and `IOStatisticsLogging.ioStatisticsSourceToString()`.

Control flow: `testMetricsRegister()` touches one file and checks the registry's files-created counter equals one. `testStreamStatistics()` writes a 26-byte file, reads it to EOF, logs stream statistics, closes the stream, then asserts filesystem instrumentation and registry counters record 26 stream-read bytes.

State and persistence: creates small S3 files; metrics accumulate on the test filesystem instrumentation instance.

Dependencies and integration points: S3A instrumentation registry, stream close/merge logic, Hadoop metrics2 counters, and IOStatistics display helpers.

Risks: counters are sensitive to prior operations if the filesystem is reused unexpectedly; stream statistics merge occurs on close, so missing close would hide updates; reads must consume exactly 26 bytes.

Test signals: catches failures to register file-created metrics or merge per-stream read counters into filesystem metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AMiscOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AMiscOperations.java

Purpose: Miscellaneous S3A behavior tests for non-recursive create, direct PUT validation, ETag checksums, uninitialized filesystem calls, and path qualification slash fixups.

Important APIs/types/functions: `createNonRecursive()`, `RequestFactoryImpl`, `PutObjectOptions`, `S3AFileSystem.putObjectDirect()`, `S3ADataBlocks.BlockUploadData`, `Constants.ETAG_CHECKSUM_ENABLED`, `EtagChecksum`, `HeaderProcessing.XA_ETAG`, `CommonPathCapabilities.FS_CHECKSUMS`, and `S3AFileSystem.makeQualified()`.

Control flow: setup enables checksums and configuration removes encryption overrides. Tests write non-recursively, attempt invalid direct PUT with content length -1 and assert no object is created, toggle checksums off/on, compare checksums across empty/non-empty/overwritten files, reject negative checksum lengths, check past-EOF length returns same checksum, call `toString()`/`getIOStatistics()` on uninitialized filesystems, and verify trailing slash handling for paths, double slashes, and root.

State and persistence: creates small S3 objects and toggles checksum config on the live filesystem config. No persistent local state.

Dependencies and integration points: S3A upload request factory, audit spans, checksum capability/xattr projection, path URI qualification, and encryption-independent checksum behavior.

Risks: mutating checksum config on the filesystem assumes option is not cached; direct PUT test depends on validation before upload; URI/path slash behavior is subtle and can break with Hadoop Path changes.

Test signals: catches checksum regressions, invalid upload validation holes, and path normalization bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AMiscOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AMultipartUtils.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AMultipartUtils.java

Purpose: Tests listing of pending multipart uploads, including iterator paging and optional prefix filtering.

Important APIs/types/functions: `MultipartUtils`, `S3AFileSystem.listUploads()`, `MultipartTestUtils.createPartUpload()`, `MultipartTestUtils.cleanupParts()`, `MultipartTestUtils.IdKey`, AWS SDK `MultipartUpload`, `Constants.MAX_PAGING_KEYS`, and `RemoteIterators.foreach()`.

Control flow: configuration disables FS caching and forces small list page size of two. Setup skips if multipart upload tests are unavailable. The test creates five pending uploads, lists by computed prefix and with null prefix, verifies all expected `(key, uploadId)` pairs are present, and cleans up uploads in `finally`.

State and persistence: creates live pending multipart uploads in S3 and must abort them in cleanup. Uses a set of expected upload IDs/keys.

Dependencies and integration points: S3 multipart upload APIs, S3A upload listing iterators, paging, audit spans, and test cleanup utilities.

Risks: leaked multipart uploads if cleanup fails; list output may include unrelated uploads, so matching must ignore extras; page size makes iterator bugs visible.

Test signals: verifies multipart upload listing returns all created uploads across pages and prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AMultipartUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3APrefetchingCacheFiles.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3APrefetchingCacheFiles.java

Purpose: Verifies prefetching input stream creates local cache files with expected size and restrictive permissions.

Important APIs/types/functions: `enablePrefetching()`, `Constants.PREFETCH_BLOCK_SIZE_KEY`, `Constants.BUFFER_DIR`, `PublicDatasetTestUtils.getExternalData()`, `FSDataInputStream.readFully()`, local `FileSystem`, `FileStatus`, and `FsAction`.

Control flow: setup creates an isolated buffer directory under the configured buffer dir, selects external data, and opens the appropriate filesystem. The test skips client-side encryption, reads ranges to trigger prefetch of multiple blocks, locates `.bin` files containing `fs-cache-` under the buffer dir, and asserts each file is length `prefetchBlockSize` with user read/write and no group/other permissions.

State and persistence: creates local cache files under a UUID buffer directory and deletes the top directory in teardown. Reads external S3 data but does not write remote data.

Dependencies and integration points: S3A prefetch cache file manager, local filesystem permissions, external data configuration, and client-side-encryption compatibility.

Risks: local directory deletion only removes the top directory if empty; permission behavior can vary by platform/umask; external data and endpoint overrides affect availability.

Test signals: catches failures to create cache files, wrong cache block sizing, and unsafe cache-file permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3APrefetchingCacheFiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3APrefetchingInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3APrefetchingInputStream.java

Purpose: Validates the prefetching input stream's caching, in-memory small-file path, request counts, memory/cache gauges, random reads, lazy positioned reads, and post-close status probes.

Important APIs/types/functions: `enablePrefetching()`, `Constants.PREFETCH_BLOCK_SIZE_KEY`, `S3APrefetchingInputStream`, `S3AInputStreamStatistics`, IO statistics counters/gauges `STREAM_READ_PREFETCH_OPERATIONS`, `ACTION_HTTP_GET_REQUEST`, `STREAM_READ_OPENED`, `STREAM_READ_BLOCKS_IN_FILE_CACHE`, `STREAM_READ_ACTIVE_MEMORY_IN_USE`, and `ACTION_EXECUTOR_ACQUIRED`.

Control flow: configuration enables prefetch and sets 10 KiB block size. `createLargeFile()` writes a multi-block object and computes block count. Full-read tests read sequentially via stream or positioned `readFully` and assert first block synchronous plus remaining blocks prefetched. Random large-file test partially reads/seeks to create cached blocks and uses `eventually()` for async counters. Small-file test ensures one GET and no prefetch/buffer-pool use. Post-close test verifies `getPos()`, `getIOStatistics()`, and stream statistics remain available after close and `seekToNewSource()` is unsupported.

State and persistence: writes S3 objects; prefetch internals maintain memory/file cache state tracked by IOStatistics. Async prefetch means some assertions use polling.

Dependencies and integration points: S3A prefetch stream, caching input stream, in-memory input stream, IOStatistics, async executor, and client-side-encryption skip behavior.

Risks: exact counters can shift with prefetch strategy changes; asynchronous prefetch makes timing-sensitive assertions; large buffer loop increments bytesRead by buffer length rather than actual read request size but bounded by file-size condition.

Test signals: strong regression coverage for prefetch request economics, resource cleanup, cache gauges, and closed-stream observability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3APrefetchingInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3APrefetchingLruEviction.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3APrefetchingLruEviction.java

Purpose: Parameterized stress test for LRU eviction in `S3ACachingInputStream` when prefetch cache capacity is one or two blocks.

Important APIs/types/functions: `Constants.PREFETCH_MAX_BLOCKS_COUNT`, `Constants.PREFETCH_BLOCK_SIZE_KEY`, `enablePrefetching()`, `FSDataInputStream.readFully(position, ...)`, `seek()`, IOStatistics gauges/counters `STREAM_READ_BLOCKS_IN_FILE_CACHE`, `STREAM_EVICT_BLOCKS_FROM_FILE_CACHE`, and `STREAM_FILE_CACHE_EVICTION`.

Control flow: for max blocks `1` and `2`, configuration sets prefetch and cache capacity. The test writes a multi-block file, opens one stream, submits seven concurrent partial read/seek tasks across several blocks, waits for completion, asserts cache gauge settles to the configured capacity while stream is open, then after close asserts cache gauge returns to zero and eviction counters are at least four and internally consistent.

State and persistence: writes one S3 object per parameter. Uses a daemon fixed thread pool and countdown latch; closes stream to release cache.

Dependencies and integration points: prefetch cache LRU policy, concurrent stream reads, IOStatistics, and async prefetch cancellation behavior.

Risks: concurrent use of one input stream can expose timing-dependent behavior; comments note transient failures around async prefetch cancellation; exact eviction count is lower-bounded instead of exact.

Test signals: catches cache-capacity violations, missing cleanup on close, and divergence between eviction counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3APrefetchingLruEviction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ARequesterPays.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ARequesterPays.java

Purpose: Tests requester-pays bucket support, ensuring S3A adds the requester-pays header when enabled and fails with access denied when disabled.

Important APIs/types/functions: `Constants.ALLOW_REQUESTER_PAYS`, `Constants.S3A_BUCKET_PROBE`, `PublicDatasetTestUtils.getRequesterPaysObject()`, `FSDataInputStream`, `IOStatisticAssertions`, `StreamStatisticNames.STREAM_READ_OPENED`, and `S3ATestUtils.streamType()`.

Control flow: configuration removes bucket overrides for the requester-pays bucket. Success test enables requester pays and bucket probe, opens the public requester-pays object, reads last then first byte to force one or more GET requests, checks stream-open counts according to classic vs prefetch stream, and lists the parent. Failure test disables requester pays and expects `AccessDeniedException` containing `403` when opening the object.

State and persistence: reads public requester-pays data; does not write. Uses a separate filesystem resolved from the requester-pays path.

Dependencies and integration points: public requester-pays dataset, S3A request header propagation to bucket probes, GETs, and list calls, and stream-type-specific request behavior.

Risks: public dataset or billing/config availability can change; stream-open counter expectations differ by stream type; client-side encryption is skipped for success path.

Test signals: validates requester-pays option reaches all needed S3 requests and that missing option fails clearly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ARequesterPays.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AStorageClass.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AStorageClass.java

Purpose: Parameterized storage-class tests across disk and array fast-upload buffers. It verifies storage class metadata on create/copy/rename for default, reduced redundancy, Glacier, invalid, and empty values.

Important APIs/types/functions: `Constants.STORAGE_CLASS`, `STORAGE_CLASS_REDUCED_REDUNDANCY`, `STORAGE_CLASS_GLACIER`, `FAST_UPLOAD_BUFFER`, `FAST_UPLOAD_BUFFER_DISK`, `FAST_UPLOAD_BUFFER_ARRAY`, `HeaderProcessing.XA_STORAGE_CLASS`, `decodeBytes()`, `S3AContract`, and `FileSystem.rename()`.

Control flow: constructor selects buffer type. Configuration skips unless storage-class tests are enabled, disables FS caching, removes relevant overrides, and sets fast-upload buffer. Each test creates a contract filesystem, makes a directory, asserts directory markers have no storage class, touches a file, checks expected xattr storage class, and renames/copies where appropriate. Glacier expects `AccessDeniedException`/`InvalidObjectState` on rename because archived objects cannot be read directly.

State and persistence: writes S3 directory markers and objects with varied storage class. No local state beyond parameter.

Dependencies and integration points: S3 object storage-class metadata, S3A PUT/copy header propagation, xattr header projection, fast-upload buffer implementations, and archive-object read semantics.

Risks: reduced redundancy or Glacier support may vary by store/region; invalid storage class is expected to degrade to no metadata rather than fail; directories intentionally differ from files.

Test signals: catches lost storage class on create or rename and verifies archive class failures are surfaced as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AStorageClass.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ATemporaryCredentials.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ATemporaryCredentials.java

Purpose: Tests STS temporary credential acquisition, validation, session-token propagation into S3A and delegation tokens, expiry metadata, bad endpoint/region handling, and exception translation.

Important APIs/types/functions: `STSClientFactory`, `StsClient`, `TemporaryAWSCredentialsProvider`, `MarshalledCredentials`, `MarshalledCredentialBinding`, `SessionTokenIdentifier`, `requestSessionCredentials()`, `toAWSCredentials()`, `assertCredentialsEqual()`, `ASSUMED_ROLE_STS_ENDPOINT`, `ASSUMED_ROLE_STS_ENDPOINT_REGION`, `AWS_CREDENTIALS_PROVIDER`, and `SESSION_TOKEN`.

Control flow: setup requires session tests and configures delegation-token session binding. `testSTS()` shares parent credentials, requests STS credentials, writes them to a cloned config, verifies S3 access with temporary credentials, then corrupts the token and expects S3 access failure. Other tests validate blank/empty credential rejection, delegation-token origin and exact credential propagation, expiry within expected duration, invalid STS token failure, region/endpoint combinations via `expectedSessionRequestFailure()`, validation on load, empty credentials, and request exception translation.

State and persistence: `credentials` holds a shared credential provider list closed in teardown. Tests write small S3 files with temporary credentials and call live STS endpoints.

Dependencies and integration points: AWS STS, S3A credential provider binding, delegation-token session binding, retry invoker, marshalled credential validation, region/endpoint signing rules, and filesystem creation with cloned configs.

Risks: live STS/network/account permissions required; clock skew affects expiry assertions; expected exception types vary by endpoint/region behavior; corrupted token failure can occur at filesystem creation or file IO.

Test signals: broad credential-chain signal covering both successful temporary credential use and many failure/validation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ATemporaryCredentials.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ATestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ATestUtils.java

Purpose: Integration tests for `S3ATestUtils` property lookup helpers, especially precedence and the sentinel for unsetting system properties.

Important APIs/types/functions: `getTestProperty()`, `getTestPropertyLong()`, `getTestPropertyInt()`, `getTestPropertyBool()`, `UNSET_PROPERTY`, Hadoop `Configuration`, and `System.setProperty()/clearProperty()`.

Control flow: `clear()` removes the test system property before each test. Each test starts with a default, sets a Hadoop config value, then sets a Java system property and verifies system property precedence. `unsetSysprop()` sets the property to `UNSET_PROPERTY`, after which lookup falls back to config or default as appropriate.

State and persistence: mutates one JVM system property named `undefined.property`; cleared before each test but not always after. Uses `Configuration(false)` to avoid default resource noise.

Dependencies and integration points: S3A test utility configuration precedence used by integration-test setup and property pushdown.

Risks: JVM system properties are global and can leak if tests run in unusual order; parsing failures for numeric/bool variants are not covered here.

Test signals: confirms system property override and explicit unset sentinel behavior for string, long, int, and boolean helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ATestUtils.java -->
