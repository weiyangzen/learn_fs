# subset-b-000265 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4.c -->
## sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4.c

Purpose: vendored LZ4 1.8.3 block compressor/decompressor implementation used by OverlayBD's zfile compressor layer. It implements raw block compression APIs, streaming compression/decompression contexts, dictionary-aware paths, partial decode, and deprecated compatibility wrappers. It is not the LZ4 frame format; callers must persist compressed sizes and original sizes separately.

Important APIs/functions: `LZ4_compress_default`, `LZ4_compress_fast`, `LZ4_compress_fast_extState`, `LZ4_compress_destSize`, `LZ4_decompress_safe`, `LZ4_decompress_safe_partial`, `LZ4_decompress_fast`, streaming APIs such as `LZ4_createStream`, `LZ4_loadDict`, `LZ4_compress_fast_continue`, `LZ4_saveDict`, `LZ4_createStreamDecode`, `LZ4_decompress_safe_continue`, and dictionary helpers. Core work is in `LZ4_compress_generic` and `LZ4_decompress_generic`, which are parameterized by output-limit, table type, dictionary mode, and decode end condition.

Control flow: compression sets up endian/memory helpers, hashes 4-byte sequences into U16/U32/pointer tables, searches matches with acceleration-based skip, emits literal length, literals, 16-bit match offset, and match length. Decompression reads tokens, copies literals, resolves match offsets against current prefix/external dictionaries, performs fast shortcut copies when safe, and returns negative offsets on malformed input. Streaming compression maintains `LZ4_stream_t_internal` state (`hashTable`, `currentOffset`, dictionary pointer/size, optional dictionary context) and renormalizes offsets near 2GB.

State/persistence: state is in caller-owned or heap-allocated LZ4 stream structures; no file persistence. The hash table and dictionary pointers are process-local and depend on dictionary memory remaining stable for streaming calls. Dependencies are C runtime, compiler intrinsics, and `lz4.h`.

Integration points: zfile's compressor wrapper can call this block API and persists the needed block sizes/CRC itself. Risks: unsafe `LZ4_decompress_fast` can read past intended input and should only be used when original size and trusted data are guaranteed; `LZ4_wildCopy` intentionally overwrites within required slack; streaming dictionary APIs are sensitive to buffer lifetime and overlap. Test signals: `lz4/test.c` covers a basic compress/decompress round trip; zfile tests provide higher-level LZ4 zfile coverage with random reads, CRC validation, and decompression.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4.h -->
## sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4.h

Purpose: public C header for the vendored LZ4 block API. It exports version constants, symbol-visibility macros, compression bounds, one-shot compression/decompression, advanced stateful APIs, streaming APIs, static-linking-only internals, and deprecated compatibility entry points.

Important APIs/types: version macros report 1.8.3. `LZ4_MAX_INPUT_SIZE` and `LZ4_COMPRESSBOUND` define caller allocation constraints. `LZ4_stream_t` and `LZ4_streamDecode_t` are exposed as unions for static allocation but documented as ABI-unstable. Internal structs hold hash tables, offsets, dictionary pointers, and decode prefix/external dictionary metadata.

Control flow contract: callers allocate destination buffers, pass exact compressed sizes to safe decompression, pass known original output size to fast decompression, and manage one block at a time. Streaming compression requires previous 64KB source data to remain stable unless `LZ4_saveDict` is used. Streaming decompression requires previously decoded data to remain available or supplied through `LZ4_setStreamDecode`.

State/persistence: the header defines in-memory stream state only. It deliberately avoids container metadata; any file format must store compressed block sizes, original sizes, checksums, and framing externally.

Dependencies/integration: included by `lz4.c`, `lz4/test.c`, and compressor adapters. It uses `stddef.h` and optionally `stdint.h`, with `extern "C"` guards for C++ consumers.

Risks: static-linking-only definitions are not stable API/ABI; deprecated functions remain available but should not guide new code. `LZ4_decompress_fast` is explicitly unsafe for untrusted input because compressed size is not bounded. Test signals come from the basic sample and from zfile exercising LZ4 through OverlayBD's persisted block format.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/test.c -->
## sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/test.c

