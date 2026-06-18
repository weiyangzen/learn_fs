# sources/cloud-native/buildkit/api/services/control/control_bench_test.go

## Purpose
Benchmarks vtproto marshal/unmarshal performance for hot progress messages: `Vertex`, `VertexStatus`, and `VertexLog`.

## APIs, Flow, And State
Benchmark functions construct sample messages, then loop over `MarshalVT` or `UnmarshalVT`. Global sinks `Buf`, `VertexOutput`, `VertexStatusOutput`, and `VertexLogOutput` prevent compiler optimization from discarding results. Samples use `time.Now`, `opencontainers/go-digest`, protobuf timestamps, and representative fields for digests, names, byte counts, streams, and log bytes.

## Dependencies And Integration
Depends on generated vtproto methods in `control_vtproto.pb.go`, standard protobuf marshal for creating encoded buffers, and `testify/require` for benchmark-time error checks. It exercises message types generated from `control.proto`.

## Risks And Test Signals
This is performance coverage, not semantic test coverage. It does not benchmark every Control message, map-heavy structures, or streaming gRPC. It can catch vtproto generation/compatibility failures at compile time and provides benchmark signals for progress serialization hot paths.
