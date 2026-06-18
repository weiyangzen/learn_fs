# Research Group subset-b-000263

This grouped report covers OverlayBD LSMT memory indexes and tests, registry-backed file systems, stream conversion service configuration, and tar/EROFS integration. Each source file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/index.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/lsmt/index.cpp

## Purpose
Implements the in-memory mapping indexes used by OverlayBD's log-structured mapped table layer. It provides immutable read indexes, writable level-0 indexes, combo indexes that overlay writable mappings on read-only backing mappings, merge/compression helpers, and an optional linearized B+tree lookup accelerator.

## Important APIs and Types
Key concrete types are `Index`, `IndexLBPT`, `LevelIndex`, `Index0`, and `ComboIndex`. Factory exports include `create_memory_index0`, `create_memory_index`, `create_level_index`, `create_combo_index`, `merge_memory_indexes`, `compress_raw_index`, and `compress_raw_index_predict`. Helpers validate mapping order and mapped-offset ranges, trim lookup edge mappings, and choose AVX-512 accelerated inner search on x86_64 when supported.

## Control Flow
Read-only `Index::lookup` binary-searches sorted `SegmentMapping` ranges, copies intersecting mappings, and trims the first/last result to the requested `Segment`. `Index0::insert` mutates a `std::set` by splitting or erasing overlapping old mappings before inserting the new mapping. `ComboIndex::lookup` walks front mappings and fills gaps from the backing index. `merge_indexes` recursively gives newer layers precedence, tags merged mappings by source layer, and trims boundary ranges.

## State and Persistence
The file owns only memory state: vectors, sets, optional raw buffers, B+tree nodes, allocation counters, virtual size, and ownership flags. Persistence is indirect: these mappings describe which logical sectors are present, zeroed, or remotely mapped in LSMT data files.

## Dependencies and Integration Points
Depends on `index.h`, LSMT file constants from `file.h`, Photon logging/utilities, and Photon filesystem types. `file.cpp` and warp-file paths consume these indexes for read, write, commit, stack, flatten, restack, and remote-data operations.

## Risks
Mapping correctness is sensitive to packed bit-field limits, sector units, sorted non-overlap assumptions, tag overflow, and ownership of raw buffers. `Index0` mutates set elements via casts, which depends on not changing sort keys after insertion except in carefully bounded split paths. `compress_raw_index_predict` ignores mapped-offset continuity, unlike `compress_raw_index`, so it is only a size estimate.

## Test Signals
`lsmt/test/test.cpp` exercises lookup trimming, overlap insertion, layered merge tags, compression, sparse writes, commit, stacking, zfile-backed layers, restack, warp files, and multithreaded verification. Useful additional checks are ASAN/UBSAN runs around `Index0` mutation and large mapping sets that force B+tree fallback/accelerated lookup paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/index.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/index.h -->
# sources/cloud-native/overlaybd/src/overlaybd/lsmt/index.h

## Purpose
Declares the LSMT segment mapping model and abstract memory-index interfaces used by OverlayBD layer files. The header defines the public contract for building, querying, merging, compressing, and combining logical-to-physical sector mappings.

## Important APIs and Types
`Segment` stores logical offset and length in sector units. `SegmentMapping` extends it with mapped offset, zeroed marker, and layer tag. `RemoteMapping` describes externally backed remote data ranges. `IMemoryIndex`, `IMemoryIndex0`, and `IComboIndex` define read-only, writable, and combined index operations. Exported C factories create writable/read-only/combo indexes and merge or compress mapping arrays. `foreach_segments` emits zero/hole callbacks for gaps and data callbacks for mapped ranges.

## Control Flow
Callers construct an index from sorted mappings or start with `create_memory_index0`, insert mappings, then query by `lookup` or `foreach_segments`. `foreach_segments` repeatedly calls `lookup` in bounded batches of 16, invokes the zero callback for holes or zeroed mappings, invokes the data callback for real mappings, and advances the requested segment until fully covered.

## State and Persistence
The header defines compact packed mapping records. Offset and length bit widths impose the persistent representable range for serialized LSMT indexes: 50-bit logical offsets, 14-bit lengths, and 55-bit mapped offsets.

## Dependencies and Integration Points
Integrated by LSMT file implementations, tests, tar/EROFS remote-data import, and any code that needs to present OverlayBD layer contents as a file. Uses Photon filesystem types indirectly through implementation files.

