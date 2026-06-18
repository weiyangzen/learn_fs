# Research Group: subset-b-000495

This grouped report covers the requested Alluxio FUSE and underfs files. Each source file has its own marker-delimited section for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/LaunchUserGroupAuthPolicyTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/LaunchUserGroupAuthPolicyTest.java

Purpose: unit coverage for `LaunchUserGroupAuthPolicy`, the FUSE auth policy that uses the process launch user and group rather than per-request FUSE context credentials. The test extends `AbstractAuthPolicyTest`, creates the policy with `LaunchUserGroupAuthPolicy.create(mFileSystem, Configuration.global(), Optional.empty())`, and calls `init()`.

Important APIs and control flow: `setUserGroupIfNeeded` is invoked on a non-existent `AlluxioURI` and must not create or mutate the file; `mFileSystem.getStatus` still throws `FileDoesNotExistException`. `getUid` and `getGid` accept arbitrary names but return `AlluxioFuseUtils.getSystemUid()` and `getSystemGid()`.

State, dependencies, integration, risks, tests: the file depends on PowerMock preparation for `AlluxioFuseUtils`, JUnit assertions, the inherited in-memory filesystem, and global Alluxio configuration. It checks that launch-user auth is stable and non-invasive. Risk is limited coverage: it does not test existing-file ownership mutation because the policy intentionally needs no owner/group update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/LaunchUserGroupAuthPolicyTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/SystemUserGroupAuthPolicyTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/SystemUserGroupAuthPolicyTest.java

Purpose: unit coverage for `SystemUserGroupAuthPolicy`, which maps FUSE request uid/gid values to system user/group names and writes those into Alluxio metadata. The setup creates the policy with the optional FUSE filesystem, initializes it, and PowerMocks `AlluxioFuseUtils` static user/group lookup methods.

Important APIs and control flow: `setUserGroupIfNeed` builds a `FuseContext` backed by a 32-byte `ByteBuffer`, sets uid/gid, injects it through `mFuseFileSystem.setContext`, and verifies `URIStatus` owner/group become `systemUser` and `systemGroup`. `getUidGid` confirms reverse lookup via `getUid(USER)` and `getGid(GROUP)`.

State, dependencies, integration, risks, tests: state flows through the FUSE context and Alluxio file status metadata. Dependencies include PowerMock, Mockito matchers, `FuseContext`, and the inherited test filesystem. The test signal is strong for successful mapping but does not cover unknown uid/gid, missing optional FUSE filesystem, or failed static lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/SystemUserGroupAuthPolicyTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/cli/FuseShellTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/cli/FuseShellTest.java

Purpose: isolation tests for the FUSE special command shell, particularly metadata-cache commands addressed through `.alluxiocli` paths. The fixture builds a `MetadataCachingFileSystem` around a mocked `FileSystemContext` and a custom `GetStatusFileSystemMasterClient`, primes two cached statuses, then removes backing map entries so later hits prove cache behavior.

Important APIs and control flow: `isSpecialCommand` distinguishes reserved `.alluxiocli.metadatacache.*` paths from normal user paths. `runCommand` rejects disabled metadata cache, unknown command groups, and unknown subcommands with `InvalidArgumentRuntimeException`. Valid commands return cache size, drop one path cache entry, or drop all entries.

State, dependencies, integration, risks, tests: the main state is the metadata cache inside `MetadataCachingFileSystem`, with `mFileStatusMap` acting as the master source. Dependencies include PowerMock, Mockito, `BaseFileSystem`, `CloseableResource`, and `GetStatusPOptions`. Risks include reliance on cache internals and equality of `URIStatus`; tests do not exercise concurrent cache mutation or command paths outside metadata cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/cli/FuseShellTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/cli/MockFuseFileSystemMasterClient.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/cli/MockFuseFileSystemMasterClient.java

Purpose: package-private test double for `FileSystemMasterClient`, used by FUSE shell tests to avoid a real master. It implements the broad master-client interface with inert behavior so individual tests can subclass and override only the method under examination.

Important APIs and control flow: most mutating operations such as `createDirectory`, `completeFile`, `delete`, `rename`, `setAcl`, `setAttribute`, sync, mount, and job APIs are no-ops. Query methods return neutral defaults: `null`, `false`, `0`, `Optional.empty()`, or `Collections.EMPTY_LIST`. Connection lifecycle methods are also no-ops.

State, dependencies, integration, risks, tests: it has no fields and no persistence; all state must live in subclasses, such as `FuseShellTest.GetStatusFileSystemMasterClient`. Dependencies include many Alluxio gRPC option/result types and wire types. Main risk is interface drift: adding methods to `FileSystemMasterClient` requires updates here. It is intentionally unsuitable for tests expecting realistic master side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/cli/MockFuseFileSystemMasterClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/meta/UpdateCheckerTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/meta/UpdateCheckerTest.java

Purpose: tests `UpdateChecker` reporting for FUSE environment metadata and recent FUSE operation metrics. It verifies unchangeable info for Alluxio-backed FUSE, UFS-backed FUSE with local/S3/S3A/HDFS addresses, local kernel cache mount options, and dynamic operation counters.

Important APIs and control flow: helpers create `FuseOptions` from global configuration, UFS options, or modified `FUSE_MOUNT_OPTIONS`. `getUnchangeableFuseInfo()` is scanned for target strings such as `ALLUXIO_FS`, `LOCAL_FS`, `s3`, `s3a`, `hdfs`, and `LOCAL_KERNEL_DATA_CACHE`. `getFuseCheckInfo()` is checked after updating `MetricsSystem.timer` for read and write metrics.

State, dependencies, integration, risks, tests: state lives in global metrics timers and temporary `InstancedConfiguration` instances; each checker is closed via try-with-resources. Dependencies include `FuseConstants`, `MetricsSystem`, and FUSE option creation. Risks include global metrics contamination between tests and string-match assertions that can pass if unrelated info contains the token.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/meta/UpdateCheckerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/AbstractFuseFileSystemTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/AbstractFuseFileSystemTest.java

Purpose: shared FUSE filesystem fixture for local/S3 UFS integration-style tests of `AlluxioJniFuseFileSystem`. It extends `AbstractTest` and constructs the FUSE layer on top of a `UfsBaseFileSystem`.

Important APIs and control flow: `beforeActions` creates `AlluxioJniFuseFileSystem` with `FuseOptions.create(Configuration.global(), FileSystemOptions.create(... Optional.of(mUfsOptions)), false)`, allocates a direct `FileStat`, and opens a `CloseableFuseFileInfo`. `afterActions` cleans the direct buffer and closes file-info resources. Helpers `createEmptyFile` and `createFile` use `create`, `write`, and `release` with `O_WRONLY`.

State, dependencies, integration, risks, tests: state includes native-ish FUSE structs backed by direct buffers and open file handles encoded in `FuseFileInfo`. Dependencies include libfuse-compatible structures, `BufferUtils`, JNR open flags, and inherited UFS setup. Risk centers on cleanup correctness: missing `release` or buffer cleanup can leak native resources across tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/AbstractFuseFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/AbstractTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/AbstractTest.java

