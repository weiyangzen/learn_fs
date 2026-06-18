# Research: subset-b-008284

Grouped research report for the requested RustFS proto and rio/rio-v2 files. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/lib.rs -->
# sources/object-store/rustfs/crates/protos/src/lib.rs

Purpose: this crate entrypoint exposes generated node-service protobuf/tonic types and owns the reusable internode gRPC channel constructor used by RustFS cluster components. It wraps `mod generated` in a scoped `unsafe_code` allowance, re-exports all generated symbols, aliases the long `NodeServiceClient<InterceptedService<Channel, ...>>` type as `NodeServiceClientType`, and defines the default 100 MB gRPC message limit constant.

Important APIs and control flow: `create_new_channel(addr)` builds a tonic `Endpoint` with env-driven connect timeout, TCP keepalive, HTTP/2 keepalive interval/timeout, idle keepalive, and RPC timeout. It reads values through `rustfs_utils::get_env_u64` and `rustfs_config` defaults. For `https://` addresses it loads `rustfs_tls_runtime` outbound TLS state, optionally installs a custom root CA, derives the domain from the URL for hostname verification, and attaches an mTLS identity when present. It records dial latency/success through `rustfs_io_metrics::internode_metrics`, caches the successful `Channel` in `rustfs_common::GLOBAL_CONN_MAP`, and stores the TLS generation for the address. `evict_failed_connection(addr)` removes both the global connection and TLS generation cache entry after RPC failures.

State and persistence: state is in process memory only. `TLS_GENERATION_CACHE` is a `LazyLock<tokio::sync::Mutex<HashMap<String, u64>>>`, bounded by `TLS_GENERATION_CACHE_MAX_SIZE`. `enforce_tls_generation_cache_bound` first retains entries on the current TLS generation, then evicts one arbitrary entry if still full. This cache allows the code to detect when a connection address has moved across TLS generations and call `record_tls_consumer_stale_generation`.

Dependencies and integration points: this file sits between generated protobuf clients, tonic transport, global RustFS connection caching, TLS runtime publication, and internode metrics. It must remain compatible with the generated `node_service` module and any caller expecting cached tonic channels to be reused or evicted globally.

Risks: URL hostname parsing is intentionally simple and may not handle uncommon URL forms; a malformed HTTPS address can fall back to TLS without explicit domain. Cache eviction chooses the first hash-map key when all retained entries are current generation, so eviction order is nondeterministic. Failed dials are not cached, so repeated callers can stampede dead peers unless upstream throttles retries. The test signal is narrow but relevant: it verifies cache bounding removes an entry when the retained generation is still full.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/main.rs -->
# sources/object-store/rustfs/crates/protos/src/main.rs

Purpose: this build-generation utility compiles `node.proto` and FlatBuffers model schemas into checked-in generated Rust modules under `crates/protos/src/generated`. It is tool-version gated so local builds avoid regenerating code when `protoc` or `flatc` are older/incompatible unless explicitly forced by environment.

Important APIs and control flow: `main()` probes `protoc --version`, compares only the major version against `VERSION_PROTOBUF`, and skips generation with cargo warnings unless the version is equal/newer under the current `BUILD_PROTOS` policy. When generation proceeds, it calls `tonic_prost_build::configure()` with output directory `generated/proto_gen`, `--experimental_allow_proto3_optional`, well-known type compilation, bytes mapping for all fields, and `emit_rerun_if_changed(false)`. It then writes `generated/proto_gen/mod.rs` and `generated/mod.rs` manually with license headers and module exports. FlatBuffers generation is delegated to `compile_flatbuffers_models`, which probes `flatc`, creates `generated/flatbuffers_generated/mod.rs`, updates the parent generated module to re-export requested modules, and runs `flatc --rust --gen-mutable --gen-onefile --gen-name-strings --filename-suffix ""` for each `.fbs` model. `fmt()` finally invokes `cargo fmt -p rustfs-protos`.