## Risks
All APIs assume sector-granular offsets and lengths. Misordered or overlapping read-only mappings break lookup semantics. Bit-field packing is ABI-sensitive, so persisted index compatibility depends on compiler/platform layout assumptions.

## Test Signals
Tests should assert structure sizes/layout expectations, lookup of gaps and trimmed edges, max-length splitting behavior, remote mapping propagation, and callback order from `foreach_segments`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/test/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/lsmt/test/CMakeLists.txt

## Purpose
Defines the LSMT unit/integration test executable `lsmt_test` and registers it with CTest.

## Important APIs and Types
It includes gflags and gtest from environment-provided roots, builds `test.cpp`, exposes Photon includes, and links `gtest`, `gtest_main`, `gflags`, `pthread`, `photon_static`, and `overlaybd_lib`.

## Control Flow
CMake creates the executable and adds a CTest entry invoking `${EXECUTABLE_OUTPUT_PATH}/lsmt_test`.

## State and Persistence
No runtime state is stored here. The test binary itself creates temporary files under `/tmp` through the fixture code.

## Dependencies and Integration Points
Depends on environment variables `GFLAGS` and `GTEST`, plus the broader OverlayBD library target. It is gated by the parent build's testing configuration.

## Risks
Tests will fail to configure if the environment variables or static libraries are missing. Since `test.cpp` includes implementation files directly as well as linking `overlaybd_lib`, duplicate symbol risks depend on how the library is composed.

## Test Signals
Successful configure, build, and CTest registration are the primary signals; runtime coverage comes from `test.cpp`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/test/lsmt-filetest.h -->
# sources/cloud-native/overlaybd/src/overlaybd/lsmt/test/lsmt-filetest.h

## Purpose
Provides GoogleTest fixtures and helpers for exercising LSMT file behavior across writable layers, read-only layers, sparse writes, compressed commits, stacked files, warp files, and Photon threading.

## Important APIs and Types
Defines `FileTest`, `FileTest2`, `FileTest3`, and `WarpFileTest`. Helpers create/open RW and RO layers, generate randomized sector-aligned writes, maintain a verify image, compare file contents, create committed layers, load stacked images, and build warp-file layers with remote mapping operations.

## Control Flow
Fixtures initialize a Photon local filesystem rooted at `/tmp`, generate deterministic layer filenames, create LSMT files with `LayerInfo`/`WarpFileArgs`, perform randomized `pwritev` or discard operations, and verify full virtual-size reads against the local verification file. Cleanup removes generated layer, data, index, merged, and verify files where enabled.

## State and Persistence
Fixture state tracks layer filenames, current/next layer IDs, parent UUIDs, virtual size, opened `IFile` handles, and compressed-layer sizes. Test persistence is temporary local files representing LSMT data/index/committed layers.

## Dependencies and Integration Points
Includes `index.cpp` and `file.cpp` directly, plus zfile, Photon localfs/thread/uuid utilities, gtest, gflags, and syscalls. It is the main behavioral harness for the LSMT file and index implementation.

## Risks
Randomized tests use a fixed seed in `test.cpp` but still depend on `/tmp` capacity and selected IO engine. Some teardown paths return early, leaving files for inspection but increasing local state leakage. Direct implementation inclusion may diverge from production build linkage.

## Test Signals
Strong signals are byte-for-byte verification against the check file after create/open/commit/stack/flatten/repack/restack, plus UUID preservation checks and multi-thread Photon verification.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/test/lsmt-filetest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/test/test.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/lsmt/test/test.cpp

## Purpose
Implements LSMT index and file tests. It validates low-level mapping operations and high-level OverlayBD layer workflows under randomized writes and layered reads.

## Important APIs and Types
Tests cover `Index`, `LevelIndex`, `Index0`, `ComboIndex`, `merge_memory_indexes`, `compress_raw_index`, `compress_raw_index_predict`, `create_level_index`, LSMT RW/RO file APIs, `stack_files`, `merge_files_ro`, `flatten`, `seek_data`, `restack`, zfile commits, and warp-file remote data.

## Control Flow
The file starts with deterministic random seed setup, Photon initialization, gtest/gflags parsing, and `RUN_ALL_TESTS`. Individual tests construct mapping arrays for exact expected output, use randomized sector writes, commit layers to RO files, reopen them, stack lower and upper files, flatten to new layers, and compare all reads to the verification file.

