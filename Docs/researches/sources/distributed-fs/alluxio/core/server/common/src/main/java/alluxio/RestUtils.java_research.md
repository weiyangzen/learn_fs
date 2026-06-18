## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/RestUtils.java

### Purpose
`RestUtils` centralizes REST endpoint invocation, authentication user setup, response creation, and exception-to-error-response conversion.

### Important APIs, Types, And Functions
`call(RestCallable<T>, AlluxioConfiguration, Map<String,Object>)` and overload without headers wrap endpoint logic. `RestCallable<T>` is the endpoint functional interface. `ErrorResponse` carries gRPC status code and message. Private `createResponse` handles success values, and `createErrorResponse` maps exceptions through `AlluxioStatusException`.

### Control Flow
Before invoking an endpoint, `call` sets `AuthenticatedClientUser` from `ServerUserState.global()` when security is enabled and no client user is set. It returns an error response if that setup fails. It then invokes the callable, creates an OK response, or catches any exception and returns a server-error response entity.

### State And Persistence
It may set thread-local/authenticated client user state. No persistence.

### Dependencies And Integration Points
Used by Alluxio REST resources. Depends on JAX-RS `Response`, Jackson `ObjectMapper`, gRPC `Status`, security utilities, and Alluxio status exceptions.

### Risks
All endpoint exceptions produce HTTP 500 via `Response.serverError()` even though the entity carries a more specific gRPC status code. String responses are explicitly JSON-encoded but headers are not applied in the string branch. Void handling checks `object instanceof Void`, which does not catch null returns.

### Test Signals
No direct test in this subset. REST endpoint tests should check JSON string behavior, error entities, headers, and auth setup.
