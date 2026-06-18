# subset-b-000233 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/registry.rs -->
# sources/cloud-native/nydus/storage/src/backend/registry.rs

## Purpose
`registry.rs` implements the `BlobBackend` for OCI/Docker registry-backed blobs. It turns a `RegistryConfig` into a `Registry` object, creates per-blob `RegistryReader`s, handles registry authentication challenges, reads blob byte ranges, follows registry redirects to object storage, caches redirect/auth state, and exposes metrics/retry metadata to the storage layer.

## Important APIs, Types, And Functions
`RegistryError` is the backend-specific error surface and converts into `BackendError`, preserving feature-gated Dragonfly proxy errors as request errors so retry classification can still see forbidden/rate-limit cases. `RegistryState` holds shared backend configuration and mutable caches: scheme, host, repo, retry limit, auth caches, redirect cache, bearer token expiration, and cached bearer challenge parameters. `Registry::new` validates base64 basic auth, builds `Connection` and `request::Request`, initializes `RegistryState`, registers dynamic config auth, and starts the refresh thread.

`RegistryReader` implements `BlobReader` with `blob_size`, `try_read_ctx`, and `try_stream_read`. The internal `request` method handles the standard 401 challenge flow for Basic and Bearer auth. `_try_read` handles ranged blob reads, redirect caching, redirect URL rewriting, HTTPS-to-HTTP fallback when `skip_verify` allows it, and response copying into caller buffers. `_stream_read` opens a streaming response and intentionally omits `Range` for offset zero so Dragonfly can cache the whole blob.

`Cache` and `HashCache<T>` provide lock-protected string/hash caches for auth headers, config-auth snapshots, method fallback, and redirects. `First` serializes only the initial request across concurrent readers so the first request can populate shared auth state before the startup surge of blob reads proceeds. `TokenResponse`, `BasicAuth`, `BearerAuth`, and `Auth` model registry authentication.

## Control Flow
Construction flows through `Registry::new`: config to `ConnectionConfig`, `Connection::new`, `Request::new`, auth trimming/validation, `RegistryState` allocation, and background token refresh. A reader is cheap and shares state/request/metrics. Reads call through `First::handle_force`, then either `HEAD /v2/<repo>/blobs/<digest>` for size or `GET` with a `Range` header for data. If no redirect is cached, the reader hits the registry API path, optionally authenticates via a 401 challenge, handles TLS fallback, follows 3xx `location`, optionally rewrites scheme/host, and then reads from the redirected URL. If a cached redirected URL returns 401/403, it is invalidated and the read retries once through the registry API.

Auth control flow starts with any cached `Authorization` header. On 401 with an auth header, the request is retried without the stale header to get a correct `www-authenticate` challenge. Bearer token fetching tries POST first unless GET was previously cached for that host; on POST failure it retries GET and remembers GET. Successful auth headers are cached for later registry requests.

## State And Persistence Behavior
No durable state is written by this file. Mutable process state includes `cached_auth`, dynamic-config auth snapshots, redirect URL cache keyed by blob id, cached GET-vs-POST auth method, bearer token expiry, and cached bearer challenge. The refresh thread polls config and token expiry every five seconds until `Request::shutdown` is observed. `Scheme` is an atomic HTTPS/HTTP switch, so fallback changes process-wide behavior for the registry instance. Metrics are allocated per registry id and released in `Drop`.

## Dependencies And Integration Points
This module depends on `reqwest` headers/status/methods, `url::Url`, `arc_swap`, `base64`, `serde_json`, `nydus_api::RegistryConfig`, `nydus_utils::config`, and `BackendMetrics`. It integrates with `backend::connection` for transport, `backend::request` for direct/proxy/Dragonfly routing, `BlobBackend`/`BlobReader` traits for cache consumers, and optional Dragonfly proxy error typing.

## Risks And Edge Cases
`parse_auth` is intentionally simple and splits challenge parameters on `",` and `=`, which is vulnerable to unusual quoted values containing delimiters. Redirect caching assumes redirected URLs are reusable until 401/403; other expiry/failure modes will surface as read errors rather than cache invalidation. HTTPS-to-HTTP fallback mutates shared scheme for the backend and is only gated by `skip_verify`; once set, later reads use HTTP. The refresh thread is detached and only exits after shutdown polling. `HeaderValue::to_str().unwrap()` and header parsing `unwrap()` can panic if a registry returns invalid header values in paths that are otherwise expected.