## State and Persistence
Tests persist temporary data/index/layer files under `/tmp`, use global flags for virtual size, layer count, write count, IO engine, and verification, and track global mapping state for performance tests.

## Dependencies and Integration Points
Depends on fixtures in `lsmt-filetest.h`, Photon localfs/thread runtime, zfile/gzip integration, and LSMT implementation internals. It provides regression coverage for the file/index contracts used by registry, tar import, and image tooling.

## Risks
Performance tests insert one million mappings and can be slow or memory-heavy. The fixed seed improves repeatability but does not cover broad random distributions. Some assertions rely on internal casts to concrete implementation classes.

## Test Signals
Exact mapping equality, allocation block count checks, full-image read verification, compressed commit reopen, sparse-file behavior, checksum zfile paths, restack correctness, warp UUID semantics, and multithreaded reads are the main acceptance signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/test/test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/registryfs/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/registryfs/CMakeLists.txt

## Purpose
Builds the static `registryfs_lib` target from all registryfs C++ sources.

## Important APIs and Types
Uses `file(GLOB SOURCE_REGISTRYFS "*.cpp")`, requires CURL, and adds CURL, RapidJSON, and Photon include directories to the target.

## Control Flow
CMake discovers local `.cpp` files, creates a static library, and publishes include paths needed by consumers.

## State and Persistence
No runtime state is defined. Build output is the static registry filesystem library.

## Dependencies and Integration Points
Integrates registry filesystem v1/v2 and uploader code into OverlayBD consumers that need remote OCI registry blob access.

## Risks
The glob includes every `.cpp` in the directory, so adding experimental files automatically changes the library. The target does not explicitly link CURL here, so linkage must be satisfied by consumers or other parent targets.

## Test Signals
Build success with CURL/RapidJSON/Photon configured and successful linkage by downstream OverlayBD binaries are the relevant signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/registryfs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/registryfs/registryfs.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/registryfs/registryfs.cpp

## Purpose
Implements the original curl-backed registry filesystem. It exposes OCI/Docker registry blobs as read-only Photon files with range GET support, authentication challenge handling, redirect caching, optional acceleration proxying, and metadata size caching.

## Important APIs and Types
`RegistryFSImpl` implements `RegistryFS`; `RegistryFileImpl` implements `VirtualReadOnlyFile`. Important methods include `GET`, `getActualUrl`, `getScopeAuth`, `authenticate`, `getAuthUrl`, `setAccelerateAddress`, `open`, `stat`, `RegistryFileImpl::preadv`, `getMetaLength`, and exported factory `new_registryfs_v1`.

## Control Flow
Opening a path constructs a file and calls `fstat`, which obtains metadata with a one-byte/ranged GET. Reads use `preadv`, clamp requested bytes to cached file size, and call `RegistryFSImpl::GET`. `GET` resolves or reuses an actual URL, attaches bearer auth when needed, optionally rewrites through an acceleration URL, issues a curl GET with range headers, and invalidates URL cache on non-2xx responses.

## State and Persistence
Runtime state includes a small curl identity pool, cached metadata sizes, cached bearer tokens by scope, cached actual URLs, CA/client cert/key paths, timeout, and acceleration prefix. It does not persist files locally.

## Dependencies and Integration Points
Depends on Photon curl wrapper, Photon HTTP URL/header utilities, `ObjectCache`, RapidJSON, base64 helper, Photon virtual files, and password callback delegation. It is created through `new_registryfs_v1` declared in `registryfs.h`.

## Risks
TLS verification is explicitly disabled despite CA configuration. Challenge parsing is simple comma splitting and can misparse quoted commas. `preadv` declares `ret_len` in retry logging without initialization. URL/token caches need careful invalidation on auth failures.

## Test Signals
Useful tests include anonymous registry reads, bearer-token auth reads, redirects, 401/403 retry invalidation, content-range size parsing, timeout behavior, acceleration URL rewriting, and client certificate configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/registryfs/registryfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/registryfs/registryfs.h -->
# sources/cloud-native/overlaybd/src/overlaybd/registryfs/registryfs.h

## Purpose
Declares the public registry filesystem and uploader interfaces used to read from and push to OCI-compatible registries.

