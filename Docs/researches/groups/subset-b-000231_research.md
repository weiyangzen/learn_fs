# subset-b-000231 research

This grouped report covers the requested `nydus-image`, `nydusctl`, `nydusd`, and shared `nydus` library files. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/main.rs -->
# sources/cloud-native/nydus/src/bin/nydus-image/main.rs

## Purpose
`main.rs` is the `nydus-image` CLI entrypoint. It builds, merges, validates, inspects, stats, compacts, optimizes, unpacks, and exports RAFS/Nydus image artifacts by translating Clap arguments into `nydus_builder`, `nydus_rafs`, `nydus_storage`, and `nydus_service` operations.

## Important APIs, Types, And Functions
`OutputSerializer` writes optional JSON results for build and check commands, including build version, bootstrap/blob outputs, trace summaries, RAFS version, and compressor. `prepare_cmd_args` defines the complete CLI surface: `create`, `chunkdict generate`, `merge`, `check`, `optimize`, Linux-only `export`, `inspect`, `stat`, `compact`, and `unpack`. `init_log` wires the shared logger. `Command` is a namespace for command handlers and argument helpers. Key handlers are `create`, `chunkdict_generate`, `merge`, `compact`, `unpack`, `check`, `optimize`, `inspect`, `stat`, and Linux `export_block`. Helper functions validate paths, parse storage/backend/configuration, blob ids, chunk/batch sizes, prefetch policy, blob offsets, and RAFS version.

## Control Flow
`main` builds the Clap parser, initializes logging and tracing, then dispatches to the matching `Command` method. `create` performs the most complex flow: parse conversion type, storage targets, compression/digest settings, whiteout behavior, parent bootstrap, feature flags, encryption, and attributes; validate per-conversion conflicts; create `BuildContext`, `BlobManager`, optional chunk dictionary, optional blob-cache generator, and `BootstrapManager`; choose `DirectoryBuilder`, `TarballBuilder`, or `StargzBuilder`; run `Builder::build`; then serialize output. `merge` loads source bootstraps, optional blob metadata lists, parent bootstrap, and chunk dictionary before calling `Merger::merge`. `check` loads a `Validator`, prints referenced blob metadata, and writes check JSON. `unpack`, `compact`, `optimize`, `inspect`, and `stat` mostly build backend/configuration state and delegate to their specialized modules.

## State And Persistence
The command writes bootstrap files, blob files, blob cache files, chunk-dictionary bootstraps, compacted/optimized bootstraps, exported block images, unpacked tar files, stat JSON, and optional output JSON. It mutates `ConfigV2.internal.blob_accessible` and cache validation flags to match backward compatibility and command behavior. Tracing state is collected through root/event/timing tracers. It does not keep daemon state, except for Linux block export through service APIs.

## Dependencies And Integration Points
The file is the user-facing integration point for `nydus_builder` builders, deduplication database/chunkdict logic, `RafsSuper` metadata loading, storage backends from `BlobFactory`, localfs backends, unpack/stat/validator/inspect modules, shared `nydus` logging/build-info helpers, and Linux `nydus_service` block export. It relies on Clap value sources for default-vs-user option decisions and uses `anyhow` context for command errors.

## Risks
The large option matrix is the main risk. Conversion-type conflict checks must stay synchronized with builder capabilities, RAFS format limits, blob-cache behavior, encryption requirements, and feature flags. Several list parsing paths use `expect`, so malformed comma-separated numeric metadata can panic. `Arc::get_mut(...).unwrap()` assumes configuration references are not cloned before mutation. Backend config JSON parsing has unwraps in deprecated localfs compatibility. `merge` exits with code 2 for inconsistent filesystems, which callers may depend on. Linux-only export builds JSON strings from paths, so quoting and validation matter.

## Test Signals
This file has a small unit test for accepting `/dev/stdin` as a source file. Most behavioral coverage is indirect through builder, validator, stat, unpack, inspect, and service tests. Important manual or integration test signals include CLI conflict matrices, create output JSON, RAFS v5/v6 builds, chunk dictionary generation from SQLite, merge failure exit codes, unpack with localfs and remote backends, stat over blob directories, and Linux export block mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/stat.rs -->
# sources/cloud-native/nydus/src/bin/nydus-image/stat.rs

## Purpose
`stat.rs` computes statistics for RAFS bootstraps: filesystem object counts, file-size and chunk-size distributions, compressed/uncompressed sizes, hardlink-aware file totals, and optional deduplication comparisons between base and target images.

## Important APIs, Types, And Functions
`DedupInfo` stores threshold-based dedup accounting. `ImageInfo` stores per-image directory/file/symlink/chunk counts, size histograms, owned/reference chunk counters, and deduplicated totals. `ImageStat` is the public command object with `new`, `stat`, `finalize`, `dump_json`, and `dump`. It owns a `HashChunkDict` used to compare target chunks against base chunks.

