# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ChRootedFileSystem.java

`ChRootedFileSystem` is a private `FilterFileSystem` wrapper that makes a target `FileSystem` appear rooted at a configured URI path. It is the concrete target wrapper used by `ViewFileSystem` links: view paths are resolved to a remaining path, and this class prefixes that remaining path with the mount target root before delegating to the raw filesystem.

Important state is `myUri`, `chRootPathPart`, `chRootPathPartString`, and `workingDir`. The core API is `fullPath(Path)`, which validates the incoming path with `checkPath` and maps absolute paths to `chRootPathPart + path`, while relative paths are resolved under the chrooted working directory. `stripOutRoot(Path)` is the inverse helper used by viewfs status rewriting and nfly status wrapping. `getMyFs()` exposes the raw target filesystem for operations such as cross-mount rename when the rename policy permits it.

Control flow is intentionally repetitive: create, open, delete, list, ACL, xattr, snapshot, checksum, storage-policy, and capability methods all call `fullPath()` and then delegate to `super` or the wrapped `fs`. This keeps persistence in the underlying filesystem; this wrapper stores only process-local URI and working-directory state. `createFile()` and `openFile()` also prefix paths before returning builder APIs.

Dependencies include Hadoop `FileSystem`, `FilterFileSystem`, `Path`, permission/ACL/xattr types, and `ViewFsFileStatus` for block-location path rewriting. Integration points are `ViewFileSystem.InodeTree` target initialization, `NflyFSystem.NflyNode`, and `ViewFileSystem.getChrootedPath`.

Risks are concentrated in path string concatenation, URI qualification edge cases, and inverse root stripping. Tests should cover root chroot (`/`), non-root chroot, relative working directories, `stripOutRoot` boundary paths, all delegated metadata methods, builder APIs, and rename/status interactions through `ViewFileSystem`.
