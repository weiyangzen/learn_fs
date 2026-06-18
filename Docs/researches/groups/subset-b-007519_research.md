# subset-b-007519 Hadoop HDFS ViewFS and admin-state test research

This grouped report covers the requested Hadoop HDFS test sources. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/permission/TestStickyBit.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/permission/TestStickyBit.java

## Purpose

`TestStickyBit` verifies HDFS sticky-bit behavior under normal permission checks and ACL-enabled paths. It uses a `MiniDFSCluster` with permissions and NameNode ACLs enabled, then exercises Unix-like sticky semantics: non-owners may append to writable files, but may not delete or rename another user's child under a sticky directory. It also checks sticky-bit propagation, reset semantics, recursive delete enforcement, and persistence across NameNode restart.

## Important APIs, types, and functions

The class centers on `MiniDFSCluster`, `DistributedFileSystem`, `FileSystem`, `FsPermission`, `AclEntry`, `UserGroupInformation`, `AccessControlException`, and `FSExceptionMessages.PERMISSION_DENIED_BY_STICKY_BIT`. Key helpers are `initCluster(boolean)`, `confirmCanAppend`, `confirmDeletingFiles`, `confirmStickyBitDoesntPropagate`, `confirmSettingAndGetting`, `testMovingFiles(boolean)`, `writeFile`, and `applyAcl`.

## Control flow, state, and persistence

`@BeforeAll` creates a four-DN cluster and user-scoped file systems for `theDoctor` and `rose`; `@BeforeEach` cleans root children. The main behavior tests create paths, set octal permissions such as `01777`, then perform operations as owner and non-owner users. Persistence tests set permissions, shut down the cluster, restart without formatting, and verify sticky bits survive edit/fsimage replay while absent bits remain absent. Recursive-delete tests verify sticky checks are enforced while walking children.

## Dependencies and integration points

The test integrates HDFS permission enforcement, `DFS_PERMISSIONS_ENABLED`, `DFS_NAMENODE_ACLS_ENABLED`, ACL storage, edit-log/fsimage persistence, and UGI-based client identity. It also relies on `DFSTestUtil.getFileSystemAs` to bind clients to distinct users.

## Risks and test signals

Regressions would allow unauthorized deletes/renames, incorrectly block file appends, propagate sticky bits to new subdirectories, lose the bit after restart, or produce weak exception diagnostics. Strong signals are expected `AccessControlException` messages containing "sticky bit", user, path, and parent, plus correct `FsPermission.getStickyBit()` values before and after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/permission/TestStickyBit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/shell/TestHdfsTextCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/shell/TestHdfsTextCommand.java

## Purpose

`TestHdfsTextCommand` validates the HDFS shell `-text` display path for Avro container files. It writes a small binary Avro weather-record file into a `MiniDFSCluster`, invokes the protected `Display.Text.getInputStream(PathData)` method, and asserts that the decoded text stream exactly matches the expected JSON-record lines.

## Important APIs, types, and functions

The test uses `MiniDFSCluster`, `FileSystem`, `FSDataOutputStream`, `PathData`, `Display.Text`, Java reflection `Method`, `InputStream`, `StringWriter`, and Commons IO copy helpers. Local helpers are `createAvroFile`, `inputStreamToString`, and `generateWeatherAvroBinaryData`, the latter embedding a complete Avro binary object container payload.

## Control flow, state, and persistence

Each test starts a fresh cluster in `setUp`, creates `/test/data/testText/weather.avro`, and shuts the cluster down in `tearDown`. `testDisplayForAvroFiles` writes the byte array, constructs `PathData` from the HDFS path and configuration, makes `getInputStream` accessible by reflection, reads the decoded stream as UTF-8, and compares all five output rows including platform line separators. State is transient HDFS file content only.

## Dependencies and integration points

The test touches the FsShell display implementation, Avro input detection/decoding in `Display.Text`, HDFS stream opening through `PathData`, and UTF-8 conversion. It depends on the Avro codec/schema embedded in the byte array and on shell output formatting remaining stable.

## Risks and test signals

Risks are brittle reflection against a protected method, embedded binary fixture opacity, platform line-separator sensitivity, and exact-output coupling to Avro JSON rendering. A passing test signals that HDFS `-text` can detect Avro data and produce record-oriented text rather than raw binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/shell/TestHdfsTextCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestNNStartupWhenViewFSOverloadSchemeEnabled.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestNNStartupWhenViewFSOverloadSchemeEnabled.java

## Purpose

This test ensures NameNode startup still succeeds when the `hdfs` scheme is overloaded to `ViewFileSystemOverloadScheme`. It covers both HA and non-HA `MiniDFSCluster` startup, including a nonzero trash interval to trigger TrashEmptier initialization during NameNode service startup.

## Important APIs, types, and functions

Important pieces are `ViewFileSystemOverloadScheme`, `DistributedFileSystem`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `FsConstants.FS_VIEWFS_OVERLOAD_SCHEME_TARGET_FS_IMPL_PATTERN`, `fs.%s.impl`, and HDFS/IPC/trash configuration keys. Tests are `testHANameNodeAndDataNodeStartup` and `testNameNodeAndDataNodeStartup`.

## Control flow, state, and persistence

