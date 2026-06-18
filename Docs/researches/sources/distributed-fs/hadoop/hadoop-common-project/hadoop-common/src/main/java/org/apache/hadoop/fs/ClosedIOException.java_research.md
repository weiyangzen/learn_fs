## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ClosedIOException.java

Purpose: unstable public `PathIOException` subtype for operations attempted against a closed stream, cache, or closable resource.

Important APIs and types: constructor accepts path string and custom message, delegating to `PathIOException`.

Control flow: exception data holder only.

State and persistence behavior: exception state is path and message; no persistence.

Dependencies and integration points: used by filesystem code that wants path-aware diagnostics for closed resources.

Risks: only provides one constructor; callers needing a cause must use another exception type or wrapping.

Test signals: verify path/message formatting from `PathIOException`, serialization behavior, and use in closed-resource code paths.
