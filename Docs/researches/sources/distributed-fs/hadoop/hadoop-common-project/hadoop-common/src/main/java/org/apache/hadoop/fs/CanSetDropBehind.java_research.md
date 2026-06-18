## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CanSetDropBehind.java

Purpose: evolving stream capability interface for toggling drop-behind cache behavior.

Important APIs and types: `setDropBehind(Boolean dropCache)` accepts true/false or null to restore/default behavior, and may throw `IOException` or `UnsupportedOperationException`.

Control flow: interface only; stream implementations decide how to pass hints to OS/filesystem clients.

State and persistence behavior: no interface state. Implementations may mutate per-stream caching hints, not file contents.

Dependencies and integration points: used by streams exposed through `FSDataInputStream`/`FSDataOutputStream` and capability/probe paths.

Risks: null semantics and support vary by stream. Callers should handle unsupported operations even if the stream type is known.

Test signals: implementation tests should cover true, false, null, post-close calls, unsupported streams, and propagation to the underlying native/client cache hint.
