# Research Group subset-b-007394

This grouped report covers Hadoop `viewfs` tests and HA test fixtures. Each section preserves the exact source path and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestNestedMountPoint.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestNestedMountPoint.java

Purpose: unit-tests nested mount point support in `InodeTree`, especially longest-prefix matching, internal directory handling, fallback links, and `resolveLastComponent` behavior. The fixture creates a `Configuration`, enables nested mount points with `ConfigUtil.setIsNestedMountPointSupported`, adds six overlapping links such as `/a/b`, `/a/b/c/d/e`, `/b/c/d/e/f`, and a fallback target, then constructs an anonymous `InodeTree<TestNestMountPointFileSystem>`.

Important APIs and types: `InodeTree.resolve(String, boolean)`, `InodeTree.ResolveResult`, `InodeTree.ResultKind`, `ConfigUtil.addLink`, `ConfigUtil.addLinkFallback`, `FsConstants.VIEWFS_SCHEME`, `Path`, and local stub target filesystem classes that expose only `URI getUri()`. The anonymous tree overrides target filesystem creation for external links and internal dirs.

Control flow: each test resolves a path and asserts `kind`, `resolvedPath`, `remainingPath`, target URI/type, and `isLastInternalDirLink()`. The tests compare exact behavior when the last component should be consumed versus left unresolved. State is in-memory only and reset per test; there is no persistent filesystem IO.

Dependencies and integration: this is a direct regression suite for `InodeTree`, not `ViewFileSystem`. It validates mount-table semantics consumed by both `ViewFs` and `ViewFileSystem`.

Risks and test signals: high-value edge cases include nested links that shadow ancestors, fallback suppression when `resolveLastComponent` is false, root resolution, and mount point enumeration count. A regression usually appears as incorrect resolved prefix, wrong remaining path, fallback activation at the wrong time, or internal dirs returned as external links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestNestedMountPoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestRegexMountPoint.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestRegexMountPoint.java

Purpose: tests regex-based mount points, destination variable extraction/substitution, and interceptor integration. The fixture builds an `InodeTree` with a normal `/mnt` link and anonymous target filesystem factory, then constructs `RegexMountPoint` instances directly.

Important APIs and types: `RegexMountPoint.initialize()`, `RegexMountPoint.getVarInDestPathMap()`, `RegexMountPoint.resolve()`, `RegexMountPointResolvedDstPathReplaceInterceptor`, `ConfigUtil.addLink`, and `InodeTree.ResolveResult`. The inner `TestRegexMountPointFileSystem` records the URI passed by regex resolution.

Control flow: `testGetVarListInString` parses `$0`, `$1`, `${1}`, and `${2}` references and asserts grouping by capture index. `testResolve` matches `^/user/(?<username>\\w+)`, maps `$username` into `/namenode1/testResolve/...`, and verifies the remaining suffix. `testResolveWithInterceptor` serializes a replace interceptor and confirms underscores in the resolved destination are rewritten while the source/remaining path is not.

State and persistence: all state is in test-local configuration and `RegexMountPoint` fields; no real filesystem mutation occurs.

Dependencies and integration: validates the regex mount feature used by `InodeTree` resolution and viewfs mount-table config. It depends on Java regex named groups and Hadoop path semantics.

Risks and test signals: watch for capture variable parsing ambiguity, incorrect `resolvedPath` length, URI construction that drops leading slashes, and interceptor application to the wrong path component.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestRegexMountPoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestRegexMountPointInterceptorFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestRegexMountPointInterceptorFactory.java

Purpose: verifies factory parsing for regex mount point interceptors. The tests focus on the serialized string format and ensure valid strings produce the correct interceptor implementation while malformed type names return `null`.

Important APIs and types: `RegexMountPointInterceptorFactory.create`, `RegexMountPointInterceptor`, `RegexMountPointResolvedDstPathReplaceInterceptor`, `RegexMountPointInterceptorType.REPLACE_RESOLVED_DST_PATH`, and `RegexMountPoint.INTERCEPTOR_INTERNAL_SEP`.

Control flow: `testCreateNormalCase` builds `replaceresolvedpath:<src>:<replace>` using the canonical config name and separator, calls the factory, and asserts the returned object is a replace interceptor. `testCreateBadCase` corrupts the config-name prefix and asserts no interceptor is built.

State and persistence: no persistent state; all inputs are strings. The factory is expected to parse without side effects.

