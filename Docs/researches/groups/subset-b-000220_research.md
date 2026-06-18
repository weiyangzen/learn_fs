# subset-b-000220 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/api/src/http_endpoint_v1.rs -->
# sources/cloud-native/nydus/api/src/http_endpoint_v1.rs

Purpose: implements Nydus HTTP API v1 endpoint handlers below `HTTP_ROOT_V1 = "/api/v1"`. It translates `dbs_uhttp::Request` objects into typed `ApiRequest` messages and translates `ApiResponse` values back into JSON HTTP responses.

Important APIs/types/functions: `InfoHandler`, `FsBackendInfo`, `MetricsFsGlobalHandler`, `MetricsFsAccessPatternHandler`, `MetricsFsFilesHandler`, `MetricsFsInflightHandler`, and `ConfigHandler` all implement `EndpointHandler`. The private `convert_to_response` accepts only v1-compatible payloads: `Empty`, daemon info, filesystem metrics, backend info, inflight metrics, access patterns, and config maps.

Control flow: every handler pattern matches `(req.method(), req.body.as_ref())`, validates required query parameters or JSON body, calls the provided `kicker` closure with a concrete `ApiRequest`, then wraps the result through `convert_to_response`. `GET /daemon/backend` requires `mountpoint`; metrics endpoints optionally read `id`; file metrics also parses `latest` as bool with invalid values falling back to false. `PUT /config` parses `Config` and optionally accepts `id`.

State and persistence: the file is stateless. It only reads HTTP body/query values and forwards operations to the API server; durable state changes happen behind `ApiRequest::ConfigureDaemon` and `ApiRequest::UpdateConfig`.

Dependencies and integration points: depends on `dbs_uhttp`, common HTTP helpers in `http_handler`, and API enums/errors in `crate::http`. It is registered from `HTTP_ROUTES` in `http_handler.rs`.

Risks: unexpected `ApiResponsePayload` variants panic, so API service/handler response contracts must stay synchronized. Query extraction is string-based and boolean parse failures are silently treated as false. `Config` responses stringify a map manually before returning a body.

Test signals: unit tests cover happy and bad-method paths, required `mountpoint`, config get/put, metrics query options, and API errors returning HTTP error responses without failing the micro-http processing layer.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/api/src/http_endpoint_v1.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/api/src/http_endpoint_v2.rs -->
# sources/cloud-native/nydus/api/src/http_endpoint_v2.rs

Purpose: implements Nydus HTTP API v2 endpoint handlers below `HTTP_ROOT_V2 = "/api/v2"`, mainly daemon information/configuration and blob cache object lifecycle operations.

Important APIs/types/functions: `InfoV2Handler` maps daemon GET/PUT to `ApiRequest::GetDaemonInfoV2` and `ConfigureDaemon`. `BlobObjectListHandlerV2` supports `GET`, `PUT`, and `DELETE` for `/api/v2/blobs`. It constructs `BlobCacheObjectId { domain_id, blob_id }` from query strings and parses `Box<BlobCacheEntry>` from request bodies. The private `convert_to_response` accepts `Empty`, `DaemonInfo`, and `BlobObjectList` payloads.

Control flow: v2 handlers use the same `EndpointHandler` contract as v1. Blob GET requires `domain_id` and treats missing `blob_id` as an empty string, allowing domain-wide queries. Blob PUT parses a `BlobCacheEntry`, calls `prepare_configuration_info()`, rejects invalid entries as `BadRequest`, and sends `CreateBlobObject`. DELETE prefers `domain_id` deletion/object deletion when present; otherwise it accepts `blob_id` alone for `DeleteBlobFile`.

State and persistence: the handler owns no persistent state. It validates and dispatches blob cache object operations to the API backend, where actual cache state is created or removed.

Dependencies and integration points: depends on `BlobCacheEntry` from the crate root, `ApiRequest`/`BlobCacheObjectId`, and shared HTTP helper functions. Registered by `HTTP_ROUTES` as `/api/v2/daemon` and `/api/v2/blobs`.

Risks: unexpected response payloads panic. DELETE semantics are parameter-sensitive: `domain_id` wins over `blob_id`-only deletion, so clients must choose query strings carefully. PUT rejects configs only after JSON parse succeeds and `prepare_configuration_info()` runs.

