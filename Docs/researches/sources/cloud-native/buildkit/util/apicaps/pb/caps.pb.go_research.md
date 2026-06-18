# sources/cloud-native/buildkit/util/apicaps/pb/caps.pb.go

## Purpose
Generated Go protobuf definition for APICap. It exposes ID, Enabled, Deprecated, DisabledReason, DisabledReasonMsg, and DisabledAlternative fields used by capability negotiation.

## Important APIs, Types, And Functions
Package: `moby_buildkit_v1_apicaps`. Build tags: `none`. Key declarations observed in the file: `APICap, Reset, String, ProtoMessage, ProtoReflect, Descriptor, GetID, GetEnabled, GetDeprecated, GetDisabledReason, GetDisabledReasonMsg, GetDisabledAlternative, ...`.

## Control Flow, State, And Persistence
Control flow is protobuf reflection/getter boilerplate generated from caps.proto. No persistence; callers serialize or exchange APICap messages over API boundaries.

## Dependencies And Integration Points
Important dependencies/imports: `google.golang.org/protobuf/reflect/protoreflect, google.golang.org/protobuf/runtime/protoimpl`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are schema evolution and generated/runtime version drift. util/apicaps/caps_test.go validates consumer behavior for enabled/disabled states.
