# subset-b-000235 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/meta/batch.rs -->
# sources/cloud-native/nydus/storage/src/meta/batch.rs

## Purpose
Implements on-disk batch-inflate metadata and a builder-side helper for RAFS v6 batch chunks, where several small logical chunks share one compressed batch payload.

## Important APIs, Types, And Functions
`BatchInflateContext` is a 40-byte `#[repr(C, packed)]` record with little-endian compressed batch size and unaligned uncompressed batch size plus reserved fields. Getters/setters normalize endian format, and `as_slice()` exposes the packed record as bytes for serialization. `BatchContextGenerator` buffers uncompressed small-chunk data, records completed batch contexts, and emits `BlobChunkInfoV2Ondisk` entries via `generate_chunk_info()`.

## Control Flow
Builders append chunk bytes into `chunk_data_buf`, call `generate_chunk_info()` before dumping a small chunk so the v2 chunk receives a batch flag, batch index, and offset inside the batch buffer, then call `add_context()` after a batch payload is compressed. `to_vec()` serializes all contexts in insertion order for placement after the chunk table.

## State And Persistence
State is process-local until serialized: `chunk_data_buf` holds pending uncompressed batch data and `contexts` holds packed records later persisted inside the blob meta area. Generated v2 chunk records store zero per-chunk compressed size, the shared compressed offset, and per-chunk placement in the batch buffer.

## Dependencies And Integration Points
Depends on `BlobChunkInfoV2Ondisk` and `BlobMetaChunkInfo` setters from `meta/chunk_info_v2.rs` and is re-exported by `meta/mod.rs`. Runtime validation and lookup consume these contexts through `BlobCompressionContext.batch_info_array`.

## Risks
The unsafe byte view depends on exact packed layout and little-endian setters. `add_context()` casts `chunk_data_buf_len()` to `u32`, so callers must keep batch buffers within the on-disk field limit. Batch chunks disable CRC32 because the v2 `data` field is already used for batch index and in-batch offset.

## Test Signals
Unit tests verify endian setters, 40-byte serialization, generator buffer lifecycle, context serialization through raw packed reconstruction, and that generated chunks are marked batch. Source size reviewed: 204 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/meta/batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/meta/chunk_info_v1.rs -->
# sources/cloud-native/nydus/storage/src/meta/chunk_info_v1.rs

## Purpose
Defines the legacy RAFS v6 chunk compression-info v1 on-disk format and implements the common `BlobMetaChunkInfo` trait for range lookup, validation, and compatibility with existing blob metadata.

## Important APIs, Types, And Functions
`BlobChunkInfoV1Ondisk` is a packed 16-byte record with `uncomp_info` and `comp_info` bitfields. Constants define masks and shifts for 40-bit compressed offsets, 4K-aligned uncompressed offsets, and 24-bit encoded sizes. Trait methods get/set compressed and uncompressed offset/size, compute compressed state, return unsupported v2-only feature accessors, and validate against a `BlobCompressionContext`.

## Control Flow
Setters assert field-range compatibility, preserve unrelated bits where needed, and encode size as `size - 1`. Getters decode little-endian fields and return sizes as `encoded + 1`. Validation rejects chunks whose compressed or uncompressed end exceeds blob bounds, zero uncompressed sizes, or inconsistent uncompressed chunks.

## State And Persistence
The type is pure on-disk state. It is created by builders through `BlobMetaChunkArray::add_v1()` and is memory-mapped from `.blob.meta` by `BlobMetaChunkArray::from_file_map()` when `CHUNK_INFO_V2` is absent. V1 has no encryption, CRC32, ZRan, or batch side data.

## Dependencies And Integration Points
Implements the trait declared in `meta/mod.rs` and uses `BlobCompressionContext` plus `BLOB_CCT_CHUNK_SIZE_MASK`. Tests exercise integration through `BlobCompressionContextInfo`, `BlobMetaChunkArray`, `BlobInfo`, `BlobReader`, compression helpers, and temporary files.

## Risks
Invalid calls to unsupported v2-only methods panic through `unimplemented!()`, so generic code must only request ZRan or batch fields when feature flags and chunk format permit it. The bitfield encoding is assert-driven, which is appropriate for builder invariants but can panic if misused on untrusted construction paths.