## Control Flow
`ImageStat::stat` loads a `RafsSuper`, constructs a temporary `HashChunkDict` through `Tree::from_bootstrap`, and walks the tree pre-order. Regular files update file and padding sizes, skip duplicate hardlink inodes, count chunks, sum compressed/uncompressed chunk sizes, and fill chunk-size buckets. Directories and symlinks update object counters. For base images, all dictionary chunks are added to the global dedup dictionary. For target images, each chunk is classified as referenced if present in the base dictionary, otherwise owned. `finalize` adds padding to uncompressed totals and, when dedup is enabled, builds threshold rows from chunk reference counts.

## State And Persistence
All analysis state is in memory until `dump_json` writes a JSON report or `dump` prints text. The RAFS bootstrap and blob metadata are read only. Dedup state persists only inside `ImageStat` for the lifetime of one command invocation.

## Dependencies And Integration Points
The module depends on `RafsSuper`, `Tree`, `HashChunkDict`, `ChunkDict`, `ConfigV2`, digest algorithms, and `serde::Serialize`. It is invoked by `nydus-image stat`, which handles selecting a single bootstrap, scanning a blob directory, and optionally loading a target bootstrap.

## Risks
Histogram indexes depend on bit-length calculations and fixed bucket lengths; unusual very large files are clamped to bucket 44. Hardlink suppression is by inode number within a bootstrap, so cross-bootstrap identity is not considered. Errors from `node.chunk_count` are logged but do not fail the stat command. Directory scanning in the caller treats extensionless files as bootstraps and ignores failures at debug level, which can hide skipped images.

## Test Signals
There are no unit tests in this file. Useful signals are `nydus-image stat --bootstrap`, `--blob-dir` with multiple bootstraps, `--target` dedup comparison, JSON serialization shape, hardlink fixtures, and images with mixed chunk sizes.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/stat.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/unpack/mod.rs -->
# sources/cloud-native/nydus/src/bin/nydus-image/unpack/mod.rs

## Purpose
`unpack/mod.rs` converts a RAFS bootstrap plus blob backend into an OCI-style tar stream. It provides the `Unpacker` trait, `OCIUnpacker`, tar writer construction, RAFS iteration, and a chain of inode-type-specific section builders.

## Important APIs, Types, And Functions
`Unpacker::unpack` is the public abstraction. `OCIUnpacker::new` records bootstrap, optional blob backend, output path, and a builder factory. `OCIUnpacker::load_rafs` loads `RafsSuper`. `OCITarBuilderFactory::create` opens the output tar and builds section builders. `create_builders` assembles socket, hardlink, directory, regular-file, symlink, FIFO, char-device, and block-device builders from `pax.rs`. `OCITarBuilder::append` picks the first builder whose `can_handle` returns true and appends every `TarSection`.

## Control Flow
`OCIUnpacker::unpack` loads the RAFS metadata, creates an `OCITarBuilder`, iterates all RAFS inodes using `RafsIterator`, and appends each node/path pair to the tar. Builder order matters: sockets are skipped, hardlinks are detected before regular files, directories are emitted before regular files, and special nodes fall through to their own builders. Regular-file builder creation resolves every blob in the RAFS blob table into a `BlobReader` and stores per-blob compressors.

## State And Persistence
The module writes one tar file, truncating any existing output. It reads RAFS metadata and blob data through the configured backend. It keeps short-lived builder state, including the tar writer, hardlink map in the PAX hardlink builder, per-blob readers, and compressor maps.

## Dependencies And Integration Points
It integrates `nydus-image unpack`, `RafsSuper`, `RafsIterator`, `RafsInodeExt`, `BlobBackend`, `BlobInfo`, `tar::Builder`, and the PAX/OCI builders in `pax.rs`. Backend resolution is provided by `main.rs`, either from `--blob`, `--blob-dir`, or non-local backend configuration.

## Risks
All regular files require a valid blob backend; missing backend readers fail builder creation. Builder ordering is semantically important for hardlinks and sockets. `append` fails on any inode type not recognized by the chain. Tar output is truncated before iteration, so later RAFS/blob errors leave a partial tar. The module does not call `Builder::finish` explicitly, relying on drop behavior.

## Test Signals
There are no direct tests in this file. `pax/test.rs` covers chunk reading, while end-to-end unpack tests should validate directories, hardlinks, symlinks, special files, xattrs, long paths, compressed/uncompressed chunks, and missing backend errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/unpack/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/unpack/pax.rs -->
# sources/cloud-native/nydus/src/bin/nydus-image/unpack/pax.rs

