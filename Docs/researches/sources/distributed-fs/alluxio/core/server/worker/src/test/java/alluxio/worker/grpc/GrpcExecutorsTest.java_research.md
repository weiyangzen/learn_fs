# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/GrpcExecutorsTest.java

Purpose: verifies worker gRPC executor wrappers propagate authenticated client user context into worker threads.

Important APIs and helpers: setup and teardown manipulate `AuthenticatedClientUser`. `validateAuthenticatedClientUser(ExecutorService)` submits tasks under two different context users and asserts `AuthenticatedClientUser.getClientUser()` inside the executor matches the caller context.

Control flow and state: each test obtains an executor from `GrpcExecutors` for block reader, block writer, or async cache manager work. The caller context is changed between submissions to ensure wrapping is per-task rather than a stale thread-local value.

Dependencies and integration: depends on `GrpcExecutors`, `AuthenticatedClientUser`, `AuthenticatedUserInfo`, and Java `ExecutorService`.

Risks and test signals: strong signal for security/impersonation context propagation. It does not validate executor sizing, shutdown, or exception handling.
