# Research: subset-b-008070

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/v1/AbstractS3SDKV1Tests.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/v1/AbstractS3SDKV1Tests.java

## Purpose

`AbstractS3SDKV1Tests` is the common JUnit 5 integration-test base for exercising Apache Ozone's S3 Gateway with the AWS Java SDK v1. Concrete standalone and HA/Ratis test classes inherit it via `OzoneTestBase` and `NonHATests.TestCase`, while this base owns the SDK-specific client setup and the behavior suite.

The class validates S3 API compatibility across bucket lifecycle, object put/get/head/copy, object tags, conditional headers, MD5 digest validation, multipart upload, presigned URLs, quota failures, snapshot reads, and edge cases where objects were created through the native Ozone client rather than S3. It also documents unsupported or partially supported S3 features in the leading comment, including versioning, lifecycle, bucket policies, encryption, event notifications, and several ACL modes.

## Important APIs, Types, and Functions

- `createClient()` obtains the `MiniOzoneCluster` from `OzoneTestBase.cluster()` and creates an AWS SDK v1 `AmazonS3` through `S3ClientFactory.createS3Client()`.
- Bucket APIs under test include `createBucket`, `doesBucketExist`, `doesBucketExistV2`, `listBuckets`, `deleteBucket`, `getBucketAcl`, and `setBucketAcl`.
- Object APIs under test include `putObject`, `getObject`, `getObjectMetadata`, `copyObject`, `deleteObject`, `doesObjectExist`, `setObjectAcl`, `setObjectTagging`, and `getObjectTagging`.
- Multipart APIs under test include `initiateMultipartUpload`, `uploadPart`, `completeMultipartUpload`, `abortMultipartUpload`, `listMultipartUploads`, and `listParts`.
- Presigned URL tests use `GeneratePresignedUrlRequest`, `HttpURLConnection`, and helper utilities from `S3SDKTestUtils` to exercise raw HTTP GET, HEAD, PUT, POST, and DELETE flows.
- Native Ozone integration uses `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `OzoneOutputStream`, `OzoneManagerProtocol`, `OmBucketInfo`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and `ReplicationConfig`.
- Helper methods `multipartUpload`, `initiateMultipartUpload`, `uploadParts`, `completeMultipartUpload`, and `abortMultipartUpload` encapsulate the low-level MPU sequence and assert intermediate response fields.

## Control Flow

The suite is class-lifecycle based (`@TestInstance(PER_CLASS)`) and initializes one shared `AmazonS3` client before tests run. Tests generally allocate unique bucket and key names through `uniqueObjectName()`, create the required bucket, perform one S3 operation sequence, then assert SDK response fields and server-side error mapping.

The object tests progress from basic put/copy behavior into conditional request coverage. `If-None-Match` and `If-Match` cases assert success, `PreconditionFailed` status `412`, and preservation of the original ETag after failed overwrites. Copy-object tests check source ETag constraints; in SDK v1 failed source-copy preconditions are asserted as a null `CopyObjectResult`, which is an SDK-v1-specific behavior worth preserving in compatibility tests.

Multipart control flow follows the AWS sequence: initiate upload, upload parts, collect `PartETag` values, and complete or abort. Pagination tests create multiple outstanding MPUs, walk `keyMarker` and `uploadIdMarker`, check truncation and next-marker semantics, and verify prefix filtering. Part listing tests upload a fixed-size file, page through `ListParts`, and compare part numbers and ETags.

The nested `PresignedUrlTests` creates a fixed bucket once and then uses generated URLs outside the SDK request path. MPU presigned flow manually builds the complete-MPU XML payload, uploads 5 MB chunks with `RandomAccessFile`/`ByteBuffer`, captures ETags from HTTP headers, and posts completion XML back to the S3 Gateway.

## State and Persistence Behavior

Most state is persisted in the MiniOzoneCluster through real S3 Gateway requests. The suite verifies not just SDK return values but durable object metadata, tags, ETags, object presence/absence, and bucket emptiness. Several tests intentionally cross the S3/Ozone boundary: objects created with `OzoneOutputStream` lack S3 ETags and must still be readable/listable through S3, and Ozone snapshots created by `ObjectStore.createSnapshot` must be exposed through `.snapshot/<snapshot>/<key>` S3 keys.

The empty-object tests assert a storage-allocation invariant: a zero-length S3 object has `dataSize == 0`, no key locations, and does not increase SCM allocated-block metrics. Quota tests mutate the underlying Ozone bucket quota and expect S3 writes to fail with `QuotaExceeded`.

Incomplete multipart uploads are treated as bucket contents for delete-bucket purposes until explicitly aborted. This is an important persistence contract because MPU metadata alone must block bucket deletion with `BucketNotEmpty`.

## Dependencies and Integration Points

The file depends on AWS SDK v1 S3 and TransferManager types, JUnit 5, AssertJ, Commons IO, Hadoop/Ozone mini-cluster test infrastructure, Ozone client APIs, S3 Gateway constants/utilities, and S3 error-table constants. It integrates with the Ozone S3 Gateway through `S3ClientFactory`, and with core Ozone services through `MiniOzoneCluster`, SCM metrics, Ozone Manager protocol calls, and Ozone object-store clients.

Important external compatibility points include AWS SDK v1 request/response object shapes, raw HTTP presigned URL behavior, S3-compatible error codes/status codes, MD5/ETag conventions, tag count headers, and multipart marker ordering.

## Risks and Edge Cases

- Tests assume deterministic ETags for known small payloads and per-part MD5 values; changes to checksum semantics or quoting could break many assertions.
- Some SDK v1 behavior differs from v2, notably failed copy preconditions returning `null` rather than throwing an exception.
- The helper `initiateMultipartUpload` only attaches tags when metadata is non-empty, so adding tag-only MPU coverage would need care.
- Multipart helper digest validation reads from a shared `fileInputStream` while upload requests read from the file path; this relies on matching sequential part order.
- Presigned URL MPU code manually serializes XML and strips ETag quotes, making it sensitive to XML shape, ETag quoting, and signed-header requirements.
- ACL tests contain TODO-disabled assertions for bucket ACL correctness and assert object ACL `NotImplemented`; these are test signals for known incomplete functionality.
- Shared nested presigned bucket names are fixed, so concrete subclasses or parallel test execution must avoid cross-run collisions.

## Test Signals

Strong success signals include exact S3 status/error-code assertions (`NoSuchBucket`, `NoSuchKey`, `BucketNotEmpty`, `BadDigest`, `InvalidDigest`, `PreconditionFailed`, `NoSuchUpload`, `QuotaExceeded`, `NotImplemented`), content round trips, metadata/tag validation, pagination marker checks, raw HTTP response codes for presigned URLs, and native Ozone verification of storage allocation and snapshots. The suite is a broad compatibility guard for AWS SDK v1 clients against Ozone S3 Gateway behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/v1/AbstractS3SDKV1Tests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/v2/AbstractS3SDKV2Tests.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/v2/AbstractS3SDKV2Tests.java

## Purpose

`AbstractS3SDKV2Tests` is the AWS Java SDK v2 counterpart to the SDK v1 S3 Gateway integration-test base. It verifies Ozone's S3-compatible behavior using v2 `S3Client`, `S3AsyncClient`, v2 presigner APIs, v2 transfer manager, and v2 model exception semantics.

The class overlaps with v1 coverage for core bucket/object/MPU/presigned behavior, but it also adds v2-only or v2-focused compatibility checks: conditional GET/HEAD requests, destination-side copy preconditions, resumable transfer-manager download after ETag mismatch, expected-bucket-owner verification for many endpoints, link-bucket ownership cases, and the S3 Express-style `ListDirectoryBuckets` API over Ozone FSO buckets.

## Important APIs, Types, and Functions

- `createClient()` builds `S3Client` and `S3AsyncClient` via `S3ClientFactory.createS3ClientV2()` and `createS3AsyncClientV2()`.
- `closeClient()` closes both clients after the class, reducing resource leakage from Apache HTTP/async client internals.
- Core SDK v2 APIs under test include `putObject`, `getObject`, `getObjectAsBytes`, `headObject`, `copyObject`, `listBuckets`, `listObjects`, `listObjectsV2`, object tagging APIs, and delete APIs.
- Multipart APIs use `CreateMultipartUploadRequest/Response`, `UploadPartRequest/Response`, `CompletedPart`, `CompletedMultipartUpload`, and `CompleteMultipartUploadRequest/Response`.
- Presigned flows use `S3Presigner` and typed presign requests for get/head/put/delete/create-MPU/upload-part/complete-MPU. The tests execute the URLs with both `HttpURLConnection` and AWS SDK v2 `SdkHttpClient`.
- `S3TransferManager` and `ResumableFileDownload` validate SDK v2 transfer behavior against Ozone object replacement.
- Nested ownership tests exercise `expectedBucketOwner` and `expectedSourceBucketOwner` across bucket, object, tagging, MPU, copy, delete, and link-bucket calls.
- `ListDirectoryBucketsTests` uses `ListDirectoryBucketsRequest`, `ListDirectoryBucketsResponse`, and Ozone `BucketLayout.FILE_SYSTEM_OPTIMIZED` buckets to validate directory-bucket listing behavior.

## Control Flow

The class initializes shared sync and async clients once per class and closes them at the end. Most tests build request objects through SDK v2 builders, perform an operation, and assert v2 response fields or `S3Exception` details.

Core object flow checks ETag quoting as emitted by SDK v2, tag parsing for header-only tag keys, sorted tag-return order, conditional put failure behavior, conditional GET/HEAD response codes (`304` and `412`), zero-byte object storage invariants, and MD5 validation. Multipart tests initiate, upload, complete, or abort using explicit SDK v2 model objects and use `stripQuotes` where server ETags need to be compared to raw MD5 hex.

Copy tests cover both source preconditions (`copySourceIfMatch`, `copySourceIfNoneMatch`) and destination preconditions (`ifMatch`, `ifNoneMatch`). Unlike the v1 suite, failed preconditions are expected to throw `S3Exception` with status `412`.

The nested presigned tests build an SDK v2 `S3Presigner` from the live client's endpoint, region, credentials provider, and path-style configuration. They then execute signed URLs through two independent HTTP paths. The MPU presigned test runs two complete upload cycles, one via `HttpURLConnection` and one via `SdkHttpClient`, each manually uploading parts and posting complete-MPU XML.

Ownership verification first creates a default bucket, records the owner from `getBucketAcl`, and seeds an object. It then verifies correct owner values pass and `WRONG_OWNER` fails with `403 Access Denied` across endpoint groups. Link-bucket tests create source buckets in a non-S3 volume and link them into the S3 volume, including a dangling-link case after deleting the source bucket.

Directory-bucket tests create FSO buckets through the Ozone client, call `listDirectoryBuckets` by setting `maxDirectoryBuckets`, and verify filtering, pagination, response fields, max-zero behavior, and coexistence with regular `ListBuckets`.

## State and Persistence Behavior

The tests persist real buckets, keys, tags, multipart upload state, link-bucket metadata, and snapshots in the MiniOzoneCluster. They inspect persisted object data through SDK reads, Ozone native reads, head responses, tag counts, and storage metrics. Empty-object storage is verified to avoid block allocation just as in the v1 suite.

The resumable download test intentionally persists one object version, pauses a transfer, overwrites the object with different content, and resumes. The expected persistence behavior is that the resumed transfer detects the ETag mismatch and downloads the current object content rather than leaving stale data.

Ownership tests rely on persisted ACL owner metadata and expected-owner checks being enforced before endpoint actions mutate state. Directory-bucket tests persist FSO bucket layout metadata and then clean those buckets through Ozone APIs in `finally` blocks.

## Dependencies and Integration Points

This file integrates AWS SDK v2 S3 sync/async clients, the SDK v2 Apache HTTP client, the SDK v2 presigner, SDK v2 transfer manager, JUnit 5, AssertJ, Commons IO, Ozone MiniOzoneCluster, Ozone object-store APIs, Ozone bucket layout/link-bucket APIs, and S3 Gateway constants/utilities.

It is an important compatibility boundary for SDK v2 model behavior: quoted ETags, typed exceptions, builder-only request construction, expected-owner headers, `ListDirectoryBuckets` routing, presigner signed headers, and transfer-manager resume semantics.

## Risks and Edge Cases

- Many assertions depend on SDK v2 ETag quoting, while helpers sometimes strip quotes; inconsistent server quoting can break otherwise valid data paths.
- Presigned PUT and MPU tests mutate signed header maps before HTTP execution; changes in presigner immutability or required signed headers could affect the tests.
- The `testPresignedUrlDelete` second half reuses a presigned DELETE URL after re-uploading the object, which assumes the URL remains valid for the same bucket/key and duration.
- `initiateMultipartUpload` always builds `Tagging.builder().tagSet(tags)`; callers currently pass tags in the low-level helper path, but a future null call would need guarding.
- Directory-bucket tests create and delete FSO buckets through Ozone native APIs, so cleanup failures can affect later list results.
- Ownership tests share fixed bucket/key names inside nested classes; parallel subclass execution needs isolation.
- Link-bucket and dangling-bucket coverage depends on Ozone ownership resolution semantics, which are more complex than plain bucket ACL reads.

## Test Signals

Key signals are exact `S3Exception` status/error-code assertions, successful content round trips, tag count and sorted tag validation, ETag changes after overwrites, zero-block empty object verification, transfer-manager resumed content validation, expected-owner `403 Access Denied`, link-bucket pass/fail checks, presigned raw HTTP status codes, and directory-bucket filtering/pagination/field assertions. The class is a high-value regression guard for AWS SDK v2 compatibility and newer S3 Gateway features.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/v2/AbstractS3SDKV2Tests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/resources/ozone-site.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/resources/ozone-site.xml

## Purpose

This `ozone-site.xml` is the test-resource configuration overlay for the `integration-test-s3` module. It tunes MiniOzoneCluster/S3 Gateway integration tests toward deterministic, faster behavior and S3-relevant data-path settings.

## Important Properties

- `ozone.om.transport.class` selects `org.apache.hadoop.ozone.om.protocolPB.Hadoop3OmTransportFactory`.
- `ozone.om.s3.grpc.server_enabled=false` disables the OM S3 gRPC server path for these tests, keeping coverage on the HTTP S3 Gateway path.
- Handler/thread settings such as `hdds.container.ratis.num.write.chunk.threads.per.volume=4`, `ozone.scm.handler.count.key=20`, and `ozone.om.handler.count.key=20` raise concurrency for test workloads.
- `hdds.container.ratis.datastream.enabled=true` enables datastream behavior in the container Ratis path.
- Heartbeat and close-container timing are shortened with `hdds.heartbeat.interval=1s`, `ozone.scm.heartbeat.thread.interval=100ms`, and `ozone.scm.close.container.wait.duration=1s`.
- Ratis queue byte limits are set for container, OM, and SCM HA appenders.
- Chunk/block/container and client buffer sizes are set to small test-friendly values: 1 MB chunks, 4 MB blocks, 128 MB containers, and MB-scale stream/datastream buffers.
- `hdds.datanode.volume.min.free.space=5GB` enforces a minimum free-space threshold in test datanodes.

## Control Flow and State Behavior

The file has no executable control flow. Hadoop/Ozone configuration loading treats each `<property>` entry as an override available on the test classpath. Those values affect cluster startup and runtime behavior before S3 tests issue operations.

The state impact is indirect but significant: smaller chunk/block sizes make multipart and allocation tests easier to reason about, short heartbeat intervals reduce waiting in cluster-state transitions, and disabling OM S3 gRPC avoids ambiguity about which S3 implementation path a test exercised.

## Dependencies and Integration Points

The file is consumed by Hadoop `Configuration` resource loading and MiniOzoneCluster test setup. It integrates with Ozone Manager, SCM, Ratis datastream, datanode volume checks, and S3 Gateway test modules.

## Risks and Edge Cases

- Timing reductions speed tests but can mask production timing behavior or introduce flakiness on slow hosts.
- The explicit free-space requirement can fail tests on constrained CI disks.
- Disabling OM S3 gRPC is intentional for this module; tests here should not be interpreted as covering that alternate server path.
- Small block/chunk sizes are useful for test coverage but may alter allocation patterns compared with production defaults.

## Test Signals

The configuration supports test signals in the SDK test bases: predictable block allocation for empty objects, faster snapshot/container/heartbeat convergence, multipart behavior with MB-scale parts, and consistent S3 Gateway routing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/resources/ozone-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/dev-support/findbugsExcludeFile.xml

## Purpose

This SpotBugs/FindBugs exclude filter belongs to the `ozone-integration-test` module. It currently declares an empty `<FindBugsFilter>` after the standard Apache license header, meaning the module has no local static-analysis suppressions.

## Important APIs, Types, and Functions

The only meaningful XML element is the root `FindBugsFilter`. There are no `<Match>`, bug-code, class, method, or field rules.

## Control Flow and State Behavior

There is no runtime control flow and no persisted application state. Maven's SpotBugs plugin reads this file as an exclude filter. Because it is empty, all SpotBugs findings remain eligible unless suppressed elsewhere by parent configuration or annotations.

## Dependencies and Integration Points

The integration point is `integration-test/pom.xml`, which configures `spotbugs-maven-plugin` with `${basedir}/dev-support/findbugsExcludeFile.xml`. The file is part of build-time quality enforcement for the integration-test module.

## Risks and Edge Cases

- An empty filter is a useful quality signal, but adding noisy integration-test patterns later may tempt broad suppressions.
- If the file path changes without updating the POM, SpotBugs plugin configuration can fail or silently miss intended filters depending on plugin behavior.
- The legacy name says `findbugs`, while the configured plugin is SpotBugs; this is normal in many Hadoop/Ozone modules but can confuse maintainers.

## Test Signals

The file itself has no tests. Its signal is build-time: the module is intended to run static analysis without local excludes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/pom.xml

## Purpose

This Maven POM defines the `ozone-integration-test` module under the Apache Ozone parent. It packages the module as a test-support jar and wires the broad dependency surface required by Ozone integration tests: Hadoop clients and test jars, HDDS/Ozone modules and test jars, MiniOzoneCluster, security/Kerberos/KMS/Ranger components, Ratis, RocksDB, filesystem modules, S3 Gateway, CLI tools, and common utility libraries.

## Important Build Elements

- Parent coordinates are `org.apache.ozone:ozone:2.3.0-SNAPSHOT`; artifact is `ozone-integration-test` with jar packaging.
- Most dependencies are `test` scope, reflecting that this module is for integration-test code rather than production runtime code.
- Hadoop dependencies include `hadoop-auth`, `hadoop-common` plus test jar, `hadoop-distcp` plus test jar, HDFS artifacts, KMS artifacts, MapReduce jobclient/core, and MiniKDC.
- Ozone/HDDS dependencies include clients, common/config/container/SCM/server framework modules, admin/client/server interfaces, test utils, manager, mini-cluster, filesystem, CLI, Recon, Freon, S3 Gateway, tools, and RocksDB checkpoint differ.
- Security and ecosystem dependencies include Ranger integration, BouncyCastle, Kerby, Curator, servlet/JAX-RS APIs, Jackson, Guava, Commons libraries, OkHttp, Ratis modules, RocksDB JNI, SLF4J, and reload4j.
- Some Hadoop/KMS/DistCp dependencies exclude reload4j/log4j/SLF4J implementations to keep logging bindings controlled.
- `ozone-s3gateway` is included with a wildcard exclusion of all transitive dependencies, implying this module expects needed transitive dependencies to be supplied explicitly elsewhere.
- Build plugins configure `spotbugs-maven-plugin` to use `dev-support/findbugsExcludeFile.xml` and `maven-compiler-plugin` with annotation processing disabled via `<proc>none</proc>`.

## Control Flow and State Behavior

The POM has no application control flow. During Maven builds it controls dependency resolution, test compilation classpath, static analysis filtering, and compiler behavior. Its state impact is build artifact and classpath composition: integration tests compile against many production and test jars without shipping those dependencies as normal runtime dependencies from this module.

## Dependencies and Integration Points

This file is a central integration point for Ozone integration-test code. It binds the module to the parent build, Maven dependency management, SpotBugs, compiler settings, Hadoop test infrastructure, Ozone MiniOzoneCluster, S3 Gateway classes, security modules, storage backends, Ratis consensus libraries, and filesystem/client APIs.

## Risks and Edge Cases

- The dependency list is intentionally broad; stale or conflicting test-scope dependencies can cause classpath-sensitive integration-test failures.
- Wildcard transitive exclusion on `ozone-s3gateway` makes dependency completeness depend on this POM and parent dependency management.
- Disabling annotation processing avoids unnecessary processors during test compilation, but any future test sources that require generated annotation output would need explicit handling.
- Logging exclusions reduce binding conflicts, but adding new Hadoop/security dependencies can reintroduce duplicate logging implementations.
- Because the module is test-heavy and broad, dependency changes can have a large blast radius across unrelated integration tests.

## Test Signals

The POM's direct signal is successful Maven test compilation and plugin execution for `ozone-integration-test`. It also indirectly enables the Java test bases in this subset by providing Ozone MiniCluster, Ozone client APIs, Hadoop configuration/test utilities, SpotBugs configuration, and related test dependencies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/conf/TestConfigurationFieldsBase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/conf/TestConfigurationFieldsBase.java

## Purpose

`TestConfigurationFieldsBase` is an abstract JUnit 5 test base copied from Hadoop while the original was still JUnit 4 based. Subclasses set an XML defaults file and one or more configuration classes, and this base compares public static final configuration-key constants against XML properties and default-value constants.

It is a configuration hygiene guard: it detects config keys missing from XML docs/defaults, XML properties missing from configuration classes, mismatched XML default values, XML properties with empty values, config keys with no default constant, and selected default-value collisions such as duplicate service ports.

## Important APIs, Types, and Functions

- Subclasses implement `initializeMemberVariables()` and set `xmlFilename`, `configurationClasses`, optional error flags, skip sets, prefix skip sets, and `filtersForDefaultValueCollisionCheck`.
- `extractMemberVariablesFromConfigurationFields(Field[])` reflects over public static final `String` fields, skips default-value fields, partial/file-like values, configured skip entries/prefixes, and values that do not match the property-name regex.
- `extractPropertiesFromXml(String)` loads an XML resource into `Configuration(false)`, enables null-value properties, iterates key/value pairs, applies XML skip lists, and records null for key-only properties.
- `isFieldADefaultValue(Field)` identifies default constants by `DEFAULT_` prefix or `_DEFAULT` suffix.
- `extractDefaultVariablesFromConfigurationFields(Field[])` reflects over public static final default constants and serializes supported primitive/String types into strings.
- `compareConfigurationToXmlFields(Map, Map)` performs key-set difference.
- `setupTestConfigurationFields()` is a `@BeforeEach` method that calls subclass initialization, extracts maps, and computes missing-key sets.
- JUnit tests `testCompareConfigurationClassAgainstXml`, `testCompareXmlAgainstConfigurationClass`, `testXmlAgainstDefaultValuesInConfigurationClass`, and `testDefaultValueCollision` report and optionally fail on discovered mismatches.

## Control Flow

Each test begins with `setupTestConfigurationFields()`. The setup asserts subclass configuration is present, builds `configurationMemberVariables` by reflecting all declared fields of all configured classes, builds `xmlKeyValueMap` through Hadoop `Configuration` resource parsing, builds `configurationDefaultVariables`, then computes the two missing-key sets.

`testCompareConfigurationClassAgainstXml` logs configuration keys not present in XML and fails only when `errorIfMissingXmlProps` is true. `testCompareXmlAgainstConfigurationClass` logs XML properties without matching config constants and fails only when `errorIfMissingConfigProps` is true.

`testXmlAgainstDefaultValuesInConfigurationClass` derives possible default constant names in three patterns: `DEFAULT_` plus key constant name, replacing `_KEY` with `_DEFAULT`, and appending `_DEFAULT`. It then classifies XML properties as matching defaults, mismatching defaults, empty XML values, or having no default constant. This test logs findings but does not assert by default.

`testDefaultValueCollision` iterates requested name filters, gathers numeric default values whose constant names contain the filter, and asserts no duplicate numeric default value appears under that filter.

## State and Persistence Behavior

The class stores extracted maps and missing sets in private instance fields per test instance. Because setup runs before each test, state is recomputed from the subclass-provided class list and XML file and is not persisted outside the test object. XML loading is read-only, and reflection reads static constants without mutating target classes.

The only external side effects are logs through `LOG`, `LOG_CONFIG`, and `LOG_XML`, plus JUnit assertion failures when strict flags or collision checks detect violations.

## Dependencies and Integration Points

The file depends on Hadoop `Configuration`, Java reflection APIs, regex utilities, collection types, Commons Lang `StringUtils`, SLF4J, and JUnit 5. It integrates with Ozone/Hadoop configuration classes through reflection and with XML defaults files through Hadoop resource parsing.

Subclasses across the integration-test module can tune behavior by adding exact-key or prefix skips for generated, deprecated, private, partial, or intentionally undocumented properties.

## Risks and Edge Cases

- Property detection uses a regex that requires dotted names starting with a letter; valid but unusual configuration names outside that pattern will be ignored.
- Default matching depends on naming conventions, so semantically correct defaults with nonstandard constant names are reported as requiring manual verification.
- Duplicate config-key values across classes are logged but not failed directly in extraction.
- `Configuration` resource loading can include substitution or inherited behavior from Hadoop configuration parsing, so XML comparison is not a raw XML parse.
- `HashMap<HashMap<String,String>, HashMap<String,String>>` for mismatches is awkward and can obscure duplicate mismatch reporting, though it is only used for logs.
- Failure behavior is controlled by subclass flags; without strict flags, missing config/XML entries are informational rather than test-failing.

## Test Signals

The strongest test signals are strict missing-key assertions when enabled, null/non-null setup assertions, default numeric collision assertions, and detailed logs listing missing or mismatching entries. The class supports broad configuration documentation consistency tests rather than exercising Ozone runtime behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/conf/TestConfigurationFieldsBase.java -->