## Purpose
`pax.rs` implements the OCI tar/PAX section builders used by the RAFS unpacker. It maps RAFS inode metadata and blob chunks into tar headers, PAX extended headers, xattr records, link records, special-device records, and streaming file data.

## Important APIs, Types, And Functions
OCI builders include `OCISocketBuilder`, `OCILinkBuilder`, `OCIDirBuilder`, `OCIRegBuilder`, `OCISymlinkBuilder`, `OCIFifoBuilder`, `OCICharBuilder`, and `OCIBlockBuilder`. Shared builders are `PAXSpecialSectionBuilder`, `PAXExtensionSectionBuilder`, and `PAXLinkBuilder`. `PAXUtil` converts xattrs and long path/link names to PAX records. `Util` normalizes paths, truncates ustar names, masks Unix modes, and computes tar checksums. `ChunkReader` implements `Read` across RAFS blob chunks, including decompression.

## Control Flow
Each builder first checks inode type with `can_handle`. Directory, regular, link, and special-file builders create a ustar header, call `set_header_by_inode`, add type-specific fields, collect PAX extensions for long paths/links and xattrs, set checksums, optionally prepend an XHeader section, then emit the main section. Hardlink handling stores the first path per inode and emits later appearances as hard links. `ChunkReader::read` loads the next chunk when its current cursor is exhausted, reads compressed bytes from the appropriate blob reader at `compressed_offset`, decompresses when `is_compressed`, then fills the caller buffer across chunk boundaries.

## State And Persistence
The module writes only through the tar writer owned by `unpack/mod.rs`. In-memory state includes hardlink first-path tracking, per-blob readers and compressor algorithms, pending chunk iterator state, and current decompressed chunk data. PAX xattrs are represented as `SCHILY.xattr.*` records. Username and group name are resolved from host UID/GID databases during unpacking, so output can vary by host.

## Dependencies And Integration Points
It depends on `tar::Header`, `EntryType`, RAFS inode traits, `InodeWrapper`, `BlobReader`, `BlobChunkInfo`, `alloc_buf`, Nydus compression algorithms, Unix `nix::unistd` user/group lookup, and the parent `SectionBuilder`/`TarSection` traits. It is not a standalone tar writer; `OCITarBuilderFactory` instantiates these builders and controls ordering.

## Risks
There are several unwrap/expect paths: symlink target, chunk info lookup, xattr reads, blob reader/compressor lookup, username/group lookup fallbacks, and header path reads. Long-path truncation cuts to valid UTF-8 before relying on PAX full path records; non-UTF-8 path prefixes can still be fragile. `MockBlobReader` tests expose that short reads are possible, but production `ChunkReader::load_chunk` does not verify that the reader filled the requested compressed size. Host-dependent username/group backfill can break reproducibility. Socket inodes are silently skipped.

## Test Signals
The sibling `pax/test.rs` validates `ChunkReader` behavior for exact-size, smaller, larger, zero-length, and compressed reads. Additional useful signals are tar round trips for long names, xattrs, hardlinks, symlinks, device nodes, FIFOs, directories with trailing slash normalization, non-UTF-8 paths, and partial backend reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/unpack/pax.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/unpack/pax/test.rs -->
# sources/cloud-native/nydus/src/bin/nydus-image/unpack/pax/test.rs

## Purpose
`pax/test.rs` unit-tests `ChunkReader`, the streaming adapter that turns RAFS blob chunks into regular-file tar data for unpacking.

## Important APIs, Types, And Functions
`MockBlobReader` implements `BlobReader` over an in-memory `Vec<u8>`. `MockChunkInfo` implements enough of `BlobChunkInfo` to describe chunk offsets, sizes, blob index, and compression state. Tests are `test_read_chunk`, `test_read_chunk_smaller_buffer`, `test_read_chunk_larger_buffer`, `test_read_chunk_zero_buffer`, and `test_read_chunk_compress`. Helpers `create_default_chunk_reader` and `create_compress_chunk_reader` construct readers for uncompressed multi-chunk and gzip-compressed single-chunk cases.

## Control Flow
The default reader concatenates two 256-byte chunks and provides two metadata entries. Tests read with buffers equal to, smaller than, larger than, and zero relative to chunk boundaries to verify cursor carryover and EOF behavior. The compressed test compresses four 256-byte blocks with gzip, marks the metadata compressed, and verifies decompressed output across multiple reads.

## State And Persistence
All state is in memory. `MockBlobReader` stores source bytes and metrics; `MockChunkInfo` stores static metadata. The tests do not write files or use real backends.

## Dependencies And Integration Points
The tests depend on `BlobReader`, `BlobChunkInfo`, `BackendMetrics`, `nydus_utils::compress`, and the private `ChunkReader` from `pax.rs`. They exercise the same `Read` interface used by `tar::Builder::append` for regular file payloads.

