# Research Report: subset-b-000264

Scope: Overlaybd tar extraction/adaptation, EROFS tar tests and stress harnesses, zfile compression, CRC32C acceleration, and LZ4 QAT shim files.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_simple.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_simple.cpp

Purpose: GoogleTest coverage for EROFS tar ingestion, tar metadata replay, PAX path handling, the internal EROFS sector cache helpers, and clean versus incremental layer image construction.

Important APIs/types/functions: `ErofsTest` provides gzip inflation, Photon local/sub filesystem setup, download helpers, LSMT warp-file device creation, and blockwise verification. `ErofsPax` builds a PAX fixture and hashes the mounted EROFS tree traversal. The local `ErofsCache` declaration mirrors the internal liberofs cache contract used by `erofs_read_photon_file` and `erofs_write_photon_file`. `ErofsCacheTest` checks sector cache write/read/flush behavior. `ErofsTestCleanIncremental` provides `traverse_fs` and drives two embedded layer tarballs through clean and incremental `LibErofs::extract_tar` modes.

Control flow: tests inflate embedded gzip byte arrays into temporary tar files, wrap the tar source in an LSMT virtual device, build EROFS images with `LibErofs`, optionally dump tar headers with `UnTar::dump_tar_headers`, rebuild from metadata, mount through `create_erofs_fs`, and compare either device bytes or deterministic SHA256 traversal output. The cache test writes overlapping aligned and unaligned sectors, flushes, then reads through both cache and backing Photon file.

State and persistence: all test state is under `/tmp/tar_test`, `/tmp/pax_test`, `/tmp/erofs_cache_test`, or `/tmp/erofs_clean_incrementtal`, plus temporary `.idx`, `.meta`, image, tar, content, and checksum files. Image persistence flows through LSMT warp files and Photon local files. Cleanup is attempted in fixture teardown, but some conditions appear inverted in the clean/incremental fixture, so stale files may survive failed or skipped cases.

Dependencies/integration: depends on zlib, gtest, Photon FS, Photon extfs, gzindex/gzip adapters, LSMT warp/stack files, `LibErofs`, `create_erofs_fs`, `UnTar`, `new_sha256_file`, and `tar_file.cpp` included directly for the tar adaptor. It is an integration test rather than a pure unit test.

Risks: embedded fixture arrays make failures hard to diagnose without recreating the tar contents. Several tests use large sparse offsets and backing files, so filesystem behavior matters. Direct inclusion of `tar_file.cpp` bypasses normal library boundaries. The clean/incremental teardown uses `access(...) != 0` before unlink/rmdir in several places, which is likely wrong and can hide cleanup bugs. Hash-based traversal tests are sensitive to directory iteration ordering.

Test signals: covers tar metadata equivalence, PAX long path traversal identity, EROFS cache coherency under one-sector capacity, offsets beyond 2^32, and expected final tree/content for clean plus incremental layers including whiteout behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_simple.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_stress.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_stress.cpp

Purpose: randomized stress test suite for multi-layer EROFS construction from tar layers. It validates metadata, xattrs, content hashes, overwrite semantics, same-name upper/lower entries, whiteouts, and delete-then-recreate scenarios.

Important APIs/types/functions: `StressInterImpl` implements `StressGenInter` with random content generation, xattr creation/listing, mode/ownership/mtime generation, directory metadata, stat capture, content hashing, and name generation. `StressCase001` through `StressCase009` specialize the generator for specific coverage goals. `TEST(ErofsStressTest, TC001..TC009)` instantiates each case with different layer counts and tree sizes.

Control flow: each test seeds `rand()` with current time, constructs a case rooted at `./erofs_stress_NNN`, calls `StressBase::run`, then deletes the case. The base runner builds one tar layer at a time, updates an in-memory expected tree, converts layers into stacked LSMT images, extracts with `LibErofs`, mounts with `create_erofs_fs`, and asks the generator to reconstruct observed metadata/content from the mounted filesystem for comparison.

State and persistence: test data is persisted in relative work directories such as `./erofs_stress_006`, with generated layer tar files plus `.idx` and `.meta` LSMT sidecars. Successful runs remove the directory through `StressBase::run`; failures leave artifacts for diagnosis. Randomized names, xattrs, file contents, uid/gid, and mtimes are captured into `StressNode` records for later verification.

Dependencies/integration: integrates gtest, Photon runtime, Photon FS/xattr APIs, GNU tar command-line behavior via the base class, LSMT warp/stack files, `LibErofs`, and EROFS Photon filesystem mounting. It depends heavily on filesystem xattr support and external `tar` with `--xattrs`.

