# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeFormatException.java

## Purpose
`NameNodeFormatException` is a specific `IOException` used when NameNode formatting is rejected or fails for semantic reasons, such as reformat being disabled while metadata already exists.

## Important APIs and Types
- Public constructor `NameNodeFormatException(String message, Throwable cause)`.
- Public constructor `NameNodeFormatException(String message)`.
- `serialVersionUID` is defined for exception serialization compatibility.

## Control Flow
The class has no logic beyond exception construction. Higher-level format code throws it to distinguish format failures from generic I/O failures while preserving `IOException` compatibility.

## State and Persistence Behavior
No state beyond the exception message/cause. It does not perform persistence; it reports decisions made by `NameNode.format` and related format checks.

## Dependencies and Integration Points
It extends `java.io.IOException`, is annotated `@InterfaceAudience.Private`, and is used by `NameNode.format` when reformat is disabled by configuration and existing storage data is detected.

## Risks and Edge Cases
Because it is an `IOException`, callers that catch broad I/O failures may not distinguish operator-policy format aborts unless they check the concrete type or message. That is acceptable for current internal use but limits machine-readable failure handling.

## Test Signals
Format tests such as `TestStartup` and NameNode format/configuration tests are the expected integration coverage. A focused test should assert this exception type when `dfs.reformat.disabled` blocks formatting.