## Test Signals
Tests cover boundary bitfield encoding, old-format compatibility values, chunk lookup with holes, uncompressed range lookup, metadata reading with no compression and LZ4, and error cases for uncovered ranges. Source size reviewed: 484 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/meta/chunk_info_v1.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/meta/chunk_info_v2.rs -->
# sources/cloud-native/nydus/storage/src/meta/chunk_info_v2.rs

## Purpose
Defines the RAFS v6 chunk compression-info v2 on-disk format, including flags and attached data used for compressed, encrypted, CRC, ZRan, and batch chunks.

## Important APIs, Types, And Functions
`BlobChunkInfoV2Ondisk` is a packed 24-byte record with uncompressed info, compressed info, and a `data` field. Private setters toggle flags and populate `data` as either CRC32, ZRan index/offset, or batch index/in-batch offset. The `BlobMetaChunkInfo` implementation exposes offsets, sizes, flags, side-data accessors, CRC/data accessors, and `validate()`. `Display` prints decoded offsets, sizes, data, and flags.

## Control Flow
Offset and size setters encode into bounded bitfields: compressed offset is 40 bits, compressed size is 24 bits, uncompressed offset is 4K-granular, and uncompressed size is encoded as `size - 1`. Validation first checks common range and consistency constraints, logs unknown flags once per flag byte, then performs feature-specific validation for ZRan contexts and batch contexts.

## State And Persistence
The record is persisted in blob metadata and memory-mapped into `BlobMetaChunkArray::V2`. The `data` field is multiplexed, so producers must ensure mutually coherent flags: CRC32 uses the low 32 bits, ZRan uses high 32-bit context index plus low 32-bit offset, and batch uses high 32-bit batch index plus low 32-bit uncompressed offset in the batch buffer.

## Dependencies And Integration Points
Used by `batch.rs`, `zran.rs`, and `meta/mod.rs`; validation depends on `BlobFeatures`, `BlobCompressionContext.zran_info_array`, and `batch_info_array`. It integrates with range lookup through the `BlobMetaChunkInfo` trait and with blob feature gates for `ZRAN` and `BATCH`.

## Risks
Unknown flags are only warned, not rejected, which preserves forward compatibility but may hide producer bugs. CRC32 validation rejects a set CRC flag with value zero, so legitimate zero CRC32 values would be impossible under this format. Batch validation checks context index and in-batch bounds but relies on correct shared compressed offsets across same-batch chunks.

## Test Signals
Tests cover field encoding limits, flag toggling, ZRan and batch side-data accessors, old-format compatibility, hole-aware chunk lookup, validation failures for missing ZRan features/context arrays, encrypted behavior, and unknown flag tolerance. Source size reviewed: 544 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/meta/chunk_info_v2.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/meta/mod.rs -->
# sources/cloud-native/nydus/storage/src/meta/mod.rs

## Purpose
Acts as the RAFS v6 blob metadata hub: defines the compression-context header, loads and validates `.blob.meta` cache files, maps chunk metadata into typed arrays, serves range-to-chunk queries, exposes batch and ZRan context lookup, and adapts metadata chunks to `BlobChunkInfo`/`BlobV5ChunkInfo`.

## Important APIs, Types, And Functions
`BlobCompressionContextHeader` is the 4K on-disk trailer/header with magic values, feature bits, chunk-info compressor, offsets, compressed/uncompressed metadata sizes, and optional ZRan/batch table offsets/counts. `BlobCompressionContextInfo::new()` loads or downloads metadata and optionally inlined chunk digests. Public query methods include `get_chunks_uncompressed()`, `get_chunks_compressed()`, `add_more_chunks()`, `get_chunk_index()`, digest accessors, batch accessors, and ZRan accessors. `BlobCompressionContext` stores the mapped state, `BlobMetaChunkArray` abstracts v1/v2 arrays, `BlobMetaChunk` implements chunk traits, `BlobMetaChunkInfo` is the common on-disk entry trait, `format_blob_features()` formats feature flags, and `round_up_4k()` provides alignment.