Purpose: base fixture for testing FUSE against a UFS-backed Alluxio filesystem. It supports either a local temporary UFS or an S3A-backed path selected by the `alluxio.test.s3a.path` system property.

Important APIs and control flow: `before` copies global configuration, chooses the UFS path, registers `S3AUnderFileSystemFactory` or `LocalUnderFileSystemFactory`, sets `FUSE_MOUNT_POINT`, creates `FileSystemContext`, loads libfuse using `AlluxioFuseUtils.getLibfuseVersion`, creates `UfsFileSystemOptions`, and constructs `UfsBaseFileSystem`. It then calls subclass `beforeActions`. `after` recursively deletes the UFS root and calls `afterActions`.

State, dependencies, integration, risks, tests: state includes `mRootUfs`, `mFileSystem`, `mContext`, `mUfsOptions`, and `mIsLocalUFS`. Dependencies include Alluxio test directories, underfs factory registry, libfuse loading, and local/S3 UFS implementations. Risk: global factory registration and lib loading can affect neighboring tests; S3 mode depends on external credentials/path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/AbstractTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/FuseFileSystemDataTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/FuseFileSystemDataTest.java

Purpose: exercises data-plane behavior of `AlluxioJniFuseFileSystem` over UFS, covering create/open/write/read/release/truncate semantics and expected FUSE error codes.

Important APIs and control flow: tests use `mFileInfo.flags` with `O_WRONLY`, `O_RDONLY`, `O_RDWR`, and `O_TRUNC`; call `create`, `open`, `write`, `read`, `getattr`, `truncate`, `release`, and `unlink`; and assert codes such as `ENAMETOOLONG`, `ENOENT`, `EEXIST`, `EOPNOTSUPP`, and `ETIME`. The helper `createOpenTest` runs each scenario through open/create and optionally read-write open paths.

State, dependencies, integration, risks, tests: state includes FUSE file handles, staged incomplete writes, and file length reflected through `FileStat.st_size`. The tests signal important guarantees: no random writes, incomplete files cannot be read before release, sequential writes grow size, truncation supports zero and future extension in some contexts, and release can happen on a different thread. Risk: thread executor is not explicitly shut down; external S3 mode may behave differently for edge metadata operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/FuseFileSystemDataTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/FuseFileSystemMetadataTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/FuseFileSystemMetadataTest.java

Purpose: metadata-plane tests for `AlluxioJniFuseFileSystem` over local/S3 UFS. It validates directory/file lifecycle, rename behavior, statfs, duplicate directory creation, and chmod.

Important APIs and control flow: tests call `mkdir`, `getattr`, `unlink`, `rmdir`, `rename`, `statfs`, and `chmod`. They assert `ENOENT` and `ENAMETOOLONG` for missing/long paths, successful recursive-like deletion of non-empty directories, renames over existing files/directories, and root statfs success. `chmod` is guarded by `Assume.assumeTrue(mIsLocalUFS)` because S3 lacks POSIX modes.

State, dependencies, integration, risks, tests: state is UFS metadata and direct `FileStat`/`Statvfs` buffers. Dependencies include `AlluxioJniRenameUtils.NO_FLAGS`, `Mode`, and libfuse structs. Test signals show the UFS FUSE adapter tolerates idempotent directory creation and limited rename flags. Risks include broad success expectations for non-empty directory deletion and minimal assertions around rename destination contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/FuseFileSystemMetadataTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/AbstractStreamTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/AbstractStreamTest.java

Purpose: shared stream fixture for `FuseFileStream` tests over local/S3 UFS. It extends the UFS `AbstractTest`, installs a `LaunchUserGroupAuthPolicy`, and creates a `FuseFileStream.Factory`.

Important APIs and control flow: `beforeActions` builds and initializes auth, then passes the filesystem and auth policy to the stream factory. `getTestFileUri` returns a unique path under the UFS root. `writeIncreasingByteArrayToFile` creates a file recursively with increasing bytes. `checkFile` validates `URIStatus.length`, reads the file through `FileInStream`, and compares bytes with `BufferUtils`.

State, dependencies, integration, risks, tests: state is per-test UFS content under unique URIs and the stream factory. Dependencies include Alluxio file streams, gRPC file options, `Mode`, and `BufferUtils`. This class centralizes deterministic byte-content assertions. Risk is that auth is launch-user only, so stream tests do not exercise system-user/group policy interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/AbstractStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/InOrOutStreamInTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/InOrOutStreamInTest.java

Purpose: read-side specialization tests for `FuseFileInOrOutStream` when opened with `O_RDWR` against an existing file. It inherits most behavior from `InStreamTest` and only changes stream creation and write expectations.

Important APIs and control flow: `createStream` invokes `mStreamFactory.create(uri, OpenFlags.O_RDWR.intValue(), DEFAULT_MODE.toShort())`. The overridden `write` test creates a real file, opens the in-or-out stream, writes one byte, and expects `AlreadyExistsRuntimeException`, differentiating O_RDWR-on-existing behavior from a pure read stream's failed-precondition write.

State, dependencies, integration, risks, tests: state includes existing file content created by `writeIncreasingByteArrayToFile`. Dependencies include `FuseFileStream`, JNR open flags, and Alluxio runtime exceptions. The signal is narrow but important: O_RDWR does not imply append/overwrite permission on existing immutable Alluxio files. It does not test O_RDWR creation of missing files because that is covered by the out-side subclass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/InOrOutStreamInTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/InOrOutStreamOutTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/InOrOutStreamOutTest.java

Purpose: write-side specialization tests for `FuseFileInOrOutStream` under `O_RDWR`, inheriting the write behavior suite from `OutStreamTest` while checking unsupported read and empty-create behavior.

Important APIs and control flow: `createStream(uri, truncate)` builds `O_RDWR` flags and optionally ORs `O_TRUNC`. The `read` test writes data then calls `read`, expecting `UnimplementedRuntimeException`. `createEmpty` creates the parent directory, opens/closes an in-or-out stream without writing, then expects `NotFoundRuntimeException` when checking status.

State, dependencies, integration, risks, tests: state is a FUSE stream that only materializes a file after write/close, plus backing UFS status. Dependencies include Alluxio file status, create-directory options, and runtime exceptions. The file signals that read-write mode remains operation-specialized: read from the write path is unsupported and empty no-write close does not create a zero-length file in this mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/InOrOutStreamOutTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/InStreamTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/InStreamTest.java

Purpose: tests `FuseFileInStream`, the read-only stream implementation used by FUSE file reads. It verifies creation over existing files, random reads, and rejection of write/truncate operations.

Important APIs and control flow: `createStream` uses `O_RDONLY`. `createRead` opens an existing file, checks `getFileStatus().getFileLength()`, reads full content at offset 0, and verifies bytes. `createNonexisting` expects `NotFoundRuntimeException`. `randomRead` reads from half and third offsets. `write` expects `FailedPreconditionRuntimeException`; `truncate` expects `UnimplementedRuntimeException`.

State, dependencies, integration, risks, tests: state is immutable source file data and stream position-independent reads. Dependencies include `FuseFileStream`, `URIStatus`, `BufferUtils`, and Alluxio runtime exceptions. Test signal is strong for offset read correctness and operation boundaries. Risk: it does not test EOF partial reads or multiple sequential reads on one stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/InStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/OutStreamTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/OutStreamTest.java