Purpose: minimal C example/test for the vendored LZ4 API. It compresses a static string with `LZ4_compress_default`, decompresses it with `LZ4_decompress_safe`, and validates byte-for-byte equality.

Important functions: `run_screaming` prints an error and exits. `main` computes `src_size`, allocates `LZ4_compressBound(src_size)`, checks the returned compressed size, shrinks the allocation with `realloc`, allocates a regeneration buffer, decompresses, and validates with `memcmp`.

Control flow: the test is linear and intentionally demonstrates return-code handling. Compression failure is treated as size 0 or negative; decompression failure is negative; successful decompression must return a positive byte count. It frees compressed storage before validation but never explicitly frees `regen_buffer` before process exit.

State/persistence: all state is heap memory in one process; no files are created. Dependencies are `lz4.h`, `stdio.h`, `string.h`, and `stdlib.h`.

Integration points: useful as a smoke test for the vendored LZ4 source, but it does not exercise streaming, dictionaries, partial decode, malformed input, or OverlayBD zfile metadata. Risks/test gaps: static input is tiny and highly narrow; it cannot catch block-boundary bugs, unsafe decode misuse, or performance regressions. Higher-level zfile tests provide stronger integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/test/CMakeLists.txt -->
## sources/cloud-native/overlaybd/src/overlaybd/zfile/test/CMakeLists.txt

Purpose: CMake wiring for the zfile GoogleTest executable. It configures include/link search paths for GFlags and GTest from environment variables, builds `zfile_test` from `test.cpp`, links Photon and OverlayBD libraries, and registers a CTest test.

Important build targets: `add_executable(zfile_test ./test.cpp)`, `target_link_libraries(zfile_test gtest gtest_main gflags pthread photon_static overlaybd_lib)`, `target_include_directories(zfile_test PUBLIC ${PHOTON_INCLUDE_DIR})`, and `add_test(NAME zfile_test COMMAND ${EXECUTABLE_OUTPUT_PATH}/zfile_test)`.

Control flow: build-time only. It assumes parent CMake has set `PHOTON_INCLUDE_DIR`, `EXECUTABLE_OUTPUT_PATH`, and imported/visible `overlaybd_lib` and `photon_static`.

State/persistence: no runtime persistence, but the linked test writes temporary files under `/tmp` at execution time. Dependencies are environment variable paths `$GFLAGS` and `$GTEST`, which can make the test non-portable outside the project build environment.

Integration points: this file is the test gateway for `zfile.cpp`, `compressor.cpp`, CRC code, and Photon file abstractions. Risks: direct environment-variable include/link directories can silently resolve wrong library versions; the CTest command does not pass flags such as `--nwrites`, so default test size is used.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/test/test.cpp -->
## sources/cloud-native/overlaybd/src/overlaybd/zfile/test/test.cpp

Purpose: GoogleTest coverage for OverlayBD zfile compression, decompression, validation, header/trailer integrity, CRC implementation parity, and streaming builder equivalence.

Important types/functions: `ZFileTest` sets up a `/tmp` local filesystem and helper methods `randwrite`, `seqread`, and `randread`. Tests include `verify_compression`, `validation_check`, `ht_check`, `dsa`, and `verify_builder`. The file directly includes `../zfile.cpp` and `../compressor.cpp`, making it a white-box/integration test rather than pure public API test.

Control flow: `verify_compression` writes random data, then tests checksum disabled/enabled, algorithm values 1..2, and block sizes 4K through 64K. It compresses, opens as zfile, checks sequential and random reads, decompresses, and verifies the decompressed file is not zfile. Validation tests corrupt compressed block data and header/trailer bytes and assert failure. Builder test writes randomly sized chunks through multi-worker and single-worker builders and compares produced zfile bytes.

State/persistence: uses `/tmp/verify.data`, `/tmp/verify.zfile`, and related files through Photon localfs; random seed is fixed in `main`. Photon runtime is initialized once. Dependencies include GTest, GFlags, Photon, zfile, compressor, CRC, and local filesystem.