Risks: tests are nondeterministic because they seed from wall time and use `random_device`, so reproducing failures requires captured artifacts. Some comments do not match actual layer sizes, for example TC001 describes 50 files but returns small counts. The suite can be expensive: TC009 generates 1000 directory nodes per layer. The helper macro hides unimplemented metadata paths, so each case only validates the fields it explicitly enables.

Test signals: TC001 checks basic tree integrity, TC002 file content, TC003 file and directory xattrs, TC004 mode, TC005 uid/gid/mtime through stat, TC006 combined metadata/content, TC007 same-name replacement, TC008 whiteouts, and TC009 deletion followed by name reuse.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_stress.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_stress_base.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_stress_base.cpp

Purpose: shared stress-test engine for generating tar layers, maintaining an expected in-memory overlay tree, building stacked EROFS images, and verifying mounted EROFS output against the model.

Important APIs/types/functions: `get_randomstr`, `is_substring`, and `str_n_equal` support randomized generation and path checks. `StressFsTree::add_node`, `get_same_name`, and `get_type` encode overlay semantics for replacement and whiteout deletion. `build_layer_tree` creates a random directory hierarchy from per-directory file counts. `append_tar` shells out to GNU tar and tar concatenation. `StressBase::create_layer`, `mkfs`, `verify`, and `run` drive the full lifecycle.

Control flow: `run` rejects pre-existing workdirs, adds root to the expected tree, calls `create_layer` for each layer, builds stacked image state in `mkfs`, mounts it, and calls `verify`. `create_layer` creates a randomized host tree beneath a random prefix, calls virtual generator hooks for metadata/content, appends each object to a tar, and updates `StressFsTree`; `.wh.` names are modeled as deletion operations. `mkfs` wraps each tar in an LSMT virtual device, stacks upper layers on lower layers, and invokes `LibErofs::extract_tar`. `verify` breadth-first traverses the EROFS filesystem, reconstructs `StressNode` values via virtual hooks, and removes matching nodes from the expected tree.

State and persistence: state is split between host workdirs, layer tar files, LSMT `.idx`/`.meta` files, stacked image mappings, and in-memory `StressFsTree`. `append_tar` persists each generated object immediately into a layer tar. On success `run` removes the workdir; on error it leaves the tree and generated tars in place.

Dependencies/integration: uses Photon local filesystem, Photon directory iteration, Photon xattr-capable files supplied by case classes, `LibErofs`, `create_erofs_fs`, LSMT warp and stack APIs, and external GNU tar commands with `--xattrs --xattrs-include='*'`.

Risks: command strings are built by concatenation without shell escaping, but generated names are alphanumeric and prefixes are fixed by tests. `StressFsTree::add_node` erases map entries without deleting the old `StressNode`, so long stress runs can leak memory. Verification uses directory iteration order but tree comparison itself is path keyed. The random layer tree builder deletes `LayerNode` objects during traversal, but nested ownership is manual and fragile.

Test signals: this file is exercised indirectly by all nine stress cases and is the core signal for overlay replacement, directory/file type conflicts, whiteout deletion, xattr preservation, metadata preservation, and content hash correctness.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_stress_base.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_stress_base.h -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_stress_base.h

Purpose: declarations for the EROFS stress-test model, generator interface, host-file wrapper, and base runner.

Important APIs/types/functions: constants define image size, sector size, maximum generated name lengths, and `.wh.` prefix. `NODE_TYPE` distinguishes directory, regular file, and whiteout model nodes. `StressNode` stores path, xattrs, content hash, type, and `stat`; `equal` performs detailed comparisons. `StressHostFile` owns a Photon file used during host generation. `in_mem_meta` carries generated uid/gid/mtime data. `StressGenInter` is the virtual contract for generating and verifying per-file/per-directory metadata and layout. `StressFsTree` owns expected nodes and exposes add/query/name/type helpers. `StressBase` owns the test workdir, host filesystem, layer count, expected tree, and `run`.

Control flow: derived stress cases implement `StressGenInter`; `StressBase` invokes those hooks while building layers and while verifying mounted EROFS files. `StressFsTree::query_delete_node` validates an observed node and removes it, making an empty tree the final success condition.

State and persistence: the header models in-memory expected state only; persistence is performed by `erofs_stress_base.cpp` through host files, tar layers, and LSMT sidecars. `StressHostFile` owns an open Photon file and closes/deletes it in its destructor.

