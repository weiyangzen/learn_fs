# subset-b-007389 research

Grouped research for Hadoop common filesystem tests. Each section is keyed by source path for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGetSpaceUsed.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGetSpaceUsed.java

Purpose: validates `CachingGetSpaceUsed.Builder` and `GetSpaceUsed.Builder` construction paths for Hadoop local disk-usage measurement. It checks class selection from configuration, explicit class injection, initial used-space propagation, refresh interval propagation, and non-caching implementations.

Important APIs/types/functions: `CachingGetSpaceUsed.Builder`, `GetSpaceUsed`, `CachingGetSpaceUsed`, configuration key `fs.getspaceused.classname`, and test-only `DummyDU`/`DummyGetSpaceUsed`. `setPath`, `setInterval`, `setInitialUsed`, `setConf`, `setKlass`, `build`, `getUsed`, `getRefreshInterval`, and `running` are the exercised API surface.

Control flow/state/persistence: each test creates a fresh temp directory under `GenericTestUtils.getTestDir("TestGetSpaceUsed")`, deletes it in setup/teardown, creates a file, builds a disk-usage object, asserts properties, and closes caching instances. `DummyDU.refresh()` is intentionally a no-op so tests isolate builder state from real `du` execution. The only persistent state is temporary filesystem content removed after each test.

Dependencies/integration points: integrates with Hadoop `Configuration`, `FileUtil`, local `File`, JUnit lifecycle annotations, and the disk-usage builder reflection path. It indirectly guards production subclasses that rely on builder constructors.

Risks/test signals: reflection-based constructor failures, ignored configuration class names, accidental background refresh thread startup at interval zero, and regressions where non-caching implementations are forced through `CachingGetSpaceUsed` assumptions. Strong signal comes from asserting concrete class type, initial value, interval, and non-running state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGetSpaceUsed.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGlobExpander.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGlobExpander.java

Purpose: tests brace expansion behavior in `GlobExpander`, especially expansion around path separators and escaped braces/slashes.

Important APIs/types/functions: `GlobExpander.expand(String)` returns `List<String>`. Helpers `checkExpansionIsIdentical` and `checkExpansion` compare ordered expansions against expected strings.

Control flow/state/persistence: tests are pure and stateless. `testExpansionIsIdentical` feeds malformed, escaped, or non-expandable patterns and expects the original string. `testExpansion` exercises expandable braces, nested braces that must be preserved, suffix/prefix concatenation, escaped slash handling, and multi-alternative paths.

Dependencies/integration points: depends only on the Hadoop glob expander and JUnit. It is an input-level companion to `FileSystem.globStatus` and `GlobPattern`; no filesystem IO occurs.

Risks/test signals: protects against over-expanding nested braces, treating escaped characters as syntax, or changing expansion order. The expected list order is significant because downstream glob processing may rely on deterministic expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGlobExpander.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGlobPattern.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGlobPattern.java

Purpose: verifies translation and matching semantics of Hadoop glob patterns backed by RE2J.

Important APIs/types/functions: `GlobPattern`, `GlobPattern.compile`, `GlobPattern.matches`, RE2J `PatternSyntaxException`, and helper methods `assertMatch`/`shouldThrow`.

Control flow/state/persistence: tests are pure. Valid cases cover `*`, `?`, character classes, negated classes, escaped metacharacters, brace alternatives, literal closing braces, newline matching, and regex metacharacters that must be literal. Invalid cases require syntax exceptions for unmatched class/brace/escape patterns. A timeout-protected pathological filename guards against expensive regex behavior.

Dependencies/integration points: integrates with RE2J exception behavior and Hadoop path/glob matching. It complements glob expansion and filesystem glob status tests.

Risks/test signals: catches regex injection/literal escaping regressions, invalid pattern acceptance, and performance/pathological backtracking issues. The `@Timeout(10)` on the long history filename is a direct signal for denial-of-service style pattern translation regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGlobPattern.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestHarFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestHarFileSystem.java

Purpose: validates core `HarFileSystem` behavior that does not require a full archive fixture: URI rejection, checksum nullability, block-location offset normalization, and method-override coverage against `FileSystem`.

Important APIs/types/functions: `HarFileSystem`, `FileSystem`, `BlockLocation`, `HarFileSystem.fixBlockLocations`, `Path.getFileSystem`, `getFileChecksum`, and the reflection-only `MustNotImplement` interface listing methods HAR should inherit rather than override.