## Risks
Several trait methods are left as `todo!()` because current tests do not call them; future `ChunkReader` changes could accidentally hit those paths and panic. `MockBlobReader::try_read` uses `clone_from_slice` into the full destination buffer, which assumes the selected data slice length equals the buffer length; it works for these offsets/sizes but is not a general short-read mock. Tests do not cover backend read errors, missing blob indexes, missing compressors, encrypted chunks, batch chunks, or CRC validation.

## Test Signals
The file itself is the test signal for chunk-boundary read correctness and decompression. Passing tests indicate that `ChunkReader` can stream contiguous uncompressed chunks and one compressed chunk into arbitrary caller buffer sizes.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/unpack/pax/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/validator.rs -->
# sources/cloud-native/nydus/src/bin/nydus-image/validator.rs

## Purpose
`validator.rs` validates that a RAFS bootstrap can be loaded and traversed, optionally prints inode/chunk details, and returns referenced blob metadata for the `nydus-image check` command.

## Important APIs, Types, And Functions
`Validator` owns a loaded `RafsSuper`. `Validator::new` loads a bootstrap from a path and `ConfigV2`. `Validator::check` builds a `Tree` from the superblock, optionally prints every inode and chunk, then returns blob infos, compressor, and RAFS version.

## Control Flow
The command path constructs a validator, calls `check(verbose)`, and then formats blob details in `main.rs`. Inside `check`, `Tree::from_bootstrap` performs the structural metadata load. A DFS pre-order walk is used mainly to force traversal and to print verbose content. Compressor and RAFS version are read from metadata after traversal.

## State And Persistence
The module is read-only. Its only state is the loaded `RafsSuper` in memory. Verbose mode writes to stdout; the caller may write output JSON.

## Dependencies And Integration Points
It depends on `RafsSuper`, `Tree`, `BlobInfo`, `ConfigV2`, `compress::Algorithm`, and `RafsVersion`. It is integrated by `nydus-image check`, which also sets legacy `blob_accessible` behavior.

## Risks
Validation depth depends on what `Tree::from_bootstrap` and `walk_dfs_pre` check; this file does not independently validate blob availability or chunk payload integrity. `try_into().unwrap()` on metadata version assumes the RAFS loader never returns an unsupported version. Verbose printing can be large for big images.

## Test Signals
Unit tests cover invalid bootstrap rejection and successful RAFS v6 fixture validation with expected blob id, zstd compressor, and version. Broader coverage should include corrupt metadata, RAFS v5, multi-blob images, missing blobs, and verbose traversal.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/validator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydusctl/client.rs -->
# sources/cloud-native/nydus/src/bin/nydusctl/client.rs

## Purpose
`client.rs` is the async Unix-domain HTTP client used by `nydusctl` to communicate with the `nydusd` administration API.

## Important APIs, Types, And Functions
`NydusdClient` stores the API socket path. `new` constructs a client. `build_uri` prefixes request paths with `/api/` and adds simple query strings before converting them to `hyperlocal` Unix-socket URIs. `get`, `put`, `post`, and `delete` create a `hyper_util` Unix client, send the request, collect the response body, parse JSON error payloads when needed, and return either JSON values or unit.

## Control Flow
Command objects call `get` for information and metrics, `put` for daemon configuration, `post` for mount/create operations, and `delete` for unmount/delete operations. Each request creates a fresh client, builds a URI using the stored socket, sends optional JSON body bytes, checks HTTP status, and bails on status codes >= 400.

## State And Persistence
The client keeps only the socket path. It does not persist connections, cookies, or response data. Any daemon state changes are performed by the server endpoints reached through PUT/POST/DELETE.

## Dependencies And Integration Points
It integrates `nydusctl` command implementations with `nydusd` API routes exposed by `nydus_api` and `api_server_glue.rs`. It depends on `hyper`, `hyper_util`, `hyperlocal`, `http_body_util`, `serde_json`, and `anyhow`.

## Risks
Query parameters are concatenated without URL encoding, so special characters in mountpoints or ids can break requests. Error handling assumes error responses are JSON; non-JSON error bodies become deserialize failures. The PUT/POST/DELETE success path ignores response bodies. Creating a new client per request is simple but loses connection reuse.

## Test Signals
Unit tests cover construction and URI building with no query, one query parameter, multiple parameters, an empty query list, and representative API paths. They do not exercise real socket I/O, HTTP errors, non-JSON bodies, or URL encoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydusctl/client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydusctl/commands.rs -->
# sources/cloud-native/nydus/src/bin/nydusctl/commands.rs

## Purpose
`commands.rs` implements the high-level `nydusctl` operations: daemon info/configuration, backend/cache/filesystem metrics, mount, and umount. It turns CLI context maps into `NydusdClient` API calls and formats responses for humans or raw JSON.

