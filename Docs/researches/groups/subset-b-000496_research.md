# subset-b-000496 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSUnderFileSystem.java -->
## sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSUnderFileSystem.java

### Purpose
`GCSUnderFileSystem` is the legacy Google Cloud Storage UFS implementation backed by jets3t. It adapts GCS buckets and objects to Alluxio's `ObjectUnderFileSystem` contract, including object creation, copy, deletion, listing, metadata lookup, opening streams, and best-effort object permission discovery.

### Important APIs, Types, And Functions
The public factory entry is `createInstance(AlluxioURI, UnderFileSystemConfiguration)`, which requires `GCS_ACCESS_KEY` and `GCS_SECRET_KEY` and builds a `GoogleStorageService`. Important overrides are `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `getObjectListingChunk`, `getObjectStatus`, `getPermissions`, `getRootKey`, and `openObject`. The nested `GCSObjectListingChunk` wraps jets3t `StorageObjectsChunk` into Alluxio `ObjectListingChunk`. `mPermissions` memoizes bucket permissions.

### Control Flow
Object operations call the jets3t client directly. Copies retry three times. Listings normalize prefixes, choose a delimiter based on recursive mode, request chunked listings, and expose objects, common prefixes, and follow-up chunks. Metadata lookup maps 404 to `null` and other service failures to `IOException`. Opening delegates to `GCSInputStream`; writing delegates to `GCSOutputStream`; empty directory markers upload zero-byte objects with a precomputed MD5 hash.

### State, Persistence, And Dependencies
Persistent state lives in the GCS bucket. The class holds the bucket name, jets3t client, configuration, and cached `ObjectPermissions`. It depends on jets3t GCS APIs, Alluxio object-store base behavior, `PathUtils`, `ModeUtils`, and static owner-id mapping from configuration.

### Integration Points
The class is selected by `GCSUnderFileSystemFactory` when GCS v2 is not configured. `ObjectUnderFileSystem` supplies high-level file, directory, rename, and recursive-delete behavior around these object primitives. ACLs are not mutable through Alluxio; owner and mode setters are no-ops.

### Risks
The permission cache assumes bucket ACL and owner data do not change during the UFS lifetime. `deleteObject` and copy failures are logged and returned as booleans, so callers must inspect return values. Listing returns `null` on service errors, which can be interpreted as not found by higher layers. Permission inheritance is best effort and falls back to defaults on API failures.

### Test Signals
`GCSUnderFileSystemTest` mocks listing failures and verifies nonrecursive delete, recursive delete, and rename return false. Permission translation is covered separately in `GCSUtilsTest`; factory registration is covered by `GCSUnderFileSystemFactoryTest`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSUnderFileSystemFactory.java -->
## sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSUnderFileSystemFactory.java

### Purpose
`GCSUnderFileSystemFactory` creates the GCS UFS implementation and decides whether to instantiate the legacy jets3t implementation or the Google Cloud Storage v2 implementation.

### Important APIs, Types, And Functions
It implements `UnderFileSystemFactory`. `create(String, UnderFileSystemConfiguration)` checks `UNDERFS_GCS_VERSION`; version `2` creates `GCSV2UnderFileSystem`, otherwise it creates `GCSUnderFileSystem`. `supportsPath(String)` accepts paths starting with `Constants.HEADER_GCS`.

### Control Flow
Creation validates that the path is non-null, constructs an `AlluxioURI`, and delegates to the chosen implementation's static create method. `IOException` and jets3t `ServiceException` are logged and propagated through Guava `Throwables.propagate`.

### State, Persistence, And Dependencies
The factory is stateless and thread-safe. It depends on Alluxio configuration keys, GCS UFS classes, Guava preconditions/throwables, and the UFS factory SPI.

### Integration Points
The service registry discovers this factory so `gs://` paths can mount through the GCS module. It is the only switch point between legacy and v2 GCS clients.

### Risks
The v2 choice is a strict integer comparison; unexpected version values silently choose the legacy implementation. Propagating checked creation failures as runtime exceptions can surface later than a direct checked error path.

### Test Signals
`GCSUnderFileSystemFactoryTest` verifies that the registry finds a factory for a `gs://` path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSUtils.java -->
## sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSUtils.java

### Purpose
`GCSUtils` converts jets3t GCS bucket ACL grants into Alluxio owner-mode bits.

### Important APIs, Types, And Functions
`translateBucketAcl(GSAccessControlList, String)` returns a POSIX-style `short` mode. It checks grants for read, write, and full-control permissions. `isUserIdInGrantee` treats the configured owner id, all-users group, and authenticated-users group as matches.

### Control Flow
The method iterates every ACL grant. Read grants add owner read and execute bits, write grants add owner write, and full-control grants add owner read/write/execute. Unsupported ACL permissions such as READ_ACP do not change mode.

### State, Persistence, And Dependencies
There is no retained state. It depends on jets3t ACL types and Alluxio callers that interpret the returned mode.

### Integration Points
`GCSUnderFileSystem.getPermissionsInternal` uses this helper when it can fetch the bucket ACL, falling back to default mode when ACL inheritance fails.

### Risks
Group grants are translated into owner permission bits, not group/other bits, because the GCS UFS has no group model. The helper trusts non-null ACL and grantee identifiers.

### Test Signals
`GCSUtilsTest` covers user, all-users, and authenticated-users grants for read, write, and full control, including nonmatching user ids and ignored READ_ACP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/v2/GCSV2InputStream.java -->
## sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/v2/GCSV2InputStream.java

### Purpose
`GCSV2InputStream` is a non-thread-safe input stream over the Google Cloud Storage client library. It provides efficient offset reads and skips by using `ReadChannel.seek` instead of reading and discarding bytes.

### Important APIs, Types, And Functions
The constructor captures bucket, key, `Storage` client, and initial position. Overrides include `read()`, `read(byte[], int, int)`, `skip(long)`, and `close()`. `openStream()` creates the `ReadChannel` and seeks to `mPos`.

### Control Flow
The channel is opened lazily on the first read or skip. Reads wrap target buffers in `ByteBuffer`, update `mPos` on successful reads, and return `-1` at EOF. `skip` advances `mPos`, opens the channel if needed, and seeks directly to the new position.

### State, Persistence, And Dependencies
State is the current position, one-byte buffer, and optional `ReadChannel`. Persistent data remains in GCS. It depends on `com.google.cloud.storage.Storage`, `BlobId`, and `ReadChannel`.

### Integration Points
`GCSV2UnderFileSystem.openObject` creates this stream with `OpenOptions.getOffset()`. It provides the stream behavior used by Alluxio object-store reads under GCS v2.

### Risks
`skip` returns the requested count without checking object length, so EOF is only observed by a later read. The stream is not synchronized and should not be shared across threads. `close` does not null the channel, so reads after close rely on channel behavior.

### Test Signals
There is no direct test in this subset. Useful tests would verify offset reads, skip beyond EOF, empty-buffer reads returning zero, lazy open, and StorageException-to-IOException wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/v2/GCSV2InputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/v2/GCSV2OutputStream.java -->
## sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/v2/GCSV2OutputStream.java

### Purpose
`GCSV2OutputStream` streams writes directly into GCS using the v2 `WriteChannel`, avoiding the legacy local-temporary-file upload path.

### Important APIs, Types, And Functions
It extends `OutputStream` and implements `ContentHashable`. Constructor validates the bucket and prepares `BlobInfo`. `write` methods lazily create the write channel, update an MD5 digest when available, and write `ByteBuffer`s. `close()` closes the channel or creates an empty blob. `getContentHash()` returns a stored GCS MD5 only for empty-object creation.

### Control Flow
The first write opens `mClient.writer(mBlobInfo)`. Byte-array writes pass through `ByteBuffer.wrap`; single-byte writes use a preallocated buffer. `close` is guarded by `AtomicBoolean`; if no data was written, it creates the object via `Storage.create`.

### State, Persistence, And Dependencies
State includes the bucket/key, `Storage` client, write channel, MD5 digest, closed flag, and optional content hash. The object persists in GCS when the write channel closes or the empty blob is created.

### Integration Points
`GCSV2UnderFileSystem.createObject` returns this stream for GCS v2 writes. `ContentHashable` allows higher layers to retrieve a content hash after successful close when available.

### Risks
`write(int)` calls `ByteBuffer.putInt(b)` on a one-byte buffer, which can overflow at runtime and should be tested. For non-empty writes, the computed MD5 digest is never exposed as `mContentHash`, so content hash retrieval is incomplete. Flush is a no-op because GCS write channels do not support it.