`@BeforeAll` mutates a static configuration so `fs.hdfs.impl` resolves to the overload scheme and the target implementation resolves to `DistributedFileSystem`. Each test builds a zero-DN cluster with safe mode waiting disabled, waits active, and in the HA case transitions NameNode 0 active. `@AfterEach` shuts down the cluster. There is no persistent state beyond cluster process state.

## Dependencies and integration points

The test integrates the FileSystem implementation registry, ViewFS overload-scheme target lookup, NameNode/HA startup code, IPC retry behavior, and TrashEmptier initialization. It protects against startup code that assumes `hdfs` always maps directly to `DistributedFileSystem`.

## Risks and test signals

The main regression signal is startup failure, hang, or HA transition failure when scheme overloading is enabled. The test is intentionally coarse: it does not perform file operations, so it isolates initialization compatibility rather than runtime ViewFS routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestNNStartupWhenViewFSOverloadSchemeEnabled.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFSOverloadSchemeWithMountTableConfigInHDFS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFSOverloadSchemeWithMountTableConfigInHDFS.java

## Purpose

This subclass verifies that `ViewFileSystemOverloadScheme` can load mount-table configuration from versioned XML files stored in HDFS rather than only from in-memory `Configuration` keys. It extends the broader HDFS-scheme overload test suite and changes only mount-link persistence.

## Important APIs, types, and functions

Important APIs are `Constants.CONFIG_VIEWFS_MOUNTTABLE_PATH`, `ViewFileSystemOverloadScheme.ChildFsGetter`, `ViewFsTestSetup.addMountLinksToFile`, `FileSystem.createNewFile`, and the inherited `addMountLinks` contract from `TestViewFileSystemOverloadSchemeWithHdfsScheme`.

## Control flow, state, and persistence

`setUp` calls the parent setup, derives an HDFS `/MountTable/` directory from `fs.defaultFS`, configures it as the mount-table path, creates old and new version files `mount-table.30.xml` and `mount-table.31.xml`, then overrides `addMountLinks` to write the mount links into the newer file. Runtime state is the HDFS mount-table directory; the overload scheme should choose the highest version.

## Dependencies and integration points

The test covers ViewFS mount-table loading from HDFS, versioned mount-table file selection, `ChildFsGetter` target initialization, and inherited overload-scheme operations for local, HDFS, fallback, Nfly, and cache behavior.

## Risks and test signals

Risks include selecting the wrong mount-table version, failing to initialize the child HDFS used to read mount tables, or diverging between file-backed and configuration-backed link parsing. Passing inherited tests through this subclass signals that file-backed mount links are behaviorally equivalent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFSOverloadSchemeWithMountTableConfigInHDFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemAtHdfsRoot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemAtHdfsRoot.java

## Purpose

`TestViewFileSystemAtHdfsRoot` runs the `ViewFileSystemBaseTest` contract when the HDFS root directory itself is the target test root. It verifies ViewFileSystem behavior when mount points resolve to `/`, which is a special case because setup must not delete the root path.

## Important APIs, types, and functions

The class extends `ViewFileSystemBaseTest` and overrides `createFileSystemHelper`, `setUp`, `initializeTargetTestRoot`, `getExpectedDelegationTokenCount`, and `getExpectedDelegationTokenCountWithCredentials`. It uses `MiniDFSCluster`, `FileSystem`, `FileStatus`, `DFS_NAMENODE_DELEGATION_TOKEN_ALWAYS_USE_KEY`, and `FileSystemTestHelper`.

## Control flow, state, and persistence

`@BeforeAll` starts a two-DN HDFS cluster with delegation tokens always enabled and stores `fHdfs`. Each test assigns `fsTarget = fHdfs` before invoking the base setup. The custom root initializer qualifies `/` and deletes only existing children, leaving the root intact. The inherited base test then creates and exercises ViewFS mounts.

## Dependencies and integration points

This integrates ViewFileSystem mount-table setup with an HDFS root target, HDFS delegation-token behavior, block support flags, and the reusable base contract for path creation/listing/rename/status/token behavior.

## Risks and test signals

Key risks are destructive root deletion during setup, incorrect path qualification for root-mounted targets, and duplicate delegation tokens for one underlying filesystem. Expected token count is one because all mount paths point to the same HDFS instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemAtHdfsRoot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemClose.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemClose.java

## Purpose

`TestViewFileSystemClose` checks that a `ViewFileSystem` closes its child filesystems when inner caching and filesystem caching are disabled. It is a leak-prevention test for child target lifecycle management.

## Important APIs, types, and functions

The test uses `ViewFileSystem`, `FileSystem.get`, `FileSystem.closeAll`, `getChildFileSystems`, `ConfigUtil.addLink`, `FsConstants.VIEWFS_URI`, and `LambdaTestUtils.intercept`. Relevant configuration keys are `fs.viewfs.enable.inner.cache`, `fs.viewfs.impl.disable.cache`, and `fs.hdfs.impl.disable.cache`.

## Control flow, state, and persistence

The test builds an isolated `Configuration`, registers `fs.viewfs.impl`, disables caches, adds `/data -> hdfs://localhost/tmp/data`, creates a `ViewFileSystem`, captures its child filesystems, closes the viewfs and all cached filesystems, then verifies each child rejects create operations with "Filesystem closed". State is limited to in-memory FileSystem objects.

