# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/InvocationRaisingIOE.java

`InvocationRaisingIOE` is the void-returning, zero-argument checked-IO lambda type. It represents an operation that may throw `IOException` without returning a value.

The API is a single `apply()` method. There are no default wrappers, fields, persistence, or synchronization. Dependencies are limited to `IOException`. The Javadoc explains the design motivation: Hadoop has several historical void-callable interfaces, and this package aims to consolidate the pattern. It also warns API implementors not to rely on overloads to distinguish functional interface types, because lambda target typing can become ambiguous.

Integration is conceptual with `RunnableRaisingIOE` and `CallableRaisingIOE`: use this interface when the call should remain checked and not implement `Runnable`; use `RunnableRaisingIOE` when Java executor APIs are the target. Risks are low but include caller inconvenience when crossing into Java APIs because there is no built-in unchecked adapter on this interface. Test coverage is indirect through package compilation and neighboring functional wrapper tests.