## Control Flow
`new()` validates compile-time layout assumptions, checks chunk count, opens or creates `<blob>.blob.meta`, sizes it to `4K header + aligned metadata`, mmaps it, validates the header, and if invalid downloads encrypted/compressed metadata from the backend through `read_metadata()`. It then maps v1 or v2 chunk entries from the file map, maps batch or ZRan side tables when feature flags require them, and optionally extracts/loads inlined chunk digests from a ToC entry.

Range lookup uses binary search in `_get_chunk_index_nocheck()`, then walks adjacent entries to cover requested uncompressed or compressed ranges. ZRan paths back up to the first chunk in the same ZRan context and include context groups according to batch-size amplification. Batch paths account for shared compressed ranges and expand reads to include all chunks in the current batch. `add_more_chunks()` performs read amplification for ZRan, batch, and normal chunks.

## State And Persistence
Persistent state lives in cache files named `<blob>.blob.meta`, `<blob>.blob.digest`, and `<blob>.blob.toc`, plus data embedded in the remote/local blob. `FileMapState` owns the mmap backing, while `ManuallyDrop<Vec<...>>` views typed arrays over mapped memory without freeing the mmap storage. The state also stores feature bits, blob sizes, optional digest arrays, batch contexts, ZRan contexts, and dictionaries.

## Dependencies And Integration Points
Integrates with backend `BlobReader`, device `BlobInfo`, `BlobFeatures`, `BlobChunkInfo`, `BlobChunkFlags`, v5 compatibility, ToC extraction, `FileMapState`, compression/decompression, encryption, digest handling, and constants for max chunk size/count. It re-exports v1/v2 chunk formats, batch generators, ZRan generators, and ToC support for builder/runtime callers.

## Risks
This file is unsafe-layout heavy: it converts mmap regions into vectors with `Vec::from_raw_parts()` and relies on `ManuallyDrop` to avoid freeing mapped memory. Header validation is central; missing checks can turn corrupt metadata into unsafe typed access. `get_compressed_size()` unwraps `get_batch_context()` after a prior batch-index read, so validation must protect against malformed batch indices. `get_chunks_compressed()` has a nested `einval!(einval!(...))` in one error path, and large read-amplification settings can return many chunks.

## Test Signals
Tests cover 4K alignment, loading real ZRan fixture metadata, ZRan compressed/uncompressed range lookup, ZRan read amplification, header getters/setters and stable digest, feature formatting, batch read amplification, and shared helpers used by v1 tests. Source size reviewed: 2,510 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/meta/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/meta/toc.rs -->
# sources/cloud-native/nydus/storage/src/meta/toc.rs

## Purpose
Defines the RAFS blob table-of-contents format and extraction logic for inlined blob components such as `image.boot`, `blob.meta`, `blob.meta.header`, `blob.digest`, and `rafs.blob.toc`.

## Important APIs, Types, And Functions
Constants name well-known ToC entries. `TocEntryFlags` maps supported entry compression algorithms. `TocEntry` is a 128-byte on-disk record with flags, 16-byte name, uncompressed digest, compressed offset/size, and uncompressed size. `TocEntryList` manages entries, parsing, cache fallback, extraction, and RAFS metadata extraction. `TocLocation` describes explicit or auto-detected ToC offset/size and optional digest validation.

## Control Flow
`TocEntryList::read_from_cache_file()` validates location, tries a small cache file, parses it if valid, otherwise downloads ToC data from the blob into a `.toc_downloading` file and atomically renames it. `read_toc_header()` either reads the final up-to-4K area of the blob or an explicit location. `parse_toc_header()` validates the trailing tar header for `rafs.blob.toc`, checks optional digest, and copies 128-byte records into entries. Extraction locates requested entries, verifies existing output by digest, writes to temporary files, and renames on success.

## State And Persistence
The ToC list itself is in-memory, but it persists cache files for downloaded ToC headers and extracted bootstrap/digest files. `toc_digest` and `toc_size` summarize parsed ToC content. Temporary `.toc_downloading` files protect against partial cache writes.

## Dependencies And Integration Points
Uses `BlobReader`/`BlobBufReader`, `BlobFactory`, `ConfigV2`, `RafsDigest`, tar headers, zstd decoding, and allocation helpers. `meta/mod.rs` uses ToC extraction to fetch inlined chunk digest files, and `extract_rafs_meta()` builds a backend reader from config to extract `image.boot`.