Control flow/state/persistence: `testHarUri` creates invalid `har://` paths and expects `IOException` during filesystem resolution. `testFileChecksum` constructs a HAR path and asserts checksum is null. `testFixBlockLocations` mutates `BlockLocation` arrays in place across eight range-overlap scenarios plus a MAPREDUCE-1752 regression. `testInheritedMethodsImplemented` iterates declared `FileSystem` methods, skips static/private/final methods, and uses reflection to require HAR to override only methods not in the allowlist.

Dependencies/integration points: tightly couples HAR to the evolving `FileSystem` API, including append, ACL, XAttr, snapshot, storage policy, open-file builders, multipart upload, trash, and bulk delete signatures. Reflection makes this a maintenance gate whenever `FileSystem` adds methods.

Risks/test signals: highest-risk signal is API drift: new `FileSystem` methods must be classified as HAR-specific overrides or inherited defaults. Block-location tests catch off-by-one and partial-overlap errors in archived-file reads. URI tests protect HAR authority parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestHarFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestHarFileSystemBasics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestHarFileSystemBasics.java

Purpose: builds minimal local HAR directory structures and tests `HarFileSystem` initialization, metadata caching, read-only semantics, path qualification, list status, version handling, and URI forms.

Important APIs/types/functions: `HarFileSystem`, `FileSystem.getLocal`, `_index`, `_masterindex`, `getHarVersion`, `getUri`, `getHomeDirectory`, `getWorkingDirectory`, `getMetadata`, `listLocatedStatus`, `makeQualified`, `FileContext.getFileContext`, and mutating methods expected to throw.

Control flow/state/persistence: setup creates a temp local root, a `.har` directory, empty index files, and writes the HAR version into `_masterindex`; teardown closes HAR and deletes the tree. Positive tests assert version/URI/home/working directory, metadata reuse for identical underlying FS, LRU eviction after `METADATA_CACHE_ENTRIES_DEFAULT + 1` archives, initialization without an explicit underlying FS, authority preservation, and fixture-based located-status listing from `/test.har`. Negative tests delete `_index`, overwrite `_masterindex` with unsupported version after a timestamp delay, and call mutation methods expecting `IOException`.

Dependencies/integration points: depends on local FS, HAR metadata cache, `Shell.WINDOWS` path adjustment, bundled `/test.har` resource, `FsPermission`, and `FileContext` registration of `har` URIs.

Risks/test signals: cache invalidation by modification time is timing-sensitive; unsupported-version tests rely on a one-second timestamp granularity delay. It signals regressions in HAR read-only guarantees, URI authority handling, metadata cache eviction, and initialization from classpath filesystem resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestHarFileSystemBasics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestHardLink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestHardLink.java

Purpose: tests Hadoop `HardLink` helpers against the host local filesystem: link count discovery, single hardlink creation, multi-file hardlink creation, empty batches, and Windows command-template syntax.

Important APIs/types/functions: static imports from `HardLink` including `createHardLink`, `createHardLinkMult`, `getLinkCount`, `supportsHardLink`, and `HardLinkCGWin`. Helpers build source/target directories and validate content/link counts.

Control flow/state/persistence: `@BeforeAll` and `@AfterEach` delete static temp directories; `@BeforeEach` recreates `src`, `tgt_one`, and `tgt_mult` with three files containing unique strings. Single-link tests create multiple links to the same source and then append through one link to prove shared inode content. Multi-link tests hardlink all names from a directory and verify count/content. Empty-list test ensures no filesystem change. Windows syntax test inspects command array literals without executing Windows commands.

Dependencies/integration points: depends on local filesystem hardlink support, Hadoop `FileUtil`, Java `FileReader/FileWriter`, and OS-specific command generation.

Risks/test signals: tests are intentionally lightweight and assume permissions are valid; they do not cover negative permission failures. They catch link count regressions, content-copy masquerading as hardlinking, empty-batch side effects, and accidental command string mangling on Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestHardLink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestListFiles.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestListFiles.java

Purpose: verifies `FileSystem.listFiles(Path, boolean)` over local files and directories, including recursive and non-recursive behavior and block-location population.

Important APIs/types/functions: `FileSystem.getLocal`, `RemoteIterator<LocatedFileStatus>`, `LocatedFileStatus`, `FSDataOutputStream`, `makeQualified`, and helper `writeFile`.

