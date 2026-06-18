## sources/cloud-native/buildkit/util/grpcerrors/intercept.go

Purpose: gRPC server/client interceptors that automatically encode outgoing BuildKit errors and decode incoming gRPC errors.

Important APIs: `UnaryServerInterceptor`, `StreamServerInterceptor`, `UnaryClientInterceptor`, `StreamClientInterceptor`.

Control flow: server unary/stream handlers pass errors through `ToGRPC` and call `stack.Helper` when errors are present. Unary server defends against invalid conversion returning nil by logging or panicking under `BUILDKIT_DEBUG_PANIC_ON_ERROR`, then restoring the original error. Client unary decodes with `FromGRPC`; stream client currently returns `ToGRPC(ctx, err)` for streamer errors.

State/persistence: stateless middleware except environment-variable panic behavior. Dependencies: gRPC, BuildKit stack, `log`, `os`.

Integration points: plugged into BuildKit gRPC server/client setup. Risks: stream client uses `ToGRPC` rather than `FromGRPC`, which is notable because unary client decodes remote errors; may be intentional for local streamer setup errors but deserves care. Test signals: indirect through `grpcerrors_test.go`; no interceptor-specific tests here.