## Test Signals
The local test module covers cache helpers, fallback scheme behavior, auth config validation and dynamic updates, URL construction, auth challenge parsing, `First` concurrency/renewal behavior, token response decoding, error conversion/display, `respond` status handling, config auth helpers, fallback error classification, and stream-read unsupported behavior. The tests are mostly unit-level with mocked/simple objects; live registry redirect/auth integration is not covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/registry.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/request.rs -->
# sources/cloud-native/nydus/storage/src/backend/request.rs

## Purpose
`request.rs` is the unified request routing layer used by storage backends. It wraps `Connection`, injects common/custom headers, records diagnostic request context, and chooses between direct HTTP, HTTP proxy, and feature-gated Dragonfly SDK proxy paths. It also normalizes HTTP and Dragonfly SDK responses behind one `Response` enum.

## Important APIs, Types, And Functions
`RequestError` distinguishes generic routing errors, `ConnectionError`, and optional Dragonfly `ProxyError`. `Response` wraps `reqwest::blocking::Response` or feature-gated `GetResponse` and exposes `status`, `headers`, `reader`, `text`, and `copy_to`. `Request::new` stores the connection, proxy config, parsed custom headers, prefetch flag, and dynamic-config id while registering initial proxy settings in `nydus_utils::config`.

`Request::call` is the main API. It takes method, URL, optional query/form/body, mutable headers, status-catching preference, backend context, and a temporary proxy-disable flag. `is_success_status` treats 2xx and 3xx as success, matching backend redirect-handling needs. `parse_custom_headers_from_env` adds `User-Agent: nydusd/1.0.0` and accepts valid `NYDUS_HEADER_*` environment variables.

## Control Flow
Every call first extends caller headers with configured custom headers and populates `BackendContext.method`, `url`, and proxy booleans. If proxying is disabled by request, context, or absent proxy URL, the request goes directly to `Connection::call_with_proxy_control`; auth calls use this path to avoid proxy URL rewriting. With `backend-dragonfly-proxy`, a scheduler endpoint and GET method can route to `ProxySDKClients::request`, with Dragonfly priority derived from `RequestSource`. If SDK is unavailable or disabled, the call falls through to HTTP proxy mode and injects Dragonfly priority/use-p2p headers before using `Connection::call`.

After an HTTP proxy response, feature-gated logic inspects the Dragonfly error-type header. A 429 maps to `ProxyError::TooManyRequests`, a 403 maps to `ProxyError::Forbidden`, and other proxy-marked statuses become common errors. Without the feature, the module is a direct/proxy wrapper around `Connection`.

## State And Persistence Behavior
`Request` keeps immutable construction-time proxy config plus a config id for dynamic reads of the Dragonfly scheduler endpoint. `dragonfly_scheduler_endpoint` calls `nydus_utils::config::get_changed`, allowing scheduler hot reload without rebuilding the request. No file state is persisted. `shutdown` delegates to the shared `Connection`, and `is_shutdown` reads the connection atomic flag.

## Dependencies And Integration Points
The module depends on `reqwest` method/status/header types, `nydus_api::ProxyConfig`, `backend::connection`, `BackendContext`, optional `backend::proxy`, optional Dragonfly client types, and `nydus_utils::config`. It is used by registry, S3/object storage, and other backend implementations as the common transport abstraction.

## Risks And Edge Cases
Custom environment headers are parsed only at construction time; later environment changes do not apply. Header names/values that fail parsing are silently ignored. Header extension can overwrite caller headers with environment-provided headers, including `User-Agent`. SDK proxy mode rejects non-GET methods; callers must disable SDK or avoid proxying for writes/auth. Dynamic config uses the original configured endpoint as the comparison baseline each call, which is fine for fetching current values but means change reporting is not a stored state transition in this object.