Control flow/state/persistence: static setup initializes local FS and deletes the test root. `testFile` writes one file and asserts both recursive and non-recursive listing return exactly that file with length and one block location. `testDirectory` checks empty directories, one-file directories, mixed root/nested files with set-based order-independent recursive validation, and non-recursive root listing returning only direct files.

Dependencies/integration points: uses local FS implementation of `listFiles`, block location generation, and path qualification. Test paths can be overridden by subclasses through `setTestPaths`.

Risks/test signals: catches directory traversal regressions, accidental directory entries in file listings, missing block locations, path qualification mismatches, and recursive/non-recursive confusion. Ordering is intentionally ignored for recursive multi-file results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestListFiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalDirAllocator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalDirAllocator.java

Purpose: exercises `LocalDirAllocator` allocation, recovery, and diagnostic behavior across relative, absolute, and qualified local directory configurations.

Important APIs/types/functions: `LocalDirAllocator`, context key `mapred.local.dir`, `createTmpFileForWrite`, `getLocalPathForWrite`, `getLocalPathToRead`, `getAllLocalPathsToRead`, `removeContext`, `isContextValid`, `DiskErrorException`, and constant `E_NO_SPACE_AVAILABLE`.

Control flow/state/persistence: parameterized tests run the same scenarios for three path forms. They manipulate real directories under `build/test/temp`, switch permissions read-only/read-write, create temp files, inspect allocator current index, and delete buffer directories. Scenarios include read-only first disk, missing dirs, round-robin/randomized distribution, a disk becoming read-only, many allocations, access-check parent creation behavior, absent/empty configs, no side-effect paths from qualified strings, read lookup iteration semantics, context cache removal, invalid blank path, insufficient-space diagnostics, and directory tree recovery after ancestor deletion for unknown and known sizes.

Dependencies/integration points: depends on `LocalFileSystem`, `Shell` chmod commands, platform assumptions excluding Windows for permission-sensitive cases, and Hadoop disk checker behavior.

Risks/test signals: sensitive to platform permission semantics and filesystem free space. It catches stale cached directory health, NPEs from bad config, accidental creation of literal `file:` directories, broken iterator contracts, poor error diagnostics, and recovery regressions from HADOOP-18636/HADOOP-19554.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalDirAllocator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFSCopyFromLocal.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFSCopyFromLocal.java

Purpose: specializes the copy-from-local contract suite for `LocalFileSystem` and documents self/recursive copy edge cases.

Important APIs/types/functions: `AbstractContractCopyFromLocalTest`, `LocalFSContract`, `copyFromLocalFile(delSrc, overwrite, src, dst)`, `createTempFile`, `createTempDirectory`, `assertPathExists`, and `assertPathDoesNotExist`.

Control flow/state/persistence: the inherited contract supplies setup and common copy tests. Local additions copy a file to its own parent with source deletion, copy a directory to itself with source deletion, copy a parent into its child with source deletion, and copy a parent into its child without deletion. The no-delete case intentionally asserts recursive nested output exists, documenting current local behavior rather than rejecting it.

Dependencies/integration points: integrates local FS with the generic contract framework. Uses Java temp files/directories converted to Hadoop `Path` through URI constructors.

Risks/test signals: catches dangerous deletion behavior when source and destination overlap. The recursive-copy case is a risk marker: local FS may recurse deeply depending on underlying copy implementation, so future fixes must preserve or consciously update the documented behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFSCopyFromLocal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFSFileContextCreateMkdir.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFSFileContextCreateMkdir.java

Purpose: binds the generic `FileContextCreateMkdirBaseTest` suite to the local `FileContext` implementation.

Important APIs/types/functions: `FileContext.getLocalFSFileContext`, inherited `fc` field, and inherited create/mkdir assertions from `FileContextCreateMkdirBaseTest`.

Control flow/state/persistence: `setUp` installs a fresh local `FileContext` before delegating to the base setup. All substantive behavior is inherited and runs against local FS paths.

Dependencies/integration points: verifies the `FileContext` API layer, not the direct `FileSystem` API. It depends on the base test contract for recursive creation, directory creation, and error behavior.

Risks/test signals: this file is small but important as an adapter. A failure usually indicates local `FileContext` setup, URI resolution, or base contract behavior diverging from local FS expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFSFileContextCreateMkdir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFSFileContextMainOperations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFSFileContextMainOperations.java