Risks/test signals: strong signal for block indexing, partial reads, CRC detection, decompression, and ordered multi-worker output. Gaps include no explicit zstd adaptor coverage here, no malformed jump-table fuzzing, no ownership/lifetime assertions, and tests may be relatively expensive due to default `nwrites=16384` and repeated random reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/test/test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/thirdparty/CMakeLists.txt -->
## sources/cloud-native/overlaybd/src/overlaybd/zfile/thirdparty/CMakeLists.txt

Purpose: optional custom build target for zfile third-party acceleration libraries: Intel DML when `ENABLE_DSA` is set and ISA-L when `ENABLE_ISAL` is set.

Important build actions: defines `thirdparty_lib`, sets `THIRDPARTY_PATH`, checks out pinned DML commit `5a2956...`, configures/builds/installs DML into a local build directory, copies `libdml*.a` and headers to `${LIBRARY_OUTPUT_PATH}`. For ISA-L it checks out commit `ad8dce...`, runs `autogen.sh`, `./configure`, `make`, copies `libisal.a`, and exports `crc.h`.

Control flow: build commands run as `add_custom_command(TARGET thirdparty_lib ...)` side effects attached to the custom target. They mutate submodule working trees by `git checkout` and place static artifacts in the library output path.

State/persistence: persistent build outputs land under third-party build directories and `${LIBRARY_OUTPUT_PATH}`. Dependencies include git, cmake, make/autotools, DML source tree, ISA-L source tree, and writable output directories.

Integration points: provides accelerated CRC/DSA support used by zfile CRC paths and tested by `ZFileTest.dsa`. Risks: build is not hermetic, mutates source checkout state, lacks explicit byproducts, and can be fragile under parallel or read-only builds. Network is not used here, but missing submodules or toolchains break the target.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/thirdparty/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/zfile.cpp -->
## sources/cloud-native/overlaybd/src/overlaybd/zfile/zfile.cpp

Purpose: implements OverlayBD's zfile container: a random-readable compressed file format with 512-byte header/trailer, per-block compressed data, optional per-block CRC, block-length index, and Photon `IFile` adapters for reading and writing.

Important types/functions: `CompressionFile::HeaderTrailer` stores magic, digest, flags, index offset/size/CRC, original size, and `CompressOptions`. `JumpTable` reconstructs block start offsets from 32-bit block lengths using partial offsets and 16-bit deltas. `CompressionFile::BlockReader` batches compressed block reads and exposes iterators. Public functions are `zfile_open_ro`, `zfile_compress`, `zfile_decompress`, `zfile_validation_check`, `is_zfile`, and `new_zfile_builder`. Builders include single-threaded `ZFileBuilder` and ordered multi-worker `ZFileBuilderMP`.

Control flow: compression writes an unsealed header, compresses fixed-size raw blocks, optionally appends salted CRC32C to each block, records compressed lengths, writes the index, fills trailer metadata, writes a sealed trailer, and may overwrite the header with trailer metadata. Read path loads header/trailer, validates header digest and optional index CRC, builds the jump table, then `pread` maps requested raw offsets to compressed blocks, verifies CRC with retry/reload, decompresses full or partial blocks, and copies requested spans.

State/persistence: persistent on-disk state is the zfile layout and metadata. In-memory state includes jump table, compressor instance, validity mode, builder buffers, worker semaphores, and block-length vectors. Dependencies include Photon virtual files/threads, compressor adapters, CRC32C, UUID, and POSIX stat.

Integration points: `switch_file.cpp` detects and opens zfiles; zfile tests exercise public APIs; compressor code supplies LZ4/ZSTD algorithms. Risks: `zfile_open_ro` constructs compressor args before disabling verify in the local copy, so option mutation order deserves review; jump-table delta grouping depends on block size and 16-bit limits; multi-worker builder ordering relies on semaphores and shared `m_block_len`/`moffset`; `zfile_compress` accepts null args only as an error but tests intentionally call it. Test signals are strong for round trip, random reads, CRC/header corruption, and builder equivalence.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/zfile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/zfile.h -->
## sources/cloud-native/overlaybd/src/overlaybd/zfile/zfile.h

