<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/generator_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/generator_test.go

## Purpose

This test file validates construction and byte generation for external metadata generators with mocked chunks.

## Important APIs, Types, and Functions

`MockChunk` uses `testify/mock` to implement the `backend.Chunk` interface. `TestNewGenerators` checks object/chunk counts and backend passthrough for normal and empty input. `TestGenerate` checks wrapper generation. `TestMetaGeneratorGenerate` checks non-empty byte output for populated and empty metadata.

## Control Flow

Tests create synthetic chunk and object content, call constructors or generators, and assert structural counts and selected fields. The generation tests do not parse the byte stream; they only assert success and non-zero length.

## State and Persistence Behavior

There is no filesystem or global state. All state is in-memory generator objects and mock call expectations.

## Dependencies and Integration Points

The tests depend on `backend.Result`, `backend.ChunkOndisk`, `backend.ObjectOndisk`, `testify/assert`, and `testify/mock`. They signal that empty metadata is considered valid and still has header/meta bytes.

## Risks and Test Signals

Coverage confirms basic construction but not byte-level ABI correctness, little-endian field values, object offset calculation, msgpack failure handling, or duplicate object ID semantics. ABI regression tests would be valuable for this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/generator_test.go -->
