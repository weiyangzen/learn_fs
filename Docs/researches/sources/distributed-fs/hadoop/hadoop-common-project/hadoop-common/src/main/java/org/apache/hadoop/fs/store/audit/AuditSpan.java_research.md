# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditSpan.java

Purpose: private unstable interface representing an audit span that can be activated/deactivated in a thread and carry operation metadata.

Important APIs, types, and functions: `getSpanId()`, `getOperationName()`, `getTimestamp()`, `activate()`, `deactivate()`, default `close()`, default `isValidSpan()`, and default `set()`.

Control flow: spans are activated for filesystem operations and remain active until deactivated/closed. `close()` delegates to `deactivate()` for try-with-resources use; implementations may expose invalid fallback spans.

State and persistence: no state in the interface. Implementations carry span IDs, operation names, timestamps, attributes, and thread activation state.

Dependencies and integration points: extends `Closeable` and is used by `AuditSpanSource`, `ActiveThreadSpanSource`, `AuditingFunctions`, and object-store auditors.

Risks and test signals: there is no span stack, so activating a span replaces previous active context in implementations. Tests should cover close/deactivate semantics, invalid spans, attribute setting, unique IDs, and multi-thread activation behavior.
