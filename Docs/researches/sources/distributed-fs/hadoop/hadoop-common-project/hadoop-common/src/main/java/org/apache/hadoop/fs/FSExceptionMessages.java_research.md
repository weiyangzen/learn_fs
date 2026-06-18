## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSExceptionMessages.java

Purpose: `FSExceptionMessages` centralizes standard filesystem exception message strings, using HDFS wording as the reference for common stream, seek, EOF, buffer, permission, sticky-bit, and abort unsupported errors.

Important APIs and types: it is a public constants class exporting messages such as `STREAM_IS_CLOSED`, `NEGATIVE_SEEK`, `CANNOT_SEEK_PAST_EOF`, `EOF_IN_READ_FULLY`, `TOO_MANY_BYTES_FOR_DEST_BUFFER`, `PERMISSION_DENIED`, `PERMISSION_DENIED_BY_STICKY_BIT`, and `ABORTABLE_UNSUPPORTED`.

Control flow, state, and persistence: there is no runtime behavior or state. Constants are compile-time shared strings used by other filesystem classes.

Dependencies and integration: `FSInputChecker`, `FSInputStream`, `FSDataOutputStream`, and many filesystem implementations use these strings to keep diagnostics consistent across connectors.

Risks and test signals: risk is compatibility of exact messages in tests, logs, and user diagnostics. Tests should not overfit unnecessarily, but API-level tests may assert these constants where specific wording is part of a documented contract. Static analysis can catch duplicate divergent messages in filesystem code.