### Test Signals
No direct tests are present. High-value tests would cover single-byte writes, byte-array writes, duplicate close, empty object close, StorageException wrapping, and `getContentHash` behavior for non-empty writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/v2/GCSV2OutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/v2/GCSV2UnderFileSystem.java -->
## sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/v2/GCSV2UnderFileSystem.java

### Purpose
`GCSV2UnderFileSystem` is the Google Cloud Storage UFS implementation based on `com.google.cloud.storage`. It implements the `ObjectUnderFileSystem` primitives using the newer GCS client library.

### Important APIs, Types, And Functions
`createInstance` loads explicit service-account credentials from `GCS_CREDENTIAL_PATH` or application-default credentials, configures retry settings, and creates a `Storage` service. Core overrides include `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `getObjectListingChunk`, `getObjectStatus`, `getPermissions`, `getRootKey`, and `openObject`. The nested `GCSObjectListingChunk` wraps paged `Blob` listings.

### Control Flow
Listings normalize prefixes and either call `Storage.list` with a prefix only for recursive scans or with `currentDirectory` for one-level scans. Each page is converted to object statuses and followed with `getNextPage`. Metadata lookup treats null and 404 as not found. Writes use `GCSV2OutputStream`; reads use `GCSV2InputStream`.

### State, Persistence, And Dependencies
State is the storage client, bucket name, and UFS config. Persistent data is in the GCS bucket. Dependencies include Google auth, gax retry settings, `StorageOptions`, Alluxio object UFS support, and `ModeUtils` for default permissions.

### Integration Points
`GCSUnderFileSystemFactory` selects this implementation when `UNDERFS_GCS_VERSION` is `2`. It provides the same `getUnderFSType` value as legacy GCS, so upper layers see it as `"gcs"`.

### Risks
ACL inheritance is not implemented; permissions always use configured default mode and empty owner/group. `getCommonPrefixes` returns an empty array even for directory listings, relying on `currentDirectory` blobs instead of explicit common prefixes. Empty object creation does not set the static directory hash in metadata.

### Test Signals
There are no direct v2 tests in this subset. Useful coverage would mock `Storage` for listing pagination, copy/delete failures, credentials selection, retry settings, open offsets, and empty-object behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/v2/GCSV2UnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/test/java/alluxio/underfs/gcs/GCSUnderFileSystemFactoryTest.java -->
## sources/distributed-fs/alluxio/underfs/gcs/src/test/java/alluxio/underfs/gcs/GCSUnderFileSystemFactoryTest.java

### Purpose
This JUnit test verifies that the GCS UFS module registers a factory for `gs://` paths.

### Important APIs, Types, And Functions
The single `factory()` test calls `UnderFileSystemFactoryRegistry.find("gs://test-bucket/path", Configuration.global())` and asserts that a non-null `UnderFileSystemFactory` is returned.

### Control Flow
The test relies on module service discovery and global configuration. It does not instantiate an actual GCS client or validate credentials.

### State, Persistence, And Dependencies
No persistent state is modified. Dependencies are JUnit, Alluxio configuration, and UFS factory registry metadata.

### Integration Points
This is a smoke test for `GCSUnderFileSystemFactory.supportsPath` and service registration.

### Risks
It does not verify the version switch between legacy and v2 implementations, error propagation, unsupported paths, or required credential checks.

### Test Signals
A failure indicates the module is not visible to the registry or does not recognize `gs://` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/test/java/alluxio/underfs/gcs/GCSUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/test/java/alluxio/underfs/gcs/GCSUnderFileSystemTest.java -->
## sources/distributed-fs/alluxio/underfs/gcs/src/test/java/alluxio/underfs/gcs/GCSUnderFileSystemTest.java

### Purpose
`GCSUnderFileSystemTest` validates legacy GCS UFS failure behavior for operations implemented through object listings.

### Important APIs, Types, And Functions
The setup creates a mocked `GoogleStorageService` and injects it into a `GCSUnderFileSystem`. Tests cover `deleteDirectory` in recursive and nonrecursive modes and `renameFile`.

### Control Flow
Each test configures `listObjectsChunked` to throw `ServiceException`. It then calls the high-level `ObjectUnderFileSystem` operation and asserts the result is false.

### State, Persistence, And Dependencies
No external GCS state is used. The test depends on Mockito, JUnit, Alluxio `DeleteOptions`, and default UFS configuration.

### Integration Points
The tests indirectly exercise `GCSUnderFileSystem.getObjectListingChunk` and the inherited object-store delete/rename logic.

### Risks
Coverage is limited to listing exceptions. It does not test successful listing, pagination, object status, copy retries, delete failures, permission inheritance, or stream creation.

### Test Signals
Passing tests indicate service listing errors are converted into non-successful high-level operations rather than uncaught exceptions for these paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/test/java/alluxio/underfs/gcs/GCSUnderFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/test/java/alluxio/underfs/gcs/GCSUtilsTest.java -->
## sources/distributed-fs/alluxio/underfs/gcs/src/test/java/alluxio/underfs/gcs/GCSUtilsTest.java

### Purpose
`GCSUtilsTest` verifies translation from jets3t GCS ACL grants to Alluxio owner-mode bits.

### Important APIs, Types, And Functions
Setup builds a `GSAccessControlList` and a canonical user grantee. Tests call `GCSUtils.translateBucketAcl` with matching and nonmatching user ids and with group grantees.

### Control Flow
Each test grants one or more permissions and asserts the expected octal mode. Read maps to `0500`, write to `0200`, read plus write to `0700`, and full control to `0700`.

### State, Persistence, And Dependencies
The ACL is in-memory only. Dependencies are JUnit and jets3t ACL classes.

### Integration Points
This test protects `GCSUnderFileSystem` permission inheritance from bucket ACLs.

### Risks
It does not cover null grantees, null ACLs, duplicate grants beyond simple OR behavior, or interaction with configured default modes.

### Test Signals
Passing tests show that user, all-users, and authenticated-users ACL grants are treated as owner permissions as intended by the GCS UFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/test/java/alluxio/underfs/gcs/GCSUtilsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/pom.xml -->
## sources/distributed-fs/alluxio/underfs/hdfs/pom.xml

### Purpose
This Maven module builds the HDFS under file system extension and packages it against a configurable shaded Hadoop dependency.

### Important APIs, Types, And Functions
The artifact is `alluxio-underfs-hdfs`. Properties define `ufs.hadoop.version` and the versioned library jar name. Profiles choose `ufs-hadoop-2` or default `ufs-hadoop-3` and include `alluxio-shaded-hadoop`. Additional profiles optionally include ACL and ActiveSync support classes. The templating plugin generates `UfsConstants`.

### Control Flow
By default, compilation excludes `SupportedHdfsAclProvider` and `SupportedHdfsActiveSyncProvider`. Activating `hdfsAcl`, `hdfsActiveSync`, or `hdfsAclandActiveSync` overrides exclusions. Build plugins shade, copy/rename, filter templates, and preprocess sources.

### State, Persistence, And Dependencies
The build persists compiled extension artifacts and generated Java templates. Runtime code depends on `alluxio-core-common`, shaded Hadoop, and commons-lang3.

### Integration Points
The generated `alluxio.UfsConstants.UFS_HADOOP_VERSION` is read by HDFS factory/version logic and by HDFS EC class loading checks.

### Risks
Feature classes are excluded unless the right Maven profile is active, so runtime reflection in `HdfsUnderFileSystem` may silently fall back to no-op providers. Versioned jar naming must match deployment expectations.

### Test Signals
Module tests compile against the selected profile and validate factory discovery, version parsing, HDFS configuration, and positioned-read switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java-templates/alluxio/UfsConstants.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java-templates/alluxio/UfsConstants.java

### Purpose
This template generates compile-time constants for the HDFS UFS module.

### Important APIs, Types, And Functions
It defines `UfsConstants.UFS_HADOOP_VERSION`, filled from Maven property `${ufs.hadoop.version}`, and has a private constructor.

### Control Flow
The templating plugin filters this source into generated Java sources during the Maven build.

### State, Persistence, And Dependencies
There is no runtime mutable state. The generated constant persists in the compiled extension jar.

### Integration Points
`HdfsUnderFileSystemFactory.getVersion` returns this value, and `HdfsUnderFileSystem` compares it to the EC minimum version when initializing Hadoop erasure-coding classes.

