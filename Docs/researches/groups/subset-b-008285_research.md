# subset-b-008285 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/encrypt_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/encrypt_reader.rs

## Purpose
Implements streaming AES-256-GCM encryption and decryption wrappers for `tokio::io::AsyncRead`. `EncryptReader` converts plaintext into framed encrypted blocks; `DecryptReader` reverses that framing, supports multipart object segments, validates plaintext length and CRC32, and keeps compatibility with older nonce layouts.

## Important APIs, types, and functions
- `EncryptReader<R>::new` and `new_multipart` wrap an async reader with a 32-byte key and 12-byte nonce.
- `DecryptReader<R>::new` and `new_multipart` consume encrypted block streams and optionally advance through explicit multipart part numbers.
- `poll_read` on both readers is the main state machine.
- `multipart_part_nonce`, `derive_part_nonce`, `derive_legacy_part_nonce`, `derive_block_nonce`, and `derive_nonce_offset` define nonce derivation.
- `TryGetIndex`, `EtagResolvable`, and `HashReaderDetector` capabilities are delegated to the inner reader.

## Control flow
`EncryptReader::poll_read` first drains any buffered framed bytes, then reads up to `ENCRYPTION_BLOCK_SIZE` bytes from the inner reader. Non-empty reads are CRC32-hashed, encrypted with a nonce derived from the base nonce plus `block_index`, prefixed with an 8-byte header and plaintext-length uvarint, buffered, and copied to the caller. EOF emits a `0xFF` terminator header once. `DecryptReader::poll_read` drains plaintext first, then incrementally reads an 8-byte header, handles `0xFF` segment terminators, reads the declared payload, decodes the plaintext length, tries primary and legacy nonces, checks plaintext length and CRC32, buffers plaintext, and advances the block counter.

## State and persistence behavior
All state is in-memory stream state: buffered bytes, current offsets, block index, multipart part index, header progress, payload progress, and completion flags. The wire format is persisted wherever encrypted object data is stored: 8-byte headers, uvarint plaintext lengths, ciphertext plus GCM tag, CRC32, and terminator records. Multipart streams persist each part as its own terminated encrypted segment.

## Dependencies and integration points
Depends on `aes_gcm`, `crc_fast`, `rustfs_utils` uvarint helpers, `pin_project_lite`, Tokio `AsyncRead`, and `tracing`. It integrates with `HashReader`, `EtagReader`, compression readers, and compression indexes via capability delegation. Multipart nonce behavior is important for object upload/download paths that concatenate encrypted part streams.

## Risks and edge cases
The file comment calls the crypto wrapper demonstrational, but it is used as object data plumbing, so nonce uniqueness is critical. The current decryptor indexes `ciphertext_buf[0..16]` before checking the payload is at least 16 bytes, which can panic on malformed short payloads. The 24-bit header length limits payload sizes and must stay compatible with block sizing. Legacy nonce fallbacks intentionally accept weaker historical streams but widen the accepted ciphertext surface.

## Test signals
Tests cover round-trip encryption, large 1 MiB payloads, tiny chunked reads, pending reads, `ReaderStream` and `HardLimitReader` integration, multipart segment concatenation, distinct per-block nonces, non-collision across parts, and legacy single-nonce and multipart nonce layouts.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/encrypt_reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/errors.rs -->
# sources/object-store/rustfs/crates/rio/src/errors.rs

## Purpose
Defines strongly typed validation errors used by the `rio` readers when request bodies, object checksums, SHA-256 values, and declared sizes do not match observed stream data.

## Important APIs, types, and functions
- `Sha256Mismatch`, `BadDigest`, `ChecksumMismatch`, and `InvalidChecksum` represent integrity failures.
- `SizeTooSmall`, `SizeTooLarge`, `SizeMismatch`, and `IncompleteBody` represent body length failures.
- `is_checksum_mismatch` lets higher layers detect a `ChecksumMismatch` through a dynamic error reference.

## Control flow
The file contains no runtime state machine. Its structs are constructed by readers such as `HardLimitReader` and `HashReader`, then carried inside `std::io::Error` or exposed directly as error sources. `is_checksum_mismatch` performs a single `downcast_ref` check.

## State and persistence behavior
There is no persistence. Error structs store expected and observed values as strings or `i64` counts so API layers can map internal validation failures to S3-compatible responses and diagnostics.

