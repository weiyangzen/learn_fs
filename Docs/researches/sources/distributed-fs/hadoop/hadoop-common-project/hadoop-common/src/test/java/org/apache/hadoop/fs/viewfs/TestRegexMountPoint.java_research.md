# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestRegexMountPoint.java

Purpose: tests regex-based mount points, destination variable extraction/substitution, and interceptor integration. The fixture builds an `InodeTree` with a normal `/mnt` link and anonymous target filesystem factory, then constructs `RegexMountPoint` instances directly.

Important APIs and types: `RegexMountPoint.initialize()`, `RegexMountPoint.getVarInDestPathMap()`, `RegexMountPoint.resolve()`, `RegexMountPointResolvedDstPathReplaceInterceptor`, `ConfigUtil.addLink`, and `InodeTree.ResolveResult`. The inner `TestRegexMountPointFileSystem` records the URI passed by regex resolution.

Control flow: `testGetVarListInString` parses `$0`, `$1`, `${1}`, and `${2}` references and asserts grouping by capture index. `testResolve` matches `^/user/(?<username>\\w+)`, maps `$username` into `/namenode1/testResolve/...`, and verifies the remaining suffix. `testResolveWithInterceptor` serializes a replace interceptor and confirms underscores in the resolved destination are rewritten while the source/remaining path is not.

State and persistence: all state is in test-local configuration and `RegexMountPoint` fields; no real filesystem mutation occurs.

Dependencies and integration: validates the regex mount feature used by `InodeTree` resolution and viewfs mount-table config. It depends on Java regex named groups and Hadoop path semantics.

Risks and test signals: watch for capture variable parsing ambiguity, incorrect `resolvedPath` length, URI construction that drops leading slashes, and interceptor application to the wrong path component.