Purpose: public zfile interface for opening, creating, validating, detecting, compressing, and decompressing OverlayBD zfile data through Photon `IFile` objects.

Important APIs: `MAX_READ_SIZE` is 64KiB and bounds zfile block read/decompression buffers. `zfile_open_ro(file, verify, ownership)` returns a read-only decompressed view. `zfile_compress(src, dst, args)` writes a complete compressed zfile. `zfile_decompress(src, dst)` materializes raw bytes. `zfile_validation_check(src)` verifies CRC-enabled zfiles. `new_zfile_builder(file, args, ownership)` returns a streaming writer. `is_zfile(file)` returns 1/0/-1 for zfile/normal/error.

Control flow contract: callers provide already-open Photon files and decide ownership. `verify` controls per-block CRC checking during read; format/header validation always happens during open/detection. Builders require `close()` to finalize index/trailer.

State/persistence: the header declares API only; persistent format details live in `zfile.cpp`. Dependencies are `compressor.h` and Photon file types.

Integration points: used by switch-file fallback/local switch logic, compressor tools, and tests. Risks: C linkage exposes C++ Photon pointer types, so ABI use is effectively project-internal; callers must respect ownership and close semantics or leak/incompletely seal zfiles. Tests in `zfile/test/test.cpp` cover most API paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/zfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zstd/CMakeLists.txt -->
## sources/cloud-native/overlaybd/src/overlaybd/zstd/CMakeLists.txt

Purpose: builds the zstd adaptor library from all `*.cpp` files in the directory.

Important build actions: `file(GLOB SOURCE_ZSTD "*.cpp")`, `add_library(zstd_lib STATIC ${SOURCE_ZSTD})`, includes `${PHOTON_INCLUDE_DIR}`, and links `photon_static` plus `${LIBZSTD}`.

Control flow/state: build-only file; no runtime state. It depends on the parent build defining Photon and libzstd variables and on glob results at configure time.

Integration points: `zstd_lib` supplies `open_zstdfile_adaptor` and `is_zstdfile` to consumers needing sequential ZSTD decompression. Risks: CMake globbing requires reconfigure to pick up added source files in older CMake workflows; `${LIBZSTD}` must be a valid library path/name. Test coverage for this specific target is not visible in the listed files.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zstd/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zstd/zstdfile.cpp -->
## sources/cloud-native/overlaybd/src/overlaybd/zstd/zstdfile.cpp

Purpose: Photon read-only adaptor that exposes a sequential decompressed view over a ZSTD-framed compressed `IFile`.

Important types/functions: `ZStdAdaptorFile` derives from `VirtualReadOnlyFile`, owns or borrows an underlying `IFile`, maintains a `ZSTD_DStream`, input buffer sized by `ZSTD_DStreamInSize`, and a `ZSTD_inBuffer`. `read` fills caller output by reading compressed chunks and calling `ZSTD_decompressStream`. `open_zstdfile_adaptor` constructs the adaptor. `is_zstdfile` checks the 4-byte ZSTD magic header and seeks back to offset 0.

Control flow: `read` loops until the caller buffer is full or underlying EOF is reached. When the input buffer is exhausted it reads more compressed bytes. On `ZSTD_decompressStream` error it returns `EIO`. When a frame ends (`ret == 0`) it reinitializes the stream for a possible following frame. `fstat` delegates to the compressed file, so size is not decompressed size.

State/persistence: streaming state is in `ZSTD_DStream`, `m_buffer`, and `m_input`; persistent state is only the underlying compressed file. Dependencies are libzstd, Photon file abstractions, and logging.

Integration points: intended for consumers that only need sequential `read`; random access methods and `lseek` are unimplemented. Risks: `is_zstdfile` uses `read` then `lseek`, so it requires a seekable source and changes/readv state on unusual file objects; `read` returning compressed `fstat` size may confuse callers expecting raw size; no listed tests exercise multi-frame or error cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zstd/zstdfile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zstd/zstdfile.h -->
## sources/cloud-native/overlaybd/src/overlaybd/zstd/zstdfile.h

Purpose: public declarations for the ZSTD read adaptor.

