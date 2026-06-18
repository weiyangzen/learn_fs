<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/lang/XException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/lang/XException.java

## Purpose
`XException` is the base checked exception for this service framework. It standardizes coded errors with `MessageFormat` templates and optional throwable causes.

## Important APIs, Types, And Functions
Nested interface `ERROR` requires `getTemplate()`. Constructors support wrapping another `XException` while preserving its code/message, or building a new exception from an error code and parameters. `getError()` returns the code. Static helpers `format` and `getCause` build the message and treat the final vararg as the cause if it is a `Throwable`.

## Control Flow
Subclasses such as `ServerException`, `ServiceException`, and `FileSystemAccessException` define enums implementing `ERROR`, then delegate construction to `XException`.

## State And Persistence
Instances store the error code and inherited message/cause. No persistence exists.

## Dependencies And Integration Points
It depends on `MessageFormat` and Hadoop `Check`. It is the common error contract for server/service initialization and filesystem access failures.

## Risks
If an error template is null, a positional fallback template is generated from all parameters, including a trailing throwable. `MessageFormat` syntax has quoting rules that can surprise authors of new templates. The wrapped-`XException` constructor uses the cause's formatted message rather than reformating.

## Test Signals
Tests should cover template formatting, null-template fallback, cause extraction only from the last arg, error preservation when wrapping, and subclass enum formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/lang/XException.java -->