## Dependencies and integration points
Depends on `thiserror::Error`. `HashReader` uses `ChecksumMismatch` for content checksum mismatches, while `HardLimitReader` embeds `IncompleteBody` when EOF arrives before the declared content length. API code can use these types to map to S3 errors such as BadDigest or incomplete body.

## Risks and edge cases
Several similarly named size errors exist; callers need to preserve the correct one to avoid ambiguous client responses. `is_checksum_mismatch` only detects a direct `ChecksumMismatch`, not one nested under multiple error wrappers unless the caller unwraps sources.

## Test signals
This file has no local tests. Indirect coverage comes from `HashReader` checksum tests and `HardLimitReader` incomplete-body tests that assert specific error kinds and downcastable markers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/etag.rs -->
# sources/object-store/rustfs/crates/rio/src/etag.rs

## Purpose
Provides tests and module documentation for the trait-based ETag resolution model used by `rio`. It validates that ETags can be found through nested reader wrappers such as compression, encryption, `HashReader`, and `EtagReader`.

## Important APIs, types, and functions
- Exercises `resolve_etag_generic`.
- Uses `EtagReader`, `HashReader`, `CompressReader`, and `EncryptReader` as representative wrappers.
- Relies on `EtagResolvable` delegation implementations from `lib.rs` and the reader modules.

## Control flow
The tests create direct and nested reader stacks, sometimes consume them to EOF, then call `resolve_etag_generic`. ETag-bearing wrappers return either a configured checksum or a finalized MD5. Transforming wrappers delegate resolution to their inner reader. Tests also cover `None` paths where no ETag is available.

## State and persistence behavior
No production state is defined in this file. The important state under test lives inside wrapped readers: `EtagReader` must finish before exposing calculated MD5 values, while `HashReader` can expose configured ETags when MD5 tracking is not disk-deferred.

## Dependencies and integration points
Depends on MD5 and hex encoding in tests, `rustfs_utils::compress::CompressionAlgorithm`, Tokio readers, and the local reader stack. It is a cross-module integration test for the capability traits exported by `rio`.

## Risks and edge cases
Because this file is test-only, regressions in ETag propagation would break object metadata/reporting without touching any production code here. The tests assume wrapper order does not obscure the inner capability; new wrappers must implement the delegation macros or ETag discovery will silently return `None`.

## Test signals
Signals include direct `EtagReader` resolution, `HashReader` resolution, single and double wrapper delegation, complex compression/encryption nesting, `HashReader` in nested structures, real-world simulated stacks, and explicit no-ETag scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/etag.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/etag_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/etag_reader.rs

## Purpose
Implements an `AsyncRead` wrapper that computes an MD5 ETag while bytes pass through and optionally verifies the final MD5 against an expected checksum.

## Important APIs, types, and functions
- `EtagReader<R>` stores `inner`, `md5`, `finished`, `checksum`, and cached `resolved_etag`.
- `new` constructs the wrapper.
- `get_etag` finalizes a clone of the MD5 state once and caches the hex result.
- `AsyncRead::poll_read` updates the hasher and validates at EOF.
- Implements `EtagResolvable`, `HashReaderDetector`, and `TryGetIndex`.

## Control flow
`poll_read` returns EOF immediately after `finished` is set. Otherwise it records the buffer's existing filled length, polls the inner reader, and hashes only newly appended bytes. A zero-byte successful read is treated as EOF: it finalizes or reuses the ETag and compares it with `checksum` if present. Mismatches return `InvalidData`.

## State and persistence behavior
The reader maintains only in-memory hashing state. The persisted value is indirect: after stream completion, the MD5 hex string can become object metadata or be compared to client-provided Content-MD5/ETag expectations. `resolved_etag` prevents repeated calls from changing the observed value.

## Dependencies and integration points
Depends on `md5`, `hex_simd`, `pin_project_lite`, Tokio `AsyncRead`, and `tracing`. `HashReader` wraps streams in `EtagReader` when MD5 is not disk-deferred. Compression/encryption wrappers delegate ETag discovery through it.

## Risks and edge cases
Calculated ETags are unavailable until EOF unless an expected checksum was supplied, in which case `try_resolve_etag` returns that checksum early. Callers that need the actual computed MD5 must ensure the stream is fully consumed. MD5 is not a cryptographic integrity guarantee by itself, so stronger checksums handled by `HashReader` remain important.