Dependencies/integration: depends on C++ STL maps/strings, Photon filesystem/localfs APIs, Photon logging, gtest, LSMT file interfaces, and EROFS FS declarations. It is consumed by both the shared implementation and `erofs_stress.cpp`.

Risks: `StressHostFile::~StressHostFile` assumes `file` is non-null and will dereference null if construction failed. `StressNode(StressNode*)` does not copy `type` or `node_stat`, which would be hazardous if used for deep copies. `StressNode::equal` compares mtimes exactly, so host tar and EROFS extraction must preserve second-level times precisely. The `is_emtry` typo is part of the public helper interface.

Test signals: no standalone tests; all stress test coverage depends on the correctness of this model and interface.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_stress_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/header.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/header.cpp

Purpose: tar header parsing, path normalization, GNU long name/link handling, PAX local/global header parsing, size/path/link overrides, and tar header checksum/mode helpers for `TarCore`.

Important APIs/types/functions: `clean_name` normalizes path strings in place. `remove_last_slash` strips a trailing slash from a `string_view`. `TarCore::get_pathname`, `get_linkname`, and `get_size` apply PAX/GNU overrides before falling back to POSIX header fields. `TarCore::read_header_internal`, `read_sepcial_file`, and `read_header` advance through tar records. `PaxHeader::read_pax` and `parse_pax_records` decode PAX key/value lines. `TarHeader::get_mode`, `get_uid`, `get_gid`, `crc_calc`, and `signed_crc_calc` expose decoded metadata.

Control flow: `read_header` resets prior GNU/PAX state, reads a 512-byte header, treats two zero blocks as EOF unless ignored, validates magic/version/checksum according to option flags, and loops over GNU long name/link and PAX headers until it reaches a real file header. Special header payloads are read in whole 512-byte blocks and optionally copied to a dump file. PAX parsing stores all records and applies supported keys `size`, `path`, and `linkpath`; xattr keys are recognized but left as records for extraction.

State and persistence: `TarCore` owns current `TarHeader`, optional `PaxHeader`, and cached pathname/linkname buffers. When `dump` is supplied, regular file data offsets are temporarily stored in the header's `devmajor` bytes before writing the header to a metadata stream. This metadata stream is later consumed by meta-only extraction paths.

Dependencies/integration: used by `UnTar` extraction, tar metadata dump/replay, `TarFile` adaptor header detection, and EROFS tar ingestion. It depends on Photon `IFile`, path/logging utilities, POSIX tar constants, and option flags from `libtar.h`.

Risks: `read_sepcial_file` returns `int` but stores `size_t` values, and callers compare `size_t sz < 0`, which is ineffective. PAX support ignores many keys except size/path/linkpath and xattr records. PAX `strdup(rec.second.data())` assumes null termination of `std::string::data()`. The metadata dump's reuse of `devmajor` for offsets is non-obvious and corrupts normal device fields in the dumped header stream by design.

Test signals: `tar/test/test.cpp` covers `clean_name` and tar metadata dumping. `erofs_simple.cpp` covers PAX path behavior and EROFS metadata rebuilds.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/header.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/libtar.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/libtar.cpp

Purpose: implementation of `UnTar` extraction into a Photon filesystem, including permissions, xattrs, regular file data, hardlinks, symlinks, directories, special nodes, and turboOCI metadata-only mapping.

Important APIs/types/functions: `UnTar::set_file_perms`, `dump_tar_headers`, `extract_all`, `extract_file`, `extract_regfile_meta_only`, `extract_regfile`, `extract_hardlink`, `extract_symlink`, `extract_dir`, and `extract_block_char_fifo`.

Control flow: `extract_all` loops through `read_header`, normalizes names, skips root, dispatches to `extract_file`, and applies deferred directory mtimes after all entries. `extract_file` ensures parent directories, converts OCI whiteouts, handles overwrite removal, dispatches by tar type, applies permissions/xattrs/time, defers directory mtime, and tracks unpacked paths. `dump_tar_headers` writes file headers and skips regular file payloads. Regular extraction streams payload blocks from the source tar into an output file while respecting tar block padding. Meta-only extraction creates sparse file extents, reads fiemap data, and writes remote mappings to the base LSMT file instead of copying payload bytes.

State and persistence: extraction mutates the target Photon filesystem. `unpackedPaths` prevents whiteout/removal logic from deleting entries already created by the current tar stream. `dirs` stores directory mtime values for delayed restoration. Meta-only mode persists file extents through `LSMT::RemoteMapping` ioctl calls into `fs_base_file`.

