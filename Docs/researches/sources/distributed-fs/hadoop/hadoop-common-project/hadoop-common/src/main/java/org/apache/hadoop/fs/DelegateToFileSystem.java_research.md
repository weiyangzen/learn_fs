## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DelegateToFileSystem.java

Purpose: `DelegateToFileSystem` adapts an old `FileSystem` implementation to the newer `AbstractFileSystem` API used by `FileContext`. It forwards most filesystem operations after applying `AbstractFileSystem` path checks and initialization.

Important APIs and types: the constructor initializes the delegate, passes scheme/authority/default-port data to `AbstractFileSystem`, and shares statistics. Delegated operations include create, delete, block locations, checksums, status, listing, mkdir, open, truncate, rename, ownership/permission/times, symlinks, server defaults, delegation tokens, async open with options, and path capability checks.

Control flow, state, and persistence: `getDefaultPortIfDefined` converts `FileSystem.getDefaultPort() == 0` into `-1` to match `URI.getPort()` semantics. `createInternal` has meaningful local logic: when `createParent` is false, it verifies a present parent path, existing status, and directory type before calling `primitiveCreate`. `getFileLinkStatus` rewrites symlink targets from qualified to plain. No state is persisted beyond the delegate reference and shared statistics.

Dependencies and integration: this class is the bridge between `FileSystem`, `AbstractFileSystem`, `FileContext`, `Options.ChecksumOpt`, token APIs, permissions, and `OpenFileParameters`.

Risks and test signals: risks are behavioral mismatches between `FileSystem` and `AbstractFileSystem`, especially symlink qualification, default-port handling, parent creation semantics, and token list handling when `addDelegationTokens` returns null or empty arrays. Tests should exercise delegated path checks, create-parent branches, symlink targets, rename semantics, and capability forwarding.