## Important APIs, Types, And Functions
`CommandParams` is a string map for parsed CLI context. `load_param_interval` parses optional metric polling intervals. `CONFIGURE_ITEMS_MAP` maps user-facing configuration keys such as `log-level` to daemon API keys such as `log_level`. Command structs are `CommandCache`, `CommandBackend`, `CommandFsStats`, `CommandDaemon`, `CommandMount`, and `CommandUmount`. Helpers `metric_delta` and `metric_vec_delta` compute saturating counter deltas for interval mode.

## Control Flow
`CommandCache::execute` gets blobcache metrics and prints prefetch/cache data. `CommandBackend::execute` gets backend metrics; with `interval`, it loops forever, sleeps, fetches new metrics, computes deltas, and prints bandwidth/latency distributions; without interval, it prints cumulative stats. `CommandFsStats` prints global FUSE/read operation metrics. `CommandDaemon` either PUTs mapped configuration JSON or GETs daemon info and backend collection details. `CommandMount` reads a config file, builds an `ApiMountCmd` JSON payload, and POSTs it with a mountpoint query. `CommandUmount` DELETEs the mount endpoint with a mountpoint query.

## State And Persistence
The module persists no local state. It changes daemon state through API calls: log-level updates, dynamic mount, and dynamic umount. Interval backend metrics keep only the previous JSON sample in memory.

## Dependencies And Integration Points
It depends on `NydusdClient`, shared `nydus` API types (`FsBackendDescriptor`, `FsBackendType`), JSON response shapes from `nydusd`, and `std::thread::sleep`. It is called by `nydusctl/main.rs` after Clap parsing.

## Risks
The human-format paths use many `unwrap` calls on JSON fields and array lengths, so daemon API schema drift or partial metrics can panic. `--interval 0` is accepted by parser/tests and causes a tight polling loop. `metric_vec_delta` intentionally panics on mismatched vector lengths. `CommandMount` uses `std::fs::read_to_string(...).unwrap()`, so a missing config file panics rather than returning `anyhow`. Query values are not URL encoded by the client.

## Test Signals
Unit tests cover interval parsing, overflow rejection, configuration-key mapping, scalar and vector metric deltas, counter reset saturation, empty vectors, and mismatched vector panic. API integration, real mount/umount, formatting over full daemon payloads, and zero-interval behavior need higher-level tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydusctl/commands.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydusctl/main.rs -->
# sources/cloud-native/nydus/src/bin/nydusctl/main.rs

## Purpose
`main.rs` is the `nydusctl` CLI entrypoint. It defines the command-line surface, creates a Unix-socket API client, maps subcommands to command structs, and runs them on a Tokio runtime.

## Important APIs, Types, And Functions
The async `main` function is annotated with `#[tokio::main]`. It uses build-time information from `nydus::get_build_time_info` for version output. It defines global `--sock` and `--raw`, subcommands `info`, `set`, `metrics`, `mount`, and `umount`, then dispatches to `CommandDaemon`, `CommandBackend`, `CommandCache`, `CommandFsStats`, `CommandMount`, or `CommandUmount`.

## Control Flow
After parsing, the code unwraps required `--sock`, reads the raw-output flag, and constructs `NydusdClient`. `info` calls daemon info. `set` builds a map from `KIND`/`VALUE`. `metrics` selects backend/cache/fsstats and optionally passes `interval`. `mount` collects source, mountpoint, config path, and type into a context map. `umount` collects mountpoint. If no recognized subcommand is provided, the program returns `Ok(())` without printing help.

## State And Persistence
The file itself keeps no persistent state. It can cause daemon state changes by dispatching `set`, `mount`, and `umount`. All command context is transient `HashMap<String, String>` data.

## Dependencies And Integration Points
It integrates Clap argument parsing, Tokio runtime setup, the local `client` and `commands` modules, and the shared Nydus build-info helper. It is the user-facing companion to `nydusd/api_server_glue.rs`.

## Risks
The CLI requires `--sock` as a non-global argument; users must provide it before subcommands according to Clap behavior. Several required values are unwrapped after Clap validation. There is no explicit fallback help output when no subcommand matches. The accepted `metrics --interval` string is validated later, not by Clap.

## Test Signals
There are no direct tests in this file. Existing tests in `client.rs` and `commands.rs` cover the components it dispatches to. Useful integration tests should run `nydusctl` against a test API socket for each subcommand and raw/non-raw output mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydusctl/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydusd/api_server_glue.rs -->
# sources/cloud-native/nydus/src/bin/nydusd/api_server_glue.rs

## Purpose
`api_server_glue.rs` bridges the generic `nydus_api` HTTP router to the live `nydusd` daemon controller. It maps decoded `ApiRequest` values into daemon, filesystem, blob-cache, metrics, mount, and configuration operations, then sends `ApiResponse` values back to the HTTP router.