## Test signals
Tests cover basic MD5 calculation, empty streams, repeated resolution, partial unread streams returning `None`, large random data, successful checksum verification, and checksum mismatch returning `InvalidData`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/etag_reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/hardlimit_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/hardlimit_reader.rs

## Purpose
Implements an exact-length `AsyncRead` wrapper. It allows exactly the declared number of bytes, reports `IncompleteBody` if the inner stream ends early, and rejects any bytes beyond the limit.

## Important APIs, types, and functions
- `HardLimitReader<R>::new(inner, limit)` creates the wrapper.
- `remaining` tracks bytes still required.
- `AsyncRead::poll_read` enforces underflow and overflow behavior.
- Capability delegation is provided through `delegate_reader_capabilities_generic!`.

## Control flow
If `remaining` is negative, reads fail. If `remaining` is zero, the wrapper probes the inner reader with an 8 KiB discard buffer: true EOF succeeds, but any extra byte returns an error. Otherwise it polls the inner reader into the caller buffer, subtracts the number of newly read bytes, returns `UnexpectedEof` with `IncompleteBody` if EOF occurs while bytes are still required, and errors if the read overshoots the limit.

## State and persistence behavior
State is the in-memory remaining byte count. It does not persist data, but it is a boundary guard for persisted object writes: data shorter or longer than declared content length should not become accepted object payload.

## Dependencies and integration points
Depends on Tokio `AsyncRead`, `pin_project_lite`, and the local `IncompleteBody` error. `HashReader` wraps positive-size inputs with `HardLimitReader`; encryption/decryption and HTTP streams can sit inside or outside this guard. Tests use `rustfs_utils::read_full`.

## Risks and edge cases
The wrapper must be polled after exactly reading the declared bytes to detect extra input; callers that stop immediately after the limit may miss trailing bytes. It can also block waiting for the overflow probe if the underlying stream remains open. The error for too many bytes is a generic `Other` error string rather than a typed size error.

## Test signals
Tests cover normal reads, exact limits, exceeding limits, empty streams, short input producing `UnexpectedEof` with an `IncompleteBody` marker, and rejection of extra bytes after the limit has been consumed.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/hardlimit_reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/hash_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/hash_reader.rs

## Purpose
Provides the main request-body validation reader for RustFS object I/O. `HashReader` composes length enforcement, MD5/ETag handling, SHA-256 verification, S3 checksum validation or calculation, and trailing checksum extraction around a dynamic async reader.

## Important APIs, types, and functions
- `HashReader::from_stream`, `from_reader`, and `new` construct wrappers for plain, capability-aware, or already boxed readers.
- `HashReaderMut` exposes mutable parameters and inner-reader extraction for nested wrapping.
- `add_checksum_from_s3s`, `add_checksum_no_trailer`, `add_non_trailing_checksum`, and `add_calculated_checksum` configure checksum behavior.
- `checksum`, `content_crc_type`, and `content_crc` expose validated/calculated checksum metadata.
- `AsyncRead::poll_read` updates hashers and finalizes validation at EOF.

## Control flow
Construction wraps positive-size streams in `HardLimitReader` and, unless `diskable_md5` is set, `EtagReader`. `new` detects an existing unread `HashReader` through `HashReaderDetector`, validates compatible size/checksum metadata, transfers its inner reader, and preserves checksum/trailer state. During reads, newly filled bytes increment `bytes_read` and feed optional SHA-256 and content-checksum hashers. On the first EOF, it compares SHA-256, loads trailing checksum headers if needed, calculates content checksums, fills missing calculated checksum values, or returns `ChecksumMismatch` wrapped in `InvalidData`.

## State and persistence behavior
The reader stores expected size, actual size, optional MD5, checksum selection and values, optional trailing headers, byte count, and one-shot EOF validation state. It does not persist directly, but the resulting ETag and content checksum maps are object metadata signals and the length/checksum validations decide whether incoming data is acceptable.

## Dependencies and integration points
Depends on local checksum types and hashers, `HardLimitReader`, `EtagReader`, reader capability traits, `s3s::TrailingHeaders`, HTTP headers, base64, `hex_simd`, and Tokio `AsyncRead`. It is intended for S3 PUT/upload/copy paths, trailer-aware checksums, and transformation layers such as compression/encryption using `SIZE_PRESERVE_LAYER`.