## Test Signals
Tests cover environment header parsing, success-status boundaries, request construction, proxy-mode checks, scheduler endpoint hot reload, shutdown state, direct and proxy-disabled calls, custom header injection, feature-gated SDK response adapters, SDK method rejection, Dragonfly HTTP proxy error header translation, Dragonfly priority headers for prefetch/on-demand, HTTP response helpers, and debug formatting. Tests exercise routing behavior with local/mocked HTTP facilities rather than external network services.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/request.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/s3.rs -->
# sources/cloud-native/nydus/storage/src/backend/s3.rs

## Purpose
`s3.rs` implements an S3-compatible object storage backend by specializing generic `ObjectStorage` with `S3State`. It builds object URLs and signs requests using AWS Signature Version 4 for S3 GET-style access.

## Important APIs, Types, And Functions
`S3State` stores region, access key id/secret, scheme, object prefix, endpoint, bucket name, and retry limit. `pub type S3 = ObjectStorage<S3State>` exposes the generic object storage backend under an S3 name. `S3::new` converts `S3Config` into `ConnectionConfig`, creates the transport and `request::Request`, applies the default endpoint `s3.amazonaws.com` when config omits one, and returns a configured `ObjectStorage`.

`ObjectStorageState for S3State` supplies `url`, `sign`, and `retry_limit`. `url` builds path-style resources as `/<bucket>/<prefix><key>?query` and a full URL. `sign` inserts `Host`, `x-amz-date`, `x-amz-content-sha256`, computes canonical headers, canonical request hash, string-to-sign, signing key, and `Authorization`. Helpers `sha256_hash`, `hmac_hash`, `hmac_hash_hex`, `to_signer_date`, and `to_awz_date` implement the signing pieces.

## Control Flow
Construction captures config and delegates transport details to the common connection/request stack. For each object operation, the generic object storage code asks `S3State::url` for resource/full URL, then calls `S3State::sign` with the HTTP verb and header map. Signing uses the current UTC time, the empty payload SHA-256 constant, the URI path/query parsed from the full URL, and sorted lower-case headers excluding `authorization` and `user-agent`. The signature is inserted into headers before the request is issued through `request::Request`.

## State And Persistence Behavior
The backend has no mutable token or persisted state. Credentials and endpoint configuration are held in memory for the lifetime of `S3State`. The only time-varying value is the signing timestamp generated per request. Metrics are created by the generic object storage layer when an id is provided.

## Dependencies And Integration Points
This module depends on `nydus_api::S3Config`, `BackendMetrics`, `backend::object_storage::{ObjectStorage, ObjectStorageState}`, `backend::connection`, `backend::request`, `reqwest::Method`, `http::Uri`, `hmac`, `sha2`, `hex`, and `time`. It integrates with all generic object-storage read behavior through the `ObjectStorageState` trait.

## Risks And Edge Cases
The URL builder uses path-style S3 addressing and directly concatenates `object_prefix` and object key; callers must ensure any needed delimiter or escaping is already correct. Canonical header values use `to_str().unwrap()`, so non-UTF8 header values can panic. Payload signing is fixed to the empty body hash, which is appropriate for GET/HEAD style reads but would need revisiting for body-bearing S3 operations. The canonicalization is focused on current backend needs and may not cover every S3-compatible service quirk.

## Test Signals
Tests cover backend construction, URL/resource formatting with query strings, and signature shape. The signature test verifies required signed header names and a 64-hex-character signature but does not compare against a fixed AWS test vector because the timestamp is live.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/s3.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/url_encoding.rs -->
# sources/cloud-native/nydus/storage/src/backend/url_encoding.rs

## Purpose
`url_encoding.rs` provides a compact percent-encoding helper for backend URL components. It is ported from `rust_urlencoding` and kept compatible with older Rust versions. The encoder leaves only ASCII alphanumerics and `-`, `_`, `.`, `~` unescaped.

## Important APIs, Types, And Functions
`Encoded<Str>` is a transparent wrapper implementing `Display` for on-the-fly encoding without requiring an allocation. It offers `new`, `to_str`, `to_string`, `write`, and `append_to`; `Encoded::str` helps type inference for `&str`. Free functions `encode(&str)` and `encode_binary(&[u8])` return `Cow<str>`, borrowing when the input is already safe ASCII and allocating only when escaping is needed. `append_string`, `encode_into`, and `to_hex_digit` are internal helpers.