## Dependencies and integration points

This covers ViewFS child filesystem ownership and close propagation when cache semantics do not retain shared instances. It integrates with Hadoop's global `FileSystem` cache and target filesystem close checks.

## Risks and test signals

Regressions would leave target filesystems open after closing ViewFS, causing leaks and unexpected operations after shutdown. The signal is an `IOException` containing "Filesystem closed" for every captured child.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemClose.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemHdfs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemHdfs.java

## Purpose

`TestViewFileSystemHdfs` runs ViewFileSystem against a federated two-namespace HDFS cluster and extends the base ViewFS contract with HDFS-specific behavior. It validates delegation tokens, trash roots, shell `-df`, checksums, cross-filesystem rename rejection, Nfly repair behavior, lazy target initialization under UGI, internal directory permissions, and encryption-zone enclosing-root resolution.

## Important APIs, types, and functions

The test depends on `ViewFileSystemBaseTest`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology(2)`, `FileSystem`, `FsShell`, `DFSTestUtil`, `HdfsAdmin`, `CreateEncryptionZoneFlag.PROVISION_TRASH`, `NflyFSystem.NflyKey`, `ConfigUtil.addLinkNfly`, `ConfigUtil.addLinkFallback`, `FileChecksum`, `UserGroupInformation`, and `LambdaTestUtils`. Important methods are `setupMountPoints`, `testTrashRootsAfterEncryptionZoneDeletion`, `testDf`, `testFileChecksum`, `testRenameAccorssFilesystem`, `testNflyRepair`, `testTargetFileSystemLazyInitializationWithUgi`, and `testEnclosingRoot*`.

## Control flow, state, and persistence

`@BeforeAll` configures a JKS key provider, encryption-zone listing batch size, delegation tokens, starts two federated NameNodes, and creates per-namespace working directories. Each test mounts the first namespace through inherited links and adds `/mountOnNn2` to the second namespace. Tests then manipulate HDFS files, encryption zones, Nfly target roots, permissions, and child filesystem instantiation. Persistent state is MiniDFSCluster namespace metadata and key-provider files under the test root; cleanup deletes keys and cluster state.

## Dependencies and integration points

This file integrates ViewFS with HDFS federation, encryption zones and provisioned trash, FsShell output, file checksum passthrough, Nfly replicated filesystem routing, UGI-sensitive lazy target creation, fallback filesystem handling, and `getEnclosingRoot` semantics across mounts and encryption-zone boundaries.

## Risks and test signals

Risks include wrong delegation-token deduplication, checksum delegation bugs, accidental cross-namespace rename support, Nfly not repairing missing replicas, target filesystems initialized under the wrong user, and incorrect enclosing-root discovery for encryption zones. Test signals include exact child token counts, shell output fragments, checksum equality, expected `AccessControlException`, repaired missing files, and `NotInMountpointException`/`IllegalArgumentException` for invalid roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemHdfs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLinkFallback.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLinkFallback.java

## Purpose

`TestViewFileSystemLinkFallback` is a broad `ViewFileSystem` test suite for `linkFallback` mount-table entries. It verifies that unresolved paths fall through to a configured target filesystem while explicit mount links and internal directories still shadow fallback entries correctly.

## Important APIs, types, and functions

The class extends `ViewFileSystemBaseTest` and uses `ConfigUtil.addLinkFallback`, `ConfigUtil.addLink`, `ViewFileSystem`, `MiniDFSCluster` with three federated namespaces, `FileSystem`, `FileStatus`, `FSDataOutputStream`, `FsPermission`, `FileAlreadyExistsException`, `NotInMountpointException`, and `LambdaTestUtils.intercept`. Key tests cover listing, mkdirs, create, unavailable fallback FS, root operations, mount-path conflicts, and symlink-style mount listing.

## Control flow, state, and persistence

Setup starts a three-namespace cluster, uses namespace 0 as root, and clears `/` children before each test. `setupMountPoints` installs inherited base mounts plus a default fallback. Individual tests build fresh configurations to model specific fallback trees, create real HDFS directories/files under `fallbackDir`, instantiate `viewfs://default` or named mount tables, and assert that list/create/mkdir operations either route to fallback or are blocked by mount/internal directory semantics.

## Dependencies and integration points

This file integrates ViewFS inode-tree resolution, link fallback, regular mount links, mount-link-as-symlink display, HDFS permissions, create/mkdir/listStatus routing, and failure handling when NameNodes are stopped. It also exercises `Path.mergePaths` expectations between view paths and fallback targets.

## Risks and test signals

Risks include leaking fallback entries that should be shadowed by explicit mounts, using link permissions instead of target permissions, failing to create parent structures in fallback, creating files over internal directories, or hiding fallback roots from listings. Test signals are exact listed path sets, `FileAlreadyExistsException`, `NotInMountpointException`, fallback HDFS existence checks, and failure/recovery when fallback NameNodes are stopped and restarted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLinkFallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLinkMergeSlash.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLinkMergeSlash.java

## Purpose