Test signals: unit tests cover daemon GET/PUT/bad method, blob GET required domain, invalid PUT config, both delete forms, unsupported POST, and API error conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/api/src/http_endpoint_v2.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/api/src/http_handler.rs -->
# sources/cloud-native/nydus/api/src/http_handler.rs

Purpose: provides the Unix-domain HTTP server, route table, common request parsing/response helpers, and channel bridge between HTTP endpoint handlers and the Nydus API service.

Important APIs/types/functions: `HttpResult`, `EndpointHandler`, `HttpRoutes`, `HTTP_ROUTES`, `extract_query_part`, `parse_body`, `translate_status_code`, `success_response`, `error_response`, and `start_http_thread`. `HTTP_ROUTES` is a lazy static map from exact URI paths to boxed endpoint handlers across common, v1, and v2 APIs.

Control flow: `start_http_thread` removes any existing socket path, builds a `dbs_uhttp::HttpServer`, registers the server epoll fd and an exit `Waker` with `mio::Poll`, then spawns `nydus-http-server`. The loop polls for `REQUEST_TOKEN`, drains `server.requests()`, invokes `handle_http_request`, and responds; `EXIT_TOKEN` sends `None` on the API channel and exits. `handle_http_request` parses the absolute path with `http::Uri`, finds the route, calls `EndpointHandler::handle_request`, and converts handler errors to bad requests or missing routes to not found. Successful and error responses are marked with server name and JSON content type.

State and persistence: runtime state is in the route map and mpsc channels. The only filesystem mutation is removing/recreating the Unix socket path. API requests are synchronized through `Sender<Option<ApiRequest>>` and `Receiver<ApiResponse>`.

Dependencies and integration points: integrates `dbs_uhttp`, `mio`, `url`, endpoint modules, and `crate::http` error types. It is exported by `lib.rs` behind the `handler` feature.

Risks: `kick_api_server` blocks waiting for a backend response, so a stalled API receiver stalls HTTP handling. `server.start_server().unwrap()` panics on startup failure inside the spawned thread. Query parsing prepends `http:` to absolute paths to satisfy `Url`. The route table is exact-path based and ignores path parameters.

Test signals: tests assert route registration, channel bridge error behavior, query extraction, thread exit via waker, status-code translation, JSON body parsing, and response constructors.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/api/src/http_handler.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/api/src/lib.rs -->
# sources/cloud-native/nydus/api/src/lib.rs

Purpose: crate root for `nydus-api`, defining public modules, feature-gated HTTP server exports, and build/version metadata used by Nydus components.

Important APIs/types/functions: always exposes `config`, `error`, and `http` modules and re-exports their public items. With the `handler` feature it imports logging/lazy-static macros, includes endpoint modules and `http_handler`, and re-exports `extract_query_part`, `start_http_thread`, `EndpointHandler`, `HttpResult`, `HttpRoutes`, and `HTTP_ROUTES`. `BuildTimeInfo` is a serializable struct containing package version, git commit, build time, profile, and rustc version.

Control flow: there is no runtime flow here beyond Rust module initialization. Conditional compilation controls whether handler implementation code is part of the crate.

State and persistence: no mutable state is owned by this file. `BuildTimeInfo` is a data carrier, typically populated from compile-time environment generated by the workspace build script.

Dependencies and integration points: relies on `serde` derives globally and uses `log`/`lazy_static` only when `handler` is enabled. It is the public boundary consumed by builder, daemon, and other crates that need API data types without necessarily embedding the HTTP server.

Risks: feature gating is central; downstream crates expecting `HTTP_ROUTES` or `start_http_thread` must enable `handler`. Macro imports at crate root affect older Rust macro usage in child modules.

Test signals: no tests in this file. Coverage is indirect through endpoint/http-handler tests and crates that instantiate exported config/error/http types.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/api/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/build.rs -->
# sources/cloud-native/nydus/build.rs

Purpose: Cargo build script that records compiler, profile, build time, and git revision data into compile-time environment variables.

Important APIs/types/functions: `get_version_from_cmd` runs `<executable> -V` and trims the trailing newline. `get_git_commit_hash` runs `git rev-parse --verify HEAD`. `get_git_commit_version` runs `git describe --tags`. `main` emits `cargo:rustc-env` lines for `RUSTC_VERSION`, `PROFILE`, `BUILT_TIME_UTC`, `GIT_COMMIT_HASH`, and `GIT_COMMIT_VERSION`.