State and persistence: this program writes generated Rust files directly into the source tree rather than `OUT_DIR`. It also emits cargo warnings but disables rerun-if-changed emission, so regeneration is controlled externally by running this tool/build step and environment variables, not by normal Cargo change detection.

Dependencies and integration points: depends on external `protoc`, `flatc`, `tonic_prost_build`, FlatBuffers schemas such as `models.fbs`, and Cargo workspace layout assumptions: `env::current_dir()?.join("crates/protos/src")`. `ENV_FLATC_PATH` can override the binary path. Generated modules are consumed by `lib.rs`.

Risks: only major versions are compared, despite comments documenting exact versions; newer major versions regenerate, older majors skip, and `BUILD_PROTOS` has non-obvious behavior where non-empty/non-zero values still reject equal major versions via an "Unknown version comparison error" path. Writing generated code into `src` can dirty the working tree and make builds host-tool dependent. Path assumptions fail if invoked outside the workspace root. There are no unit tests in this file; practical validation is successful code generation plus downstream compile of `rustfs-protos`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/node.proto -->
# sources/object-store/rustfs/crates/protos/src/node.proto

Purpose: this proto file defines RustFS internode `NodeService`, covering metadata/bucket operations, disk and erasure-storage operations, distributed locking, peer-admin/system introspection, IAM/policy reload hooks, rebalance/tiering controls, and live event retrieval. It is the primary RPC contract generated into tonic client/server types.

Important APIs and messages: common responses use `success` plus either `optional Error` or `optional string error_info`. Bucket APIs include `HealBucket`, `ListBucket`, `MakeBucket`, `GetBucketInfo`, and `DeleteBucket`. Disk APIs model low-level volume/object operations such as `ReadAll`, `WriteAll`, `Delete`, `VerifyFile`, `ReadParts`, `CheckParts`, `RenamePart`, `RenameFile`, `Write`, `WriteStream`, `ReadAt`, `WalkDir`, volume operations, metadata read/update/write, versioned object reads/deletes, batched deletes, `ReadMultiple`, and `DiskInfo`. Lock APIs share `GenerallyLockRequest/Response` and have batch variants. Peer-admin APIs transfer serialized byte payloads for storage/server/sys metrics and support profiling, bucket stats, IAM/policy/user/group loads/deletes, site replication reload, service signal, background heal status, metacache, pool/rebalance, tier config, and `GetLiveEvents`.

Control flow and data encoding: the proto itself is declarative, but it reveals important runtime flows. Some RPCs are bidirectional or server streaming: `WriteStream`, streamed `ReadAt`, streamed `WalkDir`. Many fields that are Rust structs elsewhere are encoded as `string` JSON (`file_info`, `opts`, lock args) or opaque `bytes` (`*_bin`, metrics, object-part infos). Newer binary fields coexist with older string fields for metadata/version calls, indicating migration compatibility.

State and persistence: requests carry disk, volume, path, version, and metadata information that mutate or inspect persistent object-store state on remote nodes. The proto does not persist itself, but field numbers are persistent wire compatibility constraints. Optional proto3 fields distinguish absent errors from empty error values.

Dependencies and integration points: generated by `main.rs` into `node_service` modules and re-exported by `lib.rs`. Server implementations must map these RPCs to storage, lock, admin, IAM, rebalance, and event subsystems; clients rely on stable names and field numbers.

Risks: a large mixed contract makes backward compatibility hard: removing or renumbering fields would break stored clients. Extensive JSON-in-string payloads reduce schema validation and push errors to runtime. The combination of `success=false`, optional `Error`, and optional string `error_info` is inconsistent across families, so clients must inspect per-RPC semantics. Test signal is indirect: generation/compile and integration tests are the main protection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/node.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/Cargo.toml -->
# sources/object-store/rustfs/crates/rio-v2/Cargo.toml

Purpose: this manifest declares `rustfs-rio-v2` as a feature-gated compatibility facade for incremental RustFS migration. Its dependency set shows the crate is not a full replacement for `rustfs-rio`; it reuses the old crate for shared reader traits and replaces specific compression/encryption/index behavior.

