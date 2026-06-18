## sources/cloud-native/buildkit/util/grpcutil/encoding/proto/proto.go

Purpose: registers a custom gRPC protobuf codec with the standard proto codec name that avoids resetting messages on unmarshal and supports vtprotobuf fast paths.

Important APIs/types: package `init` calls `encoding.RegisterCodecV2(codec{})`. `codec.Marshal`, `codec.Unmarshal`, and `codec.Name` implement gRPC encoding. `vtprotoMessage` captures vtprotobuf methods.

Control flow: marshal/unmarshal switch on vtproto, proto v2, and proto v1 adapted to v2. Small messages use plain byte slices; larger messages use `grpc/mem.DefaultBufferPool`. Unmarshal materializes buffer slices then calls `UnmarshalVT` or `proto.UnmarshalOptions{Merge:true}` to avoid reset semantics and align vt behavior.

State/persistence: global codec registration at init; pooled buffers are freed after materialization. Dependencies: gRPC encoding/mem, protobuf adaptors, default proto import for name override.

Integration points: affects all gRPC calls using the registered proto codec in this process. Risks: merge/no-reset behavior can surprise callers expecting zeroed reused messages; overriding default codec name is process-wide; vtproto implementations must honor buffer contracts. Test signals: no local tests in this subset.
