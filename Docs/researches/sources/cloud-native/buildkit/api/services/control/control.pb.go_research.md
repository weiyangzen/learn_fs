# sources/cloud-native/buildkit/api/services/control/control.pb.go

## Purpose
Generated Go protobuf model for the BuildKit Control API defined in `control.proto`. It provides message structs, enum constants, getters, reflection descriptors, dependency indexes, and type initialization for clients and servers.

## APIs, Types, And Flow
Exports `BuildHistoryEventType` with `STARTED`, `COMPLETE`, and `DELETED`; message structs for disk usage/prune (`PruneRequest`, `DiskUsageRequest`, `UsageRecord`), solving (`SolveRequest`, `CacheOptions`, `CacheOptionsEntry`, `Exporter`, `SolveResponse`), progress (`StatusRequest`, `StatusResponse`, `Vertex`, `VertexStatus`, `VertexLog`, `VertexWarning`), session (`BytesMessage`), workers/info (`ListWorkersRequest`, `ListWorkersResponse`, `InfoRequest`, `InfoResponse`), and build history (`BuildHistoryRequest`, `BuildHistoryEvent`, `BuildHistoryRecord`, `UpdateBuildHistoryRequest`, `Descriptor`, `BuildResultInfo`). Each struct has `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe `Get*` methods. Initialization builds one enum, thirty-nine messages, and one service descriptor through `protoimpl.TypeBuilder`.

## Dependencies And Integration
Imports BuildKit worker types, solver pb definitions, source policy pb definitions, Google timestamps, and Google RPC status. `client` and `cmd/buildctl` code use these structs via the generated gRPC client. Fast `MarshalVT`/`UnmarshalVT` methods are not in this file; they are generated in adjacent `control_vtproto.pb.go`, which `control_bench_test.go` benchmarks.

## State, Risks, And Test Signals
State is serialized protobuf data crossing gRPC boundaries; compatibility depends on stable field numbers and reserved/deprecated fields. Risks include editing generated code directly, changing field numbers, map key type drift, and forgetting to regenerate vtproto/grpc outputs after proto changes. Test signals include generated-file validation, Go compile, protobuf reflection use, gRPC integration tests, and vtproto benchmarks.