### Risks
String comparison is later used for a semantic version gate, so nonstandard version strings could produce incorrect ordering. A missing template filtering step would leave the placeholder literal in the runtime class.

### Test Signals
`HdfsVersionTest` checks parsing/matching behavior around Hadoop labels, indirectly protecting callers that compare configured versions to this constant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java-templates/alluxio/UfsConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/AlluxioHdfsException.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/AlluxioHdfsException.java

### Purpose
`AlluxioHdfsException` maps HDFS and WebHDFS exceptions to Alluxio runtime exceptions with gRPC statuses, error types, and retryability.

### Important APIs, Types, And Functions
`fromUfsException(Exception)` is the main conversion entry. `convertException` unwraps Jersey `ParamException`, `ContainerException`, Hadoop `RemoteException`, and some `SecurityException` causes. `toCause` handles nested causes, including the HDFS invalid-token/standby exception case.

### Control Flow
The converter normalizes wrapper exceptions first, then maps security, authorization, not found, unsupported operation, invalid argument, IO, and unknown categories to corresponding statuses. General `IOException` maps to `ABORTED`, external, retryable.

### State, Persistence, And Dependencies
No state is retained. It depends on Alluxio runtime exception types, gRPC `Status`, Hadoop IPC/security exceptions, and Jersey exceptions.

### Integration Points
`HdfsPositionedUnderFileInputStream` wraps read failures with `AlluxioHdfsException.from(e)`, surfacing lower-level HDFS errors through Alluxio's runtime-exception model.

### Risks
Most HDFS errors are marked non-retryable except generic IO, which may be too broad or too narrow depending on the original remote exception. Message extraction can assume nested causes exist for parameter errors.

### Test Signals
No direct test exists in this subset. Useful tests would cover each mapped exception category, RemoteException unwrapping, StandbyException nested in InvalidToken, and null/empty messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/AlluxioHdfsException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsAclProvider.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsAclProvider.java

### Purpose
`HdfsAclProvider` defines the abstraction for retrieving and setting HDFS ACLs without forcing all builds to compile against ACL-capable Hadoop APIs.

### Important APIs, Types, And Functions
`getAcl(FileSystem, String)` returns an Alluxio ACL/default-ACL pair or null values when ACLs are unsupported. `setAclEntries(FileSystem, String, List<AclEntry>)` writes Alluxio ACL entries to HDFS.

### Control Flow
This interface has no implementation flow. Callers use it through either `SupportedHdfsAclProvider` or `NoopHdfsAclProvider`.

### State, Persistence, And Dependencies
No state is defined. It depends on Hadoop `FileSystem` and Alluxio authorization types.

### Integration Points
`HdfsUnderFileSystem` instantiates a provider by reflection and delegates `getAclPair` and `setAclEntries`.

### Risks
Returning a pair of nulls for unsupported ACLs requires callers to distinguish unsupported from an empty ACL. Implementations must handle files and directories differently for default ACLs.

### Test Signals
There are no direct interface tests. Coverage comes from UFS ACL behavior when supported providers are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsAclProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsActiveSyncProvider.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsActiveSyncProvider.java

### Purpose
`HdfsActiveSyncProvider` abstracts HDFS inotify-based active sync support behind a provider interface.

### Important APIs, Types, And Functions
The interface exposes `getActivitySyncInfo`, `startPolling(long)`, `stopPolling`, `startSync(AlluxioURI)`, and `stopSync(AlluxioURI)`.

### Control Flow
Implementations are responsible for starting and stopping a polling thread, tracking sync points, and returning `SyncInfo` deltas or full-sync signals.

### State, Persistence, And Dependencies
The interface itself has no state. It depends on `AlluxioURI`, `SyncInfo`, and checked IO errors for polling startup.

### Integration Points
`HdfsUnderFileSystem` delegates all active-sync methods to a reflected provider or a no-op fallback.

### Risks
The interface does not prescribe threading or lifecycle semantics beyond boolean start/stop results, so implementations must be careful about duplicate starts and concurrent sync-point updates.

### Test Signals
No direct tests are present. Integration tests should validate provider availability by Hadoop version/profile and `SyncInfo` correctness after file-system events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsActiveSyncProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsPositionedUnderFileInputStream.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsPositionedUnderFileInputStream.java

### Purpose
`HdfsPositionedUnderFileInputStream` is a seekable HDFS input stream optimized for remote/random reads. It switches between positioned reads and normal buffered reads based on recent access patterns.

### Important APIs, Types, And Functions
It extends `SeekableUnderFileInputStream`. Constants `SEQUENTIAL_READ_LIMIT` and `MOVEMENT_LIMIT` drive the heuristic. Overrides include `read`, `read(byte[], int, int)`, `seek`, `skip`, `available`, `getPos`, and `markSupported`.

### Control Flow
Reads use normal `InputStream.read` when the logical position matches the underlying `Seekable` position, or positioned reads otherwise. After enough sequential reads, it seeks the underlying stream to `mPos` and uses buffered reads. Large skips or backward/far seeks reset the sequential counter.

### State, Persistence, And Dependencies
State is in-memory: logical position and sequential-read count. It wraps `FSDataInputStream` and relies on Hadoop `Seekable` and `PositionedReadable`.

### Integration Points
`HdfsUnderFileSystem.open` returns this stream when reads are remote, position-short is requested, or block locality is not satisfied.

### Risks
IOExceptions in read paths are converted to runtime `AlluxioHdfsException`, unlike many Java input streams that throw checked IOExceptions. The heuristic constants are fixed and may not fit all workloads. `skip` can advance beyond EOF before reads detect it.

### Test Signals
`HdfsUnderFileSystemTest.verifyPread` spies on a stream and verifies transitions between buffered reads and positioned reads after small skips, large skips, and far seeks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsPositionedUnderFileInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileInputStream.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileInputStream.java

### Purpose
`HdfsUnderFileInputStream` is the simple seekable wrapper over `FSDataInputStream` for local/sequential HDFS reads.

### Important APIs, Types, And Functions
It extends `SeekableUnderFileInputStream` and implements `seek(long)` and `getPos()` by delegating to the wrapped `FSDataInputStream`.

### Control Flow
All read behavior is inherited from the base filter stream. The only special control path is direct HDFS seek for repositioning.

### State, Persistence, And Dependencies
State is the wrapped input stream held by the superclass. It depends on Hadoop `FSDataInputStream`.

### Integration Points
`HdfsUnderFileSystem.open` returns this stream after seeking to the requested offset when the read is considered local/sequential.

### Risks
It provides no additional retry or recovery around reads after open. Seek errors propagate as checked IOExceptions.

### Test Signals
This class is indirectly exercised by local-style HDFS open paths; the positioned stream has stronger explicit tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileOutputStream.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileOutputStream.java

### Purpose
`HdfsUnderFileOutputStream` wraps `FSDataOutputStream` for HDFS writes and maps Alluxio flush semantics to HDFS sync semantics.

### Important APIs, Types, And Functions
It extends `OutputStream` and implements `ContentHashable`. `write` methods delegate to `FSDataOutputStream`. `flush()` calls `hsync()`. `getContentHash()` fetches file status and returns an approximate hash from length and modification time.

### Control Flow
Writes are synchronous delegation to the Hadoop stream. Close closes the underlying stream. Hash lookup happens after writing by querying the file system path.

### State, Persistence, And Dependencies
State includes the HDFS `FileSystem`, target path, and output stream. Persistent data is the HDFS file. Dependencies include Hadoop FS classes and `UnderFileSystemUtils.approximateContentHash`.

### Integration Points
`HdfsUnderFileSystem.createDirect` constructs this stream after `FileSystem.create`. Higher layers can call `supportsFlush()` and rely on flush-to-HDFS behavior.

### Risks
Calling `hsync()` on every flush can be expensive. The content hash is approximate and may not identify same-size same-mtime changes. Hash lookup after close can fail if the file was moved or not yet visible.

### Test Signals
No direct test in this subset covers output stream sync or hash behavior. Useful tests would mock `FSDataOutputStream.hsync`, close propagation, and content hash generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileSystem.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileSystem.java

### Purpose
`HdfsUnderFileSystem` is Alluxio's HDFS-backed `ConsistentUnderFileSystem`. It implements file creation, deletion, status, listing, space reporting, locations, reads, writes, renames, permissions, Kerberos login, ACL delegation, and ActiveSync delegation.

