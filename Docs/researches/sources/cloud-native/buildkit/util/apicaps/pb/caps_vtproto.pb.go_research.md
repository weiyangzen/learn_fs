# sources/cloud-native/buildkit/util/apicaps/pb/caps_vtproto.pb.go

## Purpose
Generated vtprotobuf fast-path methods for APICap. It provides CloneVT, EqualVT, MarshalVT, SizeVT, and UnmarshalVT optimized for capability negotiation.

## Important APIs, Types, And Functions
Package: `moby_buildkit_v1_apicaps`. Build tags: `none`. Key declarations observed in the file: `CloneVT, CloneMessageVT, EqualVT, EqualMessageVT, MarshalVT, MarshalToVT, MarshalToSizedBufferVT, SizeVT, UnmarshalVT`.

## Control Flow, State, And Persistence
Control flow serializes scalar string/bool fields and skips unknown wire fields. State is transient protobuf byte buffers only.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/planetscale/vtprotobuf/protohelpers, google.golang.org/protobuf/proto, google.golang.org/protobuf/runtime/protoimpl`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are generated-code drift from caps.proto and malformed wire input. caps_test.go exercises the higher-level APICap consumer rather than this generated file directly.