Purpose: tests `FuseFileOutStream`, the write-only stream implementation for FUSE writes. It focuses on file creation, truncation bookkeeping, sequential writes, and unsupported read/random-write paths.

Important APIs and control flow: `createStream` uses `O_WRONLY` and optional `O_TRUNC`. Tests cover empty file creation, create-existing failure, truncate flag overwrite, explicit truncate-to-zero then write, read rejection, random write rejection, sequential writes updating `getFileStatus().getFileLength()`, truncation to zero/default/future lengths, middle-truncate rejection, and multiple truncations before close.

State, dependencies, integration, risks, tests: state includes an in-progress stream file-length model that may exceed bytes written before close. Dependencies include create-directory options, `BufferUtils`, and runtime exceptions. Test signals document Alluxio's append limitations and sparse-like length extension semantics. Risk: it mostly checks final length/content patterns with increasing bytes, not sparse gap byte values in all cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/OutStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/jnifuse/struct/FileStatTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/jnifuse/struct/FileStatTest.java

Purpose: validates Alluxio JNI `FileStat` struct layout against the JNR FUSE `ru.serce.jnrfuse.struct.FileStat` layout and verifies direct-buffer data consistency.

Important APIs and control flow: `offset` creates `FileStat.of(ByteBuffer.allocate(256))` and a JNR stat with `Runtime.getSystemRuntime()`, then compares offsets for device, inode, nlink, mode, uid/gid, rdev, size, block fields, and atime/mtime/ctime seconds/nanoseconds. `dataConsistency` writes `st_mode` and `st_size`, reads them through accessors and through raw `ByteBuffer` offsets.

State, dependencies, integration, risks, tests: state is native-layout memory represented by heap and direct byte buffers. Dependencies include JNR runtime and platform struct definitions. This test is a guardrail for ABI compatibility with libfuse. Risk: it assumes the current platform struct layout; cross-platform differences may need platform-specific expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/jnifuse/struct/FileStatTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/jnifuse/struct/FuseFileInfoTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/jnifuse/struct/FuseFileInfoTest.java

Purpose: verifies Alluxio JNI `FuseFileInfo` struct offsets match JNR FUSE's `FuseFileInfo` layout for the fields Alluxio depends on.

Important APIs and control flow: the test loads libfuse using `LibFuse.loadLibrary(AlluxioFuseUtils.getLibfuseVersion(Configuration.global()))`, creates `FuseFileInfo` over a 256-byte buffer, creates the JNR struct using a null wrapped pointer, and asserts equal offsets for `flags` and `fh`.

State, dependencies, integration, risks, tests: state is only struct layout metadata. Dependencies include global configuration for libfuse version, `AlluxioFuseUtils`, JNR `Pointer`/`Runtime`, and the external JNR FUSE package. The test protects open flag and file-handle interop. Risk: only two fields are covered, so future Alluxio use of additional native fields would need matching assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/jnifuse/struct/FuseFileInfoTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/jnifuse/struct/StatvfsTest.java -->
# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/jnifuse/struct/StatvfsTest.java

Purpose: layout compatibility test for Alluxio JNI `Statvfs` against JNR FUSE's `Statvfs`. It guards the fields populated by FUSE `statfs` responses.

Important APIs and control flow: `offset` creates the Alluxio struct with `Statvfs.of(ByteBuffer.allocate(256))` and the JNR struct with a null wrapped pointer. It compares offsets for filesystem block size fields and free/available block fields, with a repeated `f_frsize` comparison visible in the source.

State, dependencies, integration, risks, tests: state is platform ABI layout in a `ByteBuffer`. Dependencies include JNR `Runtime` and `Pointer`. The test signal ensures FUSE filesystem space reporting writes to locations compatible with JNR expectations. Risks are limited field coverage, duplicated assertion, and platform-specific struct differences not parameterized in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/jnifuse/struct/StatvfsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/job/server/src/main/java/alluxio/underfs/JobUfsManager.java -->
# Research: sources/distributed-fs/alluxio/job/server/src/main/java/alluxio/underfs/JobUfsManager.java

Purpose: job-service implementation of `UfsManager`, responsible for resolving and caching UFS clients used by job workers. It extends `AbstractUfsManager` and queries the master for mount information on cache misses.

Important APIs and control flow: the constructor registers a `FileSystemMasterClient` with the closer. `connectUfs` connects a filesystem from the job worker RPC host. `get(mountId)` first tries `super.get`; if missing, it calls `mMasterClient.getUfsInfo`, validates URI/properties, adds the mount with mount-specific configuration, acquires a UFS resource, and calls `connectFromWorker` using the worker RPC host. On connection failure it removes the mount and throws `UnavailableException`.

State, dependencies, integration, risks, tests: state is the inherited mount cache plus master client lifecycle. Dependencies include master RPC, `UfsInfo`, `UnderFileSystemConfiguration`, and network address resolution. Risk is duplicated logic with worker UFS manager, explicit TODO noted in source, and possible service-type mismatch between job-worker and worker RPC host usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/job/server/src/main/java/alluxio/underfs/JobUfsManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/ConfExpectingUnderFileSystemFactory.java -->
# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/ConfExpectingUnderFileSystemFactory.java

Purpose: test-only UFS factory that validates mount-specific configuration before returning a local UFS. It is useful for tests that must prove configuration propagation into `UnderFileSystemFactory.create`.

Important APIs and control flow: constructor stores a custom scheme and expected config map. `supportsPath` accepts paths beginning with `<scheme>:///`. `create` checks non-null path, asserts `conf.getMountSpecificConf()` equals the expected map, strips the custom scheme down to a local path using nested `AlluxioURI`, and returns `LocalUnderFileSystem`.

State, dependencies, integration, risks, tests: state is immutable expected configuration. Dependencies include Guava `Preconditions`, local UFS, and Alluxio URI parsing. Risk: exact map equality is strict about keys/values and ignores defaults outside mount-specific config, which is intended for targeted propagation tests but not realistic factory matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/ConfExpectingUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/UnderFileSystemTestUtils.java -->
# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/UnderFileSystemTestUtils.java

Purpose: thread-safe utility class for UFS tests. The only behavior classifies UFS addresses as object storage paths.

Important APIs and control flow: `isObjectStorage(String ufsAddress)` returns true for prefixes `s3://`, `s3a://`, `gcs://`, `swift://`, or `oss://` using constants from `alluxio.Constants`. The constructor is private to prevent instantiation.

State, dependencies, integration, risks, tests: no state or persistence. Dependencies are just Alluxio URI header constants and the `UnderFileSystem` type in documentation. Integration point is test code that needs to branch behavior for object storage semantics, such as weaker directory/permission support. Risk: the list can become stale when new object-store schemes such as COS, COSN, ABFS, or ADL should be treated similarly by a given test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/UnderFileSystemTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/delegating/DelegatingUnderFileSystem.java -->
# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/delegating/DelegatingUnderFileSystem.java

Purpose: test utility `UnderFileSystem` wrapper that delegates every method to another UFS. Subclasses can override selected operations to inject behavior while inheriting pass-through coverage for the rest of the interface.