### Important APIs, Types, And Functions
`createInstance` builds Hadoop configuration. The constructor initializes Hadoop UGI/classloader state, optional EC support, a cached `FileSystem`, reflected `HdfsAclProvider`, and reflected `HdfsActiveSyncProvider`. Key overrides include `createDirect`, `deleteDirectory`, `exists`, `getAclPair`, `getBlockSizeByte`, `getDirectoryStatus`, `getFileLocations`, `getFileStatus`, `getSpace`, `getStatus`, `listStatus`, `mkdirs`, `open`, `renameFile`, `renameDirectory`, `setOwner`, `setMode`, and active-sync methods.

### Control Flow
Configuration loads `UNDERFS_HDFS_CONFIGURATION`, `UNDERFS_HDFS_IMPL`, mount-specific options, and disables HDFS client caching by default. Create/delete/mkdir/open/rename operations retry up to `MAX_TRY`. Atomic creates return `AtomicFileOutputStream`; direct creates call Hadoop `FileSystem.create` and optionally set ACLs. Reads choose positioned pread streams for remote/short/nonlocal reads and normal seekable streams otherwise. Open can try lease recovery on specific block-length errors. Recursive directory creation builds missing parents explicitly to set permissions and owner.

### State, Persistence, And Dependencies
State includes UFS configuration, a Guava `LoadingCache` of `FileSystem` by user key, ACL provider, active-sync provider, and Hadoop configuration captured by the loader. Persistent state is in HDFS. Dependencies are Hadoop FS/security/HDFS APIs, Alluxio UFS status/options, retry policies, networking utilities, and generated `UfsConstants`.

### Integration Points
`HdfsUnderFileSystemFactory` creates this class for configured HDFS prefixes. The HDFS stream wrappers provide read/write behavior. ACL and ActiveSync support are optional profile-dependent classes loaded by reflection, allowing older Hadoop deployments to run with no-op providers.

### Risks
The file-system cache currently uses a constant empty user key, so true per-user Hadoop clients are not implemented. Close intentionally does not close Hadoop `FileSystem` singletons. Version gating for EC uses string comparison. Many operations log and retry broad IOExceptions, which can duplicate non-idempotent attempts if Hadoop semantics change. Permission changes may be ignored when configured to allow owner failures.

### Test Signals
`HdfsUnderFileSystemTest` validates type, configuration preparation, and positioned-read heuristics. Factory and version tests cover discovery and version parsing, but many behaviors such as ACLs, ActiveSync, Kerberos login, lease recovery, and real HDFS space/location calls need integration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileSystemFactory.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileSystemFactory.java

### Purpose
`HdfsUnderFileSystemFactory` registers and creates HDFS UFS instances for configured HDFS-like path prefixes.

### Important APIs, Types, And Functions
It implements `UnderFileSystemFactory`. `create` returns `HdfsUnderFileSystem.createInstance`. `supportsPath(String)` checks global `UNDERFS_HDFS_PREFIXES`. `supportsPath(String, UnderFileSystemConfiguration)` also honors user-set `UNDERFS_VERSION` through `HdfsVersion.matches`. `getVersion` returns generated Hadoop UFS version.

### Control Flow
Path support scans configured prefixes and accepts the first prefix match. The configuration-aware overload additionally rejects mismatched user-requested Hadoop versions.

### State, Persistence, And Dependencies
The factory is stateless. It depends on global Alluxio configuration for prefixes, per-mount UFS configuration for version constraints, `HdfsVersion`, and generated `UfsConstants`.

### Integration Points
The UFS factory registry uses this factory to route `hdfs://` and other configured HDFS-compatible schemes to the HDFS module.

### Risks
The no-configuration overload uses global configuration only, and comments note programmatic prefix updates may not work as expected. Prefix matching is simple `startsWith`, so configuration quality matters. Version matching depends on `HdfsVersion` patterns.

### Test Signals
`HdfsUnderFileSystemFactoryTest` verifies `hdfs://` is accepted and S3/Alluxio paths are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsVersion.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsVersion.java

### Purpose
`HdfsVersion` enumerates supported Hadoop/HDFS major-minor versions and normalizes several version string formats to canonical values.

### Important APIs, Types, And Functions
Enum values cover Hadoop 1.0, 1.2, 2.2 through 2.10, and 3.0 through 3.3. `find(String)` returns the enum whose regex matches. `matches(String, String)` accepts exact equality or both strings resolving to the same enum. `getCanonicalVersion()` returns labels like `hadoop-3.3`.

### Control Flow
`find` iterates enum values in declaration order and uses precompiled regex patterns. `matches` first checks direct equality, then compares normalized enum values.

### State, Persistence, And Dependencies
State is immutable enum metadata and compiled regexes. It depends only on Java regex and nullable annotations.

### Integration Points
`HdfsUnderFileSystemFactory.supportsPath` uses it to compare user-requested UFS version with the module's compiled Hadoop version.

### Risks
Only declared versions are recognized; newer Hadoop versions require enum updates. Regexes are permissive for suffixes but only by major-minor family, not patch-level compatibility rules.

### Test Signals
`HdfsVersionTest` validates canonical names plus plain and `hadoop-`/`hadoop` labels with snapshot suffixes across all enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/NoopHdfsAclProvider.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/NoopHdfsAclProvider.java

### Purpose
`NoopHdfsAclProvider` is the fallback ACL provider when HDFS ACL support is unavailable or excluded from the build.

### Important APIs, Types, And Functions
`getAcl` returns a pair of null ACLs. `setAclEntries` accepts entries but performs no operation.

### Control Flow
All calls return immediately with unsupported/no-op behavior.

### State, Persistence, And Dependencies
There is no state and no HDFS mutation. It depends on the provider interface and Alluxio ACL types.

### Integration Points
`HdfsUnderFileSystem` uses this provider by default before trying to reflectively instantiate `SupportedHdfsAclProvider`.

### Risks
Silent no-op behavior can hide missing build profiles or disabled Hadoop ACL support unless logs from provider selection are monitored.

### Test Signals
No direct tests are present. Provider fallback is exercised when the supported ACL class is absent from the classpath.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/NoopHdfsAclProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/NoopHdfsActiveSyncProvider.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/NoopHdfsActiveSyncProvider.java

### Purpose
`NoopHdfsActiveSyncProvider` is the fallback ActiveSync provider when HDFS inotify support is unavailable or excluded.

### Important APIs, Types, And Functions
`getActivitySyncInfo` returns `SyncInfo.emptyInfo`. `startPolling` and `stopPolling` return false. `startSync` and `stopSync` are no-ops.

### Control Flow
Every method returns immediately without starting threads or tracking sync points.

### State, Persistence, And Dependencies
There is no mutable state. It depends on `SyncInfo` and `AlluxioURI`.

### Integration Points
`HdfsUnderFileSystem.supportsActiveSync` checks whether the active-sync provider is an instance of this class.

### Risks
Deployments expecting active sync can silently run without it if the supported provider is not in the extension jar or cannot initialize.

### Test Signals
No direct tests are present. ActiveSync integration tests should verify `supportsActiveSync` under the relevant build profiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/NoopHdfsActiveSyncProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/acl/SupportedHdfsAclProvider.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/acl/SupportedHdfsAclProvider.java

### Purpose
`SupportedHdfsAclProvider` implements real HDFS ACL read/write support for Hadoop versions with ACL APIs.

### Important APIs, Types, And Functions
`getAcl` calls `FileSystem.getAclStatus`, converts HDFS ACL entries into Alluxio `AccessControlList` and `DefaultAccessControlList`, and returns null default ACL for files. `setAclEntries` converts Alluxio ACL entries to Hadoop ACL entries and calls `FileSystem.setAcl`. Helper methods translate entry types and permissions.

### Control Flow
For reads, the provider checks whether the path is a directory, retrieves ACL status, sets owner/group, iterates entries, maps scopes to access/default ACL, and returns the pair. `AclException` from disabled NameNode ACLs returns nulls. For writes, every Alluxio entry is converted and passed as a full ACL spec.

### State, Persistence, And Dependencies
The class is stateless. Persistent effects are HDFS ACL mutations. It depends on Hadoop ACL APIs, Alluxio ACL models, and HDFS `AclException`.

### Integration Points
`HdfsUnderFileSystem` loads this class reflectively when present and delegates ACL methods to it.

### Risks
Permission conversion uses an `if/else if` chain on `FsAction.implies`, so combined permissions may only add the first matching action rather than all implied actions. UnsupportedOperationException on `setAcl` is swallowed, which can hide write failures on unsupported filesystems.