## Important APIs and Types
`RegistryFS` extends `photon::fs::IFileSystem` with `setAccelerateAddress`. `PasswordCB` supplies username/password pairs. C exports create v1 and v2 registry filesystems, create a registry uploader wrapping a local file, and finalize an upload while returning its digest.

## Control Flow
Consumers choose `new_registryfs_v1` or `new_registryfs_v2`, open registry blob URLs as files, optionally set an acceleration proxy prefix, and read through Photon file APIs. Upload consumers create an uploader, stream data via `write`, then call `registry_uploader_fini` to fsync/finalize and retrieve the sha256 digest.

## State and Persistence
The header defines no state itself. Implementations maintain auth, URL, HTTP-client, and upload state, while upload data is staged in the caller-supplied local file.

## Dependencies and Integration Points
Depends on Photon callbacks and filesystem abstractions. The C ABI makes the functions usable from plugin-style or dynamically linked integration code.

## Risks
Defaults use `uint64_t timeout = -1`, relying on implementation timeout semantics. The v1 factory reserves an unused sixth argument while v2 treats it as customized user agent, so callers must use the correct version.

## Test Signals
Compile/link checks for the C exports, read-only file behavior through `IFileSystem`, acceleration address behavior, and uploader finalize digest checks are the expected signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/registryfs/registryfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/registryfs/registryfs_v2.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/registryfs/registryfs_v2.cpp

## Purpose
Implements the newer Photon HTTP-client based registry filesystem and streaming uploader. It supports read-only ranged registry blob access, bearer/basic auth, redirect and metadata caches, TLS context loading, custom user-agent selection, and chunked blob upload with sha256 digest finalization.

## Important APIs and Types
`RegistryFSImpl_v2`, `RegistryFileImpl_v2`, and `RegistryUploader` are the central classes. Important methods include `get_data`, `get_actual_url`, `get_scope_auth`, `authenticate`, `refresh_token`, `refresh_client`, `RegistryFileImpl_v2::preadv`, `get_length`, `RegistryUploader::write`, `fsync`, `init_upload`, `upload_thread`, `upload_chunk`, `new_tls_context_from_file`, `new_registryfs_v2`, `new_registry_uploader`, and `registry_uploader_fini`.

## Control Flow
Reads resolve authentication and redirect state, issue ranged GETs through `HTTP_OP`, and read response bytes into caller iovecs. Upload starts a background std::thread with its own Photon runtime, initializes an upload URL by POST, uploads staged local-file chunks via PATCH as writes advance, computes sha256 on incoming writes, and completes with a PUT containing the digest.

## State and Persistence
Read-side state includes HTTP client, TLS context, metadata cache, scope-token cache, actual-URL cache, user agent, timeout, and acceleration URL. Upload-side state includes local staging file, write/upload positions, semaphores, upload URL, token, chunk buffer, SHA256 context/sum, and failure/finished flags.

## Dependencies and Integration Points
Uses Photon HTTP client, TLS stream utilities, localfs, Base64 utilities, RapidJSON, OpenSSL SHA256, std::thread, and version metadata. It is the implementation behind `registryfs.h` v2 exports.

## Risks
Ownership of TLS context is shared into uploader-created filesystem instances and needs care to avoid double-free or use-after-free. Upload retry restarts from position zero and must be compatible with local staged data. `read_file` uses a fixed 4096-byte buffer while reading `st.st_size`, risking overflow for larger cert/key files. Authentication challenge parsing was improved for quoted commas but is still custom parsing.

## Test Signals
Tests should cover bearer and basic reads, redirects, custom UA, proxy/acceleration, TLS cert/key loading, token refresh on 401/403, ranged resource-size detection, chunk upload range handling, final digest matching, and upload retry behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/registryfs/registryfs_v2.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/CMakeLists.txt

## Purpose
Builds the `overlaybd-streamConv` executable from the stream convertor sources.

## Important APIs and Types
Globs local `.cpp` files, adds Photon and RapidJSON include directories, and links `photon_static`, `gzip_lib`, `gzindex_lib`, `tar_lib`, and `yaml-cpp`.

## Control Flow
CMake creates the executable and leaves a test subdirectory hook commented out.

## State and Persistence
No runtime state is defined. The built executable later persists gzip and tar metadata under its configured work directory.

## Dependencies and Integration Points
Integrates the service with OverlayBD gzip, tar, Photon networking, and YAML configuration libraries.

