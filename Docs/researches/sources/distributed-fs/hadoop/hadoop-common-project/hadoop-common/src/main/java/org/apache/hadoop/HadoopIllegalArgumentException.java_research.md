# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/HadoopIllegalArgumentException.java

Purpose: Hadoop-specific subclass of `IllegalArgumentException` used to distinguish invalid arguments raised by Hadoop implementation code from plain JDK argument exceptions. The source was read as a complete 40-line Java file.

Important APIs/functions: public stable class `HadoopIllegalArgumentException extends IllegalArgumentException`, `serialVersionUID = 1L`, and constructor `HadoopIllegalArgumentException(String message)`.

Control flow: construction delegates directly to `super(message)`. There is no additional behavior.

State and persistence: stores only the inherited exception message and stack trace. Serializable identity is fixed by `serialVersionUID`.

Dependencies and integration: annotated with `InterfaceAudience.Public` and `InterfaceStability.Stable`, so it is part of Hadoop's public API surface. Used by Hadoop callers that want to catch Hadoop-originated invalid argument failures.

Risks: because it subclasses `IllegalArgumentException`, broad JDK exception handlers will still catch it. Adding constructors or behavior would be API-visible. The class carries no cause-taking constructor, so callers that need exception chaining must use another exception or lose cause information.

Test signals: compile/API compatibility checks, serialization compatibility if exposed across boundaries, and unit tests that assert Hadoop APIs throw this type for documented invalid arguments.