### Test Signals
No direct tests in this subset cover ACL translation. Tests should cover all FsAction combinations, named and unnamed entries, default ACLs on directories, files with null default ACL, disabled ACLs, and write conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/acl/SupportedHdfsAclProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/activesync/SupportedHdfsActiveSyncProvider.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/activesync/SupportedHdfsActiveSyncProvider.java

### Purpose
`SupportedHdfsActiveSyncProvider` implements HDFS ActiveSync using HDFS inotify events. It tracks configured sync points, batches events, records changed files, and returns `SyncInfo` when activity becomes quiet enough or old enough to sync.

### Important APIs, Types, And Functions
The constructor builds an `HdfsAdmin`, read/write locks, thread pool, sync-point list, change maps, transaction-id maps, and thresholds from configuration. Core methods are `startPolling`, `stopPolling`, `startSync`, `stopSync`, `pollEvent`, `processEvent`, `recordFileChanged`, `getActivitySyncInfo`, and `getCountSinceLastLog`.

### Control Flow
Polling opens an inotify event stream from a supplied txid or current stream, then submits a polling loop. The loop polls batches up to configured batch size, submits event-processing tasks, and periodically logs throughput. Events map CREATE/UNLINK/APPEND/RENAME/METADATA paths to sync points by prefix. `getActivitySyncInfo` ages activity windows, returns a full sync if events were missed, or returns changed-file sets when activity drops below the max threshold or exceeds max age.

### State, Persistence, And Dependencies
State is concurrent in-memory maps for changed files, activity, age, txids, current txid, missed-event flag, task queue, polling future, and sync-point list. Persistent filesystem data is not modified. Dependencies include Hadoop `HdfsAdmin`, `DFSInotifyEventInputStream`, inotify events, Alluxio `SyncInfo`, locks, executor services, and sampling logs.

### Integration Points
`HdfsUnderFileSystem` loads this class reflectively when compiled and delegates all active-sync methods. Alluxio master active-sync logic consumes the returned `SyncInfo`.

### Risks
Concurrency is subtle: event processing tasks and `getActivitySyncInfo` mutate the same maps, and `syncSyncPoint` removes map entries while tasks can still record changes. Missing events force full syncs. Path-prefix matching must handle renames into and out of sync points. Polling and processing share the same executor, which can affect latency under high event volume.

### Test Signals
No tests are included here. Valuable tests would simulate inotify batches, missing events, rename paths, concurrent sync-point removal, txid tracking, activity/age thresholds, and duplicate start/stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/activesync/SupportedHdfsActiveSyncProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/HdfsUnderFileSystemFactoryTest.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/HdfsUnderFileSystemFactoryTest.java

### Purpose
This JUnit test verifies HDFS factory discovery and rejection of non-HDFS schemes.

### Important APIs, Types, And Functions
`factory()` calls `UnderFileSystemFactoryRegistry.find` for `hdfs://`, `s3://`, `s3n://`, and `alluxio://` paths.

### Control Flow
The test asserts a factory is found for HDFS and not found for the other schemes under global configuration.

### State, Persistence, And Dependencies
No filesystem state is touched. It depends on the UFS registry and Alluxio global configuration.

### Integration Points
This protects service registration and `HdfsUnderFileSystemFactory.supportsPath` for default prefixes.

### Risks
It does not exercise mount-specific `UNDERFS_VERSION` matching or custom HDFS prefixes.

### Test Signals
Failure usually indicates broken service discovery, missing module metadata, or changed default HDFS prefix configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/HdfsUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/HdfsUnderFileSystemTest.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/HdfsUnderFileSystemTest.java

### Purpose
`HdfsUnderFileSystemTest` covers basic HDFS UFS identity/configuration behavior and the positioned-read heuristic.

### Important APIs, Types, And Functions
Setup creates a temporary local-root HDFS UFS using mount-specific Hadoop configuration. Tests cover `getUnderFSType`, `createConfiguration`, and `verifyPread`. The helper `checkDataValid` validates byte values despite signed conversion.

### Control Flow
`verifyPread` writes a local file, opens it with `OpenOptions.setPositionShort(true)`, replaces the wrapped stream with a spy `PreadSeekableStream`, performs reads/skips/seeks, and verifies counts for positioned and normal read methods.

### State, Persistence, And Dependencies
The test uses a JUnit `TemporaryFolder`. It depends on Mockito/PowerMock Whitebox, Hadoop `FSDataInputStream`, and Alluxio UFS options.

### Integration Points
It indirectly tests `HdfsUnderFileSystem.open` choosing `HdfsPositionedUnderFileInputStream` and the stream's switching behavior.

### Risks
The tests use a local filesystem path rather than a real HDFS cluster, so they do not cover block locations, Kerberos, lease recovery, space reporting, or distributed semantics.

### Test Signals
Passing tests confirm the configured implementation class is propagated, HDFS client cache disabling is set, and the pread heuristic transitions at the expected thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/HdfsUnderFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/HdfsVersionTest.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/HdfsVersionTest.java

### Purpose
`HdfsVersionTest` validates version-string normalization for all supported Hadoop version families.

### Important APIs, Types, And Functions
`find()` checks invalid input and canonical version strings. `findByHadoopLabel()` checks plain numeric, snapshot, `hadoop-`, `hadoop-<patch>`, and `hadoop<major.minor>` labels for every enum value.

### Control Flow
Assertions directly call `HdfsVersion.find` and compare returned enum values.

### State, Persistence, And Dependencies
No state is mutated. It depends only on JUnit and `HdfsVersion`.

### Integration Points
The test protects factory version compatibility checks that use `HdfsVersion.matches`.

### Risks
It does not test `matches` directly or newer versions beyond the enum list.

### Test Signals
Failures indicate a regex or canonical label drift that can prevent correctly versioned HDFS UFS modules from matching mount configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/HdfsVersionTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/PreadSeekableStream.java -->
## sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/PreadSeekableStream.java

### Purpose
`PreadSeekableStream` is a test helper that exposes both `Seekable` and `PositionedReadable` over a wrapped `FSDataInputStream` so tests can spy on normal versus positioned reads.

### Important APIs, Types, And Functions
It extends `FilterInputStream` and implements `read(long, byte[], int, int)`, both `readFully` overloads, `seek`, `getPos`, and `seekToNewSource` by delegating to the wrapped `FSDataInputStream`.

### Control Flow
Every method casts `in` to `FSDataInputStream` and delegates immediately.

### State, Persistence, And Dependencies
State is the wrapped stream. It depends on Hadoop seekable/positioned interfaces and is only used in tests.

### Integration Points
`HdfsUnderFileSystemTest.verifyPread` wraps the real stream with this helper and then a Mockito spy to count call types.

### Risks
The helper assumes the wrapped stream is always an `FSDataInputStream`; misuse with a different stream would fail by `ClassCastException`.

### Test Signals
Its value is in enabling verification that `HdfsPositionedUnderFileInputStream` chooses the intended read API after skip/seek patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/PreadSeekableStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/pom.xml -->
## sources/distributed-fs/alluxio/underfs/kodo/pom.xml

### Purpose
This Maven module builds the Qiniu Kodo UFS extension.

### Important APIs, Types, And Functions
The artifact is `alluxio-underfs-kodo`. Dependencies include Qiniu Java SDK `7.2.17`, OkHttp `3.10.0`, and Alluxio core common as provided plus test jar. Build plugins shade and copy/rename the extension artifact.

### Control Flow
The module inherits from `alluxio-underfs` and has no feature profiles. It packages external object-store dependencies into the extension as configured by parent/plugin behavior.

### State, Persistence, And Dependencies
Build output is the Kodo extension jar. Runtime dependencies are Qiniu SDK, OkHttp, and Alluxio common UFS abstractions.

### Integration Points
The module supplies `KodoUnderFileSystemFactory`, client wrappers, streams, and tests for the Kodo scheme.

### Risks
The external SDK versions are fixed and relatively old; compatibility with current Kodo endpoints and OkHttp TLS defaults should be validated separately.

### Test Signals
The module includes unit tests for factory registration, output stream local buffering, and failure handling on listing-backed operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoClient.java -->
## sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoClient.java

### Purpose
`KodoClient` centralizes Qiniu SDK and OkHttp operations used by the Kodo UFS.