Control flow: `main` reads `RUSTC` and `PROFILE`, formats the current UTC time in ISO-8601 via `time`, tries git commands, then prints Cargo directives. Git failures degrade to `"unknown"` while `RUSTC` command failures panic when `RUSTC` is set but not executable.

State and persistence: no files are written directly. Persistence is through Cargo build metadata and environment variables embedded into compiled crates. `cargo:rerun-if-changed=../git/HEAD` attempts to make rebuilds sensitive to repository head changes.

Dependencies and integration points: uses standard `Command`, `OsString`, and the `time` crate. It feeds version structs such as `BuildTimeInfo` in the API crate or binaries that read these env vars.

Risks: the rerun path is unusual for a normal `.git/HEAD` path and may not always trigger on git changes. `String::from_utf8(output.stdout).unwrap()` assumes valid UTF-8 from compiler output. Git command success status is not checked; empty stdout would become an empty string rather than `"unknown"`.

Test signals: no direct tests. Behavior is normally validated by build outputs and runtime version reporting.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/Cargo.toml -->
# sources/cloud-native/nydus/builder/Cargo.toml

Purpose: package manifest for the `nydus-builder` crate, version `0.2.0`, edition 2021, with metadata pointing to the Nydus project.

Important APIs/types/functions: not Rust code, but it defines the dependency surface used by builder modules. Core external dependencies include `anyhow`, `serde`, `serde_json`, `sha2`, `tar`, `xattr`, `gix-attributes`, `parse-size`, and system helpers such as `nix`, `libc`, and `vmm-sys-util`. Internal path dependencies are `nydus-api`, `nydus-rafs`, `nydus-storage` with `backend-localfs`, and `nydus-utils`.

Control flow: Cargo resolves these dependencies and workspace settings before compiling the builder. `package.metadata.docs.rs` enables all features and lists Linux and macOS ARM/x86 targets for documentation builds.

State and persistence: the manifest controls build graph persistence through Cargo lock/resolution and package metadata. It does not itself create runtime state.

Dependencies and integration points: this crate is integrated tightly with RAFS metadata, storage backend, utility digest/compression/crypto modules, and API configuration types. The `gix-attributes` dependency backs `attributes.rs`; `tar` backs tar header and conversion paths; `sha2` backs blob hashing.

Risks: path dependency versions must stay synchronized with sibling crates. `nydus-storage` feature selection affects available backends. Since this manifest has no feature section, conditional behavior largely comes from dependencies and higher-level workspace configuration.

Test signals: Cargo compilation and crate tests provide validation. Manifest-specific signals include dependency resolution and docs.rs target builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/attributes.rs -->
# sources/cloud-native/nydus/builder/src/attributes.rs

Purpose: parses Nydus-specific attributes files using git-attributes syntax and exposes lookups for build behavior such as external paths and CRC lists.

Important APIs/types/functions: `Attributes::from(path)` reads and parses a file with `gix_attributes::parse`. `Attributes` stores `items: HashMap<PathBuf, HashMap<String, String>>` and `crcs: HashMap<PathBuf, Vec<u32>>`. Lookup helpers include `is_external`, `is_prefix_external`, `get_value`, `get_values`, and `get_crcs`. Attribute keys currently recognized specially are `type` and `crcs`; `type=external` drives external handling.

Control flow: parser iterates parsed pattern entries, normalizes relative patterns to absolute paths by joining with `/`, records every parsed attribute as a string, parses comma-separated CRC values as hex with optional `0x`, stores CRC vectors, then walks parent directories and inserts missing parents as `type=external`.

State and persistence: state is entirely in the returned `Attributes` object. The source attribute file is read but not modified.

Dependencies and integration points: consumed by `BuildContext` and builder logic that needs path-scoped policy. Depends on `gix-attributes` for syntax parsing and `anyhow` for parse errors.

Risks: only pattern entries are processed; macro or unsupported gitattributes constructs may be ignored depending on parser output. Parent insertion can mark broad directories external, so a single deep external file affects ancestor lookup. Invalid CRC tokens fail the whole parse. `is_prefix_external` checks stored item paths starting with the target, which is useful for subtree detection but can surprise callers expecting target-starts-with-item semantics.