`TestViewFileSystemLinkMergeSlash` verifies ViewFileSystem mount tables that use `linkMergeSlash`, where the mount-table root is merged directly with a target filesystem root. It checks basic file access, invalid mixed configuration, invalid sub-mount syntax, and child filesystem reporting.

## Important APIs, types, and functions

The class extends `ViewFileSystemBaseTest` and uses `ConfigUtil.addLinkMergeSlash`, `ConfigUtil.addLink`, `MiniDFSCluster`, `DistributedFileSystem`, `FileSystem`, `FileStatus`, `FsConstants.VIEWFS_SCHEME`, and `ViewFileSystem`. The key tests are `testConfLinkMergeSlash`, `testConfLinkMergeSlashWithRegularLinks`, `testConfLinkMergeSlashWithMountPoint`, and `testChildFileSystems`.

## Control flow, state, and persistence

Setup creates a three-namespace MiniDFSCluster, picks namespace 0, clears root children before each test, and configures two named merge-slash mount tables in inherited setup. The tests also use a local `TEST_DIR` fixture to write a file, then mount that directory as merge slash and resolve it through `viewfs://ClusterMerge/`.

## Dependencies and integration points

This integrates ViewFS mount-table parsing, merge-slash exclusivity rules, child filesystem tracking, local filesystem targets, and HDFS target reporting. It protects the invariant that a mount table cannot combine merge slash with regular links and that merge slash must be rooted, not path-qualified.

## Risks and test signals

Regression signals are successful initialization for invalid mixed mount tables, acceptance of `linkMergeSlash./user`, wrong target child count, or non-`DistributedFileSystem` child type for the HDFS-backed setup. The basic access test signals that root path merging still resolves target files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLinkMergeSlash.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLinkRegex.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLinkRegex.java

## Purpose

`TestViewFileSystemLinkRegex` validates ViewFileSystem `linkRegex` mount points. It covers numbered capture groups, `${}` capture syntax, named groups, fixed destination mappings, single and multiple resolved-destination interceptors, and target filesystem reuse through the inner cache.

## Important APIs, types, and functions

Important APIs are `ConfigUtil.addLinkRegex`, `RegexMountPoint`, `RegexMountPointInterceptorType.REPLACE_RESOLVED_DST_PATH`, `ViewFileSystem.fsState.resolve`, `ChRootedFileSystem`, `MiniDFSCluster`, and `FileSystem`. Helpers include `buildReplaceInterceptorSettingString`, `linkInterceptorSettings`, `createDirWithChildren`, `createFile`, and `testRegexMountpoint`.

## Control flow, state, and persistence

Setup starts a three-namespace federated cluster and clears namespace 0 root before each test. `testRegexMountpoint` creates the expected target directory and child files, adds a regex link to a named mount table, opens `viewfs://TestViewFileSystemLinkRegexCluster/`, checks `resolvePath`, `getFileStatus`, and `listStatus`, then resolves the same source twice through internal `fsState` to assert target filesystem object reuse.

## Dependencies and integration points

The test integrates regex-based mount-table parsing, Java regex capture substitution, interceptor serialization separators, destination path rewriting, ViewFS target filesystem caching, and HDFS-backed directory access. It reaches into package-visible/internal `fsState`, so it directly protects implementation behavior as well as public API behavior.

## Risks and test signals

Risks include incorrect group substitution when paths have suffixes, broken named-group handling, interceptor order mistakes, duplicate child filesystem instances, and wrong path normalization with trailing slashes. Signals are exact resolved paths, expected child counts, and `assertSame` on underlying target filesystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLinkRegex.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemOverloadSchemeHdfsFileSystemContract.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemOverloadSchemeHdfsFileSystemContract.java

## Purpose

This class runs the HDFS filesystem contract tests through `ViewFileSystemOverloadScheme` after registering it as the implementation for the `hdfs` scheme. It ensures common HDFS contract behavior still works when HDFS paths are mediated by ViewFS mount-table resolution.

## Important APIs, types, and functions

The class extends `TestHDFSFileSystemContract` and uses `MiniDFSCluster`, `HdfsConfiguration`, `ConfigUtil.addLink`, `ViewFileSystemOverloadScheme`, `DistributedFileSystem`, `AppendTestUtil`, `FileSystemContractBaseTest.TEST_UMASK`, `CONFIG_VIEWFS_IGNORE_PORT_IN_MOUNT_TABLE_NAME`, and `getRawFileSystem`.

## Control flow, state, and persistence

`@BeforeAll` starts a two-DN HDFS cluster and records the expected working directory. `setUp` maps `fs.hdfs.impl` to the overload scheme, maps the target implementation back to `DistributedFileSystem`, adds `/user`, `/append`, and `/FileSystemContractBaseTest/` links under the default FS authority, then obtains `fs = FileSystem.get(conf)`. Overrides adapt append, root rename, root listing, and disable duplicate LS-root coverage.

## Dependencies and integration points

This integrates the generic HDFS FileSystem contract with ViewFS overload mounting, default FS authority lookup, append support, root access protection, and raw filesystem escape for preparing root-listing fixtures.

## Risks and test signals