Purpose: runs the generic `FileContextMainOperationsBaseTest` against local FS and adds local-specific checks for caching, corrupted-block support, working directory, and default file permission.

Important APIs/types/functions: `FileContext.getLocalFSFileContext`, `FileSystem.getLocal`, `FileContextTestHelper.createFile`, `FileContext.FILE_DEFAULT_PERM`, `fc.getUMask`, and inherited main-operation contract methods.

Control flow/state/persistence: setup creates a local file context and delegates to the base class. `getDefaultWorkingDirectory` caches the local FS working directory in a static field. `testFileContextNoCache` asserts separate local file context instances are not the same object. `listCorruptedBlocksSupported` returns false. `testDefaultFilePermission` creates a file and validates default permissions after umask.

Dependencies/integration points: bridges local FS through `FileContext`; depends on local default working directory and permission behavior.

Risks/test signals: catches unwanted `FileContext` instance caching, wrong default permission application, and incorrect exposure of corrupt-block APIs for local FS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFSFileContextMainOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFileSystem.java

Purpose: broad regression suite for `LocalFileSystem` and `RawLocalFileSystem` through the `FileSystem` abstraction, covering CRUD, working directory, checksum sidecars, statistics, builder APIs, rename semantics, buffered reads, and platform path behavior.

Important APIs/types/functions: `FileSystem.getLocal`, `RawLocalFileSystem`, `LocalFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FileUtil.copy`, `reportChecksumFailure`, `setTimes`, `BufferedFSInputStream`, `createFile`/`openFile` builders, `FSDataOutputStreamBuilder`, `Statistics`, `CreateFlag`, `Options.ChecksumOpt`, and mocked file status for pipe-like files.

Control flow/state/persistence: setup forces `fs.file.impl` to `LocalFileSystem`, resets the test root, and teardown restores writability, deletes temp content, and re-enables stat. Tests create local files/directories, copy/rename/delete them, read data, manipulate permissions, induce checksum quarantine by making an ancestor non-writable, set timestamps, perform randomized seek/read verification, test directory rename overwrite/move cases, strip URI fragments during resolution, verify append stream position, handle non-file/non-directory path listing, validate builder defaults/options, and assert byte statistics include CRC sidecar IO for classic and builder APIs.

Dependencies/integration points: integrates local FS with checksum FS wrappers, raw local streams, statistics accounting, Mockito spies/mocks, platform assumptions, and builder option validation.

Risks/test signals: high-value regression coverage for local IO semantics. Signals include CRC byte accounting mismatches, checksum failure quarantine path regressions, random seek/read corruption, rename semantics changes, builder unsupported mandatory keys, fragment leakage, Windows path inconsistencies, and pipe-file status handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFileSystemPermission.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFileSystemPermission.java

Purpose: validates local filesystem permission, umask, rename permission preservation, and group ownership behavior.

Important APIs/types/functions: `LocalFileSystem`, `FsPermission`, config key `FS_PERMISSIONS_UMASK_KEY`, `mkdirs`, `create` with explicit permission, `setPermission`, `setOwner`, `getFileStatus`, `Shell.getGroupsCommand`, and helper `getPermission`.

Control flow/state/persistence: tests run only on non-Windows. They create files/directories under a temp prefix, set umasks, assert default and explicit permissions after umask application, rename files/directories and verify permissions survive, set permissions to none/all, set group ownership to the current user's groups when available, and update umask at runtime to ensure newly created dirs observe the changed value. Cleanup deletes created paths and resets umask in the runtime test.

Dependencies/integration points: depends on Unix permission semantics, shell group command output, and local FS status loading.

Risks/test signals: catches stale umask caching, permission loss during rename, incorrect create/mkdir permission masking, and `setOwner` group failures. Platform sensitivity is explicitly guarded by assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFileSystemPermission.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFsFCStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFsFCStatistics.java

Purpose: specializes `FCStatisticsBaseTest` for local `FileContext` statistics and expected checksum sidecar byte accounting.

Important APIs/types/functions: `FileContext.getLocalFSFileContext`, `FileSystem.Statistics`, inherited `blockSize`, and `getFsUri`.

