## sources/cloud-native/buildkit/solver/errdefs/errdefs.pb.go

Purpose: generated protobuf bindings for solver typed error metadata.

Important APIs/types/functions: defines message structs and getters for `Vertex`, `Source`, `Frontend`, `FrontendCap`, `CompatibilityFeature`, `Subrequest`, `Solve`, `FileAction`, `ContentCache`, `ProvenanceMaterialsIncomplete`, and `ProvenanceMaterialIncomplete`. `Solve` includes a oneof subject (`File` or `Cache`) and description map. Init builds a protobuf file descriptor and oneof wrappers.

Control flow: generated methods reset, reflect, stringify, compress descriptors, and expose field getters. No handwritten logic.

State and persistence: per-message protobuf runtime state plus unknown fields/size cache. Serialized forms carry error context across gRPC/typeurl boundaries.

Dependencies and integration points: generated from `errdefs.proto`, importing solver `pb` operation/source/range messages. Used by typed error wrappers in this package and BuildKit gRPC error serialization.

Risks and test signals: field numbers are compatibility-critical because they may cross process/version boundaries. Manual edits should be avoided. Tests in neighboring errdefs files cover some typed error round trips, but not all generated messages in this subset.