Important APIs: `open_zstdfile_adaptor(photon::fs::IFile* file, bool ownership = true)` returns a read-only decompression wrapper and optionally owns the source. `is_zstdfile(photon::fs::IFile* file)` detects a ZSTD magic header.

Control flow contract: consumers should use sequential `read`; the implementation does not support random access operations. Ownership defaults to true, so callers must avoid deleting the wrapped file after handing it to the adaptor.

State/persistence: no state in the header. Dependencies are Photon virtual-file declarations.

Integration points: linked through `zstd_lib`. Risks/test signals: absent tests in the provided subset; detection assumes the file can be read and rewound.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zstd/zstdfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/prefetch.cpp -->
## sources/cloud-native/overlaybd/src/prefetch.cpp

Purpose: implements static trace-based and dynamic file-list-based prefetching for OverlayBD images, using Photon threads to issue background reads before foreground I/O.

Important types/functions: `PrefetchFile` wraps a source file and records successful `pread` calls in record mode. `PrefetcherImpl` handles mode detection, trace dump/reload, source registration, replay queues, and worker threads. `DynamicPrefetcher` reads a prefetch file list, discovers ext4/erofs file extents via fiemap, turns extents into read tasks, and reuses replay workers. Factories are `new_prefetcher` and `new_dynamic_prefetcher`.

Control flow: static mode uses trace-file state: missing file disables, empty file records, non-empty file replays. Record mode creates a `.lock`, records reads, dumps a header plus trace records with CRC32C on stop/destruction, removes lock, and creates `.ok`. Replay mode loads and checksum-validates the trace, registers layer source files, and spawns `m_concurrency` workers to `pread` queued ranges. Dynamic mode treats the configured path as a file list, validates/trims entries, creates an erofs or extfs view of the image file, collects extents for files/directories, slices reads to 1MiB, and replays.

State/persistence: trace file contains `TraceHeader` and `TraceFormat` records; `.lock` and `.ok` sidecar files signal recording lifecycle. In-memory state includes queues, registered files, Photon join handles, and stop flags. Dependencies include Photon FS/thread/fiemap/extfs, erofs helpers, LSMT alignment, CRC32C, regex, and local filesystem calls.

Integration points: image service/config can provide `recordTracePath`; trace tests include prefetch implementation directly. Risks: replay queue access is not visibly locked across worker threads; dynamic path validation function name is misleading and regex may accept only narrow path characters; destructor shutdown must coordinate with worker thread state; dynamic replay depends on filesystem fiemap support and may issue large background reads. Test signals: `trace_test.cpp` validates dynamic erofs prefetch by checksumming files, while static record/replay has no direct listed test.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/prefetch.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/prefetch.h -->
## sources/cloud-native/overlaybd/src/prefetch.h

Purpose: public interface and lifecycle documentation for OverlayBD prefetch support.

Important APIs/types: `Prefetcher` derives from Photon `Object`, defines `Mode { Disabled, Record, Replay }` and `TraceOp { READ, WRITE }`, and declares `record`, `replay`, `new_prefetch_file`, `detect_mode`, and `get_mode`. Factories create trace-based or dynamic prefetchers.

Control flow contract: static mode is driven by trace-file existence and size; recording stops when the lock file is removed or the prefetcher is destroyed; replay uses a non-empty trace. Dynamic mode reads a file list specified via `recordTracePath` and prefetches listed files/directories.

State/persistence: header documents persistent trace, lock, and OK files but does not define binary layout. Dependencies are C++ string/cstdint and Photon filesystem.

Integration points: consumers wrap layer/source files with `new_prefetch_file` so reads can be recorded, then call `replay` when an image file is available. Risks: interface exposes raw `IFile*` ownership conventions indirectly through implementation; `TraceOp::WRITE` exists but implementation only records/replays reads in this subset. Tests are in `trace_test.cpp`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/prefetch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/switch_file.cpp -->
## sources/cloud-native/overlaybd/src/switch_file.cpp

Purpose: implements a delegating `IFile` that initially reads from a source file and can switch to a local downloaded file, optionally treating local/remote data as tar and/or zfile. It is used to move reads from remote/cache paths to local committed data after background download.

