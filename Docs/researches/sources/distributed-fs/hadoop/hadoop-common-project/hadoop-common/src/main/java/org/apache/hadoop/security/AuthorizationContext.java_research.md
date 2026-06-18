# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AuthorizationContext.java


Purpose: `AuthorizationContext` provides a process-local thread context for carrying an authorization header byte array during RPC handling.

Important APIs and types: It is a final utility class with `setCurrentAuthorizationHeader(byte[])`, `getCurrentAuthorizationHeader()`, and `clear()`, backed by a static `ThreadLocal<byte[]>`.

Control flow and state: State is scoped to the current thread. Callers set a header before invoking authorization-sensitive code, consumers retrieve it from the same thread, and `clear()` removes it to prevent leakage into later work on pooled threads.

Dependencies and integration: It has no external dependencies beyond `ThreadLocal`. It integrates implicitly with RPC server/client code that wants to bridge an authorization header without expanding method signatures.

Risks and test signals: The primary risk is stale authorization data if `clear()` is not called in finally blocks around thread-pool work. Tests should cover isolation across threads and cleanup after exceptions.