Important APIs and dependencies: runtime dependencies include `rustfs-rio` for shared traits/types, `tokio` for async reads, `pin-project-lite` for pinned reader wrappers, `bytes` and `serde_json` for index serialization, `minlz` for S2/minlz compression, `aes-gcm`, `hmac`, `sha2`, `rand`, and `hex` for DARE v2 encryption, multipart key derivation, and tests. `rustfs-utils` supplies compression algorithm type compatibility. Dev dependencies `rustfs-filemeta` and `walkdir` support generated MinIO fixture parsing tests.

State and persistence: the manifest itself has no runtime state, but it fixes the public crate identity, docs URL, categories, and workspace lints. The dependency on `minlz = "1.1.0"` is a direct non-workspace pin and is important for wire compatibility with MinIO-style S2 blocks.

Integration points: `rustfs-rio-v2` exports a subset of new readers while re-exporting `rustfs-rio` traits. Downstream code can switch imports to rio-v2 without losing APIs like `HashReader`, `EtagReader`, `LimitReader`, `TryGetIndex`, and `Index`.

Risks and test signals: because this crate mixes old and new components, semver-compatible changes in `rustfs-rio` can affect rio-v2 behavior. Crypto and compression dependencies are wire-format sensitive; updates require fixture validation. Dev dependencies indicate tests include both unit-level async reader round-trips and ignored MinIO-generated fixture checks.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/src/compress_reader.rs -->
# sources/object-store/rustfs/crates/rio-v2/src/compress_reader.rs

Purpose: this file implements rio-v2 async S2-compatible compression and decompression readers. It is designed to emit MinIO/S2 framed streams using `minlz`, maintain a seek index for large streams, and support encrypted-object padding alignment.

Important APIs and types: `CompressReader<R>` wraps an `AsyncRead`, buffers up to a block size (default 1 MiB), writes the `S2sTwO` stream identifier once, emits compressed or uncompressed framed chunks with CRC, updates a `rustfs_rio::Index`, and exposes the index through `TryGetIndex` only after more than 8 MiB uncompressed data. `with_encrypted_padding` appends a random padding frame to align the compressed output to 256-byte boundaries. `DecompressReader<R>` parses S2 chunk headers incrementally, accepts `S2sTwO` and `sNaPpY` identifiers, decodes compressed/uncompressed chunks, verifies CRC, skips index/padding/skippable chunks, and returns plaintext bytes across async poll boundaries.

Control flow: both readers first drain any buffered output, then resume their current read state. Compression accumulates a full block unless EOF occurs, chooses compressed form only if it saves enough space, writes a 24-bit chunk length and 4-byte checksum, then copies as much as the caller's `ReadBuf` can accept. Decompression persists header/body read progress, handles short reads and `Poll::Pending`, validates chunk type, and keeps decoded output in a buffer until consumed.

State and persistence: state is entirely in-reader memory: output buffers, read buffers, written byte counters, uncompressed counters, stream-header flag, optional padding multiple, and `Index`. The emitted byte stream is persistent object data, so chunk framing and CRC behavior are compatibility-critical.

Dependencies and integration points: uses `minlz::{Encoder, decode, crc}`, `tokio::io::AsyncRead`, `pin_project_lite`, `rustfs_utils::CompressionAlgorithm` for API shape, and rio traits for ETag/hash/index delegation. It integrates with rio-v2 encryption because encrypted-padding alignment affects encrypted object layout.

Risks and test signals: risks include 24-bit length overflows, accepting malformed skippable frames too broadly, random padding nondeterminism, and index offset accuracy around the stream header. Unit tests cover minlz decode compatibility, small/large/random round-trips, erasure-boundary sizes, pending sources, first-read output, resumed chunk bodies, concatenated streams, encrypted padding, and small-stream index suppression.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/src/compress_reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/src/encrypt_reader.rs -->
# sources/object-store/rustfs/crates/rio-v2/src/encrypt_reader.rs