## Important APIs, Types, And Functions
`ApiServer` owns the response sender and implements `process_request`, `respond`, daemon operations, metrics exports, mount/remount/umount, fuse-fd save/takeover/start/exit, blob cache entry create/remove/gc, and dynamic config get/update. `ApiServerHandler` owns the request receiver and loops until router shutdown. `ApiServerController` owns router and handler thread handles, the socket path, and a `mio::Waker`; `start` starts the HTTP router and handler thread, while `stop` wakes and joins them and removes the socket file.

## Control Flow
`ApiServerController::start` no-ops when no API socket is configured. Otherwise it creates two channels, builds an `ApiServer`, starts `start_http_thread`, allocates a daemon waker, then spawns the handler thread. The router decodes HTTP into `ApiRequest` and sends it to the handler. `process_request` matches every supported request and calls the corresponding helper. Helpers fetch the daemon or default filesystem service from `DAEMON_CONTROLLER`, perform the operation, map service errors into `ApiError`, and send the response back to the router channel.

## State And Persistence
The controller stores thread handles and a waker. Server operations can persist or mutate daemon state: log level, shutdown, takeover, mount table, blob cache manager entries, upgrade-manager blob entry state, dynamic config values, and blob deletion. `do_exit` triggers daemon exit and sends SIGTERM to the current process. `stop` removes the API socket path.

## Dependencies And Integration Points
This file integrates `nydus_api` routing and payload types, `nydus_service::DaemonController`, `NydusDaemon`, `FsService`, metrics exporters from `nydus_utils::metrics`, Unix signals from `nix`, and the global `DAEMON_CONTROLLER` in `nydusd/main.rs`. It is the server counterpart to `nydusctl/client.rs` and `commands.rs`.

## Risks
`GetBlobObject` is still `todo!()` and would panic if routed. `process_request` unwraps handler errors only to log them, but individual helpers contain unwraps for SIGTERM send and thread joins are only logged. API behavior depends heavily on `DAEMON_CONTROLLER` having a daemon/default filesystem/blob-cache manager set for the selected mode. Config updates accept only keys recognized by `nydus_utils::config::Keys`. Blob cache entry changes update upgrade state only when an upgrade manager exists.

## Test Signals
No unit tests are present. Important integration signals include starting with and without `--apisock`, daemon info v1/v2, log-level updates, start/exit/takeover flows, dynamic mount/remount/umount, metrics routes, config get/update, blob cache create/delete/gc, socket cleanup on stop, and unsupported-mode error responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydusd/api_server_glue.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydusd/main.rs -->
# sources/cloud-native/nydus/src/bin/nydusd/main.rs

## Purpose
`main.rs` is the `nydusd` daemon entrypoint. It defines all daemon modes and global options, initializes logging/signals/resource limits/dedup, constructs the requested daemon service, starts the optional administration API, runs the daemon controller event loop, and performs shutdown.

## Important APIs, Types, And Functions
Global lazy statics are `DAEMON_CONTROLLER`, `BTI_STRING`, and `BTI`. CLI construction helpers include `append_fs_options`, `append_fuse_options`, feature-gated `append_virtiofs_options`, `append_fscache_options`, singleton options, and block-mode option builders. Runtime helpers are `handle_rlimit_nofile_option`, `process_fs_service`, `process_singleton_arguments`, feature-gated `process_nbd_service` and `process_uffd_service`, `sig_exit`, and `main`.

## Control Flow
`main` parses options, initializes logging, registers SIGINT/SIGTERM handlers, logs build info, applies `rlimit-nofile`, optionally initializes CAS dedup, then dispatches by subcommand. Default and `fuse` paths call `process_fs_service` with FUSE mode. `virtiofs` calls the same helper with non-FUSE mode. `singleton` creates a daemon hosting shared blobcache/fscache services. Feature-gated `nbd` and `uffd` create block daemons. After construction, `main` registers the default filesystem service in `DAEMON_CONTROLLER`, starts `ApiServerController`, runs the controller loop if active, then stops API threads and shuts down the daemon.

## State And Persistence
Daemon state is stored in `DAEMON_CONTROLLER`: selected daemon, default filesystem service, singleton mode, blob-cache manager, and event-loop wakers. Persistent effects include mounted FUSE/virtiofs/block services, fscache/blobcache work directories, NBD/UFFD sockets/devices, optional dedup database usage, API socket files, log files, and resource-limit changes. `process_fs_service` may synthesize localfs JSON config, inject `IMAGE_PULL_AUTH` into registry config, and read prefetch file lists.

