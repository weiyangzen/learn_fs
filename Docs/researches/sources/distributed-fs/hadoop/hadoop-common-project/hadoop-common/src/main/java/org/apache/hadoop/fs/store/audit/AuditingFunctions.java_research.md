# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditingFunctions.java

Purpose: static helpers that wrap callables/functions/invocations so a supplied audit span is active when the wrapped work executes.

Important APIs, types, and functions: overloaded `withinAuditSpan()` methods for `CallableRaisingIOE`, `InvocationRaisingIOE`, `FunctionRaisingIOE`, and Java `Callable`.

Control flow: if the span is null, the original operation is returned. Otherwise, the wrapper calls `auditSpan.activate()` immediately before invoking the operation. It intentionally does not deactivate afterward so chained operations in the same thread keep the span active.

State and persistence: stateless utility class. Span state is managed by the supplied `AuditSpan` implementation.

Dependencies and integration points: depends on Hadoop functional interfaces and Java callable. Used when dispatching filesystem work across asynchronous or callback boundaries while preserving audit context.

Risks and test signals: comments mention deactivate around invocation, but implementation does not deactivate; tests should lock in the intended active-span propagation semantics. Also test null span passthrough, exception propagation, and activation on every invocation.