## Risks and edge cases
Wrapping an already-read `HashReader` is rejected, but nested wrapper state transfer is subtle and can lose behavior if new wrappers do not implement capability traits. SHA-256 mismatches currently return a generic string rather than the typed `Sha256Mismatch`. Trailer checksums are read only at EOF, so missing or malformed trailer values surface late. `diskable_md5` suppresses ETag resolution and must align with callers that compute MD5 elsewhere.

## Test signals
Tests cover wrapper construction, boxed capability delegation, boxed encrypt-reader inputs, basic ETag generation, diskable MD5 suppression, calculated CRC64 metadata, wrapping an existing `HashReader`, compression/encryption round trips, compressible data, and gzip/deflate/zstd compression algorithms.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/hash_reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/http_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/http_reader.rs

## Purpose
Implements HTTP-backed async read and write adapters for RustFS internode streaming RPCs and other HTTP transfers. It also centralizes reqwest client caching, outbound TLS/mTLS refresh, proxy bypass for loopback, internode metrics, classified errors, and optional read stall timeouts.

## Important APIs, types, and functions
- `HttpReader::new`, `new_with_stall_timeout`, and `with_capacity` issue a request immediately and expose the response body as `AsyncRead`.
- `HttpWriter::new` spawns a background request and exposes the request body as `AsyncWrite`.
- `InternodeHttpErrorKind`, `InternodeHttpRequestContext`, and `InternodeHttpError` classify and carry retryable HTTP/network failures.
- `get_http_client`, `build_http_client`, and `CLIENT_CACHE` manage generation-aware TLS client reuse.
- Metric helpers record outgoing requests, bytes, and classified errors for known `/rustfs/rpc/*` routes.

## Control flow
Client lookup chooses the normal or no-proxy reqwest client based on the URL host and current outbound TLS generation. `HttpReader` sends the request, rejects non-success status codes, wraps `bytes_stream` in `StreamReader`, records received bytes on each read, and resets or fires a stall timer. `HttpWriter` creates an mpsc stream of optional byte chunks, spawns a reqwest request using `Body::wrap_stream`, buffers small writes up to 1 MiB, sends large writes directly, sends `None` on shutdown, and waits for the background task to finish.

## State and persistence behavior
Persistent data is not stored here, but streaming state includes cached TLS clients, request metadata, pending writer chunks, finish state, background task handle, and one-shot error channel. Metrics are emitted to the global internode metrics registry. TLS state is refreshed by generation and stale generations are recorded.

## Dependencies and integration points
Depends on `reqwest`, `tokio`, `tokio-util`, `futures`, `bytes`, `http`, `rustfs_tls_runtime`, `rustfs_io_metrics`, `rustfs_config`, `rustfs_utils`, and `rustls_pki_types`. It integrates with internode read-file, put-file, and walk-dir RPC paths, plus the generic `Writer` enum and reader capability traits.

## Risks and edge cases
Error classification relies partly on reqwest flags and message text, which can change. `HttpWriter::new` reports success before the server response is known; write calls later observe async failures via `err_rx` or shutdown. The mpsc channel and 1 MiB buffer bound memory, but slow receivers can apply backpressure. Loopback proxy bypass is critical for tests and local RPC safety. TLS cache races are guarded, but a stale generation can still be used until detection.

## Test signals
Tests cover route-to-operation mapping, no preflight HEAD/PUT behavior, stall timeout after partial progress, many small writes, vectored writes, request error context, retryability for gateway statuses, DNS error IO kind, status error source/context, test helper retryability, and loopback proxy bypass.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/http_reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/lib.rs -->
# sources/object-store/rustfs/crates/rio/src/lib.rs

## Purpose
Defines the public surface and shared capability traits for the `rustfs-rio` crate. It re-exports reader/writer wrappers, checksum utilities, compression/encryption types, and dynamic reader abstractions used by object I/O.

## Important APIs, types, and functions
- Exports `LimitReader`, `EtagReader`, `CompressReader`, `DecompressReader`, `EncryptReader`, `DecryptReader`, `HardLimitReader`, `HashReader`, checksum APIs, `WarpReader`, `Writer`, `HttpReader`, `HttpWriter`, `Index`, and `TryGetIndex`.
- Defines `ReadStream`, `ReaderCapabilities`, `Reader`, and `DynReader`.
- Defines `EtagResolvable`, `resolve_etag_generic`, and `HashReaderDetector`.
- Provides delegation macros for wrapper capability forwarding.
- `boxed_reader` and `wrap_reader` convert typed readers to `DynReader`.