## Risks
The entry name field is limited to 16 bytes and invalid UTF-8 makes lookup fail for that entry. LZ4 is accepted as a flag but extraction returns unsupported, so producer/consumer compression choices must match this limitation. `read_toc_header()` returns `offset + 0x1000` as blob-size-like context for fallback bootstrap extraction, which assumes the auto-detect 4K read window semantics. Cache parsing only accepts files larger than 512 bytes, aligned to 128 bytes, and at most 4K.

## Test Signals
Tests with localfs fixtures cover ToC reading, explicit digest mismatch, auto-detect fallback, cache download/reuse, bootstrap extraction idempotence, compression-flag conversion, buffer extraction errors/success, entry name parsing, field getters, compressor round trips, ToC location validation, and `TocEntry` size. Source size reviewed: 1,084 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/meta/toc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/meta/zran.rs -->
# sources/cloud-native/nydus/storage/src/meta/zran.rs

## Purpose
Implements builder-side ZRan metadata generation and on-disk inflate contexts used to randomly access gzip/zlib streams in RAFS blobs.

## Important APIs, Types, And Functions
`ZranInflateContext` is a 40-byte packed record containing compressed stream offset/size, uncompressed stream offset/size, dictionary table offset/size, and zlib bit context. It exposes little-endian getters, `as_slice()`, and conversion to `nydus_utils::compress::zlib_random::ZranContext`. `ZranContextGenerator<R>` wraps `ZranGenerator` and `ZranReader`, tracks aligned uncompressed position, implements `Read`, and emits v2 chunk records and serialized ZRan context/dictionary data.

## Control Flow
Construction creates a `ZranReader`, configures min/max compressed and uncompressed sizes around `RAFS_DEFAULT_CHUNK_SIZE`, and starts with uncompressed position zero. Callers call `start_chunk()`, read through the generator, and call `finish_chunk()` to get a v2 chunk marked compressed and ZRan with context index and offset. `to_vec()` writes all fixed-size context records first, then appends dictionaries in record order.

## State And Persistence
Generator state is in memory while building. Persisted state is a sequence of `ZranInflateContext` records plus dictionary bytes stored after the chunk table in the blob compression context area. Runtime loads these through `BlobCompressionContext.zran_info_array` and `zran_dict_table`.

## Dependencies And Integration Points
Depends on `nydus_utils::compress::zlib_random`, `BlobChunkInfoV2Ondisk`, the `BlobMetaChunkInfo` setter trait, `round_up_4k()`, and `RAFS_DEFAULT_CHUNK_SIZE`. `meta/mod.rs` validates ZRan chunk indices/ranges and serves contexts to decompression paths.

## Risks
The unsafe byte slice depends on packed layout remaining 40 bytes. `finish_chunk()` increments uncompressed position by 4K-aligned chunk length, so callers must coordinate RAFS chunk alignment with tar/gzip reads. Dictionary offset accumulation is `u64`, but individual dictionary sizes are stored as `u32`.

## Test Signals
Tests verify context getters, serialized length, conversion to runtime `ZranContext`, zero values, generating chunks from a gzip tar fixture, and that serialized data includes fixed contexts plus dictionaries. Source size reviewed: 399 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/meta/zran.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/remote/client.rs -->
# sources/cloud-native/nydus/storage/src/remote/client.rs

## Purpose
Implements the client-side proxy for a remote blob manager: it connects over a Unix socket control plane, receives blob file descriptors, tracks generation tokens, and asks the server to materialize uncompressed ranges into the shared data plane file.

## Important APIs, Types, And Functions
`RemoteBlobMgr` is the public manager with `new()`, `connect()`, `start()`, `shutdown()`, `ping()`, and `get_blob_object()`. `RemoteBlobs` caches active `RemoteBlob`s and maintains a generation counter. `RemoteBlob` implements `BlobObject` using a received `File`, base offset, token, and `BlobRangeMap`. `Request`, `RequestStatus`, and `RequestResult` model synchronous request/reply waiting. `ServerConnection` owns the socket endpoint, request map, reconnect logic, and handlers for `GetBlob` and `FetchRange` replies.