Dependencies and integration: this protects regex mount configuration loading, where serialized interceptors are embedded in mount settings and must be instantiated dynamically.

Risks and test signals: failures indicate either an incompatible serialized config format, too-lenient parsing that accepts garbage, or too-strict parsing that rejects valid interceptor definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestRegexMountPointInterceptorFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestRegexMountPointResolvedDstPathReplaceInterceptor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestRegexMountPointResolvedDstPathReplaceInterceptor.java

Purpose: tests serialization, deserialization, initialization, and path-rewrite behavior for `RegexMountPointResolvedDstPathReplaceInterceptor`.

Important APIs and types: `RegexMountPointResolvedDstPathReplaceInterceptor.deserializeFromString`, constructor, `serializeToString`, `initialize`, `getSrcRegexString`, `getReplaceString`, `getSrcRegexPattern`, `interceptSource`, and `interceptResolvedDestPathStr`.

Control flow: a helper builds serialized strings with `REPLACE_RESOLVED_DST_PATH.getConfigName()` and `RegexMountPoint.INTERCEPTOR_INTERNAL_SEP`. Normal deserialization verifies string fields and delayed regex compilation. Bad deserialization appends an extra field and expects `null`. Serialization verifies round-trip format. Source interception is asserted to be identity, while resolved destination interception replaces matching regex content after initialization.

State and persistence: the only state is the configured source regex, replacement string, and lazily compiled `Pattern`; no external IO.

Dependencies and integration: this interceptor is consumed by `RegexMountPoint` after regex destination resolution and before target filesystem construction.

Risks and test signals: important regressions include accepting malformed config, compiling regex too early or not at all, rewriting source paths instead of destination paths, and using literal replacement where regex replacement is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestRegexMountPointResolvedDstPathReplaceInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFSOverloadSchemeCentralMountTableConfig.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFSOverloadSchemeCentralMountTableConfig.java

Purpose: extends overload-scheme local filesystem tests to verify centralized mount-table config files stored under `Constants.CONFIG_VIEWFS_MOUNTTABLE_PATH`. It specifically checks that the newest versioned file is used and an older invalid mount-table XML file is ignored.

Important APIs and types: `TestViewFileSystemOverloadSchemeLocalFileSystem`, `ViewFsTestSetup.addMountLinksToFile`, `Constants.CONFIG_VIEWFS_MOUNTTABLE_PATH`, `Path`, `Configuration`, and Java `FileWriter`.

Control flow: `setUp` calls the parent setup, creates `mount-table.1.xml` and `mount-table.2.xml` in the test root, and points config at that directory. The override of `addMountLinks` writes malformed XML into the old file, then writes real mount links to the latest file using the shared file serializer. Parent tests then exercise create, delete, merge slash, and conflict behavior through the overload scheme.

State and persistence: this test persists temporary mount-table XML files in the local test root and removes them through the parent teardown.

Dependencies and integration: integrates `ViewFileSystemOverloadScheme`, central mount-table discovery, local filesystem access, and helper serialization format.

Risks and test signals: a failure usually means version ordering is wrong, stale/bad files are parsed, central mount-table path handling broke, or file-backed config no longer matches in-memory config semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFSOverloadSchemeCentralMountTableConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemDelegation.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemDelegation.java

Purpose: verifies selected `ViewFileSystem` calls delegate to the correct child `FileSystem` after path translation. It includes sanity checks for fake scheme registration and comprehensive ACL delegation checks using mocked child filesystems.

Important APIs and types: `ViewFileSystemTestSetup.createConfig`, `FileSystem.get(FsConstants.VIEWFS_URI, conf)`, `ConfigUtil.addLink`, `TestChRootedFileSystem.getChildFileSystem`, `MockFileSystem`, ACL methods such as `modifyAclEntries`, `removeAcl`, `setAcl`, and `getAclStatus`, plus `FakeFileSystem` extending `LocalFileSystem`.

Control flow: static setup registers `fs1` and `fs2` schemes, mounts them under `/mounts/<scheme>`, opens a viewfs instance, and retrieves children. `testAclMethods` creates two mock mounts, performs each ACL operation through viewfs paths, and verifies the underlying mocks receive paths with the mount prefix stripped.

State and persistence: scheme bindings and mount links live in `Configuration`; `FakeFileSystem` records its URI and checksum flag.

Dependencies and integration: exercises `ViewFileSystem` delegation, chroot path mapping, ACL API coverage, and filesystem implementation lookup by scheme.