## Control flow
There is little runtime logic. The module graph is assembled, traits define default no-op capabilities, blanket impls turn compatible async readers into crate reader traits, and `Box<T>` implementations forward capability calls to boxed dynamic readers.

## State and persistence behavior
No persistent state is stored. The file defines compile-time composition rules that determine whether runtime wrappers can expose ETag, hash-reader, and compression-index information through arbitrary nesting.

## Dependencies and integration points
Depends on Tokio traits through `ReadStream`, local modules, and compression index types. The exported `DynReader` contract is used by `HashReader`, HTTP adapters, compression/encryption wrappers, and higher-level object store code that wants a single boxed async reader type with metadata capabilities.

## Risks and edge cases
The delegation macros are central: any new wrapper that forgets to use them can hide ETags, hash-reader mutation, or compression indexes from outer layers. `DEFAULT_ENCRYPTION_BLOCK_SIZE` is 1 MiB while `encrypt_reader.rs` uses an internal 8 KiB block constant, so callers should not assume this public constant controls the current encryption frame size.

## Test signals
`lib.rs` has no local tests, but `etag.rs`, `hash_reader.rs`, compression, encryption, and HTTP tests exercise the public exports and trait forwarding.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/limit_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/limit_reader.rs

## Purpose
Implements a soft byte-limiting `AsyncRead` wrapper that stops after a configured number of bytes without treating extra bytes in the inner reader as an error.

## Important APIs, types, and functions
- `LimitReader<R>::new(inner, limit)` creates the wrapper.
- Fields track `limit`, `read`, and a `scratch` buffer for partial allowed reads.
- `AsyncRead::poll_read` enforces the visible byte cap.
- Capability delegation uses `delegate_reader_capabilities_generic!`.

## Control flow
Each read computes `remaining = limit - read`. If no bytes remain, it returns EOF. If the caller buffer has room for no more than the remaining limit, it polls the inner reader directly and increments `read` by the new bytes. If the caller buffer is larger than the allowed remainder, it polls the inner reader into `scratch`, copies only the filled bytes into the caller buffer, and updates `read`.

## State and persistence behavior
State is in-memory byte accounting plus a reusable scratch buffer. The wrapper does not consume or validate bytes after the limit, so the underlying stream may still contain data. This is suitable for range-like truncation, not strict content-length enforcement.

## Dependencies and integration points
Depends on Tokio `AsyncRead` and `pin_project_lite`. It integrates with the same reader capability system as other wrappers, allowing ETag and hash metadata discovery through the limit layer.

## Risks and edge cases
Because extra bytes are not rejected, using `LimitReader` for client-declared content length would allow overlong bodies to be accepted by callers that stop at EOF from this wrapper. The scratch buffer resizes to the remaining allowed amount when the caller buffer is too large.

## Test signals
Tests cover exact reads, truncating larger data, zero limits, multiple reads across the limit boundary, and a 3 MiB random-data read.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/limit_reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/reader.rs -->
# sources/object-store/rustfs/crates/rio/src/reader.rs

## Purpose
Defines `WarpReader`, a minimal adapter that turns any plain `AsyncRead + Unpin + Send + Sync` into a reader participating in `rio` capability traits.

## Important APIs, types, and functions
- `WarpReader<R>` stores `inner`.
- `WarpReader::new` constructs the adapter.
- `AsyncRead::poll_read` forwards directly to `inner`.
- Empty implementations of `HashReaderDetector`, `EtagResolvable`, and `TryGetIndex` mark the wrapped stream as capability-compatible but with no special metadata.

## Control flow
The read path is a single delegation to `Pin::new(&mut inner).poll_read(cx, buf)`. Capability calls use default trait behavior from `lib.rs`.

## State and persistence behavior
No state is added beyond ownership of the inner reader. It does not persist data or metadata and does not transform bytes.

## Dependencies and integration points
Depends on Tokio `AsyncRead`, local `TryGetIndex`, `EtagResolvable`, and `HashReaderDetector`. `wrap_reader` and `HashReader::from_stream` use `WarpReader` to bring ordinary readers into the `DynReader` ecosystem.