Important types/functions: `try_open_zfile` checks `ZFile::is_zfile` and wraps zfiles with `zfile_open_ro`. `SwitchFile` implements `ISwitchFile` and forwards most `IFile` operations to `m_local_file` when present, otherwise `m_file`. `set_switch_file` opens a local path, wraps it as tar, then zfile if applicable, and installs it as the local target. `new_switch_file` detects zfile on the initial source and retries once.

Control flow: initial construction stores either source as local or remote. Forwarding uses the `FORWARD` macro. `pread` adds an audit threshold when serving local reads. Switching opens the local file, adapts to tar, tries zfile detection/open, and only updates `m_local_file` on success.

State/persistence: in-memory pointers to current remote and local files plus path string; destructor deletes both. Persistent state is the local file path supplied to `set_switch_file`. Dependencies are Photon filesystem/localfs, audit logging, tar adaptor, and zfile APIs.

Integration points: bridges downloaded commit files and zfile/tar formats into the image read path. Risks: no synchronization protects switching while other threads read; failed `try_open_zfile` after tar wrapping may delete only the current pointer path and needs careful ownership reasoning; forwarding writes to local when present even though local switched data may be read-only depending on adaptor. Test coverage is indirect through zfile and image service paths, not a dedicated switch-file test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/switch_file.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/switch_file.h -->
## sources/cloud-native/overlaybd/src/switch_file.h

Purpose: declares the switchable file abstraction.

Important APIs: `ISwitchFile` extends Photon `IFile` with `set_switch_file(const char *filepath)`. `new_switch_file(source, local=false, filepath=nullptr)` constructs an implementation, optionally marking the initial source as already local.

Control flow contract: callers use the returned object as an `IFile`; after a local commit/download finishes, they call `set_switch_file` to redirect operations. If initialized as local, operations start on the local file and pread audit applies.

State/persistence: no header state; implementation owns file pointers. Dependencies are Photon filesystem declarations.

Integration points: used by image/layer code that needs transparent source replacement. Risks: raw pointer factory and ownership semantics require callers to delete the returned object; no concurrency contract is documented for switching during active reads. There is no dedicated listed unit test.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/switch_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/test/CMakeLists.txt -->
## sources/cloud-native/overlaybd/src/test/CMakeLists.txt

Purpose: CMake wiring for OverlayBD image service, simple credential server, and trace/prefetch tests.

Important targets: `image_service_test` links GTest/GFlags/Photon/overlaybd libraries and includes Photon/RapidJSON. `simple_credsrv_test` links `overlaybd_image_lib`, Photon, rt/resolv/aio/pthread, and GTest. `trace_test` compiles `trace_test.cpp` plus `../tools/comm_func.cpp` and links GTest/GFlags/Photon/overlaybd libs. Each target is registered with CTest.

Control flow/state: build-only file, relying on `$GFLAGS`, `$GTEST`, `${PHOTON_INCLUDE_DIR}`, `${RAPIDJSON_INCLUDE_DIRS}`, `${EXECUTABLE_OUTPUT_PATH}`, and project libraries. Runtime tests create files under `/tmp`, bind localhost ports, and may download remote assets.

Integration points: validates image service behavior, credential HTTP loading, and dynamic prefetch. Risks: hardcoded ports can conflict; environment-variable library paths can be brittle; trace test depends on network downloads and external URLs. Test signal is broad integration coverage rather than isolated unit coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/test/image_service_test.cpp -->
## sources/cloud-native/overlaybd/src/test/image_service_test.cpp

Purpose: integration tests for image service acceleration/failover, metrics exporter, HTTP user-agent handling, dev-id registration, snapshot HTTP endpoint behavior, and snapshot creation.

Important helpers/tests: `new_server` starts a Photon TCP server. `AccelerateURL` checks p2p accelerate URL reachability. `failover` and `enableMetrics` exercise remote filesystem selection and metrics endpoint behavior. `http_client.user_agent` verifies Photon HTTP client user-agent propagation. `DevIDRegisterTest` sets up config files and image service state; `register_dev_id` checks image-file lookup and duplicate handling. `HTTPServerTest.http_server` probes `/snapshot` request validation. `CreateSnapshotTest` creates LSMT upper files and verifies snapshot data equivalence, sparse mode, and failure cases.