Risks and test signals: path translation errors can silently apply ACLs to the wrong target. Missing delegation will show as Mockito verification failures, while scheme setup regressions show as wrong child URI identity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemDelegation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemDelegationTokenSupport.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemDelegationTokenSupport.java

Purpose: tests `ViewFileSystem` delegation-token behavior, canonical service naming, child filesystem discovery, and duplicate-token suppression when several mount links reference the same child filesystem.

Important APIs and types: `FileSystem.addDelegationTokens`, `getCanonicalServiceName`, `getChildFileSystems`, `Credentials`, `Token`, `Text`, `ConfigUtil.addLink`, `FsConstants.VIEWFS_URI`, and a `FakeFileSystem` extending `RawLocalFileSystem`.

Control flow: static setup registers two fake schemes and mounts each twice. The canonical service name tests cover default and named mount tables and assert viewfs returns `null`. `testGetChildFileSystems` asserts duplicate mount links collapse to two child filesystems. `testAddDelegationTokens` first fetches tokens directly from children, then through viewfs, and confirms existing credentials prevent refetch.

State and persistence: fake filesystems keep only URI state and synthesize a token whose service is URI plus object hash. Credentials are in-memory.

Dependencies and integration: protects token aggregation for security flows where clients obtain tokens from viewfs but services use tokens from mounted filesystems.

Risks and test signals: regressions include duplicate tokens per mount, missing child tokens, non-null canonical service names for viewfs, or failure to honor existing credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemDelegationTokenSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLocalFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLocalFileSystem.java

Purpose: concrete `ViewFileSystemBaseTest` subclass that runs the generic `FileSystem` viewfs behavior suite against the local filesystem and adds NFly-specific tests.

Important APIs and types: `ViewFileSystemBaseTest`, `FileSystem.getLocal`, `ConfigUtil.addLinkNfly`, `FileSystem.get(URI.create("viewfs:///"), conf)`, `FSDataOutputStream`, `FSDataInputStream`, `FileStatus`, and `TRASH_PREFIX`.

Control flow: setup assigns `fsTarget` to local FS before the base class creates mount points and `fsView`. Teardown deletes the local test root. `testNflyWriteSimple` mounts `/nflyroot` to two local target URIs, writes one file through viewfs, lists the NFly root, and verifies both replicas contain the same UTF string. `testNflyInvalidMinReplication` configures a min replication higher than target count and expects an `IOException` mentioning minimum replication.

State and persistence: creates and deletes local test directories/files. Trash root behavior is overridden for local fallback semantics.

Dependencies and integration: covers the full base `ViewFileSystem` suite plus NFly link creation and validation.

Risks and test signals: likely regressions include local cleanup leaks, NFly replication misconfiguration not rejected, write fanout failure, or local fallback trash root mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLocalFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemOverloadSchemeLocalFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemOverloadSchemeLocalFileSystem.java

Purpose: tests `ViewFileSystemOverloadScheme` when the normal `file` scheme is overloaded to route through viewfs while delegating actual storage to `LocalFileSystem`.

Important APIs and types: `ViewFileSystemOverloadScheme`, `FsConstants.FS_VIEWFS_OVERLOAD_SCHEME_TARGET_FS_IMPL_PATTERN`, `ViewFsTestSetup.addMountLinksToConf`, `ConfigUtil` link constants, `FileSystemTestHelper`, `FSDataOutputStream`, `FSDataInputStream`, and `LocalFileSystem`.

Control flow: setup configures `fs.file.impl` to the overload class, configures the target implementation pattern to `LocalFileSystem`, initializes a local target FS, and creates a clean root. Tests add mount links, open `FileSystem.get(file:/// or file://mt/)`, then verify write/read, create/delete, root-level `linkMergeSlash`, and rejection when merge-slash is combined with other mount links.

State and persistence: local filesystem test root is created, mutated, and deleted in teardown.

Dependencies and integration: protects compatibility for deployments that use existing scheme URIs while internally applying viewfs mount tables.

Risks and test signals: high-risk behavior is scheme recursion, wrong target implementation lookup, merge-slash allowing ambiguous mounts, and authority-specific mount-table loading failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemOverloadSchemeLocalFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithAuthorityLocalFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithAuthorityLocalFileSystem.java

Purpose: concrete `ViewFileSystemBaseTest` subclass that uses `viewfs://default/` so the URI authority selects the mount table. It verifies the same local-FS-backed behavior as the base class while overriding URI qualification expectations.