Important APIs and control flow: the constructor stores `mUfs`. Methods forward lifecycle, create/delete, status, ACL, location, list, mkdir/open/rename, owner/mode, active sync, async listing, rate limiter, physical store, and capability calls directly to `mUfs`. It includes overloads for existing/nonexisting file operations and nullable iterable/listing methods.

State, dependencies, integration, risks, tests: state is the wrapped UFS reference; persistence and external state remain entirely in the delegate. Dependencies span the full Alluxio UFS interface: ACL types, statuses, options, sync info, rate limiter, and async callbacks. Risk is interface drift: new `UnderFileSystem` methods must be added here or subclasses stop compiling. It is not thread-safe beyond the delegate's behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/delegating/DelegatingUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/delegating/DelegatingUnderFileSystemFactory.java -->
# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/delegating/DelegatingUnderFileSystemFactory.java

Purpose: simple test factory that returns a preconstructed `UnderFileSystem` for paths beginning with the `delegating` scheme.

Important APIs and control flow: `DELEGATING_SCHEME` is `"delegating"`. The constructor stores the UFS. `create` ignores path and configuration and returns `mUfs`. `supportsPath` checks `path.startsWith(DELEGATING_SCHEME)`.

State, dependencies, integration, risks, tests: state is a single UFS instance shared across all creates, so tests can install a controlled delegate or spy. Dependencies are minimal: `UnderFileSystem`, `UnderFileSystemConfiguration`, and factory interface. Risk: `supportsPath` does not null-check and accepts strings like `delegatingBad`, so callers must pass validated paths or tests may match more broadly than intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/delegating/DelegatingUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystem.java -->
# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystem.java

Purpose: latency-injecting local UFS for tests. It extends `LocalUnderFileSystem`, sleeps for configured durations before selected operations, and otherwise preserves local UFS behavior.

Important APIs and control flow: overrides lifecycle, connection, create/createDirect, delete, exists, status, location, fingerprint, space, type, directory/file checks, list, mkdirs, open, rename, setOwner, setMode, and supportsFlush. Each operation calls `sleepIfNecessary` with the matching option, strips the `sleep` scheme via `cleanPath`, and delegates to `super`. `renameFile` distinguishes temporary file names with `PathUtils.isTemporaryFileName`.

State, dependencies, integration, risks, tests: state is `SleepingUnderFileSystemOptions`. Persistence is local filesystem persistence inherited from `LocalUnderFileSystem`. Dependencies include `CommonUtils.sleepMs`, `PathUtils`, UFS options, and status classes. Risks include sleeps blocking test threads, negative durations meaning no sleep, and only overridden methods receiving latency injection; inherited methods not listed have normal timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystemFactory.java -->
# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystemFactory.java

Purpose: factory for creating `SleepingUnderFileSystem` instances in tests. It binds an options object to the `sleep://` scheme so tests can register predictable operation delays.

Important APIs and control flow: the factory stores `SleepingUnderFileSystemOptions`. `create` validates the path, constructs an `AlluxioURI`, and returns a new `SleepingUnderFileSystem` using that URI, options, and UFS configuration. `supportsPath` accepts non-null paths that start with the sleep scheme header.

State, dependencies, integration, risks, tests: state is the shared options instance used by all UFS instances created from the factory. Dependencies include Alluxio URI parsing and UFS factory registration infrastructure. Risk: mutating the options after factory construction can affect later operations if the same object is shared; this is useful in tests but should be deliberate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystemOptions.java -->
# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystemOptions.java

Purpose: fluent configuration holder for operation-specific delays used by `SleepingUnderFileSystem`. Every field is a millisecond duration and defaults to `-1`, which means no sleep.

Important APIs and control flow: the class exposes getter/setter pairs for cleanup, close, connect-from-master/worker, create, delete directory/file, exists, block size, configuration, directory status, locations, file status, fingerprint, space, status, UFS type, isDirectory/isFile, listStatus/listStatusWithOptions, mkdirs, open, rename directory/file/temporary file, setConf, setOwner, setMode, and supportsFlush. Setters mutate the field and return `this`.

State, dependencies, integration, risks, tests: state is mutable and unsynchronized; callers usually build one instance per test fixture. It has no external dependencies beyond its paired UFS. Risks include negative random values in tests being valid no-sleep values, and option fields such as `setConfMs` existing even if the current `SleepingUnderFileSystem` implementation does not override a matching method.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystemOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystemOptionsTest.java -->
# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystemOptionsTest.java

Purpose: unit coverage for `SleepingUnderFileSystemOptions`, validating default values and fluent setters.

Important APIs and control flow: `defaults` creates a fresh options object and asserts `-1` for every exposed getter. `fields` generates random long values, chains setters across all delay fields, then asserts each getter returns the assigned value.

State, dependencies, integration, risks, tests: state is the mutable options object. Dependencies are JUnit and `java.util.Random`. The tests strongly cover getter/setter wiring for fields included in assertions. Risk: the test uses unconstrained `Random.nextLong`, so many values are negative; that is fine for setter storage but does not prove the sleep behavior for non-negative durations. It also omits any integration with `SleepingUnderFileSystem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystemOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/abfs/pom.xml -->
# Research: sources/distributed-fs/alluxio/underfs/abfs/pom.xml

Purpose: Maven module descriptor for Alluxio's Azure Data Lake Storage Gen2 ABFS underfs implementation. It builds `alluxio-underfs-abfs` under the `alluxio-underfs` parent.

Important APIs and control flow: it sets `build.path` and `ufs.hadoop.version` to `3.3.4`, depends on Hadoop `hadoop-azure`, provided `alluxio-core-common`, and `alluxio-underfs-hdfs`, plus a test jar. The shade plugin excludes license/signature files and specifically excludes HDFS factory service metadata so the shaded artifact exposes the ABFS factory rather than accidentally registering HDFS. The copy-rename plugin participates in distribution packaging.

State, dependencies, integration, risks, tests: build state is Maven dependency/shade output. Integration is with Hadoop ABFS classes and Alluxio's HDFS underfs base. Risks include Hadoop Azure version compatibility, service provider metadata conflicts, and reliance on the parent POM for plugin versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/abfs/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/abfs/src/main/java/alluxio/underfs/abfs/AbfsUnderFileSystem.java -->
# Research: sources/distributed-fs/alluxio/underfs/abfs/src/main/java/alluxio/underfs/abfs/AbfsUnderFileSystem.java

Purpose: Azure Data Lake Storage Gen2 ABFS implementation built on `HdfsUnderFileSystem`. It adapts Alluxio configuration into Hadoop ABFS authentication settings and normalizes object-store-like behavior.

Important APIs and control flow: `createAbfsConfiguration` starts from HDFS config, prefers account-key `SharedKey`, otherwise client credentials OAuth, otherwise managed identity OAuth with optional endpoint/tenant/client id. `createInstance` builds the Hadoop config. `getUnderFSType` returns `abfs`. `getBlockSizeByte` returns Alluxio default block size. `getStatus` rewrites `UfsFileStatus` to use this block size and non-null last-modified time. Owner/mode setters are no-ops; file locations return null.

State, dependencies, integration, risks, tests: state is Hadoop configuration and inherited HDFS filesystem state. Dependencies include `PropertyKey` templates, Hadoop Azure ABFS, and Alluxio UFS status types. Risks include auth precedence mistakes, secret logging through generic config handling, no POSIX ACL/mode support, and no locality reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/abfs/src/main/java/alluxio/underfs/abfs/AbfsUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/abfs/src/main/java/alluxio/underfs/abfs/AbfsUnderFileSystemFactory.java -->
# Research: sources/distributed-fs/alluxio/underfs/abfs/src/main/java/alluxio/underfs/abfs/AbfsUnderFileSystemFactory.java

Purpose: factory registering ABFS paths with Alluxio's UFS factory registry.

Important APIs and control flow: the public no-arg constructor has no state. `create` asserts the path is non-null and delegates to `AbfsUnderFileSystem.createInstance(new AlluxioURI(path), conf)`. `supportsPath` accepts paths beginning with `Constants.HEADER_ABFS` or `Constants.HEADER_ABFSS`.

State, dependencies, integration, risks, tests: this class is stateless and thread-safe. Dependencies include Alluxio URI parsing, constants, UFS factory interface, and `AbfsUnderFileSystem`. Integration occurs through Java service discovery in the module packaging. Risk is limited: it does not implement the configuration-aware `supportsPath(path, conf)` overload, so selection is based only on URI scheme.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/abfs/src/main/java/alluxio/underfs/abfs/AbfsUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/abfs/src/test/java/alluxio/underfs/abfs/AbfsUnderFileSystemFactoryTest.java -->
# Research: sources/distributed-fs/alluxio/underfs/abfs/src/test/java/alluxio/underfs/abfs/AbfsUnderFileSystemFactoryTest.java

Purpose: registry test proving the ABFS module contributes an `UnderFileSystemFactory` for `abfs://` and `abfss://` paths and not for unrelated Alluxio paths.