## Control Flow
`encode_binary` creates an output buffer and calls `append_string` with `may_skip=true`. `encode_into` scans leading safe bytes, writes them as unchecked UTF-8 only after confirming they are safe ASCII, then percent-encodes one unsafe byte at a time using uppercase hex digits. If the entire input is safe and skipping is allowed, it returns `Ok(true)` so `encode_binary` can return `Cow::Borrowed`.

## State And Persistence Behavior
The module is stateless. It allocates only for encoded output or writer/string append targets and has no shared state, IO state, or persistence.

## Dependencies And Integration Points
It depends only on standard library `Cow`, formatting, IO, and UTF-8 primitives. Backend modules can use it for object keys, query parameters, or path fragments where RFC3986-style percent encoding is required.

## Risks And Edge Cases
The encoder operates on bytes and assumes UTF-8 only when returning borrowed safe ASCII or writing safe fragments; non-UTF8 bytes are always escaped. It does not implement form encoding: spaces become `%20`, not `+`. It encodes `/`, `:`, `@`, and other reserved characters, so callers must choose correctly between encoding a path segment and a whole URL/path. The generic `impl<String: AsRef<[u8]>> Display` shadows the common `String` name as a type parameter, which is legal but slightly confusing.

## Test Signals
Tests cover borrowed output for safe ASCII, reserved character escaping, non-UTF8 byte encoding, consistency between helper methods and `Display`, and append/write behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/url_encoding.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/cachedfile.rs -->
# sources/cloud-native/nydus/storage/src/cache/cachedfile.rs

## Purpose
`cachedfile.rs` implements the common local file-backed blob cache object used by userspace file cache and fscache-based cache managers. `FileCacheEntry` reads blob chunks from local cache files when possible, fetches/decompresses/decrypts/validates backend data on misses, persists ready chunks, manages prefetch, supports optional at-rest cache encryption, and integrates optional content-addressable deduplication.

## Important APIs, Types, And Functions
`FileCacheMeta` owns asynchronous or synchronous loading of `BlobCompressionContextInfo` with retry/backoff and a shared error flag. `BlobCCI` wraps blob compression context access, especially for batch chunks where compressed size comes from blob metadata rather than the chunk object. `FileCacheEntry` is the central cache object and implements `AsRawFd`, `BlobCache`, and `BlobObject`.

Key persistence helpers are `persist_cached_data`, `persist_chunk_data`, `delay_persist_chunk_data`, `cache_chunk_data`, and `_update_chunk_pending_status`. Range/read helpers include `extend_pending_chunks`, `strip_ready_chunks`, `get_blob_range`, `prefetch_range`, `do_fetch_chunks`, `read`, `read_iter`, `dispatch_one_range`, `dispatch_cache_fast`, `dispatch_cache_slow`, `dispatch_backend`, `read_single_chunk`, and `read_file_cache`. `DataBuffer`, `Region`, and `FileIoMergeState` support buffer ownership and IO-region coalescing.

## Control Flow
Reads enter `BlobCache::read`. Single-entry requests dispatch directly; multi-entry requests are merged with `BlobIoMergeState` and processed range by range. `dispatch_one_range` checks and marks chunk readiness/pending state. Ready plaintext chunks without validation use `CacheFast` and read directly from the cache file into caller buffers. Chunks needing validation/decryption/decompression or non-direct maps use `CacheSlow`, which loads and validates a whole chunk before copying the requested segment. Missing chunks use `Backend`, where contiguous compressed ranges can be extended for read amplification, fetched through `BlobCache::read_chunks_from_backend`, decompressed by the trait helper, copied to user buffers, and persisted asynchronously.

Prefetch paths sort and merge requested IO ranges, mark chunks pending, fetch backend ranges, persist raw compressed ranges or per-chunk uncompressed data, and update chunk-map readiness. `BlobObject` methods allow fetching compressed/uncompressed ranges and checking all-data-ready for direct object use. Dedup, when enabled, is attempted before backend fetch in `dispatch_one_range`; successful copy from CAS marks the chunk ready.