Important APIs and types: `ViewFileSystemBaseTest`, `FsConstants.VIEWFS_SCHEME`, `FileSystem.get(URI, conf)`, `Path.makeQualified`, `TRASH_PREFIX`, and `UserGroupInformation`.

Control flow: setup initializes local `fsTarget`, invokes base setup to create mount links and a default `fsView`, then replaces `fsView` with one opened against `viewfs://default/`. `testBasicPaths` asserts URI, working directory, home directory, and path qualification use the authority-bearing scheme. Teardown removes the local test root.

State and persistence: inherits local filesystem mutations from base tests and overrides fallback trash-root calculation for local FS.

Dependencies and integration: covers authority-based mount-table resolution for `ViewFileSystem`, distinct from authorityless `viewfs:///`.

Risks and test signals: regressions surface as wrong URI authority, mount-table lookup using the default table instead of authority, incorrect home/working directory qualification, or trash root differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithAuthorityLocalFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsConfig.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsConfig.java

Purpose: verifies invalid non-nested mount configuration is rejected. It protects the rule that, when nested mount points are disabled, a mount cannot be placed beneath an existing mount path.

Important APIs and types: `ConfigUtil.setIsNestedMountPointSupported`, `ConfigUtil.addLink`, `InodeTree`, `FileAlreadyExistsException`, and anonymous implementations of the `InodeTree` filesystem factory methods.

Control flow: the single test disables nested mount points, adds `/internalDir/linkToDir2` and a child `/internalDir/linkToDir2/linkToDir3`, then constructs an `InodeTree`. The constructor is expected to throw `FileAlreadyExistsException`.

State and persistence: all config is in-memory. The dummy `Foo` type and target factory methods are placeholders because tree construction should fail before real target use.

Dependencies and integration: this is a config-level guard for both `ViewFs` and `ViewFileSystem`, since they rely on `InodeTree` mount-table validation.

Risks and test signals: if this test fails by not throwing, ambiguous nested mount tables may be accepted when compatibility mode says they should not. If it throws a different exception, error classification for callers changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsLocalFs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsLocalFs.java

Purpose: concrete `ViewFsBaseTest` subclass that runs the generic `FileContext` viewfs suite against the local filesystem.

Important APIs and types: `ViewFsBaseTest`, `FileContext.getLocalFSFileContext`, JUnit `BeforeEach` and `AfterEach`.

Control flow: setup assigns `fcTarget` to the local FS `FileContext` and then delegates to the base setup, which creates target directories, mount links, and the `fcView` viewfs context. Teardown simply delegates to the base class, which deletes the test root.

State and persistence: all file operations are inherited from the base test and occur under the local test root managed by `FileContextTestHelper`.

Dependencies and integration: this is the local concrete runner for `ViewFsBaseTest`, validating `FileContext` APIs rather than `FileSystem` APIs. It covers create, mkdir, delete, rename, ACL/xattr failures on internal dirs, block locations, link status, checksums, server defaults, and optimized list delegation inherited from the base.

Risks and test signals: failures generally originate in shared `ViewFsBaseTest` logic but can also indicate local `FileContext` initialization or cleanup behavior changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsLocalFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsOverloadSchemeListStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsOverloadSchemeListStatus.java

Purpose: tests `listStatus` behavior under `ViewFileSystemOverloadScheme`, including permission/type propagation and fallback behavior when no explicit mount links are configured.

Important APIs and types: `ViewFileSystemOverloadScheme`, `FileSystem.get`, `ConfigUtil.addLink`, `FsPermission`, `FileStatus`, `FileUtil`, `GenericTestUtils.getTestDir`, `LocalFileSystem`, and `FsConstants.FS_VIEWFS_OVERLOAD_SCHEME_TARGET_FS_IMPL_PATTERN`.

Control flow: setup overloads the `file` scheme and creates a clean test directory. `testListStatusACL` creates a file and directory, mounts them at `/file` and `/dir`, verifies listed permissions match local FS, changes local permissions, and verifies updated status including `isDirectory`. `testViewFSOverloadSchemeWithoutAnyMountLinks` opens a `file:` URI with no mount links, asserts no mount points, creates through fallback, and checks the raw local FS view is rooted correctly.

State and persistence: uses temporary local files and directories and cleans them after each/all tests.

Dependencies and integration: validates overload scheme status mapping, mount-link-as-status behavior, fallback chroot semantics, and raw target FS lookup.