Test signals: tests cover parsing, relative-path normalization, parent injection, external checks, value lookups, CRC parsing with and without `0x`, whitespace, defaults, and non-external types.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/attributes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/chunkdict_generator.rs -->
# sources/cloud-native/nydus/builder/src/chunkdict_generator.rs

Purpose: generates a RAFS bootstrap representing a chunk dictionary. It creates a minimal filesystem tree with root and `/chunkdict`, maps supplied chunk/blob metadata into RAFS chunk records, and dumps bootstrap metadata.

Important APIs/types/functions: `ChunkdictChunkInfo` describes per-chunk source image, blob id, digest, CRC, sizes, and offsets. `ChunkdictBlobInfo` describes blob-level sizes, compressor, and blob meta chunk-info positions. `Generator::generate` is the entry point. Internal helpers include `sort_chunks`, `validate_and_remove_chunks`, `build_root_tree`, `build_child_tree`, `insert_chunks`, and `validate_tree`.

Control flow: generation clones and sorts chunk inputs by blob id, compressed offset, uncompressed offset, and digest; removes blob groups whose total uncompressed size is smaller than `ctx.v6_block_size()`; builds a synthetic root directory; builds a child file named `chunkdict`; inserts chunk wrappers while creating/updating blob contexts; builds and dumps the bootstrap; then returns `BuildOutput`.

State and persistence: mutates `BuildContext`, `BootstrapManager`, and `BlobManager`. It writes bootstrap data through `bootstrap_mgr.bootstrap_storage`; blob data is referenced from chunk dictionary metadata, not produced by reading source files here.

Dependencies and integration points: integrates RAFS inode/chunk wrappers, blob metadata headers, compression algorithms, digest parsing, and builder tree/bootstrap managers. It relies on `BlobManager::get_or_cerate_blob_for_chunkdict`.

Risks: `insert_chunks` uses `unwrap()` when finding matching `ChunkdictBlobInfo`, so missing blob metadata panics. The meta compressed-size update first increments from current uncompressed size and is then overwritten by provided blob info; correctness depends on supplied metadata. Small-blob filtering prints warnings to stderr.

Test signals: tests validate small group removal, boundary-size retention, and root tree creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/chunkdict_generator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/compact.rs -->
# sources/cloud-native/nydus/builder/src/compact.rs

Purpose: implements RAFS blob compaction: removes unused blobs, optionally rebuilds low-utilization blobs, greedily merges small blobs, rewrites chunk references in the bootstrap tree, and emits a new bootstrap/blob table.

Important APIs/types/functions: `Config` controls thresholds (`min_used_ratio`, `compact_blob_size`, `max_compact_size`, `layers_to_compact`, `blobs_dir`). `ChunkKey` deduplicates chunks by digest for v5/ref or by `(blob_index, compressed_offset)` for v6. `ChunkSet` tracks unique chunks and can `dump` them into a new blob. `State` models each original blob as `ChunkDict`, `Delete`, `Invalid`, `Original`, or `Rebuild`. `BlobCompactor::compact` is the public entry.

Control flow: `compact` builds a synthetic `BuildContext`, loads original blob table and optional chunk dictionary, exits early if blob count is below threshold, reconstructs the tree from `RafsSuper`, creates `BlobCompactor`, runs `do_compact`, dumps new blobs, rebuilds bootstrap, and returns `BuildOutput`. Initialization marks chunkdict blobs, walks bootstrap BFS to deduplicate chunks against the dictionary and within the image, and builds chunk/blob-to-node indexes. Dumping either keeps/moves original blobs, skips deletes, or writes rebuilt chunks in original blob order and updates all referenced nodes.

State and persistence: mutates in-memory tree chunk metadata and blob managers, reads original blob content from `BlobBackend`, writes compacted blobs to `cfg.blobs_dir`, and overwrites/dumps bootstrap storage.

Dependencies and integration points: depends on RAFS super/layout, storage backend readers, digest/hash utilities, builder artifact writers, blob manager, chunk dictionaries, and build output generation.

