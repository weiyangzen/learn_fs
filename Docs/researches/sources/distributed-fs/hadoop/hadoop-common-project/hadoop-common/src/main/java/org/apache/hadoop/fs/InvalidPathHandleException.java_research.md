# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InvalidPathHandleException.java

Purpose: `InvalidPathHandleException` reports that constraints encoded in a `PathHandle` no longer hold when opening or resolving a handle.

Important APIs: constructors with message and message/cause.

Control flow and state: extends `IOException` with a fixed serial version. It carries only normal exception state.

Dependencies and integration: used by `FileSystem.open(PathHandle)` and implementations honoring `Options.HandleOpt` constraints such as path identity or content identity.

Risks: callers must distinguish invalid handles from missing files and other IO failures. Implementations need to preserve causes for diagnostics.

Test signals: stale/mismatched path handles, cause propagation, open-by-handle failure modes, and compatibility with handle option semantics.