Risks include contract regressions hidden by scheme overloading, wrong mount-table authority when ports are present, append path misrouting, and root operations returning different exception types. Signals are inherited contract pass/fail plus explicit `AccessControlException` for root rename and successful root listing of `/FileSystemContractBaseTest`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemOverloadSchemeHdfsFileSystemContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemOverloadSchemeWithHdfsScheme.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemOverloadSchemeWithHdfsScheme.java

## Purpose

`TestViewFileSystemOverloadSchemeWithHdfsScheme` is the main test suite for replacing the `hdfs` scheme implementation with `ViewFileSystemOverloadScheme`. It verifies mount links to HDFS and local filesystems, nonexistent targets, root listing and root create semantics, fallback links, authority-free `viewfs:/` access, target implementation validation, inner-cache behavior, Nfly rename/read/repair, and port-insensitive mount-table names.

## Important APIs, types, and functions

Important types and APIs include `MiniDFSCluster`, `ViewFileSystemOverloadScheme`, `DistributedFileSystem`, `RawLocalFileSystem`, `ConfigUtil`/`ViewFsTestSetup`, `Constants.CONFIG_VIEWFS_*`, `FsConstants.FS_VIEWFS_OVERLOAD_SCHEME_TARGET_FS_IMPL_PATTERN`, `NflyFSystem.NflyKey`, `ViewFileSystemOverloadScheme.ChildFsGetter`, `FSDataInputStream`, and `FSDataOutputStream`. Helpers include `addMountLinks`, `testMountLinkWithNonExistentLink`, `testCreateOnRoot`, `writeString`, and `readString`.

## Control flow, state, and persistence

`@BeforeAll` starts a two-DN cluster. `setUp` derives a cluster configuration, sets `fs.hdfs.impl` to the overload scheme, ignores port in mount-table name by default, and creates a local target directory. Each test adds mount links under the HDFS authority, opens `FileSystem.get(conf)` or `FileSystem.get(defaultFSURI, conf)`, performs operations through overloaded `hdfs://...` paths, and then `cleanUp` deletes all HDFS root children and closes filesystem caches.

## Dependencies and integration points

This suite touches FileSystem implementation registration, mount-table naming from HDFS authorities, HDFS/local target routing, fallback routing, ViewFS inner-cache and Hadoop FileSystem cache interaction, Nfly replicated writes and repair-on-read, and HDFS client initialization through the overloaded scheme.

## Risks and test signals

Risks include routing local paths to HDFS, accepting nonexistent target filesystems too early or too late, listing wrong root entries, creating root files without fallback, missing target implementation failures, incorrect child filesystem counts with caching disabled, Nfly not replicating or repairing, and mount-table lookup failures when URI ports differ. Signals are exact existence checks in target filesystems, expected exceptions, child count assertions, and successful Nfly reads after deleting one replica.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemOverloadSchemeWithHdfsScheme.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithAcls.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithAcls.java

## Purpose

`TestViewFileSystemWithAcls` verifies that `ViewFileSystem` correctly dispatches ACL operations to the mounted HDFS namespace. It uses two federated NameNodes and confirms ACL mutations on one mount do not leak to the other.

## Important APIs, types, and functions

Important APIs are `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology(2)`, `FileSystem`, `ConfigUtil.addLink`, `AclEntry`, `AclStatus`, `AclTestHelpers.aclEntry`, `setAcl`, `modifyAclEntries`, `removeDefaultAcl`, `removeAcl`, and `removeAclEntries`.

## Control flow, state, and persistence

`@BeforeAll` enables NameNode ACLs and starts a two-namespace cluster. Each test clears and recreates per-namespace target roots, mounts `/mountOnNn1` and `/mountOnNn2`, and opens `viewfs:///`. The test sets ACLs on namespace 1, verifies through both ViewFS and raw HDFS, modifies defaults, removes defaults and full ACLs, checks namespace 2 is still clean, then repeats mutation/removal on namespace 2.

## Dependencies and integration points

The test covers ViewFileSystem ACL method forwarding, federated mount resolution, HDFS ACL feature enablement, default ACL expansion, and isolation between mount targets.

## Risks and test signals

Risks are dispatching ACL operations to the wrong namespace, losing default ACL entries, incorrect mask/group expansion, or stale ACLs after removal. Signals are exact `AclEntry[]` arrays and zero-entry checks on the untouched namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithAcls.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithTruncate.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithTruncate.java

## Purpose

`TestViewFileSystemWithTruncate` verifies that `ViewFileSystem` advertises and forwards file truncation to an HDFS mount target. It checks both `hasPathCapability` and the final truncated length.

## Important APIs, types, and functions

