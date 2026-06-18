# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskFileCorruptException.java

Purpose: `DiskFileCorruptException` is a specific `IOException` used when the kernel reports low-level input/output errors that imply a disk file may be corrupt, for example bad media sectors.

Important APIs: it exposes two constructors: `(String msg, Throwable cause)` and `(String msg)`. It adds no fields or behavior beyond the type.

Control flow and state: this is a marker exception class. Callers can throw or catch it to distinguish likely disk-file corruption from ordinary IO failures. It has no mutable state besides inherited exception message/cause and no persistence behavior.

Dependencies and integration points: it depends only on `java.io.IOException`. It fits into DataNode disk-error handling paths that may mark blocks bad, schedule volume checks, or report failures to the NameNode.

Risks: because no extra metadata is stored, all context must be encoded in the message/cause by callers. Catching broad `IOException` before this type would erase its signal. It should be used only for actual disk-file corruption indications, not protocol/client disconnect errors.

Test signals: tests should assert cause preservation, type-based catch behavior, and integration with disk error paths that classify block or volume corruption.