## State And Persistence Behavior
`FileCacheEntry` persists cached bytes into `file` at compressed offsets for raw-data caches or uncompressed offsets for decoded caches. Cache-at-rest encryption pads writes to 4096-byte pages and derives cipher metadata from chunk digest bytes. Readiness/pending state is kept in `chunk_map`, which may be persistent depending on the map implementation. Metrics track total reads, hits, buffered backend bytes, prefetch merge counts, and entry count increments when chunks become ready. `prefetch_state` is an atomic activity counter; `workers` receives async prefetch tasks. With feature `dedup`, `Drop` triggers CAS garbage collection.

## Dependencies And Integration Points
The file is tightly integrated with `BlobCache` trait helpers in `cache/mod.rs` for backend reads, decompression, and validation. It depends on `BlobReader`, `ChunkMap`, async worker types, `CasMgr`, blob device metadata (`BlobInfo`, `BlobChunkInfo`, `BlobIo*`), compression metadata, crypto utilities, metrics, `nix::sys::uio::pwrite`, `FileRangeReader`, Tokio runtime, and fscache/file-cache managers that construct entries.

## Risks And Edge Cases
Correctness depends on pending bits always being cleared or promoted; the code has explicit cleanup paths, but any missed error path can stall a chunk until timeout. Asynchronous persistence means user data may be returned before cache writes finish; failed writes clear pending and leave future reads to retry. Direct IO requires capacity/page alignment and padding, and encrypted cache writes can persist padded bytes beyond logical chunk size. ZRan and batch chunks need metadata; missing async metadata returns errors after polling. Region merging relies on chunk ordering and continuity assertions. `DataBuffer::from_mut_slice` uses unsafe ownership tricks and must only be used where the underlying slice lifetime is controlled.

## Test Signals
Tests cover buffer ownership conversion, region type joinability, region append/continuity behavior, file IO merge splitting, batch metadata lookup through `BlobCCI`, entries-count metric increments, and `FileCacheMeta` immediate/wait/error/clone behavior. The largest runtime paths (`dispatch_backend`, async persistence, encryption, direct IO, dedup integration, and real backend failures) are mostly covered indirectly elsewhere or require integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/cachedfile.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/dedup/db.rs -->
# sources/cloud-native/nydus/storage/src/cache/dedup/db.rs

## Purpose
`dedup/db.rs` implements the SQLite persistence layer for local content-addressable deduplication. It records cache blob file paths and maps chunk digest keys to file offsets so later cache entries can reuse already-downloaded chunks.

## Important APIs, Types, And Functions
`CasDb` owns an `r2d2` pool of `rusqlite` connections. `new` appends `cas.db` to a directory; `from_file` opens/creates the database, enables WAL journal mode, creates `Blobs` and `Chunks` tables, and creates an index on `Chunks(ChunkId)`. Blob APIs include `get_blob_id_with_tx`, `get_blob_id`, `get_blob_path`, `get_all_blobs`, `add_blobs`, `add_blob`, and `delete_blobs`. Chunk APIs include `get_chunk_info`, `add_chunks`, and `add_chunk`. `begin_transaction` creates immediate transactions with rollback-on-drop, and `get_connection` installs a busy handler.

## Control Flow
Initialization opens a read-write/create SQLite database and ensures schema availability. Adding chunks first resolves the blob path to `BlobId`, then inserts `(ChunkId, ChunkOffset, BlobId)` with conflict-ignore semantics. Querying a chunk joins `Chunks` to `Blobs`, orders by `BlobId`, and returns the first matching file path and offset. Deleting blobs removes chunk rows first, then blob rows, inside one immediate transaction.

## State And Persistence Behavior
Persistent state is held in `cas.db`. `Blobs` maps integer ids to unique file paths. `Chunks` stores many chunk keys per blob with uniqueness on `(ChunkId, BlobId)`, allowing the same chunk key to exist in multiple files. WAL mode improves concurrent read/write behavior. Transactions are used for batch blob/chunk mutations and rollback automatically if dropped before commit.

## Dependencies And Integration Points
The module depends on `r2d2`, `r2d2_sqlite`, `rusqlite`, and the parent dedup module’s `Result<CasError>`. `CasMgr` uses it to record cache chunks, look up dedup sources, and remove stale blob records during garbage collection.