Important APIs include `FileSystem.truncate`, `hasPathCapability`, `CommonPathCapabilities.FS_TRUNCATE`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology(2)`, `GenericTestUtils.waitFor`, `FileSystem.isFileClosed`, `FSDataOutputStream`, and `ConfigUtil.addLink`.

## Control flow, state, and persistence

Setup starts a federated cluster, mounts `/mountOnNn1` to an HDFS test root, writes a file via ViewFS, asserts truncate capability, calls `truncate(filePath, 10)`, and if the operation is asynchronous waits until the raw HDFS file is closed. It then asserts ViewFS reports length 10. State is a temporary HDFS file under the test root.

## Dependencies and integration points

The test integrates ViewFS path resolution with HDFS truncate semantics, capability reporting, asynchronous block recovery completion, and raw HDFS status visibility.

## Risks and test signals

Risks include ViewFS not exposing `FS_TRUNCATE`, returning before HDFS completes without a usable wait path, wrong raw target path assumptions, or stale file length after truncate. Passing requires capability true and exact final length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithTruncate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithXAttrs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithXAttrs.java

## Purpose

`TestViewFileSystemWithXAttrs` verifies that extended-attribute operations through `ViewFileSystem` resolve to the correct mounted HDFS namespace and remain isolated across federated NameNodes.

## Important APIs, types, and functions

The test uses `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology(2)`, `FileSystem`, `ConfigUtil.addLink`, `setXAttr`, `getXAttr`, `getXAttrs`, and `removeXAttr`. Test fixtures are `user.a1`/`user.a2` with small byte-array values.

## Control flow, state, and persistence

Each test clears two HDFS target roots, mounts them as `/mountOnNn1` and `/mountOnNn2`, and opens `viewfs:///`. It sets two XAttrs on the first mount, verifies them through ViewFS and raw namespace 1, checks namespace 2 remains empty, removes them, then repeats the same checks on namespace 2. State is temporary XAttr metadata in the MiniDFSCluster namespaces.

## Dependencies and integration points

This covers ViewFileSystem XAttr forwarding, HDFS XAttr storage, federated mount resolution, and namespace isolation. Unlike ACL tests, no explicit XAttr config is set here, so it relies on the cluster defaults used by the HDFS test environment.

## Risks and test signals

Risks include wrong namespace resolution, byte-array corruption, incomplete removal, and leakage between mounts with identical target-root shapes. Signals are exact byte-array equality and zero-sized XAttr maps after removal or on the untouched namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithXAttrs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsAtHdfsRoot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsAtHdfsRoot.java

## Purpose

`TestViewFsAtHdfsRoot` runs the `ViewFsBaseTest` FileContext contract when the target HDFS root `/` is mounted into ViewFs. It is the FileContext counterpart to `TestViewFileSystemAtHdfsRoot`.

## Important APIs, types, and functions

The class extends `ViewFsBaseTest` and uses `MiniDFSCluster`, `HdfsConfiguration`, `FileContext`, `FileContextTestHelper`, `RemoteIterator<FileStatus>`, `DFS_NAMENODE_DELEGATION_TOKEN_ALWAYS_USE_KEY`, and inherited ViewFs base tests. It overrides `createFileContextHelper`, `setUp`, `initializeTargetTestRoot`, and `getExpectedDelegationTokenCount`.

## Control flow, state, and persistence

`@BeforeAll` enables always-use delegation tokens, starts a two-DN HDFS cluster, and gets a `FileContext` for the cluster URI. Per test, it assigns `fcTarget = fc` and runs base setup. The root initializer qualifies `/` and deletes only child paths through a `RemoteIterator`, preserving the root directory itself.

## Dependencies and integration points

This integrates FileContext/ViewFs mount-table behavior, HDFS root handling, delegation-token collection, and the base ViewFs operation contract.

## Risks and test signals

Risks are deleting the root during setup, mishandling root-qualified paths, or changing delegation-token expectations. The expected token count is eight under the inherited base mount layout with HDFS tokens enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsAtHdfsRoot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsDefaultValue.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsDefaultValue.java

## Purpose

`TestViewFsDefaultValue` verifies ViewFS default-value and quota APIs for HDFS-mounted paths. It ensures default block size, replication, server defaults, content summary, quota usage, and storage-type quotas are delegated to the target filesystem, while unmapped paths throw `NotInMountpointException`.

## Important APIs, types, and functions

Important APIs are `FileSystem.getDefaultBlockSize(Path)`, `getDefaultReplication(Path)`, `getServerDefaults(Path)`, `getContentSummary`, `getQuotaUsage`, `DistributedFileSystem.setQuota`, `setQuotaByStorageType`, `FsServerDefaults`, `QuotaUsage`, `StorageType`, and `ConfigUtil.addLink`.

## Control flow, state, and persistence

`@BeforeAll` configures DFS defaults, starts a cluster with replication capacity, creates files under `/tmp` and an unmapped path, mounts `/tmp` into `viewfs:///`, and records target paths. Tests first call default APIs on the unmapped path expecting `NotInMountpointException`, then assert values on the mounted file. Quota tests set namespace/space or storage-type quotas through raw HDFS and read them via ViewFS.

## Dependencies and integration points

This integrates ViewFS path resolution with HDFS server defaults, client-side defaults, content-summary quota reporting, and storage-type quota reporting. It also protects exception behavior for paths outside the mount table.

## Risks and test signals

Risks include returning ViewFS local defaults instead of target HDFS defaults, swallowing `NotInMountpointException`, or losing quota type fields. Signals are exact configured defaults, quota values, `-1` unset quota values, positive consumed space, and correct file/directory counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsDefaultValue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsFileStatusHdfs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsFileStatusHdfs.java

## Purpose

