# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSExceptionsProvider.java

## Purpose
`KMSExceptionsProvider.java` is the Jersey `ExceptionMapper` that converts server exceptions into HTTP responses and audit/error logs.

## Important APIs, Types, and Functions
`toResponse` performs status mapping. `createResponse` delegates to `HttpExceptionUtils.createJerseyExceptionResponse`. `getOneLineMessage` strips multiline exception messages at the platform line separator. `log` emits detailed warnings including UGI, method, URL, remote address, status, and message from `KMSMDCFilter`.

## Control Flow
The mapper unwraps Jersey `ContainerException` to its cause for classification. Security, authentication, authorization, and access-control failures map to 403; unsupported operations and illegal arguments map to 400; I/O and unknown exceptions map to 500. Authentication and authorization exceptions skip duplicate audit because access checks already audited them. Other exceptions produce KMS audit `ERROR` events.

## State and Persistence
No mutable state is kept. Persistence is through audit logging and HTTP response payloads.

## Dependencies and Integration Points
It relies on `KMSMDCFilter` request context, `KMSWebApp.getKMSAudit()`, Jersey exception mapping, Hadoop security exceptions, and `HttpExceptionUtils`. It is discovered by Jersey because `web.xml` scans the server package.

## Risks
The code checks `exception instanceof IOException` rather than `throwable instanceof IOException` after unwrapping, so an `IOException` inside `ContainerException` may be classified as generic 500 without the specific branch. Audit context can be null if the MDC filter did not run. Error payloads expose exception-derived messages, so callers may see provider details.

## Test Signals
Tests should cover every exception category, `ContainerException` unwrapping, duplicate-audit suppression for authorization failures, one-line message truncation, and response body compatibility.