Purpose: this file implements async DARE v2 AES-256-GCM encryption and decryption readers compatible with MinIO encrypted object streams, including singlepart, multipart, object-key-derived part keys, and legacy nonce-derived multipart modes.

Important APIs and types: `EncryptReader<R>` provides constructors for direct key/nonce, random nonce from object key, explicit sequence start, multipart nonce derivation, and multipart object-key derivation. It emits 16-byte DARE headers plus ciphertext/tag packages over 64 KiB plaintext payloads. `DecryptReader<R>` mirrors those modes, tracks expected nonce/reference nonce, package sequence, multipart part list, current part index, and key source. `derive_part_key(object_key, part_number)` uses HMAC-SHA256 over the little-endian part number. Both readers implement rio traits for ETag/hash/index forwarding.

Control flow: encryption buffers up to `DARE_PAYLOAD_SIZE + 1` to distinguish full non-final packages from the final package. `build_dare_package` writes version, cipher suite, payload length minus one, nonce with final flag in byte 4, derives the per-package nonce by XORing sequence into the last four nonce bytes, and authenticates header bytes 0..4 as AAD. Decryption incrementally reads headers and ciphertext, checks version/cipher, validates nonce against configured and reference nonce with final flag handling, decrypts with the sequence-derived nonce, then advances multipart state after a finalized package.

State and persistence: reader state includes AES-GCM cipher, nonce, sequence number, buffers, finalization flags, and multipart state. The persistent wire state is the DARE package stream; header bits, nonce masking, and sequence resets define compatibility with stored encrypted object parts.

Dependencies and integration points: uses `aes-gcm`, `hmac`, `sha2`, `rand`, `tokio`, and legacy `rustfs_rio::multipart_part_nonce`. It composes with compression readers and exposes underlying indexes for compressed encrypted reads. Object-key multipart mode is validated against MinIO-style part key vectors.

Risks and test signals: security risks center on nonce uniqueness, final-flag masking, sequence wrap, and accepting only correctly authenticated package streams. Zero-length input produces no package, which callers must expect. Multipart decryption relies on correct part ordering and sizes supplied out of band. Tests cover non-zero sequence starts, object-key singlepart round-trip, exact MinIO part-key vectors, multipart object-key sequence reset, and lib-level DARE package boundary/header assertions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/src/encrypt_reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/src/lib.rs -->
# sources/object-store/rustfs/crates/rio-v2/src/lib.rs

Purpose: this crate root presents rio-v2 as a compatibility facade. It exports new compression, decompression, encryption, decryption, part-key derivation, and MinIO S2 index helpers while re-exporting the legacy `rustfs-rio` reader traits and wrappers needed by downstream code.

Important APIs: public exports include `CompressReader`, `DecompressReader`, `EncryptReader`, `DecryptReader`, `derive_part_key`, `decode_minio_index_bytes`, and `minio_index_storage_bytes`. Re-exports from `rustfs_rio` include `DynReader`, `Reader`, `ReadStream`, `HashReader`, `EtagReader`, `LimitReader`, `HardLimitReader`, `WarpReader`, `TryGetIndex`, `Index`, `ReaderCapabilities`, checksum helpers, and wrapper constructors.

Control flow and integration: this file has little runtime logic; its main role is API composition. Downstream callers can opt into rio-v2 wire behavior without losing legacy API names. The module tree is private except for selected exports, so implementation details stay encapsulated.

State and persistence: no state is held here. Persistent behavior is delegated to the exported readers and index helpers, and API stability is the main concern.

Risks and test signals: facade crates can accidentally expose inconsistent behavior if legacy and v2 readers make different assumptions about indexes or compression algorithms. The embedded async test verifies `EncryptReader` emits DARE v2 package headers, preserves the configured nonce in the first header, starts subsequent headers at 64 KiB package boundaries, and sets the final flag on the final package.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/src/s2_index.rs -->
# sources/object-store/rustfs/crates/rio-v2/src/s2_index.rs