Risks and test signals: likely regressions are stale permissions, wrong directory flags, fallback rooted at initialization path instead of raw root, or hangs during fallback listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsOverloadSchemeListStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsTrash.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsTrash.java

Purpose: tests trash behavior for `ViewFileSystem`, including shell trash integration and localized trash placement inside mount points.

Important APIs and types: `ViewFileSystemTestSetup`, `TestTrash.trashShell`, `Trash.moveToAppropriateTrash`, `Trash`, `ConfigUtil.addLink`, `CONFIG_VIEWFS_TRASH_FORCE_INSIDE_MOUNT_POINT`, `FS_TRASH_INTERVAL_KEY`, `ContractTestUtils`, and `TestTrash.TestLFS`.

Control flow: setup creates a local target filesystem using `TestTrash.TestLFS`, configures a viewfs mount table, sets default FS to viewfs, and registers the same local implementation so home directory behavior is deterministic. `testTrash` delegates to Hadoop's shared trash shell test. `testLocalizedTrashInMoveToAppropriateTrash` first verifies default trash goes to target FS trash based on resolved path, then enables localized trash and verifies the file appears under `viewfs:/data/.Trash/<user>/Current`.

State and persistence: creates local files and trash directories and removes target test root plus `.Trash/Current` in teardown.

Dependencies and integration: connects viewfs path resolution with common `Trash` APIs and config flags.

Risks and test signals: regressions include trash paths built from unresolved viewfs paths when target trash is expected, localized trash ignored, or incorrect local home directory due to the filesystem implementation setting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsTrash.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsURIs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsURIs.java

Purpose: regression test for viewfs initialization when a target URI has an authority but an empty path, such as `file://foo`.

Important APIs and types: `ConfigUtil.addLink`, `FileContext.getFileContext`, `FsConstants.VIEWFS_URI`, `Configuration`, and `URI`.

Control flow: the test adds `/user -> file://foo` to an in-memory config and opens a `FileContext` for `viewfs:///`. The absence of an exception is the assertion.

State and persistence: no filesystem mutation. The test only validates URI parsing and mount-table construction.

Dependencies and integration: protects `ViewFs`/`InodeTree` URI normalization for authority-only targets. That matters for filesystems where authority is meaningful and the root path may be omitted in configuration.

Risks and test signals: if this fails, viewfs may reject legal target URIs or require a slash path where Hadoop callers historically did not. Because the test has no explicit assertions, any thrown exception is the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsURIs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsWithAuthorityLocalFs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsWithAuthorityLocalFs.java

Purpose: concrete `ViewFsBaseTest` subclass that uses an authority-bearing URI, `viewfs://mycluster/`, for `FileContext` tests. It validates authority-selected mount table behavior for `ViewFs`.

Important APIs and types: `ViewFsBaseTest`, `FileContext.getFileContext(URI, conf)`, `FsConstants.VIEWFS_SCHEME`, `MOUNT_TABLE_NAME`, and `Path.makeQualified`.

Control flow: setup assigns local `fcTarget`, invokes base setup to populate a config whose default mount table name is `mycluster`, builds `schemeWithAuthority`, and replaces `fcView` with a context opened on that URI. `testBasicPaths` asserts default filesystem URI, working directory, home directory, and qualification all include the authority.

State and persistence: inherits base test local filesystem setup and cleanup. No extra persistent state beyond the viewfs context.

Dependencies and integration: tests `FileContext`/`AbstractFileSystem` authority routing rather than `FileSystem` routing.

Risks and test signals: wrong authority handling may pass authorityless tests but fail here through URI mismatch, missing mount table entries, or incorrect working/home directory qualification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsWithAuthorityLocalFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewfsFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewfsFileStatus.java

Purpose: tests `ViewFsFileStatus`/`FileStatus` behavior for viewfs, covering serialization, erasure-coding flag retention, ACL/permission propagation for mount links, and checksum delegation path translation.

Important APIs and types: `FileSystem.get(FsConstants.VIEWFS_URI, conf)`, `ConfigUtil.addLink`, `FileStatus.write/readFields`, `DataOutputBuffer`, `DataInputBuffer`, `ContractTestUtils.assertNotErasureCoded`, `FsPermission`, Mockito, `InodeTree.ResolveResult`, and `ViewFileSystem.getFileChecksum`.

