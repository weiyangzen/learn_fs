# sources/cloud-native/buildkit/sourcepolicy/policysession/denyerror.go

## Purpose
Typed deny-message error propagation for source policy decisions. It registers DecisionResponse with typeurl, wraps ordinary errors with repeated DenyMessage details, exposes Unwrap/ToProto for grpcerrors, and recursively extracts messages from an error chain.

## Important APIs, Types, And Functions
Package: `policysession`. Build tags: `none`. Key declarations observed in the file: `init, DenyMessagesError, Unwrap, ToProto, WrapDenyMessages, DenyMessages, WrapError`.

## Control Flow, State, And Persistence
The only state is the error chain; no persistence. Control flow preserves the wrapped error as the causal error and appends nested deny messages outermost after recursively collected inner messages.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/typeurl/v2, github.com/moby/buildkit/sourcepolicy/pb, github.com/moby/buildkit/util/grpcerrors, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is loss of user-facing policy diagnostics if callers wrap errors without preserving the chain. Test signal is indirect through grpc typed error handling and policy-session use, not a local unit test.