Purpose: this file converts between legacy `rustfs_rio::Index` values and MinIO/S2 index storage bytes. It supports both full S2 skippable index frames and MinIO's stored headerless form.

Important APIs and types: `minio_index_storage_bytes(index)` converts an `Index` to an internal `S2Index`, encodes a full index frame, then strips the chunk header, `s2idx` header, trailing size, and trailer when possible. `decode_minio_index_bytes(bytes)` first tries to load a full S2 index, then restores headers around headerless bytes and loads again, returning a legacy `Index`. Private `S2Index`, `S2IndexInfo`, and `LegacyIndexJson` model the conversion boundary.

Control flow: encoding writes chunk type `0x99`, 24-bit chunk length, `s2idx\0`, signed zig-zag varints for totals/block size/entry count, optional uncompressed deltas, predicted compressed-offset deltas, trailing total size, and `\0xdi2s`. Decoding reverses this with strict validation: buffer length, chunk type, header, nonnegative uncompressed size/block size, bounded entry count, valid flag, monotonic offsets, and trailer. `restore_index_headers` reconstructs the full frame around stored bytes.

State and persistence: there is no mutable global state. The persistent artifact is the serialized index stored with compressed object data. `MAX_INDEX_ENTRIES` limits memory growth and malformed input exposure.

Dependencies and integration points: depends on `bytes::Bytes`, `serde_json`, and `rustfs_rio::Index`. It bridges rio-v2 S2 compression with legacy index search APIs and MinIO object metadata/storage expectations.

Risks and test signals: `legacy_index_to_s2_index` depends on `Index::to_json()` field names, creating a fragile JSON-mediated conversion inside Rust code. Encoding allows `total_compressed = -1` but rejects negative uncompressed sizes. Header stripping/restoring must stay byte-for-byte compatible with MinIO fixture expectations. Tests cover Go-compatible signed varint examples, headerless round-trip, and unknown compressed total decoding.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/src/s2_index.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/tests/minio_fixture_lab/lab.py -->
# sources/object-store/rustfs/crates/rio-v2/tests/minio_fixture_lab/lab.py

Purpose: this Python CLI captures real MinIO backend fixtures for rio-v2 compatibility validation. It can initialize a fixture layout, add an externally prepared case, or run a disposable local MinIO matrix covering SSE-S3, SSE-KMS, and SSE-C in singlepart and multipart shapes.

Important APIs and control flow: data classes define `LabPaths`, `MinioLauncher`, `FixtureCase`, and KMS config. `discover_minio_launcher` chooses an explicit binary, `minio.exe` under a root, a bundled default binary, or `minio` from `PATH`. `build_default_cases` creates six stable case IDs. `build_request_record` builds encryption headers, including KMS context base64 and SSE-C key/MD5. `S3Client` implements enough SigV4 signing and S3 requests for bucket creation, object upload, multipart upload, completion, and `HEAD`. `capture_case` creates deterministic plaintext, starts MinIO with temporary disks and optional local TLS certs, waits for health/S3 readiness, uploads the case, captures HEAD metadata, stores backend files plus JSON manifests, and cleans workdirs unless requested.

State and persistence: fixture artifacts are persisted under `artifacts/minio-fixture-lab` by default, with `layout.json`, per-case `manifest.json`, optional `request.json`, `head.json`, `plaintext.sha256`, and copied backend disk files. Temporary runtime state lives under `_runner` and is deleted by default.

Dependencies and integration points: uses standard-library subprocess, urllib, XML, OpenSSL CLI for local TLS certs, a MinIO binary, and MinIO KMS secret-key env configuration. Generated fixtures are consumed by `minio_generated_fixtures.rs` and by developers validating DARE/S2 metadata behavior.