## Risks
Glob-based source inclusion can accidentally pull in local experiments. The executable assumes the linked gzip/tar libraries provide stream parsing and metadata generation.

## Test Signals
Build/link success and manual service startup with a YAML config are the primary signals; there are no active CTest entries here.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/config.h -->
# sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/config.h

## Purpose
Defines typed YAML-backed configuration groups for the stream convertor service.

## Important APIs and Types
`LogConfigPara` exposes log level, path, size limit, rotate count, and mode. `GlobalConfigPara` exposes UDS address, HTTP bind address/port, reuse-port flag, work directory, and nested log config. `AppConfig` contains the global config.

## Control Flow
Accessors generated by `APPCFG_PARA` read values from YAML nodes and provide defaults when keys are absent. `stream_conv.cpp` merges user YAML over default `gconfig` and consumes these accessors during startup and logging setup.

## State and Persistence
Configuration values are held in YAML nodes. The work directory and log file settings determine runtime filesystem persistence.

## Dependencies and Integration Points
Depends on `config_utils.h`, `yaml-cpp`, STL strings/vectors, and the stream convertor main program.

## Risks
Accessor defaults hide missing configuration, which is convenient but can mask typos. The namespace closing comment names `ImageConfigNS`, but the actual namespace is `App`.

## Test Signals
YAML decode tests should verify defaults, overrides, nested log config, and invalid type behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/config_utils.h -->
# sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/config_utils.h

## Purpose
Provides the YAML configuration base class, accessor macros, recursive merge helper, and yaml-cpp conversion hook for stream convertor config structs.

## Important APIs and Types
`App::ConfigGroup` derives from `YAML::Node`, can load a YAML file, and includes `charfilter` for stripping hyphens. `APPCFG_PARA` and `APPCFG_CLASS` generate typed accessors/constructors. `mergeConfig` recursively overlays maps. `YAML::convert<T>` supports encoding/decoding classes derived from `ConfigGroup`.

## Control Flow
`mergeConfig` clones the left node, walks right-hand keys, recursively merges map values when keys already exist, and otherwise copies new keys. Non-map nodes are replaced by the right node.

## State and Persistence
The helper stores config as in-memory YAML nodes loaded from disk by yaml-cpp. No persistence is written.

## Dependencies and Integration Points
Depends on Photon `ENABLE_IF_BASE_OF` utility, yaml-cpp, and the config structs in `config.h`.

## Risks
Because config groups inherit from `YAML::Node`, object slicing and implicit node conversions can be subtle. `parseYAML` takes `const std::string&` but calls `std::move`, which has no useful effect and may confuse readers.

## Test Signals
Tests should cover recursive map merging, scalar replacement, defaults through generated accessors, and yaml-cpp conversion for nested config groups.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/config_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/stream_conv.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/stream_conv.cpp

## Purpose
Implements `overlaybd-streamConv`, a Photon network service that accepts gzipped tar streams and generates reusable gzip and tar metadata indexes in a work directory.

## Important APIs and Types
`StreamConvertor` owns server state and defines `Task`. Important methods are `valid_request`, `gen_meta`, `do_task`, `serve`, `start`, and `stop`. Process-level functions include `stop_by_signal`, `set_log_config`, and `main`.

## Control Flow
Startup initializes Photon, installs signal handlers, loads YAML config, configures logging, creates `StreamConvertor`, and starts TCP HTTP plus optional UDS servers. HTTP `/generateMeta` validates body length then passes the request stream into `do_task`. `do_task` wraps input in `open_gzstream_file`, uses `UnTar::dump_tar_headers` to write a temporary tar metadata file, saves the gzip index, renames tar metadata to a sha256-derived filename, and logs throughput.

## State and Persistence
Persistent output is written under `globalConfig.workDir`: gzip index data generated by the gz stream file and tar metadata named `<sha256>.tar.meta`. Runtime state includes local filesystem adaptor, TCP/UDS servers, HTTP server, workdir, and bind address.

## Dependencies and Integration Points
Depends on Photon networking/filesystem/thread/signal/logging, OverlayBD gzip and tar libraries, sha256 file tooling, yaml-cpp, and the config headers.

## Risks
`main` reads `argv[1]` without checking `argc`. HTTP response JSON construction appears malformed around `message`/UUID quoting. `server` is global and signal handlers assume it is initialized. Workdir creation is shallow and does not handle nested paths.

