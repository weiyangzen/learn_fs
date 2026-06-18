# sources/cloud-native/buildkit/sourcepolicy/pb/policy_vtproto.pb.go

## Purpose
Generated vtprotobuf fast-path methods for source policy protobuf messages. It adds CloneVT, EqualVT, MarshalVT/MarshalToSizedBufferVT, SizeVT, and UnmarshalVT for Rule, Update, Selector, AttrConstraint, and Policy.

## Important APIs, Types, And Functions
Package: `moby_buildkit_v1_sourcepolicy`. Build tags: `none`. Key declarations observed in the file: `CloneVT, CloneMessageVT, EqualVT, EqualMessageVT, MarshalVT, MarshalToVT, MarshalToSizedBufferVT, SizeVT, UnmarshalVT`.

## Control Flow, State, And Persistence
Control flow is generated per-message serialization/deserialization with explicit field tags, repeated field loops, map/list cloning, size precomputation, and unknown-field skipping. It has no persistence beyond protobuf byte slices.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/planetscale/vtprotobuf/protohelpers, google.golang.org/protobuf/proto, google.golang.org/protobuf/runtime/protoimpl`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are generated-code drift from policy.proto and malformed protobuf inputs. Test signal comes from protobuf generation consistency and sourcepolicy policy tests, not handwritten unit tests here.
