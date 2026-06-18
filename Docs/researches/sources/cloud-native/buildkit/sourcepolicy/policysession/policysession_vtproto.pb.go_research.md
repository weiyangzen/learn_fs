# sources/cloud-native/buildkit/sourcepolicy/policysession/policysession_vtproto.pb.go

## Purpose
Generated vtprotobuf fast-path methods for policy-session messages. It covers CheckPolicyRequest, CheckPolicyResponse oneofs, DecisionResponse, and DenyMessage.

## Important APIs, Types, And Functions
Package: `policysession`. Build tags: `none`. Key declarations observed in the file: `CloneVT, CloneMessageVT, EqualVT, EqualMessageVT, MarshalVT, MarshalToVT, MarshalToSizedBufferVT, SizeVT, UnmarshalVT`.

## Control Flow, State, And Persistence
Control flow clones nested platform/source/cap maps, serializes oneof variants and repeated deny messages, and unmarshals protobuf wire data with unknown-field handling. It holds no durable state.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/frontend/gateway/pb, github.com/moby/buildkit/solver/pb, github.com/moby/buildkit/sourcepolicy/pb, github.com/planetscale/vtprotobuf/protohelpers, google.golang.org/protobuf/proto, google.golang.org/protobuf/runtime/protoimpl`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are regeneration drift from policysession.proto and oneof/map wire compatibility. Integration depends on gRPC policy verifier traffic.