## Test Signals
Useful tests include startup with minimal YAML, `/generateMeta` with empty and valid bodies, UDS streaming path, generated `.tar.meta` and gzip index presence, malformed gzip/tar rejection, and signal-triggered shutdown.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/stream_conv.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/CMakeLists.txt

## Purpose
Builds the base static `tar_lib` and wires in tar tests and the EROFS sublibrary.

## Important APIs and Types
Globs local tar `.cpp` sources, creates `tar_lib`, includes Photon headers, conditionally adds `test`, adds `erofs`, and links `tar_lib` privately against `erofs_lib`.

## Control Flow
CMake creates the tar library first, then descends into EROFS so EROFS support is available to tar consumers.

## State and Persistence
No runtime state is defined here. Build artifacts are static libraries.

## Dependencies and Integration Points
Connects tar handling to Photon and EROFS conversion code. Consumers of `tar_lib` can use EROFS-backed functionality via the private link.

## Risks
Glob-based inclusion and private EROFS linkage can hide dependency changes from consumers. Formatting lacks a newline before `include(FetchContent)` in the displayed concatenated output of adjacent CMake files, but each file remains separate.

## Test Signals
Build `tar_lib` and run tar/EROFS tests when `BUILD_TESTING` is enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/CMakeLists.txt

## Purpose
Fetches, configures, builds, and links the external `erofs-utils` library, then builds OverlayBD's `erofs_lib` wrapper sources.

## Important APIs and Types
Uses `FetchContent_Declare` pinned to erofs-utils commit `eec6f7a2755dfccc8f655aa37cf6f26db9164e60`, runs `autogen.sh`, `configure`, and `make`, caches include/config/static-library paths, builds local `erofs_lib`, force-includes erofs-utils `config.h`, and links against `liberofs.a`.

## Control Flow
Configure-time `execute_process` builds the third-party C library before compiling local C++ wrapper code. Tests are added when `BUILD_TESTING` is enabled.

## State and Persistence
FetchContent populates and builds erofs-utils under the CMake build tree. No application runtime state is defined.

## Dependencies and Integration Points
Requires network/source availability at configure time unless FetchContent is cached, autotools, make, and a toolchain compatible with erofs-utils.

## Risks
Running build commands during CMake configure can make configuration slow and fragile. The configuration disables compression and multithreading features, so wrapper behavior depends on those chosen options. Network fetches reduce reproducibility without a populated cache.

## Test Signals
Successful FetchContent population, autotools configure/make, local `erofs_lib` compilation, and downstream EROFS tests are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_common.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_common.cpp

## Purpose
Adapts Photon `IFile` objects to erofs-utils virtual file operations and provides a small sector cache that handles unaligned 512-byte reads/writes required by EROFS image construction and reading.

## Important APIs and Types
Implements `ErofsCache::write_sector`, `read_sector`, `flush`, `erofs_read_photon_file`, `erofs_write_photon_file`, target vfops (`pread`, `pwrite`, `fsync`, `fallocate`, `ftruncate`, `read`, `lseek`), and source vfops (`read`, `lseek`, with other operations unimplemented).

## Control Flow
Unaligned reads/writes round the requested span to sector boundaries, use a scratch sector for partial first/last sectors, and process aligned middle sectors through the cache. The cache evicts the lowest-address cached sector when at capacity, flushing dirty data before reuse. Target vfops call the helper functions; source vfops expose sequential read and lseek from the tar source file.

## State and Persistence
`ErofsCache` stores sector buffers in a map plus dirty address set and writes dirty sectors to the underlying Photon file on eviction or flush. This is the main persistence bridge for generated EROFS image bytes.

## Dependencies and Integration Points
Depends on `erofs_common.h`, Photon logging, erofs-utils `erofs_vfile` operations, and Photon file APIs. Used by both `liberofs.cpp` image creation and `erofs_fs.cpp` image reading.

## Risks
The eviction policy is address-ordered rather than LRU. The destructor does not flush or free cache entries by itself, so callers must call `flush`. `erofs_target_fallocate` checks `if (ret)` inside a loop even successful writes return nonzero, which can return early incorrectly for chunks larger than 4096.

## Test Signals
Tests should cover unaligned partial-sector writes/reads, dirty eviction, flush persistence, target pwrite/pread round trips, and source read/lseek behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_common.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_common.h -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_common.h

