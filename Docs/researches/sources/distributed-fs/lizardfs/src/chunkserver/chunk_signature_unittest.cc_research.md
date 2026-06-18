# sources/distributed-fs/lizardfs/src/chunkserver/chunk_signature_unittest.cc

## Purpose
This GoogleTest file verifies chunk signature read and serialization compatibility.

## Important APIs, Types, And Functions
- `ReadingOldSignatureFromFile` creates a temp file with `LIZC 1.0` signature bytes and a legacy XOR type id, then validates converted `ChunkPartType`.
- `ReadingFromFile` validates current `LIZC 1.1` two-byte type id parsing.
- `SerializedSize` asserts current signatures serialize to 22 bytes.
- `Serialize` asserts exact serialized bytes for a known id/version/type.

## Control Flow
Tests write byte vectors to temporary files, open them, read signatures at offset 5, and assert parsed fields. Serialization tests use repository `serialize` helpers and compare vectors.

## State And Persistence
Temporary files simulate persisted chunk headers. No repository state is changed.

## Dependencies And Integration Points
It depends on GoogleTest, `TemporaryDirectory`, Unix file APIs, `ChunkSignature`, `slice_traits`, and `unittests/chunk_type_constants.h`.

## Risks
Tests do not cover MooseFS signature id, invalid signature ids, short reads, corrupt type payloads, or EC current type examples.

## Test Signals
This is strong compatibility coverage for legacy/current LizardFS signature formats and exact binary layout.