Control flow/state/persistence: setup creates a local test root through `FileContext`; teardown deletes it. Overrides assert that reads count two block-size reads for read and positional-read, while writes count `blockSize + 12` to include CRC bytes. The URI under test is `file:///tmp/test`.

Dependencies/integration points: depends on local `FileContext`, file-scheme statistics sharing, and checksum sidecar size assumptions.

Risks/test signals: catches statistics regressions where FileContext local reads/writes stop including checksum IO or count a different number of bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFsFCStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocatedFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocatedFileStatus.java

Purpose: verifies deprecated `LocatedFileStatus` constructors remain usable with null and non-null permissions.

Important APIs/types/functions: `LocatedFileStatus`, `BlockLocation`, `FsPermission`, `Path`, and Mockito `mock`.

Control flow/state/persistence: creates a mocked block-location array, constructs one status with a null permission, and constructs another with a mocked permission. No assertions are needed beyond successful construction.

Dependencies/integration points: protects binary/source compatibility for legacy callers constructing located statuses directly.

Risks/test signals: catches constructor nullability regressions or accidental removal/behavior changes in deprecated status construction paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocatedFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestPath.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestPath.java

Purpose: comprehensive unit tests for Hadoop `Path` parsing, normalization, URI conversion, glob escaping, Windows handling, serialization, Avro reflection, qualification, and path merging.

Important APIs/types/functions: `Path` constructors, `toString`, `toUri`, `isAbsolute`, `getParent`, `getName`, `makeQualified`, `mergePaths`, `suffix`, `isWindowsAbsolutePath`, `FileSystem.globStatus`, `listStatus`, Java serialization, and `AvroTestUtil.testReflect`.

Control flow/state/persistence: most tests are pure string/URI assertions. Filesystem-backed glob tests create local directories including a literal `*` name, compare `listStatus` and escaped/unescaped `globStatus`, and clean through temp-root usage. Platform-specific tests use Windows/non-Windows assumptions. Serialization uses byte-array streams; Avro sets trusted package system property.

Dependencies/integration points: integrates with Java `URI`, local filesystem globbing, Hadoop config constants, shell platform flags, and Avro reflection.

Risks/test signals: high signal for path compatibility. It catches normalization drift, colon/drive-letter ambiguity, dot-segment resolution bugs, fragment/query encoding mistakes, reserved character handling, escaped glob misbehavior, Windows absolute detection, merge semantics across schemes/authorities, and serialization contract breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestPath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestQuotaUsage.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestQuotaUsage.java

Purpose: validates `QuotaUsage` builder defaults, quota accounting fields, formatted output, human-readable output, and equality.

Important APIs/types/functions: `QuotaUsage.Builder`, getters for file/directory count, namespace quota, space consumed/quota, `QuotaUsage.getHeader`, `toString`, `toString(true)`, `StorageType.SSD`, `typeConsumed`, `typeQuota`, and `equals`.

Control flow/state/persistence: pure DTO tests construct quota objects with no quota, namespace/space quota, and storage-type quota data; then assert getter values and exact formatted strings.

Dependencies/integration points: supports CLI/reporting consumers of quota output and storage-type quota accounting.

Risks/test signals: exact string assertions catch formatting regressions in user-facing quota reports, including `none`, `inf`, negative remaining quota, and human unit conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestQuotaUsage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestRawLocalFileSystemContract.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestRawLocalFileSystemContract.java

Purpose: runs the generic filesystem contract against `RawLocalFileSystem` with local-specific disables and validates native/non-native permission loading consistency.

Important APIs/types/functions: `FileSystemContractBaseTest`, `RawLocalFileSystem`, `DF`, `NativeCodeLoader`, `StatUtils.setPermissionFromProcess`, `DeprecatedRawLocalFileStatus.loadPermissionInfoByNativeIO`, and `loadPermissionInfoByNonNativeIO`.

Control flow/state/persistence: setup installs the raw local filesystem. The contract disables rename and root-dir tests because local rename semantics differ and root writes are unsafe. Case sensitivity is inferred from OS and `DF.getFilesystem`, accounting for Docker mounts of Mac/Windows volumes. `testPermission` requires native code, creates a file, compares native and non-native owner/group/permission loading, then chmods normal and sticky-bit modes and compares again.

Dependencies/integration points: depends on native Hadoop libraries, shell chmod/stat behavior, `DF`, host filesystem type, and generic contract tests.

