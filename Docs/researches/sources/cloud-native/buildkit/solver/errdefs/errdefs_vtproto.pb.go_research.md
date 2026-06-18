<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/errdefs_vtproto.pb.go -->
## sources/cloud-native/buildkit/solver/errdefs/errdefs_vtproto.pb.go

Purpose: generated vtprotobuf support for the `solver/errdefs` protobuf messages used as typed gRPC error payloads. It gives BuildKit's error details fast deep clone, equality, marshal, size, and unmarshal paths without reflection-heavy generic protobuf handling.

Important APIs and types: methods are generated on `Vertex`, `Source`, `Frontend`, `FrontendCap`, `CompatibilityFeature`, `Subrequest`, `Solve`, `FileAction`, `ContentCache`, `ProvenanceMaterialsIncomplete`, and `ProvenanceMaterialIncomplete`. The key method families are `CloneVT`, `CloneMessageVT`, `EqualVT`, `EqualMessageVT`, `MarshalVT`, `MarshalToVT`, `MarshalToSizedBufferVT`, `SizeVT`, and `UnmarshalVT`. Oneof wrappers `Solve_File` and `Solve_Cache` also receive clone/equality/marshal/size handling.

Control flow: marshal methods compute exact size, fill buffers backward with field tags and varints, and preserve `unknownFields`. Unmarshal methods scan wire fields, validate wire types and tags, append repeated fields, instantiate nested protobuf values, and preserve unknown wire segments via `protohelpers.Skip`.

State and dependencies: the file has no durable state; it mutates receiver fields during unmarshal and allocates cloned slices/maps for deep-copy safety. It depends on `solver/pb` vtproto helpers for nested `pb.Op`, `pb.SourceInfo`, and `pb.Range`, plus `google.golang.org/protobuf` and Planetscale `protohelpers`.

Integration points: wrapper files such as `frontend.go`, `source.go`, `solve.go`, and `provenance.go` rely on `CloneVT` when extracting error chains and on vt marshaling when typed details cross gRPC.

Risks and test signals: because this is generated code, manual edits are high risk and should be regenerated from `errdefs.proto`. Main risks are schema drift, oneof handling regressions, and unknown-field loss. Direct tests are elsewhere, especially provenance round-trip tests through `grpcerrors`, which exercise generated serialization indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/errdefs_vtproto.pb.go -->
