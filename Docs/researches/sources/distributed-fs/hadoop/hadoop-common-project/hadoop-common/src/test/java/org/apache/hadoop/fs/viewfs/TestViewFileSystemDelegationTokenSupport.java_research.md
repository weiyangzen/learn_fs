# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemDelegationTokenSupport.java

Purpose: tests `ViewFileSystem` delegation-token behavior, canonical service naming, child filesystem discovery, and duplicate-token suppression when several mount links reference the same child filesystem.

Important APIs and types: `FileSystem.addDelegationTokens`, `getCanonicalServiceName`, `getChildFileSystems`, `Credentials`, `Token`, `Text`, `ConfigUtil.addLink`, `FsConstants.VIEWFS_URI`, and a `FakeFileSystem` extending `RawLocalFileSystem`.

Control flow: static setup registers two fake schemes and mounts each twice. The canonical service name tests cover default and named mount tables and assert viewfs returns `null`. `testGetChildFileSystems` asserts duplicate mount links collapse to two child filesystems. `testAddDelegationTokens` first fetches tokens directly from children, then through viewfs, and confirms existing credentials prevent refetch.

State and persistence: fake filesystems keep only URI state and synthesize a token whose service is URI plus object hash. Credentials are in-memory.

Dependencies and integration: protects token aggregation for security flows where clients obtain tokens from viewfs but services use tokens from mounted filesystems.

Risks and test signals: regressions include duplicate tokens per mount, missing child tokens, non-null canonical service names for viewfs, or failure to honor existing credentials.
