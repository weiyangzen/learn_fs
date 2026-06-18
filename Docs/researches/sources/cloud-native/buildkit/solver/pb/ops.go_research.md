# sources/cloud-native/buildkit/solver/pb/ops.go

Purpose: this file adds hand-written convenience methods on top of generated protobuf/VTProto types for `Definition` and `Op`. It hides the actual marshaling implementation behind stable methods used by solver code and tests.

Important APIs: `(*Definition).IsNil` treats a nil definition or a definition with nil `Metadata` as logically nil. `(*Definition).Marshal` delegates to `MarshalVT`, and `(*Definition).Unmarshal` delegates to `UnmarshalVT`, using vtprotobuf-generated fast paths. `(*Op).Marshal` uses `proto.MarshalOptions{Deterministic: true}` to produce stable serialized bytes for digest calculation. `(*Op).Unmarshal` delegates to `UnmarshalVT`.

Control flow: all methods are thin wrappers. The only behavioral choice is deterministic marshaling for `Op`, which is critical because BuildKit digests serialized operations and uses those digests as LLB graph identities. `Definition` marshaling does not explicitly request deterministic protobuf marshaling here because it delegates to the vtprotobuf implementation.

State and persistence: no state is stored, but serialized byte output is persistent in cache keys, LLB definitions, and digest references. `Op.Marshal` stability is especially important because `pb.Input.digest` values in the graph refer to digests of marshaled input `Op` messages.

Dependencies and integration points: this file depends on `google.golang.org/protobuf/proto` and generated methods from `ops.pb.go` plus vtprotobuf-generated methods elsewhere in the package. It is used by llbsolver loading, digest recomputation tests, and any frontend or solver path that serializes/deserializes LLB definitions.

Risks and test signals: changing `Op.Marshal` away from deterministic marshaling would destabilize digest identities. `Definition.IsNil` can be surprising because a non-nil `Definition` with nil metadata is considered nil even if other fields are populated. `vertex_test.go` provides direct signal for deterministic op marshaling and digest recomputation behavior.