Control flow: `testFileStatusSerialziation` creates a local file under a mounted directory, reads status through viewfs, serializes/deserializes it, and asserts length and erasure-coding state. `testListStatusACL` mounts a file and directory, disables mount-links-as-symlinks, verifies permissions and type flags before/after local permission changes. `testGetFileChecksum` injects a mocked `InodeTree` result and verifies checksum is called with `remainingPath`, not the original viewfs path.

State and persistence: uses a temporary local test directory cleaned after each/all tests.

Dependencies and integration: protects MapReduce serialization compatibility, viewfs status overlay behavior, and checksum delegation.

Risks and test signals: regressions include lost erasure-coding fields, stale permission mapping, mount links reported with wrong type, and checksum calls against unresolved viewfs paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewfsFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFileSystemBaseTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFileSystemBaseTest.java

Purpose: abstract `FileSystem` API test suite for `ViewFileSystem`. Concrete subclasses provide a target filesystem, usually local or HDFS, while this base class validates common mount-table behavior.

Important APIs and types: `ViewFileSystem`, `ViewFileSystem.MountPoint`, `ConfigUtil.addLink`, `ConfigUtil.addLinkFallback`, `FileSystemTestHelper`, `ContractTestUtils`, `Credentials`, `Token`, `BlockLocation`, `AclStatus`, `FsStatus`, `Trash`, `ViewFileSystemUtil`, `ViewFileSystem.InnerCache`, `FsGetter`, `NotInMountpointException`, and `AccessControlException`.

Control flow: setup creates a target root with `user`, `data`, `dir2`, `dir3`, and `aFile`, then mounts `/targetRoot`, `/user`, `/user2`, `/data`, nested internal dirs, a dangling link, and a file link. Tests cover mount point enumeration, delegation token aggregation, URI/home/working directory basics, operations through mount links, located and non-located listings, block locations, file status, resolvePath, read-only internal directory failures, ACL/xattr/snapshot/storage policy behavior, link-slash config rejection, trash roots, current/all-user trash discovery, filesystem status utilities, owner reporting under `doAs`, used-space delegation, symlink target resolution, child filesystem cache closure/leak behavior, delete-on-exit, content summary across internal dirs and local-file links, lazy target FS initialization, checksum-triggered initialization, and invalid URI handling.

State and persistence: target filesystem state is created per test and deleted in teardown. Some tests create new viewfs instances with modified config and rely on Hadoop `FileSystem.CACHE` counts.

Dependencies and integration: this is the central compatibility suite for `ViewFileSystem`, binding `InodeTree`, `ConfigUtil`, mount-table config, target filesystem delegation, trash, security, cache, and status APIs.

Risks and test signals: because it is broad, failures pinpoint regressions in path resolution, internal mount table immutability, rename strategy semantics, nested mount support, resource cleanup, or delegation to child filesystems. Cache-related tests are sensitive to global `FileSystem.CACHE`; trash and symlink tests are target-FS capability dependent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFileSystemBaseTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFileSystemTestSetup.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFileSystemTestSetup.java

Purpose: shared helper for setting up `ViewFileSystem` tests against a target `FileSystem`. It creates common mount links for test root, home directory, and working directory so standard filesystem tests work through viewfs.

Important APIs and types: `FileSystem`, `FileSystemTestHelper`, `FsConstants.VIEWFS_URI`, `ConfigUtil.addLink`, `ConfigUtil.setHomeDirConf`, `Shell.WINDOWS`, `Path`, `URI`, and `ViewFileSystem`.

Control flow: `setupForViewFileSystem` deletes/recreates the target test root, links the first component of the test dir, sets up home dir links, links the first component of the working directory, opens viewfs, and sets its working directory. `tearDown` deletes the target test root. `createConfig` registers `fs.viewfs.impl` and optionally disables cache. `setUpHomeDir` handles root-level and multi-component home dirs. `linkUpFirstComponents` special-cases Windows drive paths.

State and persistence: mutates target filesystem directories and in-memory `Configuration`; no standalone persistent metadata.

Dependencies and integration: used by many `ViewFileSystem` tests, including trash and delegation-token tests, to produce a predictable mount table.

Risks and test signals: incorrect first-component extraction can break relative paths, Windows paths, or home directory qualification. Cache flag changes affect test isolation and global `FileSystem.CACHE` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFileSystemTestSetup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFsBaseTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFsBaseTest.java

Purpose: abstract `FileContext`/`AbstractFileSystem` API test suite for `ViewFs`. It parallels `ViewFileSystemBaseTest` but exercises the newer `FileContext` surface.

