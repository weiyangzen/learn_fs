# sources/cloud-native/buildkit/sourcepolicy/policysession/provider.go

## Purpose
Server-side adapter for the PolicyVerifier gRPC service. PolicyCallback returns either a final DecisionResponse or a ResolveSourceMetaRequest asking the client/front-end to resolve more metadata.

## Important APIs, Types, And Functions
Package: `policysession`. Build tags: `none`. Key declarations observed in the file: `PolicyCallback, PolicyProvider, NewPolicyProvider, CheckPolicy, Register`.

## Control Flow, State, And Persistence
CheckPolicy delegates to the callback and enforces the oneof invariant that decision and meta request cannot both be returned. Register binds the provider to a grpc.Server.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/frontend/gateway/pb, github.com/pkg/errors, google.golang.org/grpc`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is callback contract misuse causing an error response. Tests are not local; generated gRPC and verifier integration are the main signals.