Risks/test signals: catches divergence between native and fallback permission loaders, sticky-bit parsing regressions, incorrect case-sensitivity assumptions in mounted filesystems, and unsafe generic contract expectations for raw local FS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestRawLocalFileSystemContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestStat.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestStat.java

Purpose: tests Hadoop's shell-backed `Stat` parser and execution wrapper for Linux/FreeBSD output, symlink handling, sticky bits, locale environment, and real local symlink status.

Important APIs/types/functions: `Stat`, `parseExecResult`, `getFileStatusForTesting`, `getFileStatus`, `FileStatus`, `FileSystem.enableSymlinks`, `createSymlink`, and `Stat.isAvailable`.

Control flow/state/persistence: a static `Stat` is initialized for `/dummypath`. Inner `StatOutput` feeds canned command output for missing paths, directories, files, symlinks, and sticky directories and asserts parsed status flags. Runtime tests assume `stat` availability, expect missing path failure, assert `LANG=C`, create a local directory and symlink, and compare status of target vs link.

Dependencies/integration points: depends on OS-specific `stat` output formats, symlink support, local FS, and locale-controlled command execution.

Risks/test signals: catches parser drift across GNU/BSD outputs, symlink-vs-target confusion, sticky-bit parsing errors, and missing locale isolation that could localize command output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestStat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestSymlinkLocalFS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestSymlinkLocalFS.java

Purpose: abstract local-filesystem specialization of `SymlinkBaseTest`, adding local edge cases for dangling links, partially qualified paths, target qualification, and platform exclusions.

Important APIs/types/functions: `SymlinkBaseTest`, shared `wrapper`, `createSymlink`, `getFileLinkStatus`, `getLinkTarget`, `getFileStatus`, `rename`, `setWorkingDirectory`, `FileUtil.fullyDelete`, `UserGroupInformation`, and platform assumptions.

Control flow/state/persistence: overrides base tests to skip unsupported dangling/recursive/timestamp cases on Windows or Solaris. Local tests stat nonexistent partially qualified paths, create dangling links, verify `getFileStatus` fails while `getFileLinkStatus` succeeds with owner/group/symlink/path fields, create the target later to make the link work, and verify absolute partially qualified targets remain absolute after parent rename. It also rejects local links to non-local filesystems and treats link-to-dot `IllegalArgumentException` as acceptable.

Dependencies/integration points: depends on either FileContext or FileSystem wrappers supplied by subclasses, local symlink support, raw local stat behavior, user/group information, and platform-specific symlink semantics.

Risks/test signals: catches dangling-link stat regressions, URI/path qualification mistakes, security-sensitive cross-filesystem symlink creation, and inconsistent wrapper behavior between local FileContext and FileSystem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestSymlinkLocalFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestSymlinkLocalFSFileContext.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestSymlinkLocalFSFileContext.java

Purpose: runs the local symlink test suite through the `FileContext` API.

Important APIs/types/functions: `FileContext.getLocalFSFileContext`, `FileContextTestWrapper`, inherited `TestSymlinkLocalFS` tests, and `testRenameFileWithDestParentSymlink`.

Control flow/state/persistence: `@BeforeAll` installs a `FileContextTestWrapper` over local FileContext into the inherited static wrapper. It only overrides destination-parent symlink rename to skip on Windows before delegating to the base implementation.

Dependencies/integration points: validates symlink behavior through FileContext rather than FileSystem. Inherits all local symlink filesystem state and cleanup from the base hierarchy.

Risks/test signals: catches FileContext wrapper deviations in local symlink resolution, rename semantics, and platform assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestSymlinkLocalFSFileContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestSymlinkLocalFSFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestSymlinkLocalFSFileSystem.java

Purpose: runs the local symlink suite through the `FileSystem` API and documents local/ChecksumFS deviations from the generic symlink contract.

Important APIs/types/functions: `FileSystem.getLocal`, `FileSystemTestWrapper`, inherited `TestSymlinkLocalFS`, `Options.Rename`, `FileAlreadyExistsException`, `FileNotFoundException`, and disabled inherited tests.

Control flow/state/persistence: `@BeforeAll` installs a FileSystem wrapper. Several inherited tests are disabled because raw local mkdir/create behavior and ChecksumFileSystem append support differ from generic expectations. The class overrides symlink-to-self rename to assert failure both without and with overwrite; overwrite currently accepts either already-exists or not-found due to a known HADOOP-9819 issue.

