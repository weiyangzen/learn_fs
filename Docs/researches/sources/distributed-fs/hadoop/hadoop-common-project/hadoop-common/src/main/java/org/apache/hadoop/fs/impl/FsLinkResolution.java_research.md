# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FsLinkResolution.java

## Purpose
Lambda-friendly adapter over FSLinkResolver for FileContext symlink resolution.

## Important APIs, Types, and Functions
FsLinkResolutionFunction<T>; constructor; next(AbstractFileSystem,Path); static resolve(FileContext,Path,fn).

## Control Flow
FSLinkResolver drives resolution and invokes next for each resolved AbstractFileSystem/path; next delegates to the supplied function.

## State and Persistence Behavior
Stores one function reference. No persistence.

## Dependencies and Integration Points
Depends on FSLinkResolver, FileContext, AbstractFileSystem, Path, UnresolvedLinkException.

## Risks and Test Signals
Risks are exception propagation and null function rejection. Tests should cover successful resolution, unresolved links, and IOException passthrough.