## Dependencies And Integration Points
The file integrates Clap, shared `nydus` logging/build-info/signal helpers, `nydus_service` daemon factories, `ConfigV2`, `CasMgr`, feature-gated virtiofs/NBD/UFFD modules, and the API server glue. It is the root for runtime modes consumed by external supervisors and by `nydusctl`.

## Risks
Mode-specific option compatibility is spread across Clap definitions and runtime checks. `hybrid-mode` uses `ArgAction::SetFalse`, so presence semantics are easy to misread. Some generated JSON config is built with string formatting/replacement. `process_fs_service` only creates a virtiofs daemon inside a feature gate; non-FUSE mode without the feature would not set one. `rlimit-nofile` depends on platform sysctl/proc values and can fail daemon startup. Signal handlers call into global controller state from a C handler context.

## Test Signals
There are no direct unit tests. Integration coverage should include default FUSE invocation, explicit `fuse`, `singleton`, feature-gated `virtiofs`, `nbd`, and `uffd`, API socket lifecycle, signal shutdown, `IMAGE_PULL_AUTH` config injection, prefetch-file parsing, localfs synthesized config, rlimit handling, log rotation option parsing, and dedup database initialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydusd/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydusd/virtiofs.rs -->
# sources/cloud-native/nydus/src/bin/nydusd/virtiofs.rs

## Purpose
`virtiofs.rs` implements the feature-gated virtio-fs/vhost-user daemon mode for `nydusd`. It adapts a `fuse_backend_rs::Vfs` into a `vhost_user_backend` device backend and wraps it in the shared `NydusDaemon`/`FsService` abstractions.

## Important APIs, Types, And Functions
`VhostUserFsBackend` holds queue processing state: event-index flag, kill event pair, guest memory, FUSE server, and backend request fd. `process_queue` consumes descriptor chains and dispatches FUSE messages. `VhostUserFsBackendHandler` implements `VhostUserBackendMut` and declares queue count, queue size, feature bits, memory updates, backend request fd, exit events, and event handling. `VirtioFsService` implements `FsService`. `VirtiofsDaemon` implements `NydusDaemon` and `DaemonStateMachineSubscriber`. `create_virtiofs_daemon` constructs the vhost-user daemon, service, state machine, optional initial mount, and starts daemon state transitions.

## Control Flow
The backend handler receives queue events for high-priority and request queues. For each available descriptor chain, `process_queue` builds a `Reader` and `VirtioFsWriter`, invokes `Server::handle_message`, adds the descriptor to the used ring, and signals the guest depending on EVENT_IDX state. `handle_event` loops while notifications indicate more work when EVENT_IDX is enabled. `VirtiofsDaemon::start` opens the vhost-user listener socket and spawns a `vhost_user_listener` thread. `create_virtiofs_daemon` creates state-machine channels, kicks the state machine, mounts the optional backend, then sends Mount and Start events.

## State And Persistence
Runtime state includes guest memory, virtqueue state owned by the vhost-user backend, the listener socket path, daemon state atomics, service backend collection, optional supervisor/id, and state-machine channels. Persistent external effects are the vhost-user socket and any mounted RAFS/passthrough backend state. Save/restore and inflight-op export are unsupported for this mode.

## Dependencies And Integration Points
It depends on `fuse_backend_rs`, `vhost`, `vhost_user_backend`, `virtio_queue`, `vm_memory`, `vmm_sys_util`, shared `nydus` daemon traits, `UpgradeManager`, `FsBackendCollection`, and `BuildTimeInfo`. `nydusd/main.rs` calls `create_virtiofs_daemon` when the `virtiofs` feature and subcommand are enabled.

## Risks
The queue processor treats many failures as unrecoverable I/O errors to the caller. Missing guest memory fails requests. Several lock acquisitions use `unwrap`, so poisoned mutexes panic. `set_event_idx` ignores its argument and always enables EVENT_IDX. `exit_event` comments note missing backend support for a kill event. `start` spawns a listener thread and only logs listener errors. Save/restore are unsupported, limiting live upgrade semantics compared with FUSE mode.

## Test Signals
No tests are present in this file. Useful coverage requires feature-enabled integration tests with a vhost-user client: queue negotiation, normal FUSE requests, EVENT_IDX and non-EVENT_IDX notifications, startup/shutdown, optional initial mount, API mount operations through `VirtioFsService`, and unsupported save/restore behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydusd/virtiofs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/lib.rs -->
# sources/cloud-native/nydus/src/lib.rs

## Purpose
`lib.rs` is the shared crate facade used by Nydus binaries. It re-exports service APIs, logging, signal registration, and provides small helpers for command-line argument access and build-time version reporting.

## Important APIs, Types, And Functions
`SubCmdArgs` wraps top-level and subcommand `ArgMatches`, with `new` and `values_of`. Its `ServiceArgs` implementation provides `value_of` and `is_present`, checking subcommand values first and falling back to global/top-level values. The `built_info` module exposes compile-time environment values. `dump_program_info` logs version information. `get_build_time_info` returns both a formatted version string and a `BuildTimeInfo` struct.