`TestViewFsFileStatusHdfs` verifies two HDFS-backed ViewFileSystem status behaviors: `ViewFsFileStatus` serialization/deserialization and file checksum passthrough. The serialization case protects MapReduce job submission paths that serialize `FileStatus`.

## Important APIs, types, and functions

The test uses `MiniDFSCluster`, `ViewFileSystem`, `FileSystemTestHelper`, `ConfigUtil.addLink`, `FileStatus.write/readFields`, `DataOutputBuffer`, `DataInputBuffer`, and `FileChecksum`. Paths `/tmp` and `/vfstmp` are mounted to HDFS directories.

## Control flow, state, and persistence

Cluster setup creates an HDFS working directory, configures ViewFS links, and verifies the returned filesystem class. `testFileStatusSerialziation` creates a file in raw HDFS, gets status through ViewFS, serializes it into a data buffer, reads it into a plain `FileStatus`, and compares length. `testGetFileChecksum` creates two HDFS files, compares ViewFS checksum for one with raw HDFS checksum, and asserts it differs from the other file's checksum.

## Dependencies and integration points

This covers ViewFS overlay status objects, Hadoop writable serialization, HDFS checksum calculation, and mount path translation. It is important for consumers that persist `FileStatus` across process or RPC boundaries.

## Risks and test signals

Risks include non-serializable ViewFS-specific status fields, lost file length after deserialization, checksum requests using the view path without resolving to target, or checksum collisions in the fixture. Signals are exact length equality and checksum equality/inequality comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsFileStatusHdfs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsHdfs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsHdfs.java

## Purpose

`TestViewFsHdfs` runs the FileContext-oriented `ViewFsBaseTest` over HDFS and adds a UGI lazy target initialization check. It is the `FileContext` counterpart to parts of `TestViewFileSystemHdfs`.

## Important APIs, types, and functions

Important APIs are `ViewFsBaseTest`, `FileContext`, `MiniDFSCluster`, `HdfsConfiguration`, `UserGroupInformation.doAs`, `AccessControlException`, `FsPermission`, and `DFS_NAMENODE_DELEGATION_TOKEN_ALWAYS_USE_KEY`. The primary added test is `testTargetFileSystemLazyInitialization`.

## Control flow, state, and persistence

`@BeforeAll` starts HDFS, creates the current user's working directory, and stores an HDFS `FileContext`. In each test `fcTarget` is assigned before inherited setup. The lazy initialization test first creates/deletes `/data/user1` as the current user, then constructs a ViewFs `FileContext` inside a different UGI. The first mkdir fails due to user permissions. After `/data` ownership and permissions are changed, a new UGI-created ViewFs context creates the directory and the owner is asserted as `user1`.

## Dependencies and integration points

This covers FileContext ViewFs mount resolution, target filesystem lazy creation under the creator UGI, HDFS permissions, and inherited token behavior. It validates identity capture at ViewFs construction time, not operation call time.

## Risks and test signals

Risks include initializing target filesystems under the wrong user, caching target contexts across users, or wrong delegation-token count. Signals are the expected initial `AccessControlException`, successful mkdir after permission changes, and resulting owner equal to the alternate UGI short name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsHdfs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsLinkFallback.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsLinkFallback.java

## Purpose

`TestViewFsLinkFallback` validates `linkFallback` behavior through the `AbstractFileSystem` and `FileContext` APIs rather than the `FileSystem` API. It focuses on mkdir, create, delegation-token aggregation, listFiles, and rename behavior when fallback and internal mount-directory trees overlap.

## Important APIs, types, and functions

The test uses `AbstractFileSystem.get`, `FileContext.getFileContext`, `ConfigUtil.addLinkFallback`, `ConfigUtil.addLink`, `Options.CreateOpts`, `Options.Rename.OVERWRITE`, `CreateFlag.CREATE`, `LocatedFileStatus`, `RemoteIterator`, `Token`, `DistributedFileSystem`, `FileAlreadyExistsException`, and `FileNotFoundException`. Helper `verifyRename` asserts source disappearance and destination existence.

## Control flow, state, and persistence

Setup starts a three-namespace HDFS cluster and clears namespace 0 root before each test. Each test builds a mount table, prepares fallback target trees under `/fallbackDir`, gets an `AbstractFileSystem` or `FileContext` for `viewfs://default/`, then performs operations. Mappings deliberately overlap mount internal directories and fallback directories to test shadowing and fallback routing.

## Dependencies and integration points

This integrates the newer AbstractFileSystem/ViewFs path with fallback resolution, parent creation, create-parent semantics, token collection from explicit links plus fallback, `listFiles` over fallback roots, and rename behavior across fallback/internal paths.

## Risks and test signals

Risks include API divergence from `ViewFileSystem`, failure to create parents when `createParent` is false but internal dirs exist, weak failure when fallback NameNodes are down, wrong token count, create-over-internal-dir behavior, and rename into internal directories without matching fallback structure. Signals are HDFS existence checks, exact token count 3, expected `FileAlreadyExistsException`/`FileNotFoundException`, and successful overwrite renames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsLinkFallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsWithAcls.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsWithAcls.java

## Purpose

`TestViewFsWithAcls` is the FileContext/ViewFs counterpart to the ViewFileSystem ACL test. It verifies ACL operations route to the correct HDFS namespace through `FileContext`.