Risks and test signals: defaults point to a platform-specific MinIO binary path and fixed admin credentials; captures are local-only but still run a server process. The custom SigV4 implementation must match S3 canonicalization for these request shapes. KMS secret configuration must be stable for reproducible sealed metadata. Unit tests in `test_lab.py` cover launcher selection, case matrix, request headers, multipart XML, and KMS env parsing, but not live MinIO capture.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/tests/minio_fixture_lab/lab.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/tests/minio_fixture_lab/test_lab.py -->
# sources/object-store/rustfs/crates/rio-v2/tests/minio_fixture_lab/test_lab.py

Purpose: this unittest suite validates deterministic, server-independent behavior of the MinIO fixture lab CLI. It intentionally avoids launching MinIO and instead tests selection, request construction, XML generation, and KMS configuration helpers.

Important tests and control flow: `load_lab_module` imports sibling `lab.py` dynamically so tests can run without package installation. `DiscoverMinioLauncherTests` verifies explicit binary preference, bundled default use via monkeypatched `DEFAULT_MINIO_BINARY`, rejection of a source checkout without a binary when `PATH` lookup is mocked missing, and `minio.exe` discovery under `--minio-root`. `FixtureMatrixTests` asserts the default matrix has six cases and covers SSE-S3/SSE-KMS/SSE-C across singlepart 64 KiB and multipart 8 MiB shapes, plus configured KMS key IDs. `RequestRecordTests` checks KMS context base64 formatting, SSE-S3 AES256 headers, and SSE-C customer key headers. `MultipartManifestTests` checks completion XML. `KmsSecretKeyTests` checks key-id parsing, rejection of missing separators, and env payload generation.

State and persistence: tests create temporary directories and monkeypatch module globals, restoring the bundled binary setting in `finally` blocks. No repo artifacts or fixture cases are written.

Dependencies and integration points: depends only on Python standard library. It gives fast feedback for the lab script that produces artifacts consumed by Rust ignored fixture tests.

Risks and test signals: the suite does not validate live MinIO startup, SigV4 request signing against a real server, backend artifact copying under real object layouts, TLS certificate generation, or cleanup behavior. It is strongest at preventing accidental changes to fixture IDs, header shapes, and launcher precedence, which are the stable contracts used by downstream fixture consumers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/tests/minio_fixture_lab/test_lab.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/tests/minio_generated_fixtures.rs -->
# sources/object-store/rustfs/crates/rio-v2/tests/minio_generated_fixtures.rs

Purpose: this Rust integration test file validates that locally generated MinIO backend fixtures can be decoded by RustFS file metadata code and that encryption-related object metadata matches expected SSE modes and upload shapes.

Important APIs and control flow: helper structs deserialize `request.json`, `head.json`, and `manifest.json`. `fixture_root()` uses `RUSTFS_MINIO_FIXTURE_ROOT` or defaults to `tests/fixtures/minio-generated`. `find_object_xl_meta` walks copied backend disks to locate object `xl.meta` while ignoring `.minio.sys`. `load_file_info` reads that metadata and calls `rustfs_filemeta::get_file_info` with `include_free_versions=true`. Test helpers derive metadata maps and expected fixture KMS key IDs from request headers or manifest capture data.

Test coverage: six ignored tests correspond to the lab matrix. Singlepart SSE-S3, SSE-KMS, and SSE-C tests verify request/head metadata, one part, actual sizes, content type, sealed-key metadata, KMS key/context metadata, or SSE-C customer-key metadata. Multipart SSE-S3/KMS/C tests verify two parts totaling 8 MiB, encrypted multipart marker, actual-size metadata, KMS context/key behavior, and SSE-C absence of KMS key IDs.

State and persistence: tests are `#[ignore]` because they require generated fixture directories outside normal unit-test state. They read fixture artifacts but do not mutate them.

Dependencies and integration points: depends on `rustfs-filemeta`, `serde_json`, `walkdir`, and the Python lab output format. It bridges object-store compatibility work to real MinIO backend metadata rather than synthetic byte streams.