Important APIs and control flow: the test obtains `Configuration.global()`, calls `UnderFileSystemFactoryRegistry.find` for ABFS and ABFSS sample paths, and asserts non-null factories. It then queries `alluxio://localhost/test/path` and asserts null.

State, dependencies, integration, risks, tests: state is global factory registry/service loading. Dependencies include Alluxio configuration and UFS registry. This test is a packaging/integration signal rather than behavior coverage for ABFS operations or credentials. Risk: it can pass even if actual ABFS client creation fails, because it only checks factory discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/abfs/src/test/java/alluxio/underfs/abfs/AbfsUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/adl/pom.xml -->
# Research: sources/distributed-fs/alluxio/underfs/adl/pom.xml

Purpose: Maven module descriptor for Alluxio's Azure Data Lake Gen1 underfs implementation.

Important APIs and control flow: artifact `alluxio-underfs-adl` inherits from `alluxio-underfs`, sets `ufs.hadoop.version` to `3.3.4`, depends on Hadoop `hadoop-azure-datalake`, provided core common, and `alluxio-underfs-hdfs`. Test dependencies include commons-lang3 and the core-common test jar. Shade configuration removes license/signature files and excludes HDFS factory implementation/service metadata to avoid factory collisions.

State, dependencies, integration, risks, tests: build state is Maven dependency graph and shaded artifact contents. Integration is through Hadoop ADL and the HDFS underfs base. Risks include ADL Gen1 library lifecycle/compatibility, factory service exclusion correctness, and duplicated build-path properties required for submodule builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/adl/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/adl/src/main/java/alluxio/underfs/adl/AdlUnderFileSystem.java -->
# Research: sources/distributed-fs/alluxio/underfs/adl/src/main/java/alluxio/underfs/adl/AdlUnderFileSystem.java

Purpose: Azure Data Lake Gen1 UFS implementation built on `HdfsUnderFileSystem`, translating Alluxio ADL credential properties into Hadoop configuration and adjusting object-store-like metadata.

Important APIs and control flow: `createConfiguration` copies HDFS config, forwards template-matched Azure client id, secret, and refresh URL keys, logs the Hadoop configuration object, and sets `fs.adl.oauth2.access.token.provider.type` to `ClientCredential`. `createInstance` constructs the UFS. `getUnderFSType` returns `adl`. `getBlockSizeByte` returns default Alluxio block size. `getStatus` rewrites file statuses with normalized block size. Owner/mode setters are no-ops; file locations are unsupported and return null.

State, dependencies, integration, risks, tests: state is inherited Hadoop filesystem state and Hadoop config. Dependencies include Hadoop ADL libraries, Alluxio property templates, and status classes. Risks include logging sensitive config, no locality, no ACL/mode mutation, and deprecated Gen1 backend constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/adl/src/main/java/alluxio/underfs/adl/AdlUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/adl/src/main/java/alluxio/underfs/adl/AdlUnderFileSystemFactory.java -->
# Research: sources/distributed-fs/alluxio/underfs/adl/src/main/java/alluxio/underfs/adl/AdlUnderFileSystemFactory.java

Purpose: factory that makes ADL and ADLS URI schemes available to Alluxio's UFS registry.

Important APIs and control flow: `create` checks non-null path and returns `AdlUnderFileSystem.createInstance(new AlluxioURI(path), conf)`. `supportsPath` accepts non-null paths beginning with `Constants.HEADER_ADL` or `Constants.HEADER_ADLS`.

State, dependencies, integration, risks, tests: the class is stateless and thread-safe. Dependencies include Alluxio constants, URI parsing, UFS factory API, and `AdlUnderFileSystem`. Integration depends on module service metadata after shading. Risk is low but scheme-only selection does not validate credential availability or Hadoop ADL library usability at discovery time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/adl/src/main/java/alluxio/underfs/adl/AdlUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/adl/src/test/java/alluxio/underfs/adl/AdlUnderFileSystemFactoryTest.java -->
# Research: sources/distributed-fs/alluxio/underfs/adl/src/test/java/alluxio/underfs/adl/AdlUnderFileSystemFactoryTest.java

Purpose: registry discovery test for the ADL underfs module.

Important APIs and control flow: it calls `UnderFileSystemFactoryRegistry.find("adl://localhost/test/path", Configuration.global())` twice and asserts non-null, then asserts `alluxio://localhost/test/path` returns null. The duplicated ADL lookup appears intended to cover supported paths but does not test `adls://` despite the factory supporting it.

State, dependencies, integration, risks, tests: state is global factory registry. Dependencies include Alluxio configuration and registry classes. The test signal verifies service registration for at least `adl://`. Risk: it misses `adls://`, does not create a UFS, and does not validate credentials or Hadoop configuration translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/adl/src/test/java/alluxio/underfs/adl/AdlUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs-hadoop/pom.xml -->
# Research: sources/distributed-fs/alluxio/underfs/cephfs-hadoop/pom.xml

Purpose: Maven descriptor for the CephFS Hadoop-backed UFS module, `alluxio-underfs-cephfs-hadoop`.

Important APIs and control flow: it depends on `io.github.opendataio:cephfs-hadoop` while excluding log4j and slf4j-log4j12, plus provided core common and `alluxio-underfs-hdfs`. The shade plugin excludes license/signature files and removes HDFS UFS factory service metadata, preserving this module's factory identity. Copy-rename plugin participates in packaging.