Dependencies/integration points: validates local symlink behavior through FileSystem and the checksum wrapper stack, not FileContext.

Risks/test signals: protects documented deviations and catches rename-to-self regressions. Disabled tests are risk markers where local FS does not meet generic contract assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestSymlinkLocalFSFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestTrash.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestTrash.java

Purpose: large integration test suite for Hadoop trash behavior through `Trash`, `TrashPolicyDefault`, `FsShell`, local/test local filesystems, checkpointing, expunge, skipTrash, permissions, custom policies, and emptier threads.

Important APIs/types/functions: `Trash`, `TrashPolicy`, `TrashPolicyDefault.Emptier`, `FsShell`, `FS_TRASH_INTERVAL_KEY`, `FS_TRASH_CHECKPOINT_INTERVAL_KEY`, `FS_TRASH_CLEAN_TRASHROOT_ENABLE_KEY`, `moveToTrash`, `checkpoint`, `getEmptier`, `getCurrentTrashDir`, `Path.mergePaths`, test `TestLFS`, custom `TestTrashPolicy`, `AuditableTrashPolicy`, and `AuditableCheckpoints`.

Control flow/state/persistence: tests close all FS instances before each test and delete the temp trash root after each test. `trashShell` is the main scenario: toggles trash interval disabled/enabled, creates files/dirs, runs `-rm`, `-rmr`, `-expunge`, `-expunge -immediate`, validates current/checkpoint dirs, verifies deleting inside trash does not re-trash, blocks deletion of trash parent, tests `-skipTrash`, repeated deletion creates suffixed names, captures shell output suggesting `-skipTrash`, recognizes old checkpoint name formats, and immediate expunge removes all checkpoints/current. Other tests cover `-fs` expunge, non-default FS trash, pluggable policy selection, checkpoint interval normalization, moving empty dirs, trash restarts with a fake auditable policy, permission preservation, real emptier checkpoint/deletion timing, and cleanup of non-checkpoint directories under `.Trash` when enabled.

Dependencies/integration points: integrates shell command behavior, local FS, custom filesystem registration, configuration keys, permissions, time/checkpoint formatting, `SubjectInheritingThread`, and user trash root layout.

Risks/test signals: timing-sensitive emptier tests can be flaky under load, but they provide strong coverage of checkpoint lifecycle. The suite catches accidental permanent deletion, trash root recursion/deletion safety issues, skipTrash behavior, repeated-name collision handling, permission loss, custom policy instantiation, FS-specific expunge routing, interval misconfiguration, and thread leak risks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestTrash.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestTruncatedInputBug.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestTruncatedInputBug.java

Purpose: regression test for HADOOP-1489, where `BufferedInputStream.mark()` interaction with checksum reads could truncate local input.

Important APIs/types/functions: `FileSystem.getLocal`, `FSDataInputStream`, `DataOutputStream`, `seek`, `mark`, config key `io.file.buffer.size`, and `getFileStatus`.

Control flow/state/persistence: writes a zero-filled file of four IO buffers, opens it with the same buffer size, seeks near the end beyond initially buffered data, reads a few bytes, calls `mark(1)`, then reads to EOF and asserts the final position equals file size. The filesystem is closed in `finally`.

Dependencies/integration points: targets `ChecksumFileSystem`/local FS input buffering. Uses real temp local file data under `GenericTestUtils.getTestDir`.

Risks/test signals: catches a narrow but important read-after-seek/mark truncation regression. The note states fixed code makes `mark()` a no-op, so any future mark support must preserve full reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestTruncatedInputBug.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/audit/TestCommonAuditContext.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/audit/TestCommonAuditContext.java

Purpose: verifies global and thread-local behavior of `CommonAuditContext`, including default process/thread entries, dynamic values, entry point notation, and add/remove operations.

Important APIs/types/functions: `CommonAuditContext.currentAuditContext`, `setGlobalContextEntry`, `getGlobalContextEntry`, `getGlobalContextEntries`, `removeGlobalContextEntry`, `noteEntryPoint`, constants `PARAM_COMMAND`, `PARAM_PROCESS`, `PARAM_THREAD1`, and `PROCESS_ID`.

Control flow/state/persistence: tests set a global command entry and enumerate globals, verify process ID global entry, assert process is not present in the current local context, compare thread ID value to current thread id, reset context and install a supplier-backed dynamic key that reflects `AtomicBoolean` changes, set command entry point from `this` and null, and add/remove a local key.