Control flow: tests write JSON configs into `/tmp/overlaybd`, create `ImageService`, create image files from config, perform reads/writes via aligned vectors, and delete resources. Several tests bind fixed local ports (`64208`, `64210`, `9862`, `9863`, `18731`) and rely on service startup side effects.

State/persistence: uses `/tmp/overlaybd`, `/var/log`, local LSMT data/index files, and localhost servers. Dependencies include Photon HTTP/socket/curl, GTest, image service implementation included directly, image file/LSMT, RapidJSON via build, and local filesystem.

Integration points: high-level regression suite for config parsing, p2p acceleration fallback, exporter behavior, service HTTP API, and snapshot layering. Risks: direct `system("echo ...")` JSON setup is shell-sensitive; hardcoded ports and `/opt/overlaybd/baselayers/ext4_64` fixture make tests environment-dependent; direct inclusion of `.cpp` can hide linkage issues. Test signal is valuable for end-to-end behavior but less hermetic.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/test/image_service_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/test/simple_credsrv_test.cpp -->
## sources/cloud-native/overlaybd/src/test/simple_credsrv_test.cpp

Purpose: tests loading registry credentials from an HTTP credential service, including timeout behavior.

Important types/functions: `SimpleAuthHandler` implements Photon `HTTPHandler`, returns a JSON body with `"success": true` and nested auth fields, deliberately sleeps before writing to exercise timeout handling. Test `auth.http_server` starts a local HTTP server on `127.0.0.1:19876/auth`, then calls `load_cred_from_http` with timeout values 1 and 2 and checks failure then success.

Control flow: the server is configured with keep-alive and content length, sleeps for one second, writes the body, and the client path parses credentials through image service/config code included directly via `../image_service.cpp`.

State/persistence: no file persistence in the active path; commented code references a local credential file. Dependencies include Photon HTTP/socket/thread, RapidJSON, GTest, localfs, and image service config functions.

Integration points: validates credential retrieval used by image service remote registry access. Risks: timing-based assertion may be flaky on slow systems; fixed port can conflict; returned JSON has blank username/password so it mostly validates request/parse success rather than credential values. Test signal covers timeout branch and success branch.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/test/simple_credsrv_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/test/trace_test.cpp -->
## sources/cloud-native/overlaybd/src/test/trace_test.cpp

Purpose: integration tests for dynamic prefetch trace generation and replay over ext4/tar and erofs images, verifying prefetched physical extents reconstruct expected file checksums.

Important components: `MockFile` wraps an `IFile` and supports `pread(nullptr, ...)` by reading into an internal buffer, matching zfile/prefetch no-copy read behavior. `download` and `download_erofs_img` fetch external fixtures. `case0` builds an ext4 image from a tarball but immediately returns, so it is disabled. `case1` downloads an erofs image, writes a file list, creates an erofs fs, runs `new_dynamic_prefetcher(...)->replay(dst)`, then checks file contents by reading fiemap physical extents from the image and hashing reconstructed output.

Control flow: active case downloads `alpine.img`, opens it through `MockFile`, writes list entries including `/etc/`, builds an erofs filesystem view, invokes dynamic prefetch, then for each expected file maps extents with `fiemap`, reads physical ranges from the raw image file, writes them to a temp check file, and compares SHA256.

State/persistence: uses `/tmp/trace_test`, downloaded images/tarballs, list/check files, and network access to GitHub URLs. Dependencies include Photon, extfs/erofs, gzip/tar helpers, prefetch implementation included directly, sha256file, and system `curl`/`wget`.

Integration points: directly validates `DynamicPrefetcher::generate_trace`, file-list parsing, erofs detection, fiemap extent handling, and replay worker reads. Risks: network and external fixture dependency, hardcoded checksums, disabled ext4 case, fixed workdir reuse, and worker completion relies on destructor/replay synchronization. Test signal is strong for erofs dynamic prefetch but weak for static trace record/replay.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/test/trace_test.cpp -->
