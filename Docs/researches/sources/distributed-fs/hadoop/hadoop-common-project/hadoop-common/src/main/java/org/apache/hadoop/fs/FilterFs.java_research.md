# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FilterFs.java

Purpose: `FilterFs` is the `AbstractFileSystem` equivalent of `FilterFileSystem`: a private/evolving base for wrapping another `AbstractFileSystem` and forwarding operations so subclasses can transform selected behavior.

Important APIs: constructor over an `AbstractFileSystem`, `getMyFs`, statistics and URI methods, create/delete/status/list/open/mkdir/rename/setters, symlink support, delegation tokens, ACL/xattr/snapshot/storage-policy APIs, async open options, multipart uploader, capabilities, and enclosing-root lookup.

Control flow and state: it stores final `myFs` and initializes its superclass from the wrapped URI/scheme/default port. Most path-affecting methods call `checkPath` before delegation; some methods such as `getFsStatus(Path)`, `resolvePath`, `renameInternal(src,dst,overwrite)`, `createSymlink`, and ACL/xattr methods delegate directly and rely on wrapped implementation validation. No persistent state is introduced beyond the wrapped reference.

Dependencies and integration: used by `DelegateToFileSystem`/`FileContext` paths where `AbstractFileSystem` is the API boundary. It integrates with `Options.ChecksumOpt`, `OpenFileParameters`, ACLs, xattrs, snapshots, storage policies, tokens, and multipart upload builders.

Risks: inconsistent explicit `checkPath` coverage means subclasses relying on wrapper-level path validation may need to override more methods. It preserves wrapped statistics and capabilities exactly, so wrapper-added behavior must be reflected by overrides. Constructor errors propagate as `URISyntaxException`.

Test signals: exercise path validation on create/delete/open/rename, direct delegation methods, capability pass-through, token pass-through, and subclass overrides that enforce transformed URI or authorization semantics.