Risks: backend reads use `expect`, so missing blobs can panic. `prepare_to_rebuild` appears to check `!is_rebuild()` before converting `Original` to `Rebuild`, which may make rebuild threshold behavior fragile. `take_blob(idx)` removes from a vector while iterating original indexes, so keeping original blobs relies on state/order interactions. Greedy merge is size-only, not locality-aware. Size calculations use compressed sizes that may be zero and then require backend `blob_size()`.

Test signals: tests cover chunk key construction, chunk set merge/dump, state transitions, chunk rewrite validation, compactor creation, chunkdict blob marking, BFS dedup index construction, dump error/success paths, and compaction state changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/compact.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/blob.rs -->
# sources/cloud-native/nydus/builder/src/core/blob.rs

Purpose: owns data blob dumping and blob metadata emission for RAFS builds.

Important APIs/types/functions: `Blob::dump` is the high-level data path. `Blob::finalize_blob_data` flushes batched data, writes inline tar headers/ToC entries, and validates external blob ids. `Blob::dump_meta_data` serializes, compresses, encrypts, writes, and indexes v6 blob chunk metadata. `get_compression_algorithm_for_meta` forces Zstd for ref conversions.

Control flow: for `DirectoryToRafs`, it asks `BlobLayout::layout_blob_simple` for prefetch-first nodes, dumps each node's chunk data, records prefetch size for early entries, and finalizes. Tar/ref conversions mostly derive blob id and compressed size from tar/zran readers, then finalize. Unsupported conversions are left `unimplemented!()`. Metadata dumping optionally appends zran or batch context, compresses chunk-info data, encrypts data/header if enabled, writes data and header, writes tar headers when inline meta or blob ToC is enabled, and records ToC entries plus chunk digest arrays.

State and persistence: writes blob bytes through an `Artifact`, updates `BlobContext` cursors, hash, sizes, chunk digest arrays, metadata header, and ToC entries. It may also write blob cache data via `BuildContext::blob_cache_generator`.

Dependencies and integration points: uses `BlobLayout`, `Node::dump_node_data`, `BlobManager`, storage blob meta layouts, compression, crypto, RAFS digesting, and conversion settings from `BuildContext`.

Risks: external blob id validation requires 64-character ids and fails late. Unsafe slice conversion is used to serialize chunk digests for ToC. Empty metadata or zero uncompressed size suppresses v6 meta output. Ref conversion correctness depends on tar/zran reader position and digest state.

Test signals: tests verify metadata compression algorithm selection for ref conversion variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/blob.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/bootstrap.rs -->
# sources/cloud-native/nydus/builder/src/core/bootstrap.rs

Purpose: builds and dumps RAFS bootstrap metadata from a builder `Tree`, including inode numbering, directory layout, hardlink handling, parent bootstrap loading, and blob table integration.

Important APIs/types/functions: `Bootstrap::new`, `build`, `dump`, private `build_rafs`, and `load_parent_bootstrap`. `Bootstrap` owns a `Tree` and coordinates with `BuildContext`, `BootstrapContext`, `BootstrapManager`, and `BlobManager`.

Control flow: `build` assigns root inode number 1, inserts root into prefetch and hardlink maps, recursively builds RAFS metadata, then fixes v6 dirents from the root offset. `build_rafs` sets directory child counts and v5 child indexes or v6 directory offsets, assigns sequential indexes to children, detects hardlinks by `(layer_idx, src_ino, src_dev)`, reuses inode numbers for hardlinks, lays out v6 non-directory offsets, inserts nodes into prefetch, and recurses through directories. `dump` chooses v5 or v6 serialization based on blob table, then finalizes memory/file storage; directory storage is renamed to a digest-derived filename.

State and persistence: mutates tree nodes, prefetch tracking, `BootstrapContext` inode map/offset/writer, and bootstrap storage path. Parent bootstrap loading reads an existing RAFS superblock and prepends parent blobs.

Dependencies and integration points: depends on `nydus_rafs` metadata layout and compatibility checks, builder tree/node logic, artifact storage, and blob manager tables.

Risks: root inode assertions assume a fresh bootstrap context. Hardlink handling is layer-aware, but cross-layer real inode differences are called out as tricky. Digest-derived file finalization requires reading all bootstrap bytes. Parent compatibility must match compressor, digester, chunk size, uid/gid, version, and tarfs mode.

