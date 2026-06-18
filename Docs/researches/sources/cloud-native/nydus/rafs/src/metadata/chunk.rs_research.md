# sources/cloud-native/nydus/rafs/src/metadata/chunk.rs

## Purpose
`chunk.rs` provides `ChunkWrapper`, a version-erasing and ownership-normalizing adapter for RAFS chunk metadata. It lets builder and conversion code manipulate chunk fields through one API whether the backing data is an owned v5 `RafsV5ChunkInfo`, an owned v6 intermediate chunk, or a reference to an existing `BlobChunkInfo` implementation.

## Important APIs, Types, and Functions
- `ChunkWrapper::{V5,V6,Ref}` distinguishes owned v5, owned v6-as-v5-intermediate, and borrowed trait-object chunk metadata.
- `new(RafsVersion)` creates an owned default wrapper for v5 or v6.
- Getter/setter methods expose digest, blob index, compressed/uncompressed offsets and sizes, v5 chunk index, file offset, compression/encryption/batch flags, and CRC fields.
- `set_chunk_info()` bulk-populates chunk location/size/flag fields. It honors encryption only for the v6 variant; v5 records compression and CRC flags.
- `copy_from()` copies data across owned v5/v6 wrappers and converts supported reference wrappers into owned data first.
- `store()` serializes the effective chunk as a `RafsV5ChunkInfo` through `RafsStore`, including v6 and reference cases.
- `ensure_owned()` converts supported `Ref` variants into `V5` or `V6` by downcasting to `BlobMetaChunk`, `DirectChunkInfoV6`, `TarfsChunkInfoV6`, `CachedChunkInfoV5`, or `DirectChunkInfoV5`.
- `as_blob_v5_chunk_info()` and `to_rafs_v5_chunk_info()` bridge generic `BlobChunkInfo` trait objects to the v5-compatible field set required by RAFS metadata.

## Control Flow
Read-only operations dispatch directly by enum variant. Mutating operations first call `ensure_owned()`; if the wrapper is a supported reference type, it is converted into an owned `RafsV5ChunkInfo` payload and the mutation proceeds. Unsupported references panic. Serialization follows the same conversion path for `Ref`, constructing a temporary `RafsV5ChunkInfo` and storing it.

## State and Persistence Behavior
Owned variants store chunk metadata in memory until written with `store()`. `Ref` variants share external chunk metadata through `Arc<dyn BlobChunkInfo>` and are immutable until converted. Persistence format is v5 chunk layout even for v6 intermediate data, matching the rest of RAFS v6 code that reuses `RafsV5ChunkInfo` as an intermediate representation for chunk tables and conversion.

## Dependencies and Integration Points
The wrapper depends on storage traits from `nydus_storage::device`, the v5 chunk layout type, direct and cached chunk implementations from sibling modules, and `BlobMetaChunk` from storage metadata. It is an integration point between image-building/conversion code and runtime chunk providers. It also participates in `InodeWrapper::create_chunk()` and any code that needs to serialize chunk metadata without caring whether it came from cached v5, direct v5, direct v6, tarfs, or blob metadata.

## Risks and Edge Cases
- Unsupported `Ref` trait objects panic rather than returning `Result`, so callers must only wrap known chunk implementations before calling v5-specific accessors or mutations.
- `set_chunk_info()` ignores the `is_encrypted` argument for v5 by design; using it with a v5 target loses encryption state.
- `is_compressed()`, `is_batch()`, `crc32()`, and similar `Ref` accessors call `as_blob_v5_chunk_info()` and therefore require the reference to implement the v5 extension trait by downcast.
- `Display` and `Debug` for references can panic on unsupported reference types.
- The conversion funnel assumes v6 chunk metadata can be represented in `RafsV5ChunkInfo`; future v6-only fields would need explicit extension.

## Test Signals
Tests cover v5 and v6 wrappers, supported cached/tarfs references, setter/getter round trips, `copy_from()` between versioned wrappers, expected panics for unsupported `MockChunkInfo` references and forbidden direct mutation of unknown references, and formatting output. Coverage validates the panic contract but does not cover `store()` error propagation or `DirectChunkInfoV6`/`BlobMetaChunk` reference conversions directly.