Dependencies/integration: depends on `TarCore` parsing, Photon FS and xattr APIs, Photon fiemap, LSMT remote mapping ioctls, POSIX ownership/time/mode semantics, and whiteout helpers in `whiteout.cpp`.

Risks: exact ownership and device-node restoration depends on privileges and `TAR_CHECK_EUID`. Xattr failures are selectively ignored only for unsupported or invalid user namespace cases. Hardlink targets are trusted after path normalization. Meta-only mapping relies on fiemap, fallocate, and the overloaded `header.devmajor` offset when replaying tar-index streams.

Test signals: tar integration tests cover full untar, metadata-only replay equivalence, gzip stream tar metadata, and generated tar header adaptor behavior; EROFS tests reuse `dump_tar_headers` for image equivalence.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/libtar.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/libtar.h -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/libtar.h

Purpose: public declarations and constants for Overlaybd's libtar-derived parser and extractor.

Important APIs/types/functions: tar constants define block size, name/prefix lengths, filesystem block size, GNU long header types, PAX keys, and option flags. `TarHeader` maps the POSIX ustar header and exposes metadata/checksum helpers. `PaxHeader` owns parsed PAX overrides and raw records. `TarCore` wraps a source `IFile`, current header, parser options, PAX state, and pathname/linkname helpers. `UnTar` extends `TarCore` with extraction into a target `IFileSystem`, optional base file, meta-only mode, tar-index replay mode, xattr filesystem pointer, unpacked path set, and deferred directory time list.

Control flow: callers instantiate `UnTar` or `TarCore`, call `read_header` to advance, inspect `header` and helper getters, or call `extract_all` / `dump_tar_headers`. `UnTar` private methods implement per-type extraction and whiteout handling.

State and persistence: `TarCore` owns transient parser state for a single stream. `UnTar` owns mutable extraction bookkeeping and writes persistent filesystem objects or LSMT mappings. PAX objects free allocated buffers in destructors; `TarHeader` long name/link pointers are freed by `TarCore` reset/destruction.

Dependencies/integration: included by `header.cpp`, `libtar.cpp`, `whiteout.cpp`, `tar_file.cpp`, tar tests, and EROFS code paths. Depends on Photon `IFile`, `IFileSystem`, `IFileSystemXAttr`, fiemap, tar/POSIX headers, and STL containers.

Risks: helper functions are `static` in the header, so each translation unit gets its own copy. The `libtar_version` variable is defined in the header, which can create multiple definitions if included in multiple linked objects without compiler/linker tolerance. Raw owning pointers and manual allocation require careful reset ordering. Macros for file type detection combine tar typeflag and mode in ways that may classify unusual malformed headers.

Test signals: exercised through tar unit/integration tests and EROFS tests; no direct header-only tests beyond compile and consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/libtar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/tar_file.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/tar_file.cpp

Purpose: Photon file/filesystem adaptor for Overlaybd blob files that are physically wrapped in a minimal tar header/trailer but should be exposed to callers as the inner payload file.

Important APIs/types/functions: `TarFile` derives from `ForwardFile_Ownership` and translates all offsets by `base_offset`. `TarFs` derives from `ForwardFS_Ownership` and wraps opened files. Public functions are `is_tar_file`, `new_tar_file_adaptor`, and `new_tar_fs_adaptor`; internal helpers include `new_tar_file`, `open_tar_file`, `strlcpy`, `TarFile::read_header`, `mark_new_tar`, `write_header_trailer`, `is_new_tar`, and `format_pax_record`.

Control flow: `TarFs::open` opens the underlying file and calls `open_tar`. Empty files opened for writing are initialized as new tar blobs with a temporary three-block header. Existing tar files are detected by ustar magic/version/checksum and wrapped. `TarFile::read_header` parses the tar header, records payload size, sets `base_offset` to one block or three blocks if PAX is present, and seeks to payload start. Reads/writes/seeks/fstat/fallocate/fadvise are translated by `base_offset`. On close, a new tar blob is finalized with PAX size record, regular file header, and two zero trailer blocks.

State and persistence: new files are first marked with fake magic/version values and finalized at close. Finalization writes the header at offset zero and trailers at aligned end-of-file. Existing tar files report logical payload size; new tar files report backing size minus header. The underlying `IFile` is owned and closed by the adaptor.

Dependencies/integration: depends on Photon forward file/filesystem wrappers, `TarCore` and `TarHeader` helpers from libtar, POSIX passwd/group lookup for header metadata, and Overlaybd remote blob consumers that need transparent tar skipping.

