# sources/cloud-native/buildkit/api/services/control/control_grpc.pb.go

## Purpose
Generated gRPC bindings for the BuildKit Control service. It exposes typed clients, server interfaces, registration, stream aliases, method handlers, and `grpc.ServiceDesc`.

## APIs, Types, And Flow
Exports full method-name constants, `ControlClient`, concrete `controlClient`, `NewControlClient`, `ControlServer`, `UnimplementedControlServer`, `UnsafeControlServer`, `RegisterControlServer`, stream aliases, unary handlers, streaming handlers, and `Control_ServiceDesc`. Client methods use `cc.Invoke` for unary calls and `cc.NewStream` plus generic client streams for server/bidi streams. Server handlers decode requests, invoke interceptors for unary calls, and wrap streams in generic server stream types. Registration verifies `UnimplementedControlServer` is embedded by value to avoid nil pointer panics.

## Dependencies And Integration
Requires gRPC-Go v1.64+ (`SupportPackageIsVersion9`) and the message types from `control.pb.go`. BuildKit clients call `NewControlClient`; daemon-side control implementations register with `RegisterControlServer`.

## State, Risks, And Test Signals
No state is stored here beyond stream lifetimes; runtime state is in the server implementation and gRPC transport. Risks include direct edits to generated code, mismatched gRPC/protobuf generator versions, changed service methods without server implementation updates, and streaming cancellation/CloseSend regressions. Test signals are Go compile, gRPC integration tests for solve/status/session/history/prune, and generated-file validation.
