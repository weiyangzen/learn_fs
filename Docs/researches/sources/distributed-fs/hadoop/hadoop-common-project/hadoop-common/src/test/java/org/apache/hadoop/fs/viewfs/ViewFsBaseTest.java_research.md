# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFsBaseTest.java

Purpose: abstract `FileContext`/`AbstractFileSystem` API test suite for `ViewFs`. It parallels `ViewFileSystemBaseTest` but exercises the newer `FileContext` surface.

Important APIs and types: `ViewFs`, `ViewFs.MountPoint`, `FileContext`, `AbstractFileSystem`, `ChRootedFs`, `FileContextTestHelper`, `ConfigUtil`, `FsServerDefaults`, `BlockLocation`, `AclStatus`, `CreateFlag`, `Token`, Mockito, `LambdaTestUtils`, and `NotInMountpointException`.

Control flow: setup creates local target directories/files and configures a mount table named `mycluster` with `/targetRoot`, `/user`, `/user2`, `/data`, internal links, a dangling link, and a file link. Tests cover mount enumeration, delegation tokens, path qualification, create/delete/mkdir/rename through mount links, rename strategy variants, block locations, listing internal dirs, file status and file link status, checksum path delegation, symlink targets, resolvePath, read-only internal directory modifications, ACL/xattr/snapshot failures, internal-dir ownership, server defaults for mount and internal paths, optimized `listLocatedStatus` and `listStatusIterator` delegation to the underlying `AbstractFileSystem`, and no-primary-group error handling.

State and persistence: target FS state is created per test through `FileContext` and removed in teardown. `MockFs` keeps a static mock cache keyed by URI authority for delegation verification.

Dependencies and integration: central coverage for `ViewFs`, `ChRootedFs`, `InodeTree`, `FileContext`, and `AbstractFileSystem` integration.

Risks and test signals: failures usually expose mismatches between `FileSystem` and `FileContext` behavior, incorrect `remainingPath` delegation, internal-dir mutability, server-default propagation, or optimized listing fallback to less efficient APIs.