## Control Flow
Binaries call `get_build_time_info` to populate Clap versions and daemon API info. `nydusd` wraps parsed arguments in `SubCmdArgs` so shared service constructors can read either subcommand-specific or global options. `dump_program_info` logs build details after logging is initialized.

## State And Persistence
This file has no mutable state. Build info is compiled into constants through environment variables. Logging output is produced by callers that invoke `dump_program_info`.

## Dependencies And Integration Points
It depends on Clap `ArgMatches`, `nydus_api::BuildTimeInfo`, the local `logger` and `signal` modules, and re-exports all of `nydus_service`. It is imported by `nydus-image`, `nydusctl`, and `nydusd`.

## Risks
The `ServiceArgs::value_of` fallback uses `try_get_one(...).unwrap_or_default()`, suppressing Clap lookup errors as absent values. `is_present` only recognizes boolean flags with value `true`, not counted flags or value presence. Build info environment variables must be defined by the build system or compilation fails.

## Test Signals
There are no direct tests. Effective coverage is indirect through CLI binaries using build-info strings and `SubCmdArgs` in global/subcommand option combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/logger.rs -->
# sources/cloud-native/nydus/src/logger.rs

## Purpose
`logger.rs` centralizes logging setup and formatting for Nydus binaries using `flexi_logger`, colored console output, optional file output, optional rotation, runtime log-level control, and panic logging.

## Important APIs, Types, And Functions
`log_level_to_verbosity` maps `LevelFilter` to a numeric verbosity. `get_file_name` shortens source file paths around `/src/`. `opt_format` formats file logs and non-colored output; info logs omit file/line, while other levels include them. `colored_opt_format` applies terminal colors. `setup_logging` configures file or stderr logging, optional rotation by size, max log level, and `log_panics` backtrace hook.

## Control Flow
Callers pass optional log path, log level, and rotation size. For file logging, the code builds a `FileSpec` from the provided path without canonicalization, preserves explicit suffixes to avoid flexi_logger adding `.log`, resolves relative parent directories against current working directory, starts a trace-level flexi logger with `opt_format`, and optionally enables timestamped compressed rotation. Without a file path, it starts colored console logging. In both cases it sets the global max log level and installs a panic hook.

## State And Persistence
The logger installs a global logging backend and panic hook. With file logging, it appends to the target file and may create rotated compressed logs. With console logging, output is emitted to stderr/stdout according to flexi_logger behavior. Log level can later be changed by API glue through `log::set_max_level`.

## Dependencies And Integration Points
It depends on `flexi_logger`, `log`, `log_panics`, current working directory resolution, and Nydus error macros from `nydus_api`. It is re-exported by `lib.rs` and used by `nydus-image` and `nydusd`.

## Risks
Rust logging can only be initialized once per process; tests avoid calling `setup_logging` directly. Path parsing rejects non-UTF-8 stems/extensions. Rotation size multiplication can overflow for extremely large MB values. Formatting intentionally hides file/line for info logs, which can reduce diagnosability. `get_file_name` uses string searches and can produce surprising prefixes for unusual paths.

## Test Signals
Unit tests cover verbosity mapping, file-name shortening, formatting behavior for info/debug/warn/error and missing file info, and path component extraction for rotation setup. They do not initialize the global logger, avoiding one-time logger conflicts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/logger.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/signal.rs -->
# sources/cloud-native/nydus/src/signal.rs

## Purpose
`signal.rs` provides a tiny wrapper for registering Unix signal handlers through `nix`.

## Important APIs, Types, And Functions
`register_signal_handler` takes a `nix::sys::signal::Signal` and an extern "C" handler function pointer, builds a `SigAction` with empty flags and mask, and calls `sigaction`.

## Control Flow
Callers provide the signal and handler. The function constructs the action and installs it in an unsafe block. Registration failure panics via `unwrap`, based on the assumption that daemon binaries cannot operate correctly without signal handling.

## State And Persistence
It mutates process-global signal disposition. There is no file or durable persistence.

## Dependencies And Integration Points
It depends on `nix::sys::signal` and `libc` handler ABI. `lib.rs` re-exports it. `nydusd/main.rs` uses it to register SIGINT and SIGTERM handlers that notify `DAEMON_CONTROLLER`.

## Risks
The wrapper does not expose flags, masks, or error handling. Handlers run in async signal context, so the caller-provided function must be signal-safe or accept the risk. Panicking during registration aborts startup.

## Test Signals
There are no tests. Practical validation is daemon startup and graceful shutdown via SIGINT/SIGTERM.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/signal.rs -->