## Purpose
Declares shared EROFS wrapper constants, cache structures, Photon-file helpers, and erofs-utils virtual file operation adapters.

## Important APIs and Types
Defines sector constants, alignment macros, `EROFS_ROOT_XATTR_SZ`, `EROFS_UNIMPLEMENTED`, `EROFS_UNIMPLEMENTED_FUNC`, `liberofs_inmem_sector`, `ErofsCache`, and `liberofs_file`. Declares read/write helpers and target/source vfops.

## Control Flow
The declarations establish two directions: target operations read/write the generated EROFS image through an `ErofsCache`, while source operations read/lseek the incoming tar stream.

## State and Persistence
`ErofsCache` state includes the backing file pointer, capacity, cached sectors, and dirty sector set. This state controls when generated image sectors hit the backing file.

## Dependencies and Integration Points
Depends on erofs-utils `erofs/io.h`, Photon filesystem abstractions, and STL maps/sets. Included by `erofs_common.cpp`, `erofs_fs.cpp`, and `liberofs.cpp`.

## Risks
Macros such as `erofs_min(a, b)` lack protective parentheses around the whole expression. Cache ownership is raw-pointer based and relies on explicit flush/free paths in implementation code.

## Test Signals
Compile checks against erofs-utils headers, sector alignment unit tests, and cache flush/eviction tests are appropriate.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_fs.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_fs.cpp

## Purpose
Implements a read-only Photon filesystem over an EROFS image. It supports path lookup, file stat/read/fiemap/xattr operations, directory iteration, filesystem magic checks, and filesystem construction from an image file.

## Important APIs and Types
Implements `ErofsFileSystem`, `ErofsFile`, `ErofsDir`, internal `liberofs_nameidata`, `liberofs_dir_context`, `do_erofs_ilookup`, `do_erofs_readdir`, `erofs_check_fs`, and `erofs_create_fs`.

## Control Flow
`ErofsFileSystem` initializes erofs superblock state with target vfops. Path lookup walks components from root, reads directory blocks, compares dirents, and follows symlinks by recursively walking link targets. `ErofsFile::pread` maps file logical ranges with `erofs_map_blocks`, zero-fills holes/EOF, and reads mapped data with `erofs_read_one_data`. `opendir` collects dirents into a vector-backed `ErofsDir`.

## State and Persistence
The filesystem keeps an erofs superblock and a target `liberofs_file` with cache over the image. File objects keep a copied inode. No writes are exposed; most mutating filesystem methods return `-EROFS_UNIMPLEMENTED`.

## Dependencies and Integration Points
Depends on erofs-utils inode, dir, map, xattr, and superblock APIs, Photon filesystem/fiemap/virtual file interfaces, and shared adapters from `erofs_common`.

## Risks
Symlink following lacks an explicit recursion/depth limit. `fiemap` assumes caller-provided extent capacity is sufficient. Many filesystem operations are unimplemented, so consumers must treat it as read-only. `ErofsFileSystem` logs superblock read failure but still constructs an object.

## Test Signals
Signals include magic detection, stat/open/pread for regular files, hole zero-fill, directory iteration, xattr list/get, symlink path traversal, and negative tests for unsupported mutation APIs.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_fs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_fs.h -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_fs.h

## Purpose
Declares the Photon read-only filesystem, file, and directory wrappers for EROFS images.

## Important APIs and Types
`ErofsFileSystem` implements `photon::fs::IFileSystem`; `ErofsFile` extends `VirtualReadOnlyFile` and `IFileXAttr`; `ErofsDir` implements `photon::fs::DIR`. Free functions `erofs_check_fs` and `erofs_create_fs` expose image detection and filesystem creation.

## Control Flow
Consumers call `erofs_check_fs` on an image file, then `erofs_create_fs`, then use standard Photon filesystem methods such as `open`, `stat`, and `opendir`. Returned files support `fstat`, `fiemap`, `pread`, and read-only xattr access.

## State and Persistence
Opaque private structs hold erofs superblock/file inode state in implementation. The wrapper reads from the supplied image file and does not mutate it.

## Dependencies and Integration Points
Depends on Photon filesystem, virtual-file, fiemap, logging, and STL vector headers. Used by tar/image code that wants to mount or inspect generated EROFS layers.

## Risks
The interface advertises the full `IFileSystem` surface, but most mutating methods are implemented as unsupported. Callers need to handle null returns and negative `EROFS_UNIMPLEMENTED` values.