## Risks And Edge Cases
`add_blob` returns `last_insert_rowid`, which is meaningful for newly inserted rows but can be misleading after `INSERT OR IGNORE` for an already-existing blob; current callers do not rely on the returned id for existing rows. In `add_chunks`/`add_chunk`, missing blob ids become SQL `NULL` values through `Option<u64>` binding, which may create chunk records with no valid blob association unless SQLite constraints reject the row; callers normally add the blob first. The busy handler always returns true, so lock waits can be unbounded. Foreign keys are declared but SQLite foreign-key enforcement is not explicitly enabled.

## Test Signals
Tests cover blob insertion/query/deletion, reopening the same database, listing blobs, adding chunks, first-match lookup across duplicate chunk keys, and deletion cascading behavior implemented manually by deleting chunks before blobs.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/dedup/db.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/dedup/mod.rs -->
# sources/cloud-native/nydus/storage/src/cache/dedup/mod.rs

## Purpose
`dedup/mod.rs` implements the in-process content-addressable storage manager used by file cache entries when the `dedup` feature is enabled. It converts blob/chunk metadata into stable chunk keys, records ready chunks in `CasDb`, copies matching chunks from existing cache files into new cache files, maintains an open-file cache, and garbage-collects stale database records.

## Important APIs, Types, And Functions
`CasError` wraps IO, rusqlite, and r2d2 errors. `CasMgr` owns a `CasDb` and an `RwLock<HashMap<String, Arc<File>>>` of open source files. A global `CAS_MGR` singleton can be installed and retrieved with `set_singleton` and `get_singleton`. `dedup_chunk` is the reuse path: compute chunk key, look up `(path, offset)`, open/cache the source file, copy bytes with `copy_file_range`, and report success/failure. `record_chunk` canonicalizes a cache file path and records a chunk key/path/offset through `record_chunk_raw`. `chunk_key` combines the blob digest algorithm name with the chunk digest, skipping default/empty digests. `gc` removes database and fd-cache entries for source files that no longer exist.

## Control Flow
When a cache miss is about to fetch from backend, `FileCacheEntry` may call `CasMgr::dedup_chunk`. If a matching chunk key exists, the manager finds a source blob file, opens it on demand or reuses an `Arc<File>`, validates that cached file metadata still exists, and copies `chunk.uncompressed_size()` bytes from the recorded offset to the destination chunk’s uncompressed offset. After successful cache persistence, `FileCacheEntry` calls `record_chunk`, which writes the blob path and chunk key mapping to SQLite. On drop of a dedup-enabled `FileCacheEntry`, `gc` scans all database blob paths and removes missing ones.

## State And Persistence Behavior
Persistent dedup metadata is in the SQLite database managed by `CasDb`; process-local state is the singleton and open source-file cache. Paths are canonicalized before recording in normal `record_chunk`, but `record_chunk_raw` accepts caller-provided paths for tests or lower-level use. Stale paths are cleaned lazily when `dedup_chunk` notices missing metadata or during `gc`.

## Dependencies And Integration Points
The module depends on `CasDb`, `BlobInfo`, `BlobChunkInfo`, `RafsDigest`, `copy_file_range`, and standard file/open/path synchronization primitives. It integrates with `cachedfile.rs` behind the `dedup` feature for pre-backend copy reuse and post-persist recording.

## Risks And Edge Cases
Dedup silently returns false on most lookup/open/copy failures so the caller can fall back to backend reads. This is operationally resilient but can hide persistent CAS issues unless logs are monitored. The global singleton is simple and process-wide; replacing it while readers exist could change behavior across mounts. `chunk_key` ignores default digests, so chunks without real digests are never deduplicated. `dedup_chunk` treats `metadata().is_err()` on a cached open file as stale and deletes DB rows for that path. `record_chunk` requires path canonicalization, so recording fails if the cache file path is not yet visible.

## Test Signals
Tests cover error formatting/conversions, manager creation and singleton access, empty and valid chunk-key generation, raw recording, successful copy-based dedup, failure for empty digest and nonexistent source, record no-op for empty key, garbage collection for missing files, and preserving records for existing files.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/cache/dedup/mod.rs -->