State, dependencies, integration, risks, tests: build state is dependency/shaded artifact output. Integration relies on cephfs-hadoop implementing a Hadoop-compatible filesystem used by `HdfsUnderFileSystem`. Risks include native/Hadoop Ceph library compatibility, logging dependency exclusions, and factory service conflicts if shading filters drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs-hadoop/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs-hadoop/src/main/java/alluxio/underfs/cephfshadoop/CephfsHadoopUnderFileSystem.java -->
# Research: sources/distributed-fs/alluxio/underfs/cephfs-hadoop/src/main/java/alluxio/underfs/cephfshadoop/CephfsHadoopUnderFileSystem.java

Purpose: thin `HdfsUnderFileSystem` subclass for CephFS through the cephfs-hadoop adapter.

Important APIs and control flow: `createInstance` calls inherited `createConfiguration(conf)` and constructs `CephfsHadoopUnderFileSystem`. The constructor passes URI, Alluxio UFS config, and Hadoop config to the superclass. `getUnderFSType` returns `cephfs-hadoop`.

State, dependencies, integration, risks, tests: state and persistence are inherited from `HdfsUnderFileSystem` and the cephfs-hadoop Hadoop filesystem. Dependencies include Hadoop `Configuration`, Alluxio URI/config types, and the cephfs-hadoop module dependency. Risk is mostly delegated: this class does not customize permissions, block size, locality, or error mapping, so any Ceph-specific semantics must be correctly handled by the Hadoop adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs-hadoop/src/main/java/alluxio/underfs/cephfshadoop/CephfsHadoopUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs-hadoop/src/main/java/alluxio/underfs/cephfshadoop/CephfsHadoopUnderFileSystemFactory.java -->
# Research: sources/distributed-fs/alluxio/underfs/cephfs-hadoop/src/main/java/alluxio/underfs/cephfshadoop/CephfsHadoopUnderFileSystemFactory.java

Purpose: factory for the cephfs-hadoop UFS implementation, extending HDFS factory behavior while narrowing path support to the CephFS Hadoop scheme.

Important APIs and control flow: `create` null-checks path and returns `CephfsHadoopUnderFileSystem.createInstance(new AlluxioURI(path), conf)`. `supportsPath(path)` checks `Constants.HEADER_CEPHFS_HADOOP`; `supportsPath(path, conf)` delegates to the path-only check.

State, dependencies, integration, risks, tests: stateless and thread-safe. Dependencies include Alluxio constants, URI parsing, HDFS UFS factory base, and CephfsHadoop UFS. Risk: configuration-aware support does not validate Ceph version or required properties, so discovery can succeed before runtime connection/configuration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs-hadoop/src/main/java/alluxio/underfs/cephfshadoop/CephfsHadoopUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs/pom.xml -->
# Research: sources/distributed-fs/alluxio/underfs/cephfs/pom.xml

Purpose: Maven descriptor for the native CephFS UFS module.

Important APIs and control flow: artifact `alluxio-underfs-cephfs` inherits from `alluxio-underfs`, sets `build.path`, and depends on provided `alluxio-core-common`, the CephFS Java/native binding dependency from the parent dependency management, and packaging plugins. Unlike Hadoop-backed modules, this module does not route through HDFS and therefore does not need HDFS factory service exclusions.

State, dependencies, integration, risks, tests: build state is the native CephFS adapter artifact. Integration risk is higher than pure Java adapters because runtime needs the Ceph native libraries and compatible Java binding. Packaging must ensure service discovery for `CephFSUnderFileSystemFactory` and no missing native classes at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephFSUnderFileSystem.java -->
# Research: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephFSUnderFileSystem.java

Purpose: native CephFS `UnderFileSystem` implementation using `com.ceph.fs.CephMount`. It extends `ConsistentUnderFileSystem` and implements `AtomicFileOutputStreamCallback` for atomic writes.

Important APIs and control flow: `createInstance` configures auth id, config file, semicolon-separated config options, key/keyfile/keyring, monitor hosts, MDS namespace, mount uid/gid, mount point, and localized reads before mounting. Operations use `stripPath`, `lstat`, `statfs`, `openInternal`, `deleteInternal`, and retry loops with `CountingRetry(MAX_TRY)`. It supports create/direct create, recursive delete, existence/status, block/space reporting, listStatus, mkdirs with parent creation and owner attempts, seekable open via `CephInputStream`/`CephSeekableInputStream`, rename, chmod, and flush support.

State, dependencies, integration, risks, tests: persistent state is remote CephFS; object state is `mMount`, which is unmounted on close. Dependencies include Ceph native Java APIs, Alluxio UFS option/status classes, `PathUtils`, and retry policies. Risks include native library availability, mount lifecycle, no-op owner support, null file locations, recursive delete correctness, and visible source anomalies in this checkout around duplicated/extra braces near keyfile/delete/open code that would warrant compile verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephFSUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephFSUnderFileSystemFactory.java -->
# Research: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephFSUnderFileSystemFactory.java

Purpose: factory for the native CephFS UFS implementation.

Important APIs and control flow: `create` validates the input path and delegates to `CephFSUnderFileSystem.createInstance(new AlluxioURI(path), conf)`, propagating checked creation failures as runtime failures if required by the interface. `supportsPath` matches the native CephFS URI header from Alluxio constants, and the configuration-aware overload mirrors the path-only check.

State, dependencies, integration, risks, tests: stateless factory; integration is through UFS registry service loading and the native CephFS module. Dependencies include Alluxio constants, URI parsing, `UnderFileSystemConfiguration`, and the native UFS class. Risk is discovery without environment validation: path support does not prove Ceph libraries, auth, monitor hosts, or mount configuration are usable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephFSUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephInputStream.java -->
# Research: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephInputStream.java

Purpose: input stream over an open CephFS file descriptor. It is the low-level stream used by `CephFSUnderFileSystem.open`.

Important APIs and control flow: the stream stores `CephMount`, file descriptor, current position, and file length. `read` variants call Ceph read operations and advance position; `seek` repositions using Ceph seek support and validates offsets; `skip` is implemented through seek-like movement; `available`/EOF behavior derive from length and current position; `close` closes the descriptor once.

State, dependencies, integration, risks, tests: state is mutable stream position plus ownership of a native Ceph file descriptor. Dependencies include `CephMount` and Java `InputStream` semantics. Risks include descriptor leaks on missed close, native exceptions mapping to IOExceptions, thread-unsafety, and correctness of EOF/position accounting when remote file size changes after open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephOutputStream.java -->
# Research: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephOutputStream.java

Purpose: output stream over a native CephFS file descriptor, returned by direct create paths in `CephFSUnderFileSystem`.

Important APIs and control flow: the stream stores `CephMount` and fd. `write(int)` and byte-array writes delegate to Ceph write calls; `flush` maps to Ceph fsync/sync behavior if supported by the binding; `close` closes the fd and prevents duplicate close effects. It is used after `CephFSUnderFileSystem.openInternal` opens a file with write/create/truncate flags.