## Test Signals
Compile-time interface conformance, opening real EROFS images, directory traversal, xattr reads, and unsupported-operation assertions are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/liberofs.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/liberofs.cpp

## Purpose
Builds EROFS images from tar streams using erofs-utils, then imports generated block mappings into an OverlayBD/LSMT target file as remote data mappings.

## Important APIs and Types
Defines `erofs_mkfs_cfg`, `erofs_mkfs`, `erofs_init_sbi`, `erofs_init_tar`, `erofs_write_map_file`, `erofs_close_sbi`, `erofs_close_tar`, and `LibErofs::extract_tar`. `LibErofs` is the public wrapper class.

## Control Flow
`extract_tar` prepares target and source `liberofs_file` vfops, initializes erofs superblock and tar parser state, configures rebuild options, opens a temporary block map file, runs `erofs_mkfs`, then replays the map file into the target via `IFileRW::RemoteData` ioctls. `erofs_mkfs` initializes or reads superblock state, rebuilds the inode tree from tar entries, dumps blobs, flushes buffers, writes the superblock, and resizes the erofs device.

## State and Persistence
Persistent output is written to the target Photon file through the target cache. The temporary map file records EROFS block-to-source offsets and is used to create LSMT remote mappings. Incremental mode depends on whether this is the first layer.

## Dependencies and Integration Points
Depends on erofs-utils tar/rebuild/blob/block-list APIs, LSMT `IFileRW::RemoteData`, shared EROFS Photon adapters, and Photon logging. It links through `erofs_lib` and is used by tar/image import flows.

## Risks
`meta_only` is accepted but unused. Global `rebuild_src_count` is static and not updated here, which may affect device numbering expectations. `std::tmpfile` failure is not checked before use. Map parsing is strict and can abort the import after EROFS data has already been written.

## Test Signals
Tests should build first and incremental EROFS layers from tar streams, verify generated images through `ErofsFileSystem`, check RemoteData mapping counts/offsets, and cover tar headers import mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/liberofs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/liberofs.h -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/liberofs.h

## Purpose
Declares the small public `LibErofs` wrapper for converting tar data into an EROFS-backed OverlayBD target.

## Important APIs and Types
`LibErofs(photon::fs::IFile *target, uint64_t blksize, bool import_tar_headers = false)` stores the output file, block size, and tar-header import mode. `extract_tar(photon::fs::IFile *source, bool meta_only, bool first_layer)` performs the conversion.

## Control Flow
Callers instantiate `LibErofs` with a writable target and then call `extract_tar` for each source tar stream, passing `first_layer` to select initial vs incremental EROFS construction.

## State and Persistence
The object stores the target file pointer, block size, and `ddtaridx` flag. Actual persistence is performed in `liberofs.cpp` through erofs-utils and LSMT remote mapping ioctls.

## Dependencies and Integration Points
Depends on Photon filesystem/fiemap and string view headers. Used by tar import code that wants EROFS layout generation.

## Risks
The class does not own or validate the target pointer. `meta_only` behavior is not visible in the declaration and is currently unused in the implementation.

## Test Signals
Construction with valid/invalid target files, first-layer and incremental extraction, and import_tar_headers mode should be covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/liberofs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/CMakeLists.txt

## Purpose
Defines EROFS simple and stress test executables and registers them with CTest.

## Important APIs and Types
Builds `erofs_simple_test` from `erofs_simple.cpp` and `erofs_stress_test` from `erofs_stress.cpp erofs_stress_base.cpp`. Both link gtest, pthread, Photon, tar, LSMT, gzip, gzindex, checksum, and overlaybd image libraries.

## Control Flow
CMake creates both executables, adds Photon and RapidJSON include paths, and registers `erofs_simple_test` and `erofs_stress_test` with CTest.

## State and Persistence
The CMake file defines no runtime state. The tests likely create image/tar/layer artifacts through the linked libraries.

## Dependencies and Integration Points
Depends on gflags/gtest environment paths, Photon, tar/EROFS, LSMT, gzip, checksum, and image library targets. It validates the interaction between EROFS conversion and OverlayBD image handling.

## Risks
Environment-provided gtest/gflags paths are required. Stress tests may be resource-intensive depending on their generated data sizes.

## Test Signals
Build and CTest execution of both simple and stress EROFS tests are the key signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/CMakeLists.txt -->