## Risks and edge cases
`WarpReader` intentionally hides any capabilities the original concrete type might have unless that type is wrapped through a more specific path. It requires `Unpin + Send + Sync`, matching the crate's dynamic reader contract.

## Test signals
There are no local tests. Indirect coverage comes from `HashReader::from_stream`, boxed reader capability tests, and all higher-level wrappers that accept plain `Cursor` or `BufReader` inputs.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/writer.rs -->
# sources/object-store/rustfs/crates/rio/src/writer.rs

## Purpose
Provides a small dynamic `AsyncWrite` enum for writing to memory, HTTP streams, or arbitrary boxed async writers through one type.

## Important APIs, types, and functions
- `Writer::Cursor`, `Writer::Http`, and `Writer::Other` variants.
- Constructors `from_tokio_writer`, `from_cursor`, and `from_http`.
- Accessors and consuming extractors for cursor and HTTP variants.
- `AsyncWrite` implementation delegates write, flush, and shutdown to the selected variant.

## Control flow
Construction boxes HTTP and arbitrary writers as needed. Runtime write operations pattern-match on the enum variant and pin-project the contained writer with `Pin::new`, then call the corresponding async write method.

## State and persistence behavior
`Cursor` stores bytes in memory and can be extracted with `into_cursor_inner`. `Http` writes are persisted only by the remote HTTP endpoint. `Other` delegates persistence semantics to the supplied writer.

## Dependencies and integration points
Depends on Tokio `AsyncWrite`, `std::io::Cursor`, and local `HttpWriter`. It is the output-side companion to `DynReader` for code that needs a single write target type.

## Risks and edge cases
The enum is `Unpin` only because its variants are compatible with `Pin::new` usage here; adding a non-`Unpin` writer would require a different projection strategy. Extractor methods consume or borrow only matching variants and silently return `None` otherwise.

## Test signals
There are no local tests. HTTP writer behavior is tested in `http_reader.rs`; cursor behavior relies on Tokio's `AsyncWrite` implementation for `Cursor<Vec<u8>>`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/writer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-ops/Cargo.toml -->
# sources/object-store/rustfs/crates/s3-ops/Cargo.toml

## Purpose
Defines the `rustfs-s3-ops` crate package metadata. The crate is a small data-structure/library crate for S3 operation enums and event mapping.

## Important APIs, types, and functions
The manifest names the crate `rustfs-s3-ops`, uses workspace version, edition, license, repository, rust-version, and homepage settings, and describes the crate as "S3 operation enum and event mapping for RustFS." It declares keywords/categories and disables doctests for the library target.

## Control flow
Cargo uses this file to resolve the crate and its single dependency before compiling `src/lib.rs`.

## State and persistence behavior
No runtime state exists. The manifest participates in workspace dependency resolution and package publication metadata.

## Dependencies and integration points
The only crate dependency is `rustfs-s3-types` from the workspace, which supplies `EventName`. Lints are inherited from the workspace.

## Risks and edge cases
Because the crate is intentionally narrow, adding operation mappings that need serialization or parsing would require updating dependencies and possibly enabling doctests. The manifest relies on workspace keys, so it cannot be built standalone without the workspace context.