## Important APIs, types, and functions

Important APIs are `FileContext`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology(2)`, `ConfigUtil.addLink`, `AclEntry`, `AclStatus`, `FsPermission`, `AclTestHelpers.aclEntry`, and FileContext ACL methods: `setAcl`, `modifyAclEntries`, `removeDefaultAcl`, `removeAcl`, and `removeAclEntries`.

## Control flow, state, and persistence

Setup enables HDFS ACLs, creates two HDFS `FileContext` targets, recreates per-namespace target roots with `0750`, mounts `/mountOnNn1` and `/mountOnNn2`, and opens `viewfs:///`. The test sets, modifies, and removes ACLs on the first mount, confirms raw namespace 1 matches, confirms namespace 2 stays empty, then repeats mutation/removal on namespace 2.

## Dependencies and integration points

This covers ViewFs ACL forwarding, HDFS ACL default-entry expansion, mount isolation, FileContext permission state, and federated namespace resolution.

## Risks and test signals

Risks mirror the FileSystem ACL variant: wrong namespace dispatch, default ACL loss, incorrect mask/group entries, or incomplete cleanup. Signals are exact `AclEntry[]` expectations and zero-entry checks on raw and ViewFs status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsWithAcls.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsWithXAttrs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsWithXAttrs.java

## Purpose

`TestViewFsWithXAttrs` verifies FileContext/ViewFs extended-attribute operations against federated HDFS mount targets. It confirms XAttrs are written to, read from, and removed from the correct namespace.

## Important APIs, types, and functions

The test uses `FileContext`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology(2)`, `ConfigUtil.addLink`, `FsPermission`, and FileContext XAttr methods: `setXAttr`, `getXAttr`, `getXAttrs`, and `removeXAttr`. Fixtures are `user.a1`, `user.a2`, and byte values `{0x31,0x32,0x33}` and `{0x37,0x38,0x39}`.

## Control flow, state, and persistence

Each test recreates target roots in both HDFS namespaces with `0750`, configures two ViewFs mounts, and opens `viewfs:///`. It sets two XAttrs on mount 1, verifies values through ViewFs and raw namespace 1, checks namespace 2 is empty, removes both attributes, then repeats on mount 2 and verifies cleanup.

## Dependencies and integration points

This integrates ViewFs XAttr forwarding, HDFS XAttr metadata, federated mount resolution, and byte-array preservation through FileContext APIs.

## Risks and test signals

Risks include namespace leakage, value corruption, stale attributes after removal, or API divergence between FileContext and FileSystem variants. Signals are exact byte-array equality and empty XAttr maps on untouched and cleaned namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsWithXAttrs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/AdminStatesBaseTest.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/AdminStatesBaseTest.java

## Purpose

`AdminStatesBaseTest` is a reusable HDFS test base for DataNode administrative state transitions, including decommission and maintenance. It provides cluster setup, hosts-file management, file-writing helpers, node out-of-service/in-service transitions, state waiting, DFSClient access, and cleanup utilities for derived tests.

## Important APIs, types, and functions

Important types are `MiniDFSCluster`, `DFSClient`, `HostsFileWriter`, `DatanodeInfo`, `DatanodeInfo.AdminStates`, `DatanodeReportType`, `DatanodeDescriptor`, `DatanodeManager`, `FSNamesystem`, `NameNodeAdapter`, `CombinedHostFileManager`, and `HostConfigManager`. Key methods are `setup`, `teardown`, `writeFile`, `writeIncompleteFile`, overloaded `takeNodeOutofService`, `putNodeInService`, `waitNodeState`, `startCluster`, `startSimpleCluster`, `startSimpleHACluster`, `refreshNodes`, `getDfsClient`, `validateCluster`, `getDatanodeDesriptor`, and `cleanupFile`.

## Control flow, state, and persistence

`@BeforeEach` creates `HostsFileWriter`, an `HdfsConfiguration`, optional combined host provider config, and short heartbeat/block-report/replication/decommission intervals, then initializes include/exclude host files under a temp area. Cluster start helpers build federated, simple, or HA MiniDFSClusters under the JUnit `@TempDir`. `takeNodeOutofService` resolves target DataNodes by UUID or random selection, updates decommission and maintenance host maps, writes out-of-service hosts, calls `refreshNodes`, and waits until descriptors reach the requested admin state. `putNodeInService` reconstructs current maintenance/decommission maps minus the target node, refreshes nodes, and waits for `NORMAL`.

## Dependencies and integration points

The base integrates HDFS host include/exclude management, decommission monitor timing, maintenance expiration times, NameNode block-management internals, `DFSClient.datanodeReport`, simulated capacity cluster creation, HA/federation topology builders, and HDFS file/block creation with deterministic random data.

## Risks and test signals

Risks include indefinite waits if heartbeats or admin-state transitions stall, random node selection making failures less reproducible, stale host-file state, incorrect handling of simultaneous maintenance and decommission maps, and typo-stable API names such as `getDatanodeDesriptor`. Signals for derived tests include expected live DataNode counts, admin state equality in `waitNodeState`, successful file cleanup, and correct restoration to `NORMAL` after host-file updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/AdminStatesBaseTest.java -->
