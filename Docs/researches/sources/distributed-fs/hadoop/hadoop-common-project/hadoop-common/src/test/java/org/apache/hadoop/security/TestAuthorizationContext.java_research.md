# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestAuthorizationContext.java

Purpose: Tests thread-local storage of current authorization header bytes.

Important APIs/types/functions: `AuthorizationContext.setCurrentAuthorizationHeader`, `getCurrentAuthorizationHeader`, `clear`, and `SubjectInheritingThread`.

Control flow: tests set/get in the same thread, clear behavior, isolation between main and child thread, and null/empty byte-array handling. The child thread asserts it starts without the main thread's header, sets its own, clears it, and leaves main state unchanged.

State and persistence: thread-local authorization header state.

Dependencies/integration points: security/RPC code that needs per-thread authorization metadata and Hadoop subject-inheriting thread wrapper.

Risks: byte arrays are mutable; tests do not check defensive copying. Thread-local cleanup is essential to avoid leakage in pooled threads.

Test signals: confirms basic lifecycle, null semantics, and cross-thread isolation of authorization context.