Test signals: no local tests in this file; exercised by builder integration and compaction/chunkdict paths that call build/dump.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/bootstrap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/chunk_dict.rs -->
# sources/cloud-native/nydus/builder/src/core/chunk_dict.rs

Purpose: defines the chunk dictionary abstraction used for cross-image/layer deduplication and provides a hash-map implementation backed by RAFS bootstrap metadata.

Important APIs/types/functions: `ChunkDict` trait supports adding chunks, lookup by digest and uncompressed size, blob metadata access, inner-to-real blob index mapping, and digester reporting. `()` implements a null dictionary. `HashChunkDict` stores `HashMap<RafsDigest, (Arc<ChunkWrapper>, AtomicU32)>`, blob infos, a mutexed blob index map, and a digest algorithm. `parse_chunk_dict_arg` supports `bootstrap=path` or bare path.

Control flow: `from_commandline_arg` parses the path and loads a bootstrap. `from_bootstrap_file` loads `RafsSuper`, captures blob table, checks compatibility, then either reconstructs a tree for v5/inlined-digest metadata or loads the v6 chunk table directly. `load_chunk_table` validates table byte size and converts each RAFS chunk-info entry into a `ChunkWrapper`.

State and persistence: dictionary state is in memory. It reads bootstrap files and uses mutable/atomic counters plus a mutex for blob index associations; no files are written.

Dependencies and integration points: used by `BlobManager`, `Bootstrap::load_parent_bootstrap`, compaction, and chunk dedup during node building. Depends on `nydus_api::ConfigV2`, RAFS super/config, storage `BlobInfo`, and digest utilities.

Risks: chunks are added only if the incoming digester equals the dictionary digester. Lookup permits dictionary chunks with uncompressed size 0 to match any requested size, which is intentional but broad. `()` returns `Some(inner_idx)` for `get_real_blob_idx`, while `HashChunkDict` returns `None` unless explicitly mapped. Unsupported dictionary types fail fast.

Test signals: tests cover null dictionary behavior, loading a fixture bootstrap, index mapping, argument parsing, constructor defaults, duplicate add counters, digester mismatch ignoring, lookups, and ordering/equality helper behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/chunk_dict.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/context.rs -->
# sources/cloud-native/nydus/builder/src/core/context.rs

Purpose: central builder context module. It defines conversion modes, artifact storage/writers, blob cache writers, blob contexts/managers, bootstrap context/manager, build configuration, and build output reporting.

Important APIs/types/functions: `ConversionType`, `ArtifactStorage`, `Artifact`/`ArtifactWriter`/`NoopArtifactWriter`, `BlobCacheGenerator`, `BlobContext`, `BlobManager`, `BootstrapContext`, `BootstrapManager`, `BuildContext`, and `BuildOutput`. `BlobContext` tracks blob ids, digests, compression/encryption, offsets, sizes, chunk metadata, ToC data, and cache fields. `BlobManager` manages blob indices, current blob, chunk dictionaries, blob table import/export, and external blob behavior.

Control flow: `BuildContext::new` converts CLI-style options into RAFS blob feature flags and crypto settings. `ArtifactWriter::new/finalize` handles direct single-file writes or temp-file-in-directory writes with rename-on-finalize. `BlobContext::from` reconstructs build-time blob state from existing `BlobInfo`, including special fixes for inlined metadata and optional backend reads. `BlobManager` lazily creates blob contexts, imports parent/chunkdict blobs, maps chunkdict blob indexes, and emits v5/v6 `RafsBlobTable`. `BootstrapContext` allocates inode numbers and v6 metadata block space.

State and persistence: this file owns most mutable build state. It writes artifact files, renames temp files, removes empty single-file outputs, writes blob cache data/meta files, and stores in-memory bootstrap writer data when no storage is configured.

Dependencies and integration points: used across builder core, blob dumping, bootstrap generation, compaction, chunkdict generation, and node processing. It integrates `nydus_api::ConfigV2`, RAFS layouts, storage `BlobInfo`, tar headers, compression, digest, encryption, CRC, prefetch, features, and attributes.