Important APIs and types: `ViewFs`, `ViewFs.MountPoint`, `FileContext`, `AbstractFileSystem`, `ChRootedFs`, `FileContextTestHelper`, `ConfigUtil`, `FsServerDefaults`, `BlockLocation`, `AclStatus`, `CreateFlag`, `Token`, Mockito, `LambdaTestUtils`, and `NotInMountpointException`.

Control flow: setup creates local target directories/files and configures a mount table named `mycluster` with `/targetRoot`, `/user`, `/user2`, `/data`, internal links, a dangling link, and a file link. Tests cover mount enumeration, delegation tokens, path qualification, create/delete/mkdir/rename through mount links, rename strategy variants, block locations, listing internal dirs, file status and file link status, checksum path delegation, symlink targets, resolvePath, read-only internal directory modifications, ACL/xattr/snapshot failures, internal-dir ownership, server defaults for mount and internal paths, optimized `listLocatedStatus` and `listStatusIterator` delegation to the underlying `AbstractFileSystem`, and no-primary-group error handling.

State and persistence: target FS state is created per test through `FileContext` and removed in teardown. `MockFs` keeps a static mock cache keyed by URI authority for delegation verification.

Dependencies and integration: central coverage for `ViewFs`, `ChRootedFs`, `InodeTree`, `FileContext`, and `AbstractFileSystem` integration.

Risks and test signals: failures usually expose mismatches between `FileSystem` and `FileContext` behavior, incorrect `remainingPath` delegation, internal-dir mutability, server-default propagation, or optimized listing fallback to less efficient APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFsBaseTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFsTestSetup.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFsTestSetup.java

Purpose: shared setup and mount-link serialization helper for `ViewFs`/`FileContext` tests and overload-scheme central mount-table tests.

Important APIs and types: `FileContext`, `FileContextTestHelper`, `FsConstants.VIEWFS_URI`, `ConfigUtil`, `ViewFileSystemOverloadScheme.ChildFsGetter`, `FSDataOutputStream`, `Constants.CONFIG_VIEWFS_*`, `Shell.WINDOWS`, and `Path`.

Control flow: `setupForViewFsLocalFs` prepares a local target root, links first components for test dir, home dir, and working dir, opens `FileContext` for `viewfs:///`, and sets the working directory. `tearDownForViewFsLocalFs` deletes the target test root. `setUpHomeDir` and `linkUpFirstComponents` mirror the `FileSystem` setup helper. `addMountLinksToFile` writes Hadoop XML properties to a given mount table config file and supports normal links, fallback, merge slash, and NFly links. `addMountLinksToConf` writes equivalent links directly to `Configuration`.

State and persistence: writes temporary mount-table XML when requested and mutates local test directories.

Dependencies and integration: important bridge between in-memory mount config and central mount-table files used by overload scheme tests.

Risks and test signals: serialization bugs can make file-backed and config-backed mount tables diverge; NFly source parsing is strict; wrong scheme selection in `ChildFsGetter` can write config to the wrong filesystem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFsTestSetup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ActiveStandbyElectorTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ActiveStandbyElectorTestUtil.java

Purpose: polling utility for HA elector tests. It waits for ZooKeeper lock data or elector state transitions while surfacing background test-thread exceptions.

Important APIs and types: `MultithreadedTestUtil.TestContext`, `ZooKeeperServer`, `ActiveStandbyElector`, `ActiveStandbyElector.State`, `ActiveStandbyElector.LOCK_FILENAME`, `Stat`, `NoNodeException`, `Time.now`, and `StringUtils.byteToHexString`.

Control flow: `waitForActiveLockData` loops until the active lock znode data matches expected bytes, or until the node is absent when expected data is `null`. It calls `ctx.checkException()` if a context is supplied, logs current data or missing node every 500 ms, and sleeps 50 ms between checks. `waitForElectorState` loops until `elector.getStateForTests()` equals the expected state, also checking context exceptions and sleeping.

State and persistence: reads ZooKeeper in-memory database state through the test server; it does not mutate state.

Dependencies and integration: used by failover/election tests to coordinate asynchronous ZooKeeper and elector behavior.

Risks and test signals: loops have no internal timeout, so callers must provide external timeout/context handling. Incorrect znode paths or state visibility can cause hangs; context checks are the main safety mechanism.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ActiveStandbyElectorTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ClientBaseWithFixes.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ClientBaseWithFixes.java