### Important APIs, Types, And Functions
The constructor wires `Auth`, bucket/download host/endpoint, Qiniu `BucketManager`, `UploadManager`, and `OkHttpClient`. Methods include `getBucketName`, `getFileInfo`, `getObject`, `uploadFile`, `copyObject`, `createEmptyObject`, `deleteObject`, and `listFiles`.

### Control Flow
Metadata, copy, delete, and list delegate to Qiniu SDK managers. `getObject` signs a private download URL, rewrites it through the configured endpoint, adds a byte `Range` header and `Host`, executes OkHttp, maps 404 to Alluxio `NotFoundException`, and returns the response body stream for 200/206 responses. Uploads and empty-object creation close Qiniu responses after put/delete operations.

### State, Persistence, And Dependencies
State is client configuration and SDK client instances. Persistent state is the Kodo bucket. Dependencies include Qiniu SDK, OkHttp, HTTP status codes, and Alluxio `NotFoundException`.

### Integration Points
`KodoUnderFileSystem`, `KodoInputStream`, and `KodoOutputStream` call this client for all object-store operations.

### Risks
`getObject` returns a body stream without separately managing the OkHttp `Response`, so lifecycle depends on stream close behavior. The signed URL is rewritten to `http://` endpoint, which may be inappropriate for HTTPS-only deployments. Parameter names use uppercase in upload methods but are behaviorally normal.

### Test Signals
No direct tests mock `KodoClient` internals in this subset. UFS tests mock it at the method level, and output stream tests verify upload invocation paths indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoInputStream.java -->
## sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoInputStream.java

### Purpose
`KodoInputStream` implements ranged object reads for Kodo through `MultiRangeObjectInputStream`.

### Important APIs, Types, And Functions
The constructor records key/client/position/retry policy, initializes multi-range chunk size, and fetches object size through `KodoClient.getFileInfo`. `createStream(long, long)` opens the requested byte range.

### Control Flow
For each range, the stream copies the retry policy and repeatedly calls `KodoClient.getObject`. `NotFoundException` is retried to handle eventual consistency. After retry exhaustion, it throws an `IOException` with the last not-found error.

### State, Persistence, And Dependencies
State includes key, Kodo client, current position inherited from the superclass, object length, and retry policy. It depends on Qiniu metadata exceptions and Alluxio multi-range stream support.

### Integration Points
`KodoUnderFileSystem.openObject` creates this stream with the configured object-store multi-range chunk size.

### Risks
Only not-found errors are retried by this class; other IO failures from `getObject` propagate. Constructor metadata lookup can fail before stream creation. The member name `mKodoclent` is misspelled but local.

### Test Signals
No direct tests are present. Useful tests would cover range boundaries, not-found retry, metadata failure, empty-object reads, and multi-range chunk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoOutputStream.java -->
## sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoOutputStream.java

### Purpose
`KodoOutputStream` buffers Kodo writes to a local temporary file, then uploads the completed file to Kodo on close.

### Important APIs, Types, And Functions
The constructor chooses a temporary directory, creates a UUID file, and wraps a file output stream in a buffered digest stream when MD5 is available. `write` and `flush` delegate to the local stream. `close` is guarded by `AtomicBoolean`, closes the local stream, uploads through `KodoClient.uploadFile`, and deletes the temporary file.

### Control Flow
All bytes are written locally first. Closing performs the only remote persistence step. Upload exceptions are logged but not rethrown because `close` does not declare `IOException`.

### State, Persistence, And Dependencies
State includes key, temp file, Kodo client, local output stream, optional MD5 digest, and closed flag. Temporary local state is deleted on close; durable state is the uploaded Kodo object.

### Integration Points
`KodoUnderFileSystem.createObject` returns this stream for object writes.

### Risks
Upload failures are swallowed after logging, so callers may believe close succeeded. MD5 is computed but not used for upload metadata or exposed through `ContentHashable`. Large writes require local disk capacity equal to the object size.

### Test Signals
`KodoOutputStreamTest` covers constructor IO failure, write delegation, flush delegation, and temp-file deletion on close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoUnderFileSystem.java -->
## sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoUnderFileSystem.java

### Purpose
`KodoUnderFileSystem` adapts Qiniu Kodo to Alluxio's `ObjectUnderFileSystem` abstraction.

### Important APIs, Types, And Functions
`creatInstance` validates Kodo access key, secret key, download host, and endpoint; creates Qiniu auth/configuration and OkHttp client; and returns the UFS. Core overrides include `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `getObjectListingChunk`, `getObjectStatus`, `getPermissions`, `openObject`, and `getRootKey`. The nested `KodoObjectListingChunk` wraps `FileListing`.

### Control Flow
Object primitives call `KodoClient` and map `QiniuException` to false/null/logging. Listings normalize prefixes, choose delimiter based on recursive mode, request chunks, return object statuses and common prefixes, and page using the returned marker until EOF. Reads and writes use Kodo stream wrappers.

### State, Persistence, And Dependencies
State is the Kodo client and inherited configuration. Persistent data lives in the Kodo bucket. Dependencies include Qiniu SDK models, OkHttp configuration, Alluxio object UFS support, and configured tmp dirs/chunk sizes.

### Integration Points
`KodoUnderFileSystemFactory` creates this UFS for `kodo://` paths. Higher-level object-store rename/delete behavior is inherited from `ObjectUnderFileSystem`.

### Risks
The static factory name is misspelled `creatInstance`, but callers use it consistently. `initializeKodoClientConfig` creates a dispatcher and sets max requests but does not attach it to the OkHttp builder, so that setting appears ineffective. Listing errors return null, causing high-level operations to fail as not found.

### Test Signals
`KodoUnderFileSystemTest` mocks listing failures and verifies recursive/nonrecursive directory delete and rename return false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoUnderFileSystemFactory.java -->
## sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoUnderFileSystemFactory.java

### Purpose
`KodoUnderFileSystemFactory` registers and creates the Kodo UFS for `kodo://` paths.

### Important APIs, Types, And Functions
It implements `UnderFileSystemFactory`. `create` validates non-null path and delegates to `KodoUnderFileSystem.creatInstance`. `supportsPath` checks `Constants.HEADER_KODO`.

### Control Flow
There is no caching or version selection. Path support is a simple scheme-prefix check.

### State, Persistence, And Dependencies
The factory is stateless. It depends on Alluxio URI/configuration types and the Kodo UFS implementation.

### Integration Points
The UFS registry uses this factory to route Kodo mounts.

### Risks
The factory does not validate credentials itself; failures occur during UFS creation. Documentation comments are sparse and return descriptions are empty.

### Test Signals
`KodoUnderFileSystemFactoryTest` verifies registry discovery for a `kodo://` path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/test/java/alluxio/underfs/kodo/KodoOutputStreamTest.java -->
## sources/distributed-fs/alluxio/underfs/kodo/src/test/java/alluxio/underfs/kodo/KodoOutputStreamTest.java

### Purpose
`KodoOutputStreamTest` validates local buffering behavior and close-time cleanup for Kodo writes.

### Important APIs, Types, And Functions
Tests use PowerMock to intercept constructors for `File`, `FileOutputStream`, and `BufferedOutputStream`, plus Mockito mocks for `KodoClient` and streams.

### Control Flow
`testConstructor` forces `FileOutputStream` to throw and expects an `IOException`. Write tests construct a stream, write using each overload, close it, and verify local write calls. `testClose` verifies temp-file deletion. `testFlush` verifies flush delegation.

### State, Persistence, And Dependencies
No real Kodo state is used. Some tests use mocked temp files; others use configured tmp dirs. Dependencies include PowerMockRunner, Mockito, and JUnit rules.

### Integration Points
The tests protect `KodoOutputStream`, which is returned by `KodoUnderFileSystem.createObject`.

### Risks
They do not assert upload invocation, upload failure swallowing, duplicate close behavior, or MD5 behavior.

### Test Signals
Passing tests show that writes are buffered locally, flush reaches the local stream, constructor IO errors propagate, and close attempts cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/test/java/alluxio/underfs/kodo/KodoOutputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/test/java/alluxio/underfs/kodo/KodoUnderFileSystemFactoryTest.java -->
## sources/distributed-fs/alluxio/underfs/kodo/src/test/java/alluxio/underfs/kodo/KodoUnderFileSystemFactoryTest.java

### Purpose
This test verifies Kodo factory registration for `kodo://` paths.

### Important APIs, Types, And Functions
`factory()` calls `UnderFileSystemFactoryRegistry.find("kodo://test-bucket/path", Configuration.global())` and asserts non-null.

