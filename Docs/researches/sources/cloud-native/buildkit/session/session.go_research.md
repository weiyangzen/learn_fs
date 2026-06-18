## sources/cloud-native/buildkit/session/session.go

Purpose: implements the client-side BuildKit session object: a long-lived h2c gRPC server exposed over a caller-provided `Dialer`. It lets frontends attach services such as SSH, upload, secrets, and auth to one bidirectional control connection.

Important APIs/types/functions: `Dialer` is the transport hook; `Attachable` registers a service on a `grpc.Server`; `Session` owns id, shared key, cancellation, server, net connection, and close state. `NewSession` creates the server with BuildKit grpc error interceptors, health service, and optional OpenTelemetry stats handler inherited from the input context. `Allow` registers attachables. `Run` builds session metadata containing id, shared key, and every exposed method URL, dials h2c, then serves gRPC on the returned connection. `Close` closes the connection, stops the server, waits for `Run`, and marks the session closed. `MethodURL` formats `/service/method`.

Control flow: `Run` serializes startup with `mu`, refuses work after `Close`, sets a cancel cause and `done` channel, advertises registered services in metadata, dials, releases the lock, then calls `serve`. `Close` holds the same lock while closing conn/server and waiting for `done`, so concurrent close/run paths are serialized.

State and persistence: all state is in memory. The durable-ish identity is the generated session id and caller supplied shared key, only propagated as connection metadata.

Dependencies and integration points: uses `identity`, `grpcerrors`, tracing/otelgrpc, gRPC health, and the unshown `serve` helper in this package. Consumers use `session.Caller` on the daemon side to call registered services.

Risks and test signals: `context()`/`closed()` depend on `s.ctx`, but this file never assigns it; callers should not rely on those helpers unless set elsewhere. Close waits under the mutex, so a broken serve path could stall close. Test coverage is indirect through session helpers and feature-specific providers.