Purpose: Hadoop-local copy of ZooKeeper `ClientBase` with JMX verification removed to avoid spurious test failures. It provides per-test ZooKeeper server lifecycle, client creation, and wait helpers for HA tests.

Important APIs and types: `ZKTestCase`, `TestableZooKeeper`, `ZooKeeper`, `Watcher`, `CountDownLatch`, `ServerCnxnFactory`, `ZooKeeperServer`, `ZKDatabase`, `FileTxnLog`, `ServerSocketUtil`, `GenericTestUtils`, and JUnit `BeforeEach`/`AfterEach`.

Control flow: static initialization enables ZooKeeper four-letter commands. `setUp` creates the base test dir, sets low log preallocation, initializes client tracking, creates a temp data dir, and starts a server. `createClient` variants create a `TestableZooKeeper`, wait for a `CountdownWatcher` to connect, and track clients for teardown. `send4LetterWord`, `waitForServerUp`, and `waitForServerDown` use socket diagnostics. `createNewServerInstance` starts a `ZooKeeperServer`; `shutdownServerInstance` shuts it down and closes the database. `tearDown` closes clients, stops the server, recursively deletes temp dirs, and resets factory state.

State and persistence: creates temporary ZooKeeper data/log directories under `GenericTestUtils.getTestDir()`, tracks live clients in `allClients`, and uses selected localhost ports.

Dependencies and integration: foundational fixture for HA tests that need embedded ZooKeeper without upstream JMX checks.

Risks and test signals: resource leaks, stuck ports, client list misuse before setup, and unbounded waits around server up/down are primary risks. Four-letter command enablement is test-only and security-sensitive outside tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ClientBaseWithFixes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/DummyHAService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/DummyHAService.java

Purpose: test-only `HAServiceTarget` implementation used by failover and health-monitor tests. It can operate as an in-process Mockito-spied protocol implementation or through protobuf RPC, and exposes knobs for injected failures.

Important APIs and types: `HAServiceTarget`, `HAServiceProtocol`, `ZKFCProtocol`, `NodeFencer`, `FenceMethod`, `HAServiceState`, `HAServiceStatus`, `StateChangeRequestInfo`, `ServiceFailedException`, `HealthCheckFailedException`, `RPC.Builder`, `ProtobufRpcEngine2`, `HAServiceProtocolServerSideTranslatorPB`, and `DummySharedResource`.

Control flow: constructors set initial state, optionally start protobuf RPC servers, create protocol spies, create a spy `NodeFencer`, and register the instance in a static list. `getProxy` and `getHealthMonitorProxy` return spies or refresh RPC proxies. `MockHAProtocolImpl` implements health checks, transitions to active/standby/observer, service status, and simulated unreachable behavior. Active transition increments `activeTransitionCount`, may take a shared resource, and changes state. Standby transition may release the shared resource. `DummyFencer.tryFence` increments `fenceCount`, optionally fails, and releases the shared resource.

State and persistence: volatile HA state, failure flags, counters, static instance registry, optional RPC servers, and shared-resource ownership are all test state.

Dependencies and integration: central test double for HA admin, failover controller, fencing, health monitor, observer support, and protobuf RPC paths.

Risks and test signals: important risks are static instance leakage across tests, RPC server lifecycle not explicitly closed, failure flags masking real behavior, and `getHealthMonitorProxy` assigning to `proxy` rather than `healthMonitorProxy`. Shared resource assertions catch split-brain style active ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/DummyHAService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/DummySharedResource.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/DummySharedResource.java

Purpose: small shared-resource simulator for HA failover tests. It models a resource such as a shared edit log that must be owned by at most one active service.

Important APIs and types: `DummyHAService`, synchronized `take`, `release`, and `assertNoViolations`, plus JUnit `assertEquals`.

Control flow: `take` accepts ownership when the resource is free or already held by the same service; otherwise it increments `violations` and throws `IllegalStateException`. `release` clears ownership only when the releasing service is the current holder. `assertNoViolations` asserts no double-owner attempt occurred.

State and persistence: in-memory `holder` and violation counter. All methods are synchronized to make ownership checks safe during multi-threaded failover tests.

Dependencies and integration: used by `DummyHAService` transitions and `DummyFencer` to validate active/standby/fencing flows. It is not a standalone test, but a correctness oracle for higher-level HA tests.

Risks and test signals: if callers forget to release during standby/fence paths, later `take` calls fail. Because repeated `take` by the same holder is allowed, it catches split-brain between different services rather than duplicate transition calls on one service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/DummySharedResource.java -->
