# sources/cloud-native/buildkit/sourcepolicy/policysession/verifier.go

## Purpose
Client-side session adapter for policy verification. It locates a BuildKit session by group id and constructs a generated PolicyVerifierClient over the session connection.

## Important APIs, Types, And Functions
Package: `policysession`. Build tags: `none`. Key declarations observed in the file: `NewVerifier, PolicyVerifier, Check`.

## Control Flow, State, And Persistence
NewVerifier depends on session.Manager.Get(ctx,gid,false); Check is a thin unary RPC wrapper over CheckPolicy. It holds no persistent state beyond the client handle.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/session`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is session lookup or RPC failure surfacing directly to callers. Test signal is integration-level because this file has no local test.