### Control Flow
The test performs registry lookup only; it does not create the UFS or validate credentials.

### State, Persistence, And Dependencies
No persistent state is modified. It depends on Alluxio configuration and factory registry.

### Integration Points
The test protects service discovery and `KodoUnderFileSystemFactory.supportsPath`.

### Risks
It does not reject non-Kodo schemes or test create-time configuration requirements.

### Test Signals
Failure suggests missing module service metadata or broken scheme-prefix support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/test/java/alluxio/underfs/kodo/KodoUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/test/java/alluxio/underfs/kodo/KodoUnderFileSystemTest.java -->
## sources/distributed-fs/alluxio/underfs/kodo/src/test/java/alluxio/underfs/kodo/KodoUnderFileSystemTest.java

### Purpose
`KodoUnderFileSystemTest` validates failure behavior for Kodo operations that depend on object listings.

### Important APIs, Types, And Functions
Setup injects a mocked `KodoClient` into `KodoUnderFileSystem`. Tests cover nonrecursive directory delete, recursive directory delete, and file rename.

### Control Flow
Each test configures `KodoClient.listFiles` to throw `QiniuException`, invokes the high-level operation, and asserts false.

### State, Persistence, And Dependencies
No external object-store state is used. Dependencies include Mockito, JUnit, and Alluxio UFS options.

### Integration Points
The tests exercise `KodoUnderFileSystem.getObjectListingChunk` through inherited `ObjectUnderFileSystem` logic.

### Risks
They do not cover successful listings, pagination markers, object status, stream behavior, or credential validation.

### Test Signals
Passing tests indicate listing failures are contained and surfaced as failed high-level operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/kodo/src/test/java/alluxio/underfs/kodo/KodoUnderFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/local/pom.xml -->
## sources/distributed-fs/alluxio/underfs/local/pom.xml

### Purpose
This Maven module builds the local filesystem UFS extension.

### Important APIs, Types, And Functions
The artifact is `alluxio-underfs-local`. It depends on `alluxio-core-common` as provided and its test jar for tests. Build plugins include Maven shade and copy/rename.

### Control Flow
There are no feature profiles. The module inherits versioning and plugin configuration from `alluxio-underfs`.

### State, Persistence, And Dependencies
The build emits the local UFS extension artifact. Runtime dependencies are limited to Alluxio common and Java filesystem APIs.

### Integration Points
The module contributes `LocalUnderFileSystemFactory`, `LocalUnderFileSystem`, and local UFS tests.

### Risks
Because this module is often used for tests and single-node deployments, packaging changes can break many contract tests. It depends on parent plugin behavior for extension layout.

### Test Signals
Tests cover factory recognition, local file operations, symlink handling, status, locations, and async listing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/local/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/local/src/main/java/alluxio/underfs/local/LocalUnderFileSystem.java -->
## sources/distributed-fs/alluxio/underfs/local/src/main/java/alluxio/underfs/local/LocalUnderFileSystem.java

### Purpose
`LocalUnderFileSystem` adapts the local POSIX filesystem to Alluxio's `ConsistentUnderFileSystem` interface for tests, single-node mode, or shared mounted filesystems.

### Important APIs, Types, And Functions
Core overrides include `create`, `createDirect`, `deleteDirectory`, `deleteFile`, `exists`, `getBlockSizeByte`, `getDirectoryStatus`, `getFileLocations`, `getFileStatus`, `getSpace`, `getStatus`, `isDirectory`, `isFile`, `listStatus`, `mkdirs`, `open`, `renameFile`, `renameDirectory`, `setOwner`, `setMode`, `connectFromMaster`, `connectFromWorker`, and `supportsFlush`. Nested `LocalOutputStream` exposes approximate content hashes.

### Control Flow
Paths are normalized by stripping any URI scheme. Creates optionally create parents, open buffered local output streams, and set permissions. Recursive deletes walk children before deleting the directory. Status calls read POSIX attributes and translate permissions. `mkdirs` builds missing parent stack to apply mode and ownership. `open` uses `ByteStreams.skipFully` for offsets. Listing optionally filters broken symlinks before reading attributes.

### State, Persistence, And Dependencies
State is just the inherited configuration and `mSkipBrokenSymlinks`. Persistent state is the local filesystem. Dependencies include Java `File`, NIO POSIX attributes, Alluxio path/status/options utilities, permission utilities, and network utilities for local file location.

### Integration Points
`LocalUnderFileSystemFactory` selects this class for local paths. It implements `AtomicFileOutputStreamCallback`, so atomic writes use Alluxio's atomic output wrapper.

### Risks
POSIX attribute reads can fail on non-POSIX filesystems. `File.renameTo` has platform-specific semantics and weak error reporting. Recursive delete uses `File.list`, which may return null on IO errors and then proceeds to delete the parent. Owner changes can be ignored depending on configuration, potentially diverging Alluxio metadata from local permissions.

### Test Signals
`LocalUnderFileSystemTest` covers create/delete/mkdir/open/rename/status/location/mode behavior, symlink skip configuration, operation mode, and async listing counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/local/src/main/java/alluxio/underfs/local/LocalUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/local/src/main/java/alluxio/underfs/local/LocalUnderFileSystemFactory.java -->
## sources/distributed-fs/alluxio/underfs/local/src/main/java/alluxio/underfs/local/LocalUnderFileSystemFactory.java

### Purpose
`LocalUnderFileSystemFactory` registers and creates local filesystem UFS instances.

### Important APIs, Types, And Functions
It implements `UnderFileSystemFactory`. `create` validates the path and constructs `LocalUnderFileSystem`. `supportsPath` calls `URIUtils.isLocalFilesystem`.

### Control Flow
Path support rejects null and delegates all local-path interpretation to `URIUtils`, covering Unix paths, `file://` paths, and Windows drive forms.

### State, Persistence, And Dependencies
The factory is stateless and thread-safe. It depends on Alluxio URI/configuration types and URI utilities.

### Integration Points
The UFS registry uses it for local and file-scheme paths.

### Risks
Correctness is coupled to `URIUtils.isLocalFilesystem`, especially for platform-specific Windows path variants.

### Test Signals
`LocalUnderFileSystemFactoryTest` covers Unix, file-scheme, Windows drive, and non-local HDFS cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/local/src/main/java/alluxio/underfs/local/LocalUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/local/src/test/java/alluxio/underfs/local/LocalUnderFileSystemFactoryTest.java -->
## sources/distributed-fs/alluxio/underfs/local/src/test/java/alluxio/underfs/local/LocalUnderFileSystemFactoryTest.java

### Purpose
This test verifies local UFS factory registration and path recognition across Unix, file URI, and Windows-style paths.

### Important APIs, Types, And Functions
`factory()` calls `UnderFileSystemFactoryRegistry.find` with `/local/test/path`, `file://local/test/path`, `hdfs://...`, `R:\\ramfs\\`, `file://R:/famfs`, and `R:/ramfs/`.

### Control Flow
It asserts local/file/Windows forms return a factory and the HDFS path does not.

### State, Persistence, And Dependencies
No filesystem state is used. It depends on the registry and global configuration.

### Integration Points
The test protects `LocalUnderFileSystemFactory.supportsPath` behavior through registry discovery.

### Risks
The Windows-like paths are tested as strings even on non-Windows platforms, so behavior depends on URI utility implementation rather than actual filesystem access.

### Test Signals
Failure indicates local path detection or factory service registration changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/local/src/test/java/alluxio/underfs/local/LocalUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/local/src/test/java/alluxio/underfs/local/LocalUnderFileSystemTest.java -->
## sources/distributed-fs/alluxio/underfs/local/src/test/java/alluxio/underfs/local/LocalUnderFileSystemTest.java

### Purpose
`LocalUnderFileSystemTest` validates local UFS behavior over a temporary directory.

### Important APIs, Types, And Functions
Tests cover existence, create, delete file, recursive and nonrecursive directory delete, mkdirs, create-parent false, open/read, file locations, operation mode, `isFile`, rename, directory/file status failure and success, broken symlink handling, and async listing.

### Control Flow
Setup creates a fresh temporary root and UFS. Tests create files/directories through UFS APIs, inspect local Java `File`/NIO state, and assert expected UFS statuses. Symlink tests toggle `UNDERFS_LOCAL_SKIP_BROKEN_SYMLINKS`; async listing uses `UnderFileSystemTestUtil.performListingAsyncAndGetResult`.

