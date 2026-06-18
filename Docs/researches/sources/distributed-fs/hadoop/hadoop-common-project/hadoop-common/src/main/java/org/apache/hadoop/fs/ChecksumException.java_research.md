## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ChecksumException.java

Purpose: stable public `IOException` subtype indicating a checksum mismatch or malformed checksum data at a file position.

Important APIs and types: constructor stores a description and long position; `getPos()` returns the position.

Control flow: simple exception data holder.

State and persistence behavior: serializable exception state includes message and position; no persistence.

Dependencies and integration points: thrown by `FSInputChecker`, `ChecksumFileSystem`, `ChecksumFs`, and checksum-aware streams.

Risks: position can be any caller-supplied long; code catching generic `IOException` may lose checksum-specific diagnostics unless it checks this type.

Test signals: verify message, position, serialization compatibility, and propagation through checksum read paths.
