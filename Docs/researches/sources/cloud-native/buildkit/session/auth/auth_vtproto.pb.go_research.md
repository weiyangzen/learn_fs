<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth_vtproto.pb.go -->
# sources/cloud-native/buildkit/session/auth/auth_vtproto.pb.go

Purpose: vtprotobuf-generated optimized helpers for Auth protobuf messages.

Important APIs, types, and functions: for each Auth message it defines `CloneVT`, `CloneMessageVT`, `EqualVT`, `EqualMessageVT`, `MarshalVT`, `MarshalToVT`, `MarshalToSizedBufferVT`, `SizeVT`, and `UnmarshalVT`.

Control flow and state: methods manually copy fields, compare slices/maps, encode protobuf wire format into caller-provided buffers, compute sizes, and parse wire data while preserving unknown fields. It mutates receiver slices during unmarshal for reuse.

Dependencies and integration: depends on vtprotobuf/proto helper packages and the standard protobuf `proto.Message` interface. Used wherever BuildKit opts into faster protobuf serialization.

Risks and test signals: generated code is dense and should be regenerated, not edited. Map and slice aliasing semantics matter for clone/unmarshal correctness. Test signal is protobuf round-trip, equality, clone independence, and generated-code compilation after schema changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth_vtproto.pb.go -->