## Test signals
No manifest-specific tests exist. `cargo test -p rustfs-s3-ops` would compile this manifest and run the mapping tests in `src/lib.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-ops/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-ops/src/lib.rs -->
# sources/object-store/rustfs/crates/s3-ops/src/lib.rs

## Purpose
Defines `S3Operation` and maps S3 API operations to notification `EventName` values. It also provides helper functions for event compatibility, delete-marker event selection, POST-vs-PUT object-created events, and object-created mask construction.

## Important APIs, types, and functions
- `S3Operation` enumerates bucket, object, multipart, ACL, lifecycle, replication, restore, select, and public-access operations.
- `S3Operation::as_str` returns IAM-style names such as `s3:PutObject`.
- `to_event_name`, `event_name_to_s3_operation`, and `operation_matches_event_name` map between operations and events.
- `delete_event_name_for_marker`, `put_event_name_for_post_object`, `is_object_removed_event`, and `put_object_created_event_mask` encode common notification decisions.
- Private `EventMapping` handles one-to-many compatibility.

## Control flow
Each operation maps through `event_mapping`. Simple operations use `Single(EventName)`, while `PutObject`, `DeleteObject`, and `DeleteObjects` have custom matching sets. The reverse mapping matches event variants to the best corresponding S3 operation and returns `None` for compound or internal events with no public operation.

## State and persistence behavior
No state is stored. The mappings are pure constants in match expressions. Their outputs influence emitted notification records and filtering masks, which are persisted or delivered by higher-level notification systems.

## Dependencies and integration points
Depends on `rustfs_s3_types::EventName`. Higher-level S3 handlers can use this crate to convert executed operations into notification event names and to test whether configured event subscriptions match an operation.

## Risks and edge cases
Mappings are semantic contracts. Unmapped operations such as `UploadPart` intentionally emit no event here, while complete multipart upload does. Batch delete can match both internal batch and per-object delete events. Adding a new `EventName` or `S3Operation` requires updating both forward and reverse matches plus tests.

## Test signals
Tests cover operation-to-event mapping, event-to-operation mapping, multi-variant operation matching, delete-marker and POST-object helpers, object-removed detection, created-event mask bits, and unmapped operation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-ops/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-types/Cargo.toml -->
# sources/object-store/rustfs/crates/s3-types/Cargo.toml

## Purpose
Defines the `rustfs-s3-types` crate package metadata. The crate owns reusable S3 event type definitions for RustFS.

## Important APIs, types, and functions
The manifest names the crate `rustfs-s3-types`, inherits workspace package metadata and lints, describes the crate as S3 event type definitions, and disables library doctests.

## Control flow
Cargo reads this manifest to compile the event types in `src/event_name.rs` and expose them through `src/lib.rs`.

## State and persistence behavior
No runtime state exists. Package metadata controls workspace builds and crates.io/docs presentation if published.

## Dependencies and integration points
Depends on workspace `serde` and `serde_json` for event serialization/deserialization support. `rustfs-s3-ops` depends on this crate.

## Risks and edge cases
The crate relies on workspace-managed versions. Removing serde dependencies would break the custom serialize/deserialize implementations in `EventName`.

## Test signals
No manifest-local tests exist. `cargo test -p rustfs-s3-types` would validate the event parsing and serde tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-types/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-types/src/event_name.rs -->
# sources/object-store/rustfs/crates/s3-types/src/event_name.rs

## Purpose
Defines RustFS S3 notification event names, parsing/formatting, compound event expansion, bitmask generation, schema version selection, and serde integration.

## Important APIs, types, and functions
- `EventName` enumerates object accessed/created/removed, bucket, replication, restore, transition, lifecycle, scanner, ACL/tagging, intelligent-tiering, compound `All` variants, `Everything`, and internal metrics events.
- `ParseEventNameError` reports invalid strings.
- `EventName::parse`, `try_from_event_str`, `as_str`, `expand`, and `mask` implement string and mask behavior.
- `event_schema_version` returns S3 notification schema version `2.1`, `2.2`, or `2.3`.
- `Display`, `From<&str>`, `Serialize`, and `Deserialize` connect event names to external representations.

## Control flow
Parsing is an explicit string match over supported S3 event strings and aliases. Formatting matches enum variants back to strings, with `Everything` formatting as an empty string for Go compatibility. `expand` maps compound variants to their concrete single-event lists, and `mask` uses sequential discriminants for single events or recursively ORs expanded masks for compound events.

## State and persistence behavior
There is no mutable state. The enum discriminants and mask layout are a persistence-sensitive contract for event filter masks. Serialized strings are part of S3 notification configuration and emitted event payloads.

## Dependencies and integration points
Depends on `std::fmt`, `serde`, and `serde_json` in tests. `rustfs-s3-ops` consumes `EventName` for operation mapping, and notification configuration/delivery code can use masks and schema versions.

## Risks and edge cases
Single-event discriminants must remain sequential through `LAST_SINGLE_TYPE_VALUE` or masks will change. `SINGLE_EVENT_NAMES_IN_ORDER` currently has 32 entries, while later single events are appended through `SINGLE_AWS_AND_EXTENSION_EVENTS_AFTER_COMPAT`; this preserves compatibility but requires care when adding events. `From<&str>` panics on invalid input, so fallible parsing is safer for external config. Internal events have strings but are not accepted by `parse`.

## Test signals
Tests cover serde round trips, invalid deserialization including empty `Everything`, alias parsing, AWS-compatible `ObjectCreatedAll` expansion, schema version mapping, and `try_from_event_str` success/failure.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-types/src/event_name.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-types/src/lib.rs -->
# sources/object-store/rustfs/crates/s3-types/src/lib.rs

## Purpose
Provides the public API surface for the `rustfs-s3-types` crate by exposing the event-name module.

## Important APIs, types, and functions
- Declares `mod event_name`.
- Re-exports `EventName`, `ParseEventNameError`, and `event_schema_version`.

## Control flow
There is no runtime control flow. The module declaration compiles `event_name.rs`, and the `pub use` line makes selected symbols available to downstream crates.

## State and persistence behavior
No state or persistence is implemented here. Persistence contracts come from the re-exported event enum's serialized strings and masks.

## Dependencies and integration points
Integrates `event_name.rs` with consumers such as `rustfs-s3-ops` and any notification code importing `rustfs_s3_types`.

## Risks and edge cases
Only the explicitly re-exported items are public. New helper functions added to `event_name.rs` will remain private to the crate unless added here.

## Test signals
No local tests exist. The re-export is validated indirectly when downstream crates and the `event_name.rs` tests compile.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-types/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/Cargo.toml -->
# sources/object-store/rustfs/crates/s3select-api/Cargo.toml

## Purpose
Defines the `rustfs-s3select-api` crate package metadata and dependencies for RustFS S3 Select query support.

## Important APIs, types, and functions
The manifest names the crate, inherits workspace package metadata, sets documentation URL, describes S3 Select support, and disables library doctests. Dependencies include query execution, async streaming, object-store integration, S3 protocol types, error handling, and runtime utilities.

## Control flow
Cargo resolves the declared workspace dependencies and compiles modules exported by `src/lib.rs`: `object_store`, `query`, and `server`.

## State and persistence behavior
No runtime state is defined. Dependency selection determines which backends and query engines are available to the S3 Select implementation.

## Dependencies and integration points
Key dependencies include `datafusion`, `object_store`, `rustfs-ecstore`, `s3s`, `tokio`, `tokio-util`, `futures`, `bytes`, `http`, `snafu`, `parking_lot`, `tracing`, `transform-stream`, and `url`. These tie S3 Select SQL parsing/execution to RustFS object data and server streaming.

## Risks and edge cases
This crate has a broad dependency surface. DataFusion version changes can affect error variants, SQL behavior, and planner output. The manifest relies on workspace versions and cannot be evaluated independently from the workspace.

## Test signals
No manifest-local tests exist. `cargo test -p rustfs-s3select-api` would compile this dependency set and run tests in the crate modules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/lib.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/lib.rs

## Purpose
Defines the public top-level API for S3 Select query handling: module exports, shared `QueryResult`, structured `QueryError`, and `ResolvedTable`.

## Important APIs, types, and functions
- Public modules: `object_store`, `query`, and `server`.
- `QueryResult<T>` aliases `Result<T, QueryError>`.
- `QueryError` variants cover DataFusion, not implemented features, multiple SQL statements, dispatcher build failures, cancellation, parser errors, missing/existing UDFs, and store errors.
- `From<DataFusionError>` preserves embedded `QueryError` values from `DataFusionError::External`.
- `ResolvedTable` wraps a table/path string and implements `table()` and `Display`.

## Control flow
Error conversion checks whether a DataFusion external error already contains a `QueryError`; if so it unwraps and returns it, avoiding double wrapping. All other DataFusion errors are boxed with caller location and SNAFU backtrace. `ResolvedTable` is a simple value object used by query planning/resolution code.

## State and persistence behavior
No persistent state is stored. `QueryError` captures diagnostic state, including optional backtrace/location for DataFusion failures. `ResolvedTable` stores the resolved table path/name as an owned string.

## Dependencies and integration points
Depends on `datafusion` error/parser types, `snafu`, and standard `Display`. The exported modules connect this top-level API to object-store access, query execution, and S3 Select server responses.

## Risks and edge cases
The `From<DataFusionError>` implementation unwraps a downcast after checking it, which is safe only if the external error is not concurrently changed, but the pattern is still brittle around type erasure. `MultiStatement` enforces a single-statement contract, which callers must preserve before dispatch. Error display text is part of test expectations and may leak to clients.

## Test signals
Tests cover display strings for major `QueryError` variants, conversion from DataFusion plan errors, parser error formatting, `ResolvedTable::table`, display, clone, equality, and inequality.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/lib.rs -->