Risks: many invariants are enforced by assertions, including blob meta index order and compressed offset assumptions. `ArtifactWriter::finalize` does not overwrite an existing digest-named file. `BlobManager::take_blob` removes by index. External blob id validation happens elsewhere. `ConversionType::Display` maps `TargzToStargz` to `"targz-ref"`, which may be a display bug.

Test signals: tests cover blob context reconstruction from metadata/backend config, conversion parsing/display/ref checks, artifact storage suffix/default behavior, and noop writer position/finalize behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/context.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/feature.rs -->
# sources/cloud-native/nydus/builder/src/core/feature.rs

Purpose: defines opt-in builder feature flags parsed from strings.

Important APIs/types/functions: `Feature` currently has one variant, `BlobToc`, for appending a Table of Contents footer to RAFS v6 data blobs. `TryFrom<&str> for Feature` accepts `"blob-toc"` and rejects unknown names with an upgrade-oriented error. `Features` wraps a `HashSet<Feature>` and exposes `new`, `Default`, `is_enabled`, and `TryFrom<&str>` for comma-separated feature lists.

Control flow: parsing trims the full string, splits on commas, ignores empty entries, trims each feature token, converts it to `Feature`, and inserts it into the set. Duplicate entries collapse naturally via `HashSet`.

State and persistence: state is an in-memory feature set. The enabled flags influence `BuildContext::new` and blob metadata output, especially `BlobFeatures::HAS_TOC` and tar-header behavior.

Dependencies and integration points: used by `BuildContext`, `Blob::finalize_blob_data`, and `Blob::dump_meta_data` to decide whether to write ToC entries and digest arrays.

Risks: there is no public insert method, so callers must construct from strings or internal code. Unknown features are hard errors rather than ignored for forward compatibility. `is_enabled` takes `Feature` by value, which is fine for the current enum but can be less ergonomic as variants grow.

Test signals: tests cover accepted `"blob-toc"`, rejection of unknown features, trailing commas, and whitespace around feature names.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/feature.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/layout.rs -->
# sources/cloud-native/nydus/builder/src/core/layout.rs

Purpose: computes the order in which file nodes are dumped into data blobs.

Important APIs/types/functions: `BlobLayout::layout_blob_simple(prefetch)` returns `(Vec<TreeNode>, usize)`, where the vector contains prefetch-selected nodes first followed by non-prefetch nodes, and the usize marks how many leading entries came from the prefetch lane. `should_dump_node` accepts only nodes with overlay state `UpperAddition` or `UpperModification`.

Control flow: it asks `Prefetch::get_file_nodes()` for prefetch and non-prefetch node collections, filters both through `should_dump_node`, records the count of prefetch nodes, appends non-prefetch nodes, and returns the final dump order.

State and persistence: no persistent state is stored. The returned order affects subsequent blob writes and prefetch byte accounting in `Blob::dump`.

Dependencies and integration points: depends on `Prefetch`, `TreeNode`, `Node`, and `Overlay`. It is called by `core/blob.rs` during `DirectoryToRafs` conversion.

Risks: lower-layer or unchanged nodes are intentionally skipped; correctness depends on overlay classification before layout. The routine is simple and does not account for size, locality, or dependency ordering beyond prefetch grouping.

Test signals: the unit test constructs a one-node tree, inserts it into prefetch, and verifies the layout returns one dumpable node and the expected prefetch count.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/layout.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/mod.rs -->
# sources/cloud-native/nydus/builder/src/core/mod.rs

Purpose: module declaration hub for the builder core.

Important APIs/types/functions: declares private core submodules: `blob`, `bootstrap`, `chunk_dict`, `context`, `feature`, `layout`, `node`, `overlay`, `prefetch`, `tree`, `v5`, and `v6`.

Control flow: no runtime flow. Rust module loading compiles these files as the internal builder core namespace.

State and persistence: none directly. Stateful behavior lives in declared modules such as `context`, `blob`, `bootstrap`, and `tree`.

Dependencies and integration points: controls visibility boundaries with `pub(crate)` modules. The crate root or parent modules can re-export selected items while keeping implementation details internal to the crate.

Risks: adding a new core file requires declaration here. Because all modules are crate-visible rather than public API, external crates should not depend on these paths directly.

Test signals: no tests in this file; compilation validates that declared modules exist and their internal references resolve.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/mod.rs -->
