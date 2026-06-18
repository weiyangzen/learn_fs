# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InvalidPathException.java

Purpose: `InvalidPathException` reports invalid Hadoop path strings or filesystem-specific path validation failures.

Important APIs: constructors accepting `path` and optional `reason`.

Control flow and state: extends `HadoopIllegalArgumentException`, formats a stable message, and carries only exception state. Null reason is omitted from the formatted message.

Dependencies and integration: thrown by path parsing/validation code and public filesystem APIs where invalid input is a caller argument error.

Risks: message text can be asserted by tests or users. It is unchecked via Hadoop's illegal argument type, so callers may not catch it as `IOException`.

Test signals: message formatting with and without reason, invalid characters, scheme-specific path validation, and compatibility with public API error expectations.