Risks: `flags & O_RDONLY` is not a reliable read-only test because `O_RDONLY` is zero, so `TarFs::open` may treat read-only opens as write-like and then inspect file size. `TarFile::close` can write headers multiple times if called repeatedly through destructor and user code. `read_header` assumes CachedFile lseek limitations are acceptable. The QED of PAX base offset is hard-coded to three blocks, matching this writer but not arbitrary PAX tars.

Test signals: `tar_header_check` writes through the adaptor, confirms the backing file is a tar, reopens through `new_tar_file_adaptor`, verifies fstat size, pread content, read after seek, and logical SEEK_END behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/tar_file.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/tar_file.h -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/tar_file.h

Purpose: small public interface for the tar payload adaptor used by Overlaybd remote blob handling.

Important APIs/types/functions: `new_tar_fs_adaptor(photon::fs::IFileSystem*)` returns a filesystem wrapper that auto-wraps opened tar blobs. `is_tar_file(photon::fs::IFile*)` detects a tar header at the beginning of a file. `new_tar_file_adaptor(photon::fs::IFile*)` returns either a tar-offset adaptor or the original file when not tar-wrapped.

Control flow: callers include this header and use the factories; implementation logic lives in `tar_file.cpp`.

State and persistence: the header itself has no state. The factories may produce adaptors that mutate newly created files by writing tar headers/trailers on close.

Dependencies/integration: depends only on Photon filesystem declarations in the header and is used by tar/EROFS tests and remote blob code paths that need to skip tar wrappers.

Risks: comments emphasize this is not a complete tar filesystem implementation; it is for the single-blob tar wrapper format only. Consumers must not expect directory enumeration or multi-entry tar archive semantics.

Test signals: covered by `tar/test/test.cpp::tar_header_check` and indirectly by EROFS tests that include the implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/tar_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/test/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/test/CMakeLists.txt

Purpose: CMake definition for the tar integration test executable.

Important APIs/types/functions: configures GFlags/GTest include and library directories from environment variables, creates `untar_test` from `test.cpp`, includes Photon headers, links gtest, pthread, `photon_static`, `tar_lib`, `lsmt_lib`, `gzip_lib`, `gzindex_lib`, and `checksum_lib`, and registers the test with CTest.

Control flow: build-time only. `add_test` runs `${EXECUTABLE_OUTPUT_PATH}/untar_test`.

State and persistence: no runtime state in the build file; the executable itself creates `/tmp/tar_test` artifacts during tests.

Dependencies/integration: assumes `$GFLAGS`, `$GTEST`, `${PHOTON_INCLUDE_DIR}`, and linked Overlaybd static libraries are configured by the parent build. It integrates tar tests into `BUILD_TESTING` parent flows.

Risks: environment-variable include/link paths can break reproducibility if not set. Direct linking with several static libraries means transitive dependencies must already be ordered correctly by the parent build.

Test signals: the existence of this file means tar tests are discoverable by CTest as `untar_test`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/test/test.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/test/test.cpp

Purpose: integration tests for `UnTar`, tar metadata-only extraction, gzip stream indexing, tar wrapper adaptation, and path normalization.

Important APIs/types/functions: `TarTest` provides Photon FS setup, network download helpers, file writing, LSMT device creation, and bytewise device verification. Tests are `untar`, `tar_meta`, `stream`, `gz_tarmeta_e2e`, `tar_header_check`, and `CleanNameTest.clean_name`.

Control flow: tests download or stream public tar/gzip fixtures, use `UnTar::extract_all` for full extraction, use `UnTar::dump_tar_headers` to create tar metadata streams, replay metadata into LSMT-backed extfs images, compare resulting virtual devices, and check deterministic SHA256 of metadata/index outputs. `tar_header_check` writes a generated payload through `new_tar_fs_adaptor`, closes it to finalize tar headers, detects it with `is_tar_file`, and reopens it logically.

State and persistence: uses `/tmp/tar_test`, creates downloaded archives, generated `.idx`, `.meta`, `.tar.meta`, extfs images, and checksum inputs. Fixture teardown unlinks only files listed in `filelist`; downloaded files and rootfs may remain.

Dependencies/integration: depends on gtest, Photon runtime/local/sub/ext filesystems, gzip/gzindex adapters, LSMT, libtar, tar_file implementation included directly, SHA256 file helper, and network access for several tests.

