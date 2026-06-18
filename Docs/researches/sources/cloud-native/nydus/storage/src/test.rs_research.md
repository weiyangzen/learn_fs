# sources/cloud-native/nydus/storage/src/test.rs

Purpose: supplies mock storage backend and chunk metadata types for storage unit tests.

Important APIs/types/functions: `MockBackend` holds shared `BackendMetrics` and implements both `BlobReader` and `BlobBackend`. `BlobReader::try_read` fills the destination buffer with deterministic byte values equal to the byte index modulo 256. `BlobBackend::get_reader` returns a new `Arc<MockBackend>` sharing metrics. `MockChunkInfo` is a cloneable/default chunk metadata holder. It implements `BlobChunkInfo` and `BlobV5ChunkInfo`, using `impl_getter!` to expose offsets, sizes, index, flags, and blob index.

Control flow: tests can instantiate `MockBackend` and receive successful reads without external storage. Chunk tests can set fields on `MockChunkInfo` and pass it through trait-object APIs; methods compute booleans from `BlobChunkFlags` and return zero CRC when the `HAS_CRC32` flag is absent.

State and persistence: no persistence. `MockBackend.metrics` is shared through `Arc`; read contents are generated on demand. `MockChunkInfo` is plain in-memory metadata.

Dependencies and integration points: integrates with `crate::backend::{BlobBackend, BlobReader}`, `crate::device::{BlobChunkInfo, BlobChunkFlags}`, v5 chunk metadata via `BlobV5ChunkInfo`, `nydus_utils::digest::RafsDigest`, and `nydus_utils::metrics::BackendMetrics`. It is intended for crate-internal tests because all types are `pub(crate)`.

Risks: `try_read` ignores offset and `blob_size` returns 0 even though reads can return data, so tests using it do not validate real object sizing or offset semantics. `is_encrypted` always returns false. CRC and batch/compression behavior are flag-only, so data integrity behavior must be tested elsewhere.

Test signals: this is test support rather than a test module. It strengthens other tests by avoiding network/backend dependencies but can mask offset, size, and encryption bugs if used too broadly.
