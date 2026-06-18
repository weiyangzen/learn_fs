<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/CompressedWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/CompressedWritable.java

Purpose: abstract writable base that stores its subclass fields in compressed form and inflates lazily on field access.

Important APIs, types, and functions: final `readFields()` reads compressed bytes. `ensureInflated()` inflates through `InflaterInputStream` and calls subclass `readFieldsCompressed()`. final `write()` compresses current fields through `writeCompressed()` with `Deflater.BEST_SPEED`, caches compressed bytes, and writes length plus bytes.

Control flow: after deserialization, data stays compressed until a subclass method calls `ensureInflated()`. On serialization, uncompressed state is compressed once and then reused until fields are modified by subclass logic.

State and persistence: state is the cached compressed byte array or null when inflated. Serialized form is compressed length and compressed payload.

Dependencies and integration points: used by large writable subclasses that benefit from lazy inflation and fast copying.

Risks and test signals: subclasses must call `ensureInflated()` before reading fields and must clear/update compressed cache if mutating fields. `ensureInflated()` wraps IOExceptions in RuntimeException. Tests should cover lazy read, repeated write cache reuse, mutation invalidation in subclasses, corrupt compressed data, and round-trip compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/CompressedWritable.java -->
