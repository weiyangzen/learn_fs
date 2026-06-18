## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileAlreadyExistsException.java

Purpose: `FileAlreadyExistsException` is a public stable checked exception used when a target file already exists and the requested operation is not configured to overwrite or append.

Important APIs and types: it extends `IOException` and exposes default and message constructors.

Control flow, state, and persistence: there is no custom behavior or mutable state. Normal `IOException` serialization and message handling apply.

Dependencies and integration: create paths, especially `CreateFlag.validate`, throw this exception to distinguish existing-target failures from generic IO failures. Filesystem clients can catch it to retry with overwrite, choose a different path, or report idempotency conflicts.

Risks and test signals: risks are low, but callers rely on this specific type for create semantics. Tests should verify message preservation and use in create validation and filesystem implementations when `CREATE` is used without overwrite/append against an existing path.