Risks: network downloads make tests flaky and slow outside controlled CI caches. The `download_decomp` output name is fixed as `latest.tar`, so tests share mutable state. Direct inclusion of `tar_file.cpp` risks duplicate definitions if linked differently. SHA256 expectations are brittle if upstream fixture contents change.

Test signals: strong end-to-end signal for tar extraction, turboOCI metadata equivalence, gzip stream index stability, single-file tar wrapper logic, and `clean_name` behavior for redundant separators, dot, dot-dot, root, empty, and trailing slash cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/test/test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/whiteout.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/tar/whiteout.cpp

Purpose: OCI whiteout and directory helper logic for `UnTar` extraction.

Important APIs/types/functions: constants define `.wh.`, `.wh..wh.`, `.wh..wh..opq`, and the PAX xattr prefix string. `UnTar::mkdir_hier` ensures parent directory existence. `UnTar::remove_all` recursively removes filesystem entries while respecting paths already unpacked in the current tar. `UnTar::convert_whiteout` maps OCI whiteout entries to target removal operations.

Control flow: `mkdir_hier` strips trailing slash, returns success for existing directories, fails for existing non-directories, and otherwise calls Photon recursive mkdir. `convert_whiteout` splits filename into directory/base; opaque directory markers remove children of the target directory without removing the directory itself, while `.wh.<name>` removes the target file or directory and returns a consumed-whiteout signal. `remove_all` lstat's the path, unlinks files if not unpacked, recursively traverses directories, closes the iterator, and optionally removes the directory.

State and persistence: mutates the extraction target filesystem by deleting files/directories. Reads `unpackedPaths` from `UnTar` to avoid deleting objects already produced by the current archive stream.

Dependencies/integration: called from `UnTar::extract_file` before type dispatch. Depends on Photon `Path`, directory iteration, recursive mkdir, logging, and OCI layer whiteout naming rules.

Risks: recursive removal ignores return values from nested `remove_all` calls, so partial deletion failures can be lost. Opaque directory handling requires the directory to already exist. The code assumes `basename().substr(0, whiteoutPrefix.size())` is safe for short names, which is valid for `std::string` but still easy to misread.

Test signals: EROFS stress TC008 and TC009 exercise whiteout deletion and delete-then-recreate behavior; clean/incremental simple tests include `.wh.dir2` semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/tar/whiteout.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/zfile/CMakeLists.txt

Purpose: build configuration for zfile compression, CRC32C, optional acceleration libraries, and zfile tests.

Important APIs/types/functions: globs zfile C++ sources, LZ4 C sources, and `crc32/crc32c.cpp`; creates static `crc32_lib` and `zfile_lib`; configures C++ standard levels; adds CPU-specific CRC flags; conditionally adds thirdparty dependencies and definitions for `ENABLE_DSA`, `ENABLE_ISAL`, and `ENABLE_QAT`; adds `test` subdirectory when `BUILD_TESTING`.

Control flow: at configure/build time it compiles CRC with SSE4.2/CRC32 flags on x86_64 or native/generic CRC flags on other architectures, links DSA/ISAL support when enabled, then builds zfile with Photon, CRC32, zstd, and LZ4/QAT sources.

State and persistence: no runtime state. Build outputs are static libraries and optional thirdparty artifacts under configured output paths.

Dependencies/integration: depends on Photon include/library variables, `${LIBZSTD}`, optional libpci, dml, dl, ISAL, and pthread. `zfile_lib` is the compression backend for zfile format code outside this subset.

Risks: `file(GLOB ...)` can miss source changes until CMake reconfigure. Setting `CMAKE_CXX_STANDARD` to 17 for CRC and later 14 globally may surprise downstream targets. Optional acceleration flags affect ABI/behavior and require matching thirdparty libraries and CPU features.

Test signals: build enables zfile tests through `add_subdirectory(test)` when testing is on; CRC/compressor behavior is also indirectly covered by zfile format tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/compressor.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/zfile/compressor.cpp

Purpose: implementation of zfile compression/decompression backends for LZ4 and ZSTD, with optional QAT batch path for LZ4.

Important APIs/types/functions: `BaseCompressor` implements common buffer layout, `compress`, `decompress`, `compress_batch`, and `decompress_batch`. `LZ4Compressor` implements LZ4 init, optional QAT detection/init, batch size, compression, and decompression. `Compressor_zstd` implements ZSTD compression/decompression. `create_compressor` is the exported factory.