State, dependencies, integration, risks, tests: state is the native fd and closed status. Persistence occurs immediately in the remote CephFS file. Dependencies include the Ceph Java binding and `OutputStream` contract. Risks include partial native writes, close/fdatasync error handling, and ensuring descriptor closure if stream construction succeeds but later Alluxio operations fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephSeekableInputStream.java -->
# Research: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephSeekableInputStream.java

Purpose: seekable wrapper around `CephInputStream`, adapting the Ceph stream to Alluxio's seekable stream expectations.

Important APIs and control flow: the class wraps an existing `CephInputStream`, delegates read and close operations, and exposes seek-related behavior by calling the underlying stream's seek/position logic. It is returned by `CephFSUnderFileSystem.open` after applying the requested `OpenOptions` offset.

State, dependencies, integration, risks, tests: state is wholly delegated to the wrapped `CephInputStream`, including position and file descriptor ownership. Dependencies include Alluxio seekable stream interfaces and Ceph stream implementation. Risk is thin-wrapper correctness: double close, seek-after-close, and propagation of native IOExceptions all depend on the wrapped stream's behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cephfs/src/main/java/alluxio/underfs/cephfs/CephSeekableInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cos/pom.xml -->
# Research: sources/distributed-fs/alluxio/underfs/cos/pom.xml

Purpose: Maven descriptor for Alluxio's Tencent Cloud COS native object-store UFS module.

Important APIs and control flow: artifact `alluxio-underfs-cos` depends on `com.qcloud:cos_api:5.6.28`, commons-codec, provided `alluxio-core-common`, and the core-common test jar. Build plugins include maven-shade and copy-rename for distribution packaging.

State, dependencies, integration, risks, tests: build state is shaded Java artifact output. Integration is directly with Tencent COS SDK rather than Hadoop. Risks include SDK version compatibility, transitive dependency conflicts in the shaded artifact, and the need for service metadata to expose `COSUnderFileSystemFactory`. Commons-codec is required for MD5 base64 handling in the output stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cos/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/AlluxioCosException.java -->
# Research: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/AlluxioCosException.java

Purpose: COS-specific runtime exception adapter converting Tencent COS SDK exceptions into Alluxio runtime exceptions with gRPC status and retryability metadata.

Important APIs and control flow: `from(CosClientException)` delegates to `from(null, cause)`. The overload defaults to `Status.UNKNOWN` and client error text, but if the cause is `CosServiceException`, maps the HTTP status code via `httpStatusToGrpcStatus` and uses COS error code/message. The private constructor passes `ErrorType.External` and `cause.isRetryable()` to `AlluxioRuntimeException`.

State, dependencies, integration, risks, tests: no persistent state. Dependencies include COS SDK exceptions, gRPC `Status`, `ErrorType`, and HTTP status constants. Integration point is object operations that catch `CosClientException`. Risk: unmapped COS-specific status codes become UNKNOWN; retryability relies on SDK classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/AlluxioCosException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSInputStream.java -->
# Research: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSInputStream.java

Purpose: COS object input stream with multi-range support. It extends `MultiRangeObjectInputStream` to efficiently read remote objects in bounded ranges.

Important APIs and control flow: constructors store bucket, key, COS client, start position, retry policy, and object content length from metadata. `createStream(startPos, endPos)` builds a `GetObjectRequest`, sets an inclusive range capped at content length minus one, copies the retry policy, and retries 404 responses for eventual consistency while failing immediately for other COS service exceptions. It returns a `BufferedInputStream` over object content.

State, dependencies, integration, risks, tests: state includes object length, current inherited position, and retry policy. Dependencies include Tencent COS SDK, Apache HTTP status, Alluxio multi-range stream base, and object metadata. Risks include range math for empty objects, object mutations after metadata fetch, and retry behavior only for not-found responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSOutputStream.java -->
# Research: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSOutputStream.java

Purpose: COS object output stream that stages writes to a local temporary file, then uploads the complete file on close. It implements `ContentHashable` to expose the uploaded object's ETag/content hash.

Important APIs and control flow: constructor validates bucket/key/client, creates a temp file under configured temp dirs, and wraps a `FileOutputStream` in `DigestOutputStream` for MD5 when available. `write` and `flush` operate on the local stream. `close` is guarded by `AtomicBoolean`, closes local output, uploads via `putObject` with content length and optional base64 MD5 metadata, stores ETag, and deletes the temp file in `finally`.

State, dependencies, integration, risks, tests: state includes temp file path, local stream, MD5 digest, closed flag, and content hash. Dependencies include Tencent COS SDK, commons-codec Base64, Alluxio temp-dir utilities. Risks include local disk pressure, temp deletion failure, no multipart upload for large files, and content hash unavailable before close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSUnderFileSystem.java -->
# Research: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSUnderFileSystem.java

Purpose: Tencent Cloud COS object-store `UnderFileSystem` built on `ObjectUnderFileSystem`.

Important APIs and control flow: `createInstance` validates access key, secret key, region, and app id, creates `BasicCOSCredentials`, `ClientConfig`, and `COSClient`, then derives internal bucket name as `<bucket>-<appId>`. It implements object copy, empty object creation, output stream creation, single and batch delete, listing chunks with delimiter/prefix/max keys, directory detection via folder marker or listing, object status from metadata including ETag/CRC, permissions defaults, root key, client config timeouts, and `openObject` using `COSInputStream`.

State, dependencies, integration, risks, tests: state is the COS client and bucket names. Persistence is remote COS objects and local temp files during writes. Dependencies include Tencent COS SDK, Alluxio object UFS base, property keys, and path normalization. Risks include inconsistent bucket name use in `deleteObjects` versus internal bucket, object-store directory marker semantics, no ACL/mode integration, and SDK exception wrapping gaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSUnderFileSystemFactory.java -->
# Research: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSUnderFileSystemFactory.java

Purpose: UFS factory for native Tencent COS paths.

Important APIs and control flow: `supportsPath` accepts paths starting with `Constants.HEADER_COS`. `create` null-checks path, calls `checkCOSCredentials`, and if access key, secret key, and region are present delegates to `COSUnderFileSystem.createInstance`. Otherwise it propagates an `IOException` stating credentials are unavailable. The factory itself checks fewer properties than `createInstance`, which also requires app id.

State, dependencies, integration, risks, tests: stateless and thread-safe. Dependencies include Alluxio constants, property keys, URI parsing, Guava `Throwables`, and COS UFS implementation. Risk: credential precheck mismatch can produce a later propagated exception for missing app id; `Throwables.propagate` style can obscure checked exception boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cosn/pom.xml -->
# Research: sources/distributed-fs/alluxio/underfs/cosn/pom.xml

Purpose: Maven descriptor for Alluxio's Hadoop COSN UFS module.

Important APIs and control flow: artifact `alluxio-underfs-cosn` sets `ufs.cosn.version` to `3.1.0-5.8.5`, depends on `cos_api-bundle`, `hadoop-cos` at that version, provided core common, `alluxio-underfs-hdfs`, and test jar. Shade filters exclude license/signature files and HDFS factory service metadata. The templating plugin filters `src/main/java-templates` into generated sources, substituting the COSN version constant.

