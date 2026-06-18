# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestNestedMountPoint.java

Purpose: unit-tests nested mount point support in `InodeTree`, especially longest-prefix matching, internal directory handling, fallback links, and `resolveLastComponent` behavior. The fixture creates a `Configuration`, enables nested mount points with `ConfigUtil.setIsNestedMountPointSupported`, adds six overlapping links such as `/a/b`, `/a/b/c/d/e`, `/b/c/d/e/f`, and a fallback target, then constructs an anonymous `InodeTree<TestNestMountPointFileSystem>`.

Important APIs and types: `InodeTree.resolve(String, boolean)`, `InodeTree.ResolveResult`, `InodeTree.ResultKind`, `ConfigUtil.addLink`, `ConfigUtil.addLinkFallback`, `FsConstants.VIEWFS_SCHEME`, `Path`, and local stub target filesystem classes that expose only `URI getUri()`. The anonymous tree overrides target filesystem creation for external links and internal dirs.

Control flow: each test resolves a path and asserts `kind`, `resolvedPath`, `remainingPath`, target URI/type, and `isLastInternalDirLink()`. The tests compare exact behavior when the last component should be consumed versus left unresolved. State is in-memory only and reset per test; there is no persistent filesystem IO.

Dependencies and integration: this is a direct regression suite for `InodeTree`, not `ViewFileSystem`. It validates mount-table semantics consumed by both `ViewFs` and `ViewFileSystem`.

Risks and test signals: high-value edge cases include nested links that shadow ancestors, fallback suppression when `resolveLastComponent` is false, root resolution, and mount point enumeration count. A regression usually appears as incorrect resolved prefix, wrong remaining path, fallback activation at the wrong time, or internal dirs returned as external links.
