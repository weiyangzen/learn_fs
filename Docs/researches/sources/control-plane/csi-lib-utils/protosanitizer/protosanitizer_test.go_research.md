# sources/control-plane/csi-lib-utils/protosanitizer/protosanitizer_test.go

## Purpose
This test file validates secret stripping and JSON formatting for CSI protobuf messages and scalar values.

## Important APIs, Types, And Functions
`TestStripSecrets` is the main test. Benchmarks are `BenchmarkStrip` and `BenchmarkStripLarge`. `testReq` is a representative CSI CreateVolumeRequest.

## Control Flow
The test builds current CSI and generated future-spec messages with secret maps, secret scalars, repeated secret fields, map values, oneof secret fields, nested secrets, and unknown enum values. It compares `StripSecrets(...).String()` and fmt `%v`/`%+v` output to expected JSON, confirms the original object string is unchanged, and verifies `%#v` does not reveal the chosen secret name/value. It also marshals a future message into current CSI type to verify unknown fields do not leak.

## State, Persistence, And Dependencies
Tests are in-memory. Dependencies include CSI protobufs, generated `protosanitizer/test/csitest`, protobuf marshal/unmarshal, and testify.

## Integration Points
The tests validate the safety property relied on by gRPC logging in `connection`.

## Risks And Test Signals
Expected JSON depends on protobuf reflection field names and map ordering as produced by JSON marshal. Benchmarks provide performance signals for regular and large topology-heavy requests.