Dependencies/integration points: uses AssertJ, `AbstractHadoopTestBase`, Java streams, and atomic supplier state. It guards audit metadata consumed by filesystem audit logs.

Risks/test signals: catches loss of dynamic evaluation, global/local context confusion, missing default process/thread identifiers, stale command entry point state, and broken enumeration/removal semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/audit/TestCommonAuditContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractBondedFSContract.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractBondedFSContract.java

Purpose: abstract filesystem contract that "bonds" tests to an externally configured filesystem URI for a given scheme.

Important APIs/types/functions: `AbstractFSContract`, `Configuration`, `FileSystem.get(URI, conf)`, `Path`, `FSNAME_OPTION` pattern `test.fs.%s`, `init`, `loadFilesystemName`, `getFilesystemConfKey`, `getTestFileSystem`, and `getTestPath`.

Control flow/state/persistence: `init` delegates to the base contract, reads a scheme-specific filesystem option, disables the contract when absent, otherwise parses the URI and initializes a `FileSystem`. Invalid URI or initialization arguments are wrapped as `IOException`. The test path defaults to `/test`; `toString` reports scheme and configured FS name.

Dependencies/integration points: used by concrete contract suites for remote/object filesystems that require explicit test endpoints. Integrates with `AbstractFSContract` option lookup and enabled/disabled test gating.

Risks/test signals: key risk is misconfiguration leading to skipped tests or accidental execution against the wrong filesystem. URI parsing and exception wrapping are important for clear test setup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractBondedFSContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractAppendTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractAppendTest.java

Purpose: generic contract tests for filesystems that advertise append support.

Important APIs/types/functions: `AbstractFSContractTestBase`, `SUPPORTS_APPEND`, `FSDataOutputStream`, `FileSystem.append`, `FileSystem.appendFile().build`, `ContractTestUtils.touch`, `createFile`, `dataset`, `readDataset`, `validateFileContent`, `rename`, and path capability `CommonPathCapabilities.FS_APPEND`.

Control flow/state/persistence: setup skips if append unsupported and prepares `test/target`. Tests append to empty files through classic and builder APIs, expect append to nonexistent/missing targets to fail through `handleExpectedException`, append data to existing files and validate concatenated bytes, rename a file while an append stream is open and verify bytes follow the open file handle to the renamed destination, and assert the filesystem declares append capability.

Dependencies/integration points: applies to many filesystem implementations through contract inheritance. Handles delayed create visibility for eventually consistent filesystems by sleeping before write when configured.

Risks/test signals: catches false append support declarations, append builder regressions, incorrect open-stream rename semantics, data concatenation errors, and wrong exception behavior for missing files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractAppendTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractBulkDeleteTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractBulkDeleteTest.java

Purpose: generic contract tests for the `BulkDelete` API, including wrapper/reflection paths used by libraries supporting multiple Hadoop versions.

Important APIs/types/functions: `AbstractFSContractTestBase`, `FileSystem.createBulkDelete`, `BulkDelete.bulkDelete`, `WrappedIO.bulkDelete_delete`, `DynamicWrappedIO.bulkDelete_pageSize`, `CommonPathCapabilities.BULK_DELETE`, `touch`, `intercept`, and helper `assertSuccessfulBulkDelete`.

Control flow/state/persistence: setup initializes FS, base path named after the test class, `DynamicWrappedIO`, page size, and directory creation. Tests validate page size, list-size preconditions, successful deletion through wrapped and direct FS APIs, capability declaration, rejection of paths outside base or non-absolute paths, success for nonexistent paths, undefined-but-nonfatal directory/file combinations, failure entries for non-empty parent directories, success for empty directories and empty lists, duplicate path handling, deep descendant deletion, and child path batches. Tests skip cases needing more paths than the implementation page size.

Dependencies/integration points: contract spans default and store-specific bulk delete implementations. Reflection wrappers validate compatibility behavior for applications using `WrappedIO` instead of direct compile-time APIs.

Risks/test signals: catches security boundary errors around base path validation, page-size enforcement mistakes, capability mismatches, incorrect treatment of directories/nonexistent paths, duplicate path handling, and divergence between direct and wrapped API behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractBulkDeleteTest.java -->