Control flow: factory switches on `CompressOptions::algo`, allocates a compressor, and calls `init`. Base init records block size and resizes per-batch pointer vectors. Batch methods divide the destination buffer into equal slots, set source/destination pointer vectors, validate per-slot capacity, and call algorithm-specific `do_*` methods. LZ4 defaults to `LZ4_compress_default` / `LZ4_decompress_safe`; ZSTD uses `ZSTD_compress` at level 3 and `ZSTD_decompress`.

State and persistence: compressor instances retain block size, maximum destination size, per-batch pointer vectors, and optional QAT state. They do not persist compressed data themselves; callers provide buffers and store results in zfile objects.

Dependencies/integration: used by zfile read/write code through `ICompressor`. Depends on bundled LZ4, libzstd, Photon logging, Photon filesystem declarations, and optional libpci/QAT shim. Build flags are controlled by zfile CMake.

Risks: the `ENABLE_QAT` LZ4 path appears stale: it references `raw_data` and `n` symbols that are not present in the current function scope, so QAT builds may fail. ZSTD `do_decompress` appears to pass `uncompressed_data` as input and `compressed_data` as output, reversed from the base pointer setup, which would break batch ZSTD decompression. Capacity checks assume equal destination slots and require `dst_buffer_capacity / n >= max_dst_size` even when chunks vary. `CompressArgs::workers` is not used here.

Test signals: zfile tests outside this subset should validate round trips. This subset's CMake indicates zfile tests are enabled under `BUILD_TESTING`; QAT and batch ZSTD paths need targeted tests because normal single-block LZ4/ZSTD paths may not cover them.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/compressor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/compressor.h -->
# sources/cloud-native/overlaybd/src/overlaybd/zfile/compressor.h

Purpose: public compression interface and option layout for zfile blocks.

Important APIs/types/functions: `CompressOptions` defines algorithm IDs `MINI_LZO`, `LZ4`, `ZSTD`, default block size, algorithm, level, dictionary flags, reserved fields, dictionary size, verify flag, and padding; its size is asserted to 24 bytes. `CompressArgs` carries optional dictionary file/buffer, options, header-overwrite flag, and worker count. `ICompressor` defines single and batch compress/decompress APIs plus `nbatch`. `create_compressor` is an `extern "C"` factory.

Control flow: callers construct options/args, request a compressor from `create_compressor`, then call single-block or batch APIs. The header does not implement behavior.

State and persistence: `CompressOptions` is explicitly described as written into files, so its field order and size are persistent format data. `CompressArgs` is transient runtime configuration. `ICompressor` implementations hold runtime buffers/state.

Dependencies/integration: used by `compressor.cpp` and zfile format implementation. References Photon `IFile` only by forward declaration to avoid pulling full filesystem headers into consumers.

Risks: changing `CompressOptions` layout breaks stored zfile headers. Dictionary fields are present but not substantively implemented in the compressor body in this subset. `MINI_LZO` remains an option ID but factory support is absent. Ownership of raw `dict_buf` is transferred into `unique_ptr`, so callers must not free it afterward.

Test signals: compile-time size assertion is the direct guard; runtime round-trip tests should cover option combinations, algorithm IDs, and header compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/compressor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/crc32/crc32c.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/zfile/crc32/crc32c.cpp

Purpose: CRC32C implementation with software fallback, hardware CPU instructions, and optional Intel DSA or ISA-L accelerated paths.

Important APIs/types/functions: exported functions are `crc32c`, `crc32c_extend`, string overloads, and testing helpers `crc32c_slow` / `crc32c_fast`. Internal implementations include `crc32c_hw`, `singletable_crc32c`, slicing-by-8 table logic via `crc32c_sb8_64_bit` and `multitable_crc32c`, `crc32c_sw`, optional `crc32c_dml`, optional `crc32c_isal`, `check_dsa`, and constructor/destructor hooks `crc_init` / `crc_deinit`.

Control flow: at library load, `crc_init` selects the global function pointer. On x86 with SSE4.2 it optionally prefers DSA, then ISA-L AVX512, then SSE4.2 instructions, otherwise software; on ARM with CRC32 it uses mapped builtins; other platforms use software. Public calls dispatch through `crc32c_func` with an initial or caller-supplied CRC seed.

State and persistence: the only state is process-global `crc32c_func`, initialized once by constructor. CRC values are used by zfile integrity paths but this file does not persist data directly.

Dependencies/integration: linked as `crc32_lib`, consumed by zfile. Depends on compiler intrinsics, Photon logging, optional DML high-level API, optional libpci device probing, and optional ISA-L `crc32_iscsi`.

