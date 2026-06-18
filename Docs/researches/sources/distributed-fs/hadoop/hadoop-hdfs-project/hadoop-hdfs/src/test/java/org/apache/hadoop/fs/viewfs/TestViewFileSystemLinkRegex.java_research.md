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
