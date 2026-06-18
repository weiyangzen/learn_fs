# sources/distributed-fs/lizardfs/src/chunkserver/chunk_signature.cc

## Purpose
`chunk_signature.cc` implements reading and serializing chunk file signatures for MooseFS-compatible, legacy LizardFS XOR, and current LizardFS EC-capable chunk headers.

## Important APIs, Types, And Functions
- Signature ids: MooseFS `"MFSSIGNATURE C 1.0"` via macro composition, LizardFS 1.0 `"LIZC 1.0"`, and LizardFS 1.1 `"LIZC 1.1"`.
- Default constructor creates an uninitialized signature for `readFromDescriptor`.
- Value constructor creates a serializable current-format signature.
- `readFromDescriptor` reads fixed signature bytes at an offset, extracts id/version/type, and validates signature id.
- `serializedSize` returns current serialized size.
- `serialize` writes the current `LIZC 1.1` id, chunk id, version, and current `ChunkPartType`.

## Control Flow
Reading uses `pread` to fetch `kSignatureSize` bytes. It always decodes chunk id and version after the 8-byte signature id, defaults type to standard, and then branches by signature id. MooseFS signatures have no type payload. LIZC 1.0 deserializes a legacy one-byte chunk part type and converts it. LIZC 1.1 deserializes current `ChunkPartType`. Unknown ids set `hasValidSignatureId_` false but still return true if the fixed read succeeded.

## State And Persistence
The class mirrors signature state persisted inside chunk headers: signature id, chunk id, version, and chunk type. Serialization always writes the current 1.1 format.

## Dependencies And Integration Points
It uses POSIX `pread`, protocol serialization helpers, `slice_traits`, `ChunkPartType`, legacy chunk type conversion, and `MFSCommunication` signature constants. It integrates with chunk scanning and validation code.

## Risks
- `readFromDescriptor` returns true for an unknown signature id after setting `hasValidSignatureId_` false, so callers must check both return value and `hasValidSignatureId`.
- The read size is the current maximum signature size; files containing only shorter historical signatures must still have enough bytes readable at that offset.
- Serialization compatibility depends on `ChunkPartType` binary size and encoding remaining stable.

## Test Signals
`chunk_signature_unittest.cc` covers reading LIZC 1.0 legacy signatures, reading LIZC 1.1 signatures, serialized size, and serialized bytes.