Risks and test signals: ignored tests are easy to skip in CI unless a dedicated fixture job enables them. Fixture root discovery and panic-heavy helpers favor developer clarity over graceful failures. Assertions focus on metadata decoding, not full encrypted payload decryption. Still, this is a high-value compatibility signal because it checks real `xl.meta` produced by MinIO across encryption modes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio-v2/tests/minio_generated_fixtures.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/Cargo.toml -->
# sources/object-store/rustfs/crates/rio/Cargo.toml

Purpose: this manifest defines the legacy `rustfs-rio` crate, the broader asynchronous I/O framework reused by RustFS and re-exported by rio-v2. It contains the shared reader abstractions, compression/index/checksum/encryption support, and HTTP/S3-adjacent dependencies.

Important dependencies: `tokio` with full features, `futures`, `tokio-util`, `reqwest`, `http`, `s3s`, TLS/runtime crates, metrics, config constants, tracing, `thiserror`, crypto/hash crates (`aes-gcm`, `sha1`, `sha2`, `md-5`, `base64`, `hex-simd`, `faster-hex`), CRC support, and `rustfs-utils` with `io`, `hash`, and `compress` features. Dev dependencies include `tokio-test`, `axum`, and `http-body-util`, suggesting async reader and HTTP integration tests.

State and integration: no runtime state exists in the manifest, but it defines the dependency graph that rio-v2 relies on for traits like `TryGetIndex`, `Index`, and reader wrappers. Feature choices here affect downstream crates that import `rustfs_rio` directly or through rio-v2 re-exports.

Risks and test signals: the crate has a wide dependency surface spanning crypto, compression, HTTP, TLS, and metrics. Workspace-version updates can affect behavior in multiple layers. The manifest itself has no tests; validation comes from compiling downstream crates and running module-level tests such as checksum, compression index, and compression reader tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/checksum.rs -->
# sources/object-store/rustfs/crates/rio/src/checksum.rs

Purpose: this file implements S3-compatible checksum type parsing, checksum value validation, serialization/deserialization for object metadata, and CRC combination for multipart/full-object checksums.

Important APIs and types: `ChecksumType` is a bitflag wrapper with base algorithms SHA256, SHA1, CRC32, CRC32C, CRC64NVME plus flags for trailing, multipart, includes-multipart, full-object, invalid, and none. It maps algorithms to S3 header keys, raw byte lengths, merge eligibility, object checksum type strings, header parsing, and hasher construction. `Checksum` stores type, base64 encoded value, raw bytes, and expected part count. It can be created from data or strings, validated, matched against content, serialized to maps or bytes, and combined with `add_part`.

Control flow: `get_content_checksum` first handles `x-amz-trailer`, then direct checksum headers or `x-amz-checksum-algorithm`, rejecting duplicates and invalid full-object combinations. Serialization writes checksum type as varint, raw checksum bytes, optional part count, and optional per-part raw checksums. `read_checksums` and `read_part_checksums` parse that format back into header maps. CRC combination uses GF(2) matrix operations for CRC32, CRC32C, and CRC64NVME.

State and persistence: no global state. Persistent state is the encoded checksum metadata stored on objects and reconstructed into response headers. Byte order matters: raw CRCs are stored big-endian for exported/base64 form.

Dependencies and integration points: integrates HTTP headers, `base64`, `sha1`, `sha2`, `crc-fast`, and `crate::errors::ChecksumMismatch`. It is used by upload validation, metadata persistence, and response header generation.

Risks and test signals: parsing must match AWS S3 behavior around duplicate checksum headers, trailing checksums, and full-object restrictions. Multipart serialization silently returns partial buffers if raw length is invalid, which callers must handle. CRC combination is mathematically sensitive to polynomial reflection and length handling. Tests cover CRC64NVME and CRC32C multipart combination against full-object checksums; broader header parsing cases should also be guarded.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/checksum.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/compress_index.rs -->
# sources/object-store/rustfs/crates/rio/src/compress_index.rs

