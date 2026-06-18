## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSLinkResolver.java

Purpose: `FSLinkResolver<T>` is a generic helper used mainly by `FileContext` to run an operation while resolving symlinks, potentially across multiple `AbstractFileSystem` instances.

Important APIs and types: subclasses implement `next(AbstractFileSystem fs, Path p)`. `resolve(FileContext, Path)` loops through unresolved links until the operation succeeds. Static `qualifySymlinkTarget(URI, Path, Path)` qualifies absolute targets lacking scheme and authority against the current filesystem URI and link parent.

Control flow, state, and persistence: `resolve` starts with `fc.getFSofPath(path)`, calls `next`, and catches `UnresolvedLinkException`. If symlink resolution is disabled in `FileContext` or globally in `FileSystem`, it throws explanatory `IOException`s. It detects likely cycles using `FsConstants.MAX_PATH_LINKS`. Each resolved target may select a different filesystem. No state is persisted.

Dependencies and integration: it integrates `FileContext`, `AbstractFileSystem`, `FileSystem` symlink settings, `CommonConfigurationKeys`, `Path`, and `UnresolvedLinkException`.

Risks and test signals: risks include cycle detection boundary, target qualification across schemes, disabled symlink behavior, and partial targets that already include scheme or authority. Tests should cover relative/absolute target qualification, cross-filesystem symlinks, disabled resolution, global symlink disabling, loop limits, and operation success after multiple link hops.
