# sources/control-plane/beegfs-csi-driver/pkg/beegfs/server.go

Purpose: Provides gRPC server plumbing and logging/error helpers for the BeeGFS CSI driver. It creates a non-blocking CSI gRPC server, parses endpoints, wraps requests with request IDs, sanitizes logged protobufs, and maps rich internal errors to gRPC status errors.

Important APIs/types/functions: `contextKey`, `ctxRequestIDKey`, and `requestIDCounter` implement request IDs. `grpcError` stores both a gRPC status error and an underlying `github.com/pkg/errors` cause with stack formatting; `newGrpcErrorFromCause` constructs it. `nonBlockingGRPCServer` exposes `Start`, `Wait`, `Stop`, `ForceStop`, and `serve`. `parseEndpoint` accepts `unix://` and `tcp://` endpoints. `logGRPC` is a unary interceptor. `generateRequestContext`, `logger`, `LogDebug`, `LogVerbose`, `LogError`, and `LogFatal` centralize logging.

Control flow: `Start` increments a wait group and launches `serve`. `serve` parses endpoint, removes stale Unix socket files, listens, constructs a gRPC server with `logGRPC`, registers non-nil identity/controller/node services, and serves until stopped or fatal error. `logGRPC` assigns a request ID, logs a sanitized request, invokes the handler, logs sanitized response or full error, and unwraps `grpcError` to send only the status error over gRPC.

State and persistence: State includes the active `grpc.Server`, a wait group, request ID counter, and optional Unix socket file removal. Logging writes through klog/klogr. Fatal logging exits the process with status 255.

Dependencies and integration points: Uses CSI protobuf service registration, gRPC, CSI lib `protosanitizer` for secret stripping, `go-logr`/`klogr` for logging, and shared `pkg/errors` stack traces. All CSI service implementations rely on `newGrpcErrorFromCause` and logging helpers.

Risks: `Stop` and `ForceStop` assume `s.server` is initialized; calling before `serve` assigns it could panic. `serve` logs `grpc.ErrServerStopped` as an error even though it can be normal shutdown. Request ID counter wraps at 65536, which is acceptable for log correlation but not globally unique. `parseEndpoint` does not validate protocol beyond prefix or address content beyond nonempty suffix.

Test signals: `server_test.go` specifically checks secret redaction through logging infrastructure. CSI sanity tests exercise server registration and request handling.