Purpose: this file defines the legacy compression `Index` and `TryGetIndex` trait used for seeking into compressed object streams. It can serialize/deserialize S2-style index frames and provide nearest compressed/uncompressed offsets for reads.

Important APIs and types: `TryGetIndex` defaults to no index. `Index` stores total uncompressed/compressed sizes, `IndexInfo` offset pairs, and estimated block size. `add` records monotonic offsets with a minimum uncompressed spacing of 1 MiB, updating an existing entry when the uncompressed offset is identical. `find` resolves positive or negative uncompressed offsets to the closest preceding index entry. `append_to`/`into_vec` write the skippable index frame; `load` and `load_stream` read it. `to_json` exposes a legacy JSON representation used by rio-v2 index conversion.

Control flow: serialization may call `reduce` to cap entries at `MAX_INDEX_ENTRIES`, writes marker bytes, `s2idx\0`, varint totals, estimated block size, entry count, optional uncompressed deltas, predicted compressed deltas, trailing size, and trailer. Deserialization validates marker, chunk length, optional legacy zero padding, header/trailer, sizes, entry count, flag, monotonic offsets, and returns any remaining bytes after the index.

State and persistence: `Index` is plain in-memory state until serialized into compressed object metadata/trailer bytes. The serialized frame is a persistent compatibility format and has legacy padding support.

Dependencies and integration points: uses `bytes`, `serde`, standard `Read + Seek`, and is imported by compression readers and rio-v2's S2 index bridge. `Index::to_json` is an internal compatibility bridge for new code.

Risks and test signals: varint encoding here is unsigned-style over `i64` and differs from rio-v2's signed zig-zag helpers, so cross-format assumptions require care. `find` uses a nonstandard `binary_search_by` shape for large indexes that should be monitored. Tests cover construction, add/find errors, reduction, JSON output, round-trip load, invalid marker rejection, and legacy zero-padded header acceptance.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/compress_index.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/compress_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/compress_reader.rs

Purpose: this file implements the legacy async block compression and decompression readers used by `rustfs-rio`. It frames compressed blocks with a custom 8-byte header, original-length varint, and CRC32 checksum.

Important APIs and types: `CompressReader<R>` wraps an `AsyncRead`, buffers 1 MiB blocks by default, compresses each block with `rustfs_utils::compress::compress_block`, updates a legacy `Index`, and exposes it through `TryGetIndex`. `DecompressReader<R>` reads the custom block header, body, original length varint, decompresses or passes through uncompressed blocks, verifies decompressed length and CRC32, and yields plaintext across async polls.

Control flow: compression drains buffered output first, then fills `temp_buffer` until block size, EOF, or a pending inner read with partial data. It builds a compressed block via `build_compressed_block`, increments written/uncompressed counters, adds an index entry, and copies to the caller buffer. Decompression persists header-read and body-read progress, interprets type `0x00` compressed, `0x01` uncompressed, and `0xff` end, validates the decoded length from `uvarint`, and reports invalid type, decompression errors, length mismatch, or CRC mismatch as `InvalidData`.

State and persistence: per-reader state includes buffers, positions, done flags, block size, algorithm, index, and read progress. The persistent format is the custom frame sequence. The file delegates reader capabilities to the wrapped reader via `delegate_reader_capabilities_generic_no_index!`.

Dependencies and integration points: depends on `compress_index::{Index, TryGetIndex}`, `rustfs_utils` compression/uvarint helpers, `crc-fast`, `tokio::io`, and `pin_project_lite`. rio-v2 keeps these public traits but replaces the wire format for MinIO-compatible paths.

Risks and test signals: the decompressor reads `compressed_buf[0..16]` for varint without first checking the buffer has 16 bytes, so malformed tiny blocks can panic rather than return an error. Pending behavior after partial header/body reads is stateful and important. Index entries are added after incrementing totals, so offset interpretation differs from rio-v2's S2 stream-header-aware indexing. Tests cover gzip/deflate/default round-trips, empty data, and multi-megabyte random data.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/compress_reader.rs -->
