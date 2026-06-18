<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/proto/proto.go -->
# sources/cloud-native/containerd/pkg/protobuf/proto/proto.go

## Purpose
Compatibility shim for protobuf migration by exposing Marshal and Unmarshal under containerd pkg/protobuf/proto.

## Important APIs, Types, And Functions
Marshal and Unmarshal delegate to google.golang.org/protobuf/proto for google.Message values.

## Control Flow
Calls are pass-through with no extra validation or transformation.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by shim bootstrap, runtime option, and delete response code that imports containerd protobuf helpers instead of google directly.

## Risks And Edge Cases
Only supports the modern protobuf Message interface; callers with legacy gogo values need migration adapters elsewhere.

## Test Signals
Covered indirectly by all code paths that marshal bootstrap and shim responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/proto/proto.go -->