## Control Flow
A caller creates and starts `RemoteBlobMgr`; `ServerConnection::start()` spawns a reply thread that waits for a connection and dispatches replies by tag. `get_blob_object()` reuses cached blobs or sends `GetBlob`, then constructs a `RemoteBlob` with a range map in the workdir. `fetch_range_uncompressed()` checks local range readiness and sends `FetchRange` if needed. Requests wait on condvars with a four-second timeout and retry when reconnect/generation mismatch is observed.

## State And Persistence
Persistent/cache state is the `BlobRangeMap` file under `workdir/<blob_id>`, which tracks uncompressed range readiness at 256 KiB granularity. Runtime state includes active blob cache, generation counter, per-blob token, request tags, pending request map, socket endpoint, and a shared file descriptor from the remote manager.

## Dependencies And Integration Points
Uses `remote::connection::Endpoint` for Unix-socket messages and fd passing, `remote::message` wire types, `BlobInfo`, `BlobObject`, `BlobIoRange`, `BlobRangeMap`, `nix::select`, and `vm_memory::ByteValued`. It is the bridge between remote control messages and higher-level blob IO.

## Risks
`call_fetch_range()` constructs a `FetchRangeRequest` but sets the header body size to `size_of::<GetBlobRequest>()`, which is a protocol-risk bug if the sizes differ. On non-success fetch replies, it returns `from_raw_os_error(count as i32)` instead of the result code, likely masking server errors. `reopen_blob()` updates only the token and ignores the new file/base, so reconnection assumes the original fd remains usable. The reply thread ignores `handle_reply()` errors and loops, relying on reconnect paths for recovery.

## Test Signals
The local unit test covers `Request` timeout, reconnect, and finished transitions. There are no direct tests for socket protocol exchange, generation mismatch, range-map persistence, or fetch-range error mapping in this file. Source size reviewed: 771 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/remote/client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/remote/connection.rs -->
# sources/cloud-native/nydus/storage/src/remote/connection.rs

## Purpose
Provides Unix-domain-socket listener and endpoint primitives for remote blob-manager control messages, including scatter/gather IO and file descriptor passing.

## Important APIs, Types, And Functions
`Error` classifies protocol, socket, fd, and handler failures and exposes `should_reconnect()`. `Listener` wraps `UnixListener` with optional unlink-on-create/drop, nonblocking mode, and accept handling. `Endpoint` wraps `UnixStream` and supports connect/close, `send_iovec(_all)`, `send_slice`, `send_header`, `send_message`, `send_message_with_payload`, `recv_data`, unsafe iovec receives, and typed header/body/payload receive helpers. `get_sub_iovs_offset()` maps a byte count into an iovec index and offset.

## Control Flow
Send helpers serialize headers and bodies by creating byte slices from `ByteValued`-style structs and loop through partial writes, attaching fds only on the first send attempt. Receive helpers use `recvmsg` through `ScmSocket`, convert received fds into owned `File`s, and loop until the requested iovec lengths are filled. Header/body helpers validate `MsgHeader` and message bodies before returning.

## State And Persistence
No durable persistence. `Listener` owns a socket path and removes it on drop when it created the path. `Endpoint` owns a Unix stream and can receive owned file descriptors that become `File` instances.

## Dependencies And Integration Points
Uses `dbs_uhttp::ScmSocket` for fd passing, libc `iovec`, `UnixListener`/`UnixStream`, `vm_memory::ByteValued`, and `remote::message` validators/constants. `remote/client.rs` uses `Endpoint` for request/reply communication with the remote blob manager.

## Risks
The file deliberately exposes unsafe receive APIs where callers must provide writable iovec memory. File descriptor passing over stream sockets requires receive calls to respect message boundaries or fds can be lost; the implementation documents this and tests several boundary cases. Extra fds beyond `MAX_ATTACHED_FD_ENTRIES` are silently discarded by design. `Listener::set_nonblocking(&self, block: bool)` passes its argument directly to `set_nonblocking`, so the parameter name is misleading.

## Test Signals
Tests cover listener creation/from-raw-fd, nonblocking accept without connections, data send/receive, fd passing under multiple boundary patterns and platform differences, extra-fd truncation behavior, and typed send/receive of headers and bodies. Source size reviewed: 1,049 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/remote/connection.rs -->