Risks: public functions assume `crc_init` ran and `crc32c_func` is non-null. `multitable_crc32c` computes `to_even_word` as 4 when already aligned, so short lengths under 4 are routed away but other edge cases depend on table helper assumptions. Optional DSA detection scans PCI devices at constructor time, which can be slow or permission-sensitive. Testing helper `crc32c_fast` calls hardware instructions unconditionally, so it is only safe on builds/CPUs with the required feature.

Test signals: testing namespace exposes slow and fast implementations for cross-checking. Build flags in CMake add architecture options and optional accelerator definitions; zfile tests should validate checksums across block boundaries and extension seeds.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/crc32/crc32c.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/crc32/crc32c.h -->
# sources/cloud-native/overlaybd/src/overlaybd/zfile/crc32/crc32c.h

Purpose: public CRC32C API declarations for zfile and tests.

Important APIs/types/functions: namespace `crc32` declares `crc32c(const void*, size_t)`, `crc32c(const std::string&)`, `crc32c_extend(const void*, size_t, uint32_t)`, and `crc32c_extend(const std::string&, uint32_t)`. Nested `crc32::testing` declares `crc32c_slow` and `crc32c_fast`.

Control flow: no runtime logic in the header. Consumers call the functions implemented in `crc32c.cpp`.

State and persistence: no header state. Returned CRC values are used by zfile integrity checks and can become persistent checksums in file formats.

Dependencies/integration: depends on `stdint.h` and `std::string`. Included by `crc32c.cpp` and zfile code needing checksums.

Risks: the testing fast function is exposed in the public header and can be misused on unsupported hardware if called directly. ABI depends on namespace and overload signatures remaining stable for linked consumers.

Test signals: the testing declarations allow direct slow/fast comparison in unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/crc32/crc32c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4-qat.c -->
# sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4-qat.c

Purpose: placeholder QAT-flavored LZ4 batch API implementation that currently delegates to normal LZ4 software routines.

Important APIs/types/functions: global `gDebugParam`, `qat_init`, `qat_uninit`, `LZ4_compress_qat`, and `LZ4_decompress_qat`.

Control flow: init/uninit return success without configuring state. Compress/decompress loop over `n` chunks and call `LZ4_compress_default` or `LZ4_decompress_safe` for each chunk, storing per-chunk output lengths, then return zero status.

State and persistence: no meaningful QAT state is stored; `LZ4_qat_param` is opaque and empty in the header. The functions write caller-provided destination buffers but do not persist data.

Dependencies/integration: compiled into `zfile_lib` with the bundled LZ4 sources. Called by `LZ4Compressor` only when `ENABLE_QAT` and QAT detection are active.

Risks: destination capacity is hard-coded as 4096 for every chunk instead of receiving a capacity parameter, so it is only safe when caller slot size is exactly 4096 and compressed output fits. Return value is always zero even if per-chunk LZ4 calls fail, leaving errors visible only through chunk lengths. It is not a real QAT implementation despite QAT naming.

Test signals: no direct tests in this subset. QAT-enabled compression tests should verify chunk lengths, failure propagation, and non-4096 block sizes.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4-qat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4-qat.h -->
# sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4-qat.h

Purpose: C ABI declaration for QAT-flavored LZ4 batch compression/decompression hooks, modeled after LZ4 public API visibility conventions.

Important APIs/types/functions: defines `LZ4LIB_VISIBILITY`, `LZ4LIB_API`, opaque typedef `LZ4_qat_param`, empty struct `_LZ4_qat_param`, `LZ4_compress_qat`, `LZ4_decompress_qat`, `qat_init`, and `qat_uninit`.

Control flow: header only. C and C++ consumers call the functions implemented in `lz4-qat.c`.

State and persistence: the QAT parameter type is currently empty, so no accelerator state can be represented through the public type. Persistent compressed data format is still normal LZ4 block data produced by the implementation.

Dependencies/integration: included by `compressor.cpp` under `ENABLE_QAT` and by `lz4-qat.c`. Uses `extern "C"` for C++ compatibility and includes standard `stddef.h`/`stdio.h`.

Risks: API names imply hardware acceleration, but the paired implementation is a software stub. There is no destination capacity argument, forcing the implementation to make assumptions. The empty struct limits future QAT state without ABI changes if callers allocate it by value or size.

Test signals: no standalone tests; meaningful coverage requires building with `ENABLE_QAT` and exercising `LZ4Compressor::compress_batch` / `decompress_batch`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4-qat.h -->
