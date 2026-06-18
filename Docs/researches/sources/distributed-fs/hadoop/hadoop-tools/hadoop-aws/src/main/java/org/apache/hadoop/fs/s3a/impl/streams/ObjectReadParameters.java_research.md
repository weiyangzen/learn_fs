<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectReadParameters.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectReadParameters.java

Purpose: mutable builder-style parameter object for object stream creation. It centralizes read context, object metadata, callbacks, statistics, executors, local storage, encryption, and audit span inputs so factory APIs stay stable.

Important APIs/types/functions: getters and `with...()` setters cover `S3AReadOpContext`, `S3ObjectAttributes`, `ObjectInputStreamCallbacks`, `S3AInputStreamStatistics`, bounded `ExecutorService`, `LocalDirAllocator`, `EncryptionSecrets`, and `AuditSpan`. `validate()` requires every required field with `requireNonNull()` and returns `this`.

Control flow: callers populate the object, usually validate it near stream creation, then pass it into `ObjectInputStreamFactory.readObject()`. The setters do not freeze or clone values, so later mutation by the caller remains visible.

State/persistence: keeps in-memory references only. No external persistence. Because validation is not immutability, the object is not a safe long-lived immutable configuration snapshot.

Dependencies/integration: bridges S3A read planning (`S3AReadOpContext`), metadata (`S3ObjectAttributes`), auditing, encryption, local temp allocation, statistics, and executor resources into classic, analytics, or prefetch stream factories.

Risks/test signals: missing required parameters fail late at validation or stream construction. Tests should assert all mandatory fields are checked, builder chaining preserves object identity, and factories consume the expected executor, allocator, encryption secrets, and audit span.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectReadParameters.java -->
