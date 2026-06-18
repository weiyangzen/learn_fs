# sources/cloud-native/buildkit/sourcepolicy/policysession/policysession.proto

## Purpose
Protocol schema for source policy verification sessions. It defines a unary PolicyVerifier.CheckPolicy RPC that can return either a policy decision or a metadata-resolution request.

## Important APIs, Types, And Functions
Package: `moby`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The request carries target Platform, ResolveSourceMetaResponse source metadata, and capability booleans. The response oneof is DecisionResponse or ResolveSourceMetaRequest; decisions include action, deny messages, and optional SourceOp update.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/frontend/gateway/pb/gateway.proto, github.com/moby/buildkit/solver/pb/ops.proto, github.com/moby/buildkit/sourcepolicy/pb/policy.proto`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are oneof/schema compatibility and cross-package imports from gateway, solver ops, and sourcepolicy policy schema. Generated Go/gRPC/vtproto files are derived from it.