State, dependencies, integration, risks, tests: build state includes generated Java source for `CosnUfsConstants`. Integration relies on Hadoop COS filesystem and Alluxio HDFS underfs base. Risks include keeping `ufs.cosn.version` synchronized with distribution scripts, service metadata conflicts, and generated source availability in IDE/submodule builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cosn/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cosn/src/main/java-templates/alluxio/CosnUfsConstants.java -->
# Research: sources/distributed-fs/alluxio/underfs/cosn/src/main/java-templates/alluxio/CosnUfsConstants.java

Purpose: Maven-filtered Java template that exposes the COSN Hadoop UFS version compiled into the module.

Important APIs and control flow: class `CosnUfsConstants` is final, has public static final `UFS_COSN_VERSION = "${ufs.cosn.version}"`, and a private constructor. During the Maven templating phase, the placeholder is replaced with the module property, e.g. `3.1.0-5.8.5`.

State, dependencies, integration, risks, tests: no runtime state. Integration point is `CosNUnderFileSystemFactory.getVersion`, which uses this constant for version-aware factory selection when `UNDERFS_VERSION` is set. Risk: if templating does not run, the literal placeholder may appear in compiled code or IDE analysis; version drift can prevent factory discovery for explicitly versioned mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cosn/src/main/java-templates/alluxio/CosnUfsConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cosn/src/main/java/alluxio/underfs/cosn/CosNUnderFileSystemFactory.java -->
# Research: sources/distributed-fs/alluxio/underfs/cosn/src/main/java/alluxio/underfs/cosn/CosNUnderFileSystemFactory.java

Purpose: factory for Hadoop COSN-backed UFS instances, with optional version matching.

Important APIs and control flow: `create` null-checks path and delegates to `CosnUnderFileSystem.createInstance`. `supportsPath(path)` checks `Constants.HEADER_COSN`. `supportsPath(path, conf)` first checks the scheme; if `PropertyKey.UNDERFS_VERSION` is explicitly set by the user, it must exactly equal `getVersion()`, otherwise the bundled version is assumed compatible. `getVersion` returns `CosnUfsConstants.UFS_COSN_VERSION`.

State, dependencies, integration, risks, tests: stateless and thread-safe. Dependencies include generated constants, property keys, and UFS factory API. Risk: exact version matching can reject semantically compatible patch variants; templating/version drift directly affects discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cosn/src/main/java/alluxio/underfs/cosn/CosNUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cosn/src/main/java/alluxio/underfs/cosn/CosnUnderFileSystem.java -->
# Research: sources/distributed-fs/alluxio/underfs/cosn/src/main/java/alluxio/underfs/cosn/CosnUnderFileSystem.java

Purpose: thin HDFS-adapter UFS for Tencent COSN through Hadoop COS libraries.

Important APIs and control flow: `createInstance` calls inherited `createConfiguration(conf)` and constructs `CosnUnderFileSystem`. The constructor delegates URI, Alluxio UFS config, and Hadoop config to `HdfsUnderFileSystem`. `getUnderFSType` returns `cosn`.

State, dependencies, integration, risks, tests: runtime state and persistence are inherited from `HdfsUnderFileSystem` and Hadoop COSN. Dependencies include Hadoop `Configuration`, Alluxio URI/config types, and hadoop-cos library. Risks are mostly delegated: no custom block size, permission, locality, or error mapping appears here, so correctness relies on Hadoop COSN and HDFS base behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cosn/src/main/java/alluxio/underfs/cosn/CosnUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cosn/src/test/java/alluxio/underfs/cosn/CosNUnderFileSystemFactoryTest.java -->
# Research: sources/distributed-fs/alluxio/underfs/cosn/src/test/java/alluxio/underfs/cosn/CosNUnderFileSystemFactoryTest.java

Purpose: registry tests for COSN factory discovery and version gating.

Important APIs and control flow: `factory` asserts a factory is found for `cosn://test-bucket/path` using global configuration. `version` asserts discovery works with no explicit version, works when `UNDERFS_VERSION` is `3.1.0-5.8.5`, and returns null when `UNDERFS_VERSION` is `error-version`.

State, dependencies, integration, risks, tests: state includes global mutable `Configuration`, which the test modifies. Dependencies include UFS registry and property keys. Test signal is good for version-aware selection. Risk: global config mutation may leak if not reset by test framework; the test does not instantiate a COSN UFS or validate Hadoop credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/cosn/src/test/java/alluxio/underfs/cosn/CosNUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/pom.xml -->
# Research: sources/distributed-fs/alluxio/underfs/gcs/pom.xml

Purpose: Maven descriptor for Alluxio's Google Cloud Storage underfs stream/support module.

Important APIs and control flow: artifact `alluxio-underfs-gcs` inherits from `alluxio-underfs`, sets `build.path`, and depends on the parent-managed JetS3t/Google Storage client stack, provided Alluxio core common, and packaging plugins. The module supplies GCS stream implementations used by the broader GCS UFS implementation.

State, dependencies, integration, risks, tests: build state is Maven dependency and shaded output. Integration risks include older JetS3t GoogleStorageService compatibility with modern GCS APIs, transitive HTTP dependency conflicts, and proper inclusion of service metadata/classes in distribution packaging. Stream classes also rely on temp-dir and MD5 behavior from dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSInputStream.java -->
# Research: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSInputStream.java

Purpose: GCS input stream optimized for skip/offset reads, avoiding slow read-and-discard behavior from the underlying stream by reopening from a requested offset.

Important APIs and control flow: constructors store bucket, key, `GoogleStorageService`, initial position, and retry policy. `read` lazily opens the stream and advances `mPos`. `read(byte[], off, len)` returns 0 for zero-length reads. `skip` returns 0 for non-positive values, uses buffered skip if enough bytes are available, otherwise closes the current stream, advances `mPos`, and reopens from that offset. `openStream` retries 404s and throws immediately for other service errors.

State, dependencies, integration, risks, tests: state includes current position and a nullable buffered input stream. Dependencies include JetS3t `GoogleStorageService`, `GSObject`, Apache HTTP status, and Alluxio retry policy. Risks include `skip` calling `mInputStream.available()` when stream is null in some call sequences, object mutation between reopen calls, and retry policy reuse across opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSOutputStream.java -->
# Research: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSOutputStream.java

Purpose: GCS output stream that stages data to a local temp file and uploads the full object on close. It implements `ContentHashable` using the uploaded object's MD5 hash.

Important APIs and control flow: constructor validates bucket, records key/client, creates a UUID temp file under configured temp dirs, and wraps the local stream with MD5 digesting when available. `write` and `flush` target the local stream. `close` is idempotent through `AtomicBoolean`, closes the local stream, builds a `GSObject` with file, content length, binary content type, and optional MD5, uploads through `putObject`, records base64 MD5, and deletes the temp file in `finally`.

State, dependencies, integration, risks, tests: state includes temp file, digest, local output stream, closed flag, and content hash. Dependencies include JetS3t GCS client, `Mimetypes`, Alluxio temp-dir utilities, and Java security digest APIs. Risks include local disk exhaustion, failed temp deletion, no multipart streaming upload, and no key validation beyond bucket validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSOutputStream.java -->