### State, Persistence, And Dependencies
State is confined to JUnit `TemporaryFolder`. Dependencies include Alluxio UFS APIs, configuration, NIO symlink APIs, and network hostname utilities.

### Integration Points
This is the main behavioral test suite for `LocalUnderFileSystem` and indirectly covers inherited listing async behavior.

### Risks
Tests assume POSIX-like symlink support and local permission behavior; some environments can behave differently. They do not deeply test setOwner/setMode failure modes or atomic create behavior.

### Test Signals
Passing tests provide broad confidence in local create/delete/list/status/open semantics and the broken symlink configuration toggle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/local/src/test/java/alluxio/underfs/local/LocalUnderFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/pom.xml -->
## sources/distributed-fs/alluxio/underfs/obs/pom.xml

### Purpose
This Maven module builds the Huawei OBS UFS extension.

### Important APIs, Types, And Functions
The artifact is `alluxio-underfs-obs`. Properties define `obs.version` and `hamcrest.version`. Dependencies include Huawei `esdk-obs-java`, Alluxio core common, Hamcrest for tests, and Alluxio test jar. Build plugins shade and copy/rename the extension artifact.

### Control Flow
There are no feature profiles. The module inherits common UFS build behavior from the parent.

### State, Persistence, And Dependencies
Build output is the OBS extension jar. Runtime state is provided by the OBS SDK and Alluxio common abstractions.

### Integration Points
The module provides OBS object-store implementation classes, including normal and streaming output streams.

### Risks
SDK version pinning can affect compatibility with OBS bucket types and PFS-specific APIs. The POM includes test dependencies but this subset does not include OBS tests.

### Test Signals
No OBS-specific tests are listed in this work item, so coverage should be added for stream and PFS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSInputStream.java -->
## sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSInputStream.java

### Purpose
`OBSInputStream` implements ranged reads from Huawei OBS using Alluxio's `MultiRangeObjectInputStream`.

### Important APIs, Types, And Functions
Constructors record bucket/key/client/retry policy/chunk size and fetch object content length from OBS metadata. `createStream(long, long)` builds a `GetObjectRequest` with range start/end and returns a buffered object-content stream.

### Control Flow
Each range request copies the retry policy, attempts `mObsClient.getObject`, retries only 404 not-found responses, and converts non-404 `ObsException` to `IOException`. Range end is clamped to content length minus one.

### State, Persistence, And Dependencies
State includes bucket, key, OBS client, content length, retry policy, and inherited position. It depends on Huawei OBS SDK, HTTP status codes, and Alluxio multi-range stream logic.

### Integration Points
`OBSUnderFileSystem.openObject` creates this stream with the configured multi-range chunk size.

### Risks
The constructor metadata call can fail before read retries begin. A `System.out.println` of response code leaks logging to stdout. If content length is zero, computed range end can become `-1`, relying on caller behavior for empty objects.

### Test Signals
No direct tests are present. Useful tests would cover metadata failures, range clamping, 404 retry, non-404 propagation, empty objects, and stream close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSLowLevelOutputStream.java -->
## sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSLowLevelOutputStream.java

### Purpose
`OBSLowLevelOutputStream` implements streaming/multipart OBS uploads by specializing Alluxio's `ObjectLowLevelOutputStream`.

### Important APIs, Types, And Functions
It holds an `IObsClient`, synchronized part ETags, upload id, and optional content hash. It implements multipart hooks: `initMultiPartUploadInternal`, `uploadPartInternal`, `completeMultiPartUploadInternal`, `abortMultiPartUploadInternal`, plus single-object hooks `createEmptyObject` and `putObject`. `getContentHash` returns the OBS ETag.

### Control Flow
Initialization starts a multipart upload and stores the upload id. Each part upload builds an `UploadPartRequest`, optionally sets MD5, uploads the file part, and records the returned ETag/part number. Completion submits all tags and stores the final ETag. Abort cancels by upload id. Small or empty object paths call put-object APIs directly.

### State, Persistence, And Dependencies
State includes multipart upload id, synchronized tag list, content hash, bucket/key inherited from the base class, and executor inherited from `ObjectLowLevelOutputStream`. Persistent effects are OBS objects and intermediate multipart upload state.

### Integration Points
`OBSUnderFileSystem.createObject` returns this stream when `UNDERFS_OBS_STREAMING_UPLOAD_ENABLED` is true.

### Risks
Part tag ordering relies on the OBS SDK accepting the synchronized list order as tasks complete; if completion requires sorted part numbers, parallel uploads may need explicit sorting. Abort error messages say "complete" in one path. Correct cleanup depends on base-class error handling invoking abort.

### Test Signals
No direct tests are present. Tests should cover multipart success, parallel part ordering, abort on failure, empty object creation, MD5 propagation, and content hash exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSLowLevelOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSOutputStream.java -->
## sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSOutputStream.java

### Purpose
`OBSOutputStream` buffers OBS writes to a local temporary file and uploads the whole file on close.

### Important APIs, Types, And Functions
The constructor validates bucket/key/client, creates a temp file, and wraps a local output stream in a digest stream when MD5 is available. `write` and `flush` delegate locally. `close` uploads the file with content length and optional content MD5, records the ETag as content hash, and deletes the temp file. `getContentHash` returns the ETag when available.

### Control Flow
All write calls persist locally. `close` is one-shot via `AtomicBoolean`, closes the local stream, opens a `FileInputStream`, builds `ObjectMetadata`, uploads via `ObsClient.putObject`, and cleans up in a `finally` block.

### State, Persistence, And Dependencies
State includes bucket/key, temp file, OBS client, local stream, optional MD5 digest, closed flag, and content hash. Persistent data is the OBS object; temporary local data should be deleted on close.

### Integration Points
`OBSUnderFileSystem.createObject` uses this class when streaming upload is disabled.

### Risks
Large objects require local disk space. The upload input stream is not explicitly closed, relying on upload behavior or GC. Duplicate close only logs a warning and returns. MD5 is Base64-encoded into object metadata.

### Test Signals
No direct OBS output tests are present. Useful tests would mirror Kodo/GCS output stream tests: write delegation, upload metadata, temp cleanup, duplicate close, upload failure propagation, and content hash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSUnderFileSystem.java -->
## sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSUnderFileSystem.java

### Purpose
`OBSUnderFileSystem` adapts Huawei OBS buckets to Alluxio's `ObjectUnderFileSystem`, including special handling for OBS PFS buckets and optional streaming multipart uploads.

### Important APIs, Types, And Functions
`createInstance` validates OBS access key, secret key, endpoint, and bucket type, constructs `ObsClientExt`, and extracts the bucket name. Core overrides include `cleanup`, `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `deleteObjects`, `getObjectListingChunk`, `getObjectStatus`, `isDirectory`, `getPermissions`, `getRootKey`, `openObject`, and `renameDirectory`. The nested `OBSObjectListingChunk` wraps OBS object listings.

### Control Flow
Cleanup lists multipart uploads and aborts those older than configured age. Creates choose streaming `OBSLowLevelOutputStream` or local-temp `OBSOutputStream`. Listings normalize prefixes, set delimiter and max keys, then page by marker. In PFS mode, listings and object status distinguish explicit directories via metadata mode bits. Bulk delete converts keys to `KeyAndVersion` and returns deleted keys. PFS directory rename uses OBS `renameFolder`; non-PFS delegates to inherited object-store rename.

### State, Persistence, And Dependencies
State includes `ObsClient`, bucket name, bucket type, and memoized streaming-upload executor. Persistent state is OBS objects and multipart uploads. Dependencies include Huawei OBS SDK models, Alluxio object UFS base classes, executor factories, and configuration keys for streaming upload and cleanup.

### Integration Points
The OBS factory outside this file creates this class for OBS schemes. Input/output stream classes implement read and write behavior. `ObjectUnderFileSystem` supplies higher-level directory/file semantics over the primitive object calls.

### Risks
PFS directory detection parses metadata `mode` without guarding missing/non-numeric values. Listing errors return null and can be interpreted as not found. `copyObject` writes to stdout on failure. Streaming upload executor is memoized but no explicit shutdown appears in `cleanup`. PFS and object-bucket behavior diverge in status and rename paths, requiring separate tests.

### Test Signals
No OBS tests are included in this subset. Coverage should include credential validation, PFS directory metadata, listing pagination, multipart cleanup, streaming/local output selection, bulk delete, and PFS rename status handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSUnderFileSystem.java -->
