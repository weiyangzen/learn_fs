# subset-b-000269 research

Grouped research report for the requested OverlayBD tool files, overlayfs-tools utilities, and SOCI Snapshotter repository automation/benchmark files. Each section preserves the original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/tools/CMakeLists.txt

Purpose: defines the OverlayBD command-line tool build targets for creating, applying, committing, merging, and zfile-processing OverlayBD layers.

Important APIs/types/functions: creates executables `overlaybd-commit`, `overlaybd-merge`, `overlaybd-create`, `overlaybd-zfile`, `overlaybd-apply`, and `turboOCI-apply`; creates `checksum_lib` from `sha256file.cpp`; attaches Photon include paths and links `photon_static`, `overlaybd_lib`, `overlaybd_image_lib`, and `checksum_lib` where needed.

Control flow: each CLI source is mapped directly to one executable target. Apply and TurboOCI tools receive RapidJSON includes, image-service linkage, and install RPATH. `checksum_lib` is linked only into `overlaybd-apply` because that tool can validate an uncompressed layer checksum while streaming extraction.

State and persistence: no runtime state; it controls install persistence by placing tool binaries under `/opt/overlaybd/bin` and setting RPATH to `/opt/overlaybd/lib` for binaries that load image libraries.

Dependencies/integration: integrates the tools with the broader OverlayBD CMake build, Photon runtime, image service library, zfile/tar/LSMT code, and optional checksum library.

Risks: target linkage is manually maintained, so missing library dependencies will surface as link or runtime loader failures. `overlaybd-zfile` and `overlaybd-commit` do not get install RPATH here, unlike image-service tools.

Test signals: build success verifies target composition. Runtime coverage is expected through the individual tool tests or integration scripts that call installed binaries.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/comm_func.cpp -->
# sources/cloud-native/overlaybd/src/tools/comm_func.cpp

Purpose: implements shared helpers used by OverlayBD CLI tools for opening files, creating image-service filesystems, wrapping ext4/EROFS, registry uploading, and parsing config/dev-id arguments.

Important APIs/types/functions: `open_file`, `create_overlaybd`, `create_ext4fs`, `is_erofs_fs`, `create_erofs_fs`, `create_uploader`, and `parse_config_and_dev_id`. The functions work with Photon `IFile`, `IFileSystem`, `ImageService`, zfile compression args, registryfs credentials, extfs, subfs, and EROFS helpers.

Control flow: helpers mostly fail fast: a failed open, image-service create, image-file create, mkfs, extfs/subfs creation, credential load, or uploader setup prints diagnostics and exits. `create_ext4fs` optionally formats the image file, creates an ext filesystem, then returns a subfs rooted at the requested path. `create_uploader` loads credentials for an upload URL and wraps a source file in a registry uploader.

State and persistence: mutates underlying image files when `mkfs` is requested and writes upload state through registryfs. No long-lived global state is kept.

Dependencies/integration: included by `overlaybd-apply`, `overlaybd-merge`, `turboOCI-apply`, and other tools; integrates image-service JSON configs with filesystem adaptors and registry uploads.

Risks: helpers call `exit(-1)`, so callers cannot recover. Ownership is caller-managed for returned `IFile` and `IFileSystem` objects. Upload credential lookup depends on URL matching in the credential file.

Test signals: exercised indirectly by all CLI integration tests that open image configs, create extfs/EROFS views, or push merged/committed layers.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/comm_func.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/comm_func.h -->
# sources/cloud-native/overlaybd/src/tools/comm_func.h

Purpose: declares shared OverlayBD CLI helper APIs and imports the common Photon, LSMT, zfile, image-service, and CLI11 dependencies used by tool front ends.

Important APIs/types/functions: prototypes `open_file`, `create_overlaybd`, `create_uploader`, `create_ext4fs`, `is_erofs_fs`, `create_erofs_fs`, and `parse_config_and_dev_id`; also declares an unused `generate_option(CLI::App&)`.

Control flow: as a header it only exposes helper contracts. Defaults let callers open from local FS when no `IFileSystem` is supplied and use mode `0` unless needed.

State and persistence: no state; it defines pointer-based ownership interfaces returning raw Photon objects that callers must delete.

Dependencies/integration: common include for OverlayBD tools that need image-service access, zfile compression/upload, Photon lifecycle, or CLI11 option wiring.

Risks: broad includes increase compile coupling. Raw pointers and fail-fast implementation semantics are not documented in the header, so callers must learn ownership and error behavior from `comm_func.cpp`.

Test signals: compile coverage catches signature drift; runtime coverage comes from the tools using the helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/comm_func.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/overlaybd-apply.cpp -->
# sources/cloud-native/overlaybd/src/tools/overlaybd-apply.cpp

Purpose: CLI that applies an OCI tar layer, optionally gzip/zstd-compressed, into an OverlayBD image or raw image file.

Important APIs/types/functions: defines `FIFOFile` for full-count FIFO reads and uses `create_overlaybd`, `create_ext4fs`, `UnTar`, `create_gz_index`, `open_gzfile_adaptor`, `open_zstdfile_adaptor`, `new_sha256_file`, and `ImageFile::get_base`.

Control flow: CLI parses raw/mkfs/service config/gzip index/checksum/input/image config options, initializes Photon, opens the destination image, creates an ext4 filesystem view, opens the layer, detects FIFO/gzip/zstd/plain tar input, optionally builds a gzip index for TurboOCI, wraps the stream in SHA256 tracking, then extracts all tar entries. After extraction it compares the calculated `sha256:` digest with the expected value when supplied.

State and persistence: writes filesystem mutations into the OverlayBD or raw image file, may create a gzip index file, and optionally formats the target filesystem. It reads base-layer state from `ImageFile::get_base` for overlay-aware extraction.

Dependencies/integration: integrates OCI tar parsing, gzip/zstd adaptors, OverlayBD image-service configs, extfs, and checksum validation.

Risks: checksum validation only covers bytes consumed through the wrapper; the wrapper drains trailing bytes during final digest calculation. FIFO reads require exact requested lengths and can block if producers stall. Errors terminate the process instead of returning structured status.

Test signals: apply integration should cover plain tar, gzip, zstd, FIFO input, checksum mismatch, raw mode, mkfs mode, and TurboOCI gzip-index generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/overlaybd-apply.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/overlaybd-commit.cpp -->
# sources/cloud-native/overlaybd/src/tools/overlaybd-commit.cpp

Purpose: CLI that commits an OverlayBD mutable layer into a read-only commit file, with optional zfile compression, tar wrapping, TurboOCI warp-file mode, sealing, and registry upload.

Important APIs/types/functions: uses LSMT `open_file_rw`, `open_warpfile_rw`, `open_file_ro`, `CommitArgs`, `IFileRW::commit`, `IFileRW::close_seal`, zfile `CompressOptions`/`CompressArgs`/`new_zfile_builder`, `create_uploader`, and `registry_uploader_fini`.

Control flow: after CLI parsing and Photon init, it opens data/index files as normal LSMT, TurboOCI warp, or already-sealed input. `--seal` only closes/seals the layer and exits. Otherwise it creates the output file, optionally wraps it in tar, registry uploader, and zfile builder, populates UUID/parent UUID/user tag commit args, commits through LSMT, closes output, finalizes upload, prints digest, and releases resources.

State and persistence: creates the commit output, may unlink an existing output with `-f`, may upload a blob to a registry, and may mutate the input by sealing it. UUID and parent UUID are stored in commit metadata.

Dependencies/integration: links Photon localfs, LSMT, zfile, tar adaptor, registryfs, and CLI11.

Risks: `algorithm`/block-size validation is tied to `-z`; without `-z`, `block_size` defaults to `-1` but the warning compares against `0`. Upload and tar are rejected together in commit mode. UUID strings are copied without validating length against the fixed buffer.

Test signals: useful coverage includes normal commit, TurboOCI commit, sealed commit, seal-only, invalid compression options, duplicate output with/without `-f`, and upload finalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/overlaybd-commit.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/overlaybd-create.cpp -->
# sources/cloud-native/overlaybd/src/tools/overlaybd-create.cpp

Purpose: CLI that creates OverlayBD data/index files or a raw sparse image with a requested virtual size.

Important APIs/types/functions: local `open_file`, LSMT `LayerInfo`, `create_file_rw`, `WarpFileArgs`, `create_warpfile`, Photon localfile adaptors, UUID parsing, and extfs `make_extfs`.

Control flow: parses options for parent UUID, sparse RW, TurboOCI/fastoci, raw image, mkfs, data/index paths, and virtual size in GB. It opens new data/index files with exclusive create, converts size to bytes, then either truncates raw data file, creates a TurboOCI warp file, or creates a normal LSMT RW layer. Optional `--mkfs` formats the resulting file as extfs.

State and persistence: creates data and index files, stores LSMT metadata, optional parent UUID, sparse mode flag, virtual size, and optional filesystem structures.

Dependencies/integration: produces layer files later consumed by `overlaybd-apply` and `overlaybd-commit`; depends on Photon, LSMT, CLI11, and extfs.

Risks: virtual size multiplication can overflow for very large GB input. Raw mode still opens and later deletes/closes an index file even though it is unused. All errors are process-fatal.

Test signals: should cover raw, normal, sparse, TurboOCI, parent UUID, mkfs, pre-existing output failure, and invalid size.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/overlaybd-create.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/overlaybd-merge.cpp -->
# sources/cloud-native/overlaybd/src/tools/overlaybd-merge.cpp

Purpose: CLI that compacts multiple OverlayBD layers described by an image config into a single output layer, optionally zfile-compressed and uploaded.

Important APIs/types/functions: uses `create_overlaybd`, `ImageFile::compact`, `ZFile::new_zfile_builder`, `create_uploader`, and `registry_uploader_fini`. It defines a FIFO wrapper class, though the main path does not use it.

Control flow: parses service config, compression, tar, upload, credential/TLS, image config, and output path. It initializes Photon, creates an image file from config, opens the output, optionally wraps it in zfile and registry uploader, calls `compact(rst)`, closes output, finalizes registry upload, and prints the resulting digest.

State and persistence: writes a compacted layer file, may create a registry blob, and reads all lower layers referenced by the image config through image-service abstractions.

Dependencies/integration: bridges image-service layer stack resolution with zfile compression and registryfs uploading.

Risks: the tar option block wraps `rst` before `rst` is initialized, so `-t` with upload looks suspicious and likely ineffective or unsafe. Compression defaults to enabled through `run_callback_for_default`. Upload builder ownership and zfile builder ownership are implicit.

Test signals: needed cases include compact without compression, default compression, upload success/failure, missing image config, and the tar/upload option path.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/overlaybd-merge.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/overlaybd-zfile.cpp -->
# sources/cloud-native/overlaybd/src/tools/overlaybd-zfile.cpp

Purpose: standalone zfile utility for compressing, extracting, and verifying OverlayBD zfile blobs, including optional tar adaptor wrapping and stdin streaming.

Important APIs/types/functions: defines `IStreamFile` for stdin reads, `new_streamFile`, `verify_crc`, and uses zfile `is_zfile`, `zfile_validation_check`, `zfile_compress`, `zfile_decompress`, `new_tar_file_adaptor`, and Photon localfs.

Control flow: CLI supports `-x` extract, `--verify`, `-t`, `-f`, algorithm, block size, source, and optional target. Verify mode opens a file or stdin, wraps it in tar adaptor, validates zfile checksum, and exits. Compression can read from stdin when no target path is supplied. Extraction refuses stdin. Compression creates target exclusively and writes zfile data; extraction creates target and writes decompressed bytes.

State and persistence: creates or removes target files depending on `-f`; verify is read-only.

Dependencies/integration: uses Photon runtime and filesystem adaptors with zfile/tar libraries.

Risks: invalid algorithm values other than `lz4`/`zstd` do not explicitly error before compression options are used. Verify always wraps input with tar adaptor, which assumes the expected blob layout. `lseek` on stdin returns `INT64_MAX`, which may surprise generic consumers.

Test signals: cover lz4/zstd compression, extraction, verify valid/invalid blob, pipe compression, extraction pipe refusal, tar adaptor mode, and invalid block size.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/overlaybd-zfile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/sha256file.cpp -->
# sources/cloud-native/overlaybd/src/tools/sha256file.cpp

Purpose: implements SHA256-calculating wrappers for Photon files and direct path hashing used by OverlayBD layer checksum validation.

Important APIs/types/functions: `SHA256CheckedFile` extends `SHA256File`, overriding `read`, `lseek`, `fstat`, `filesystem`, and `sha256_checksum`; factory `new_sha256_file`; utility `sha256sum`.

Control flow: wrapper initializes OpenSSL SHA256 context, forwards reads to the underlying file, updates the digest on every positive read, and finalizes after draining remaining data in `sha256_checksum`. `sha256sum` opens a path with `O_DIRECT`, stats it, reads aligned 64 KiB chunks using `pread`, updates SHA256, and returns `sha256:<hex>`.

State and persistence: no writes; state is the underlying file pointer, ownership flag, OpenSSL context, and current read position. Finalization consumes unread bytes from the wrapped file.

Dependencies/integration: used by `overlaybd-apply` to verify uncompressed tar layer checksums; depends on OpenSSL SHA APIs and Photon virtual file interfaces.

Risks: OpenSSL SHA256 APIs are deprecated in newer OpenSSL versions. `sha256_checksum` finalizes once and should not be called repeatedly. `sha256sum` uses `O_DIRECT`, which can fail on unsupported filesystems or with alignment-sensitive reads.

Test signals: cover streaming digest, ownership deletion, mismatched expected digest, small/unaligned file hashing, and repeated finalization behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/sha256file.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/sha256file.h -->
# sources/cloud-native/overlaybd/src/tools/sha256file.h

Purpose: declares the checksum wrapper abstraction for Photon read-only files.

Important APIs/types/functions: abstract class `SHA256File : VirtualReadOnlyFile` adds pure virtual `sha256_checksum()`. Factory `new_sha256_file(IFile*, bool ownership)` wraps a Photon file; `sha256sum(const char*)` hashes a filesystem path.

Control flow: consumers read through `SHA256File` as an `IFile`, then call `sha256_checksum` to obtain the final `sha256:<hex>` string.

State and persistence: header defines no concrete state; implementations own digest state and optionally own the wrapped file.

Dependencies/integration: included by apply/merge-related tools that need layer checksum handling; depends on Photon filesystem interfaces.

Risks: the digest contract implies sequential reads; random seeks or multiple consumers can produce unintuitive digests. Ownership semantics must be passed correctly.

Test signals: compile and runtime coverage through `overlaybd-apply --checksum` plus unit tests around factory ownership.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/sha256file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/turboOCI-apply.cpp -->
# sources/cloud-native/overlaybd/src/tools/turboOCI-apply.cpp

Purpose: CLI specialized for applying OCI tar or tar.gz layers into OverlayBD TurboOCI v1 images, with optional EROFS output and tar-header import/export modes.

Important APIs/types/functions: `dump_tar_headers`, `UnTar::dump_tar_headers`, `UnTar::extract_all`, `LibErofs::extract_tar`, `create_gz_index`, `ZFile::zfile_open_ro`, `create_overlaybd`, `create_ext4fs`, and `ImageConfigNS::ImageConfig`.

Control flow: parses filesystem type, mkfs, service config, gzip index path, import/export flags, input path, and image config path. It opens input, unwraps zfile if present, detects gzip and builds a gzip index, optionally exports tar headers and exits, validates image config existence, creates an OverlayBD image file, then either extracts through `LibErofs` or ext4 `UnTar` with TurboOCI metadata generation.

State and persistence: writes image filesystem data, gzip metadata, and optionally tar-header output. EROFS import uses lower-layer count from image config to decide root behavior.

Dependencies/integration: integrates zfile, gzip index, tar metadata, EROFS, extfs, image-service config, and TurboOCI extraction.

Risks: `raw` variable exists but is never exposed as a CLI option, so base-file selection always follows image-file mode. `image_config_path` is optional in CLI but required for most paths. Input zfile wrapping changes `tarf` ownership assumptions.

Test signals: cover gzip index generation, zfile input, ext4 and EROFS targets, tar-header export/import, missing config, and mkfs behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/tools/turboOCI-apply.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/version.h -->
# sources/cloud-native/overlaybd/src/version.h

Purpose: exposes the build-time OverlayBD version string as a C++ constant.

Important APIs/types/functions: macros `MACROTOSTR` and `PRINTMACRO` stringify `OVERLAYBD_VER`; `static const char OVERLAYBD_VERSION[]` stores the expanded version.

Control flow: compile-time macro expansion only.

State and persistence: no runtime state. The compiled binary embeds the version value.

Dependencies/integration: requires the build system to define `OVERLAYBD_VER`; consumers include the header to report version information.

Risks: if `OVERLAYBD_VER` is undefined, the literal string `"OVERLAYBD_VER"` is embedded, which can silently mask build metadata errors.

Test signals: binary version output or compile-time assertions should verify the macro is defined in release builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/check.c -->
# sources/cloud-native/overlayfs-tools/check.c

Purpose: implements the main consistency scanner and repair engine for `fsck.overlay`, validating whiteouts, redirect directories, opaque state, and missing impure xattrs across upper and lower overlay layers.

Important APIs/types/functions: public `ovl_scan_fix`; internal lookup contexts/data, redirect list entries, `ovl_lookup_single`, `ovl_lookup_layer`, `ovl_lookup_lower`, `ovl_lookup`, `ovl_check_whiteout`, `ovl_check_redirect`, `ovl_check_impure`, `ovl_count_impurity`, and scan result aggregation helpers.

Control flow: scanning has two passes. Pass one checks redirect xattrs and directory-tree consistency, recording valid redirect origins to detect duplicates. Pass two checks whiteouts and counts origin/redirect/merge subdirectories so missing `trusted.overlay.impure` can be repaired. It scans lower layers from bottom to top, then upper, switching read-only lower layers to no-change mode.

State and persistence: may remove invalid whiteouts, remove redirect xattrs, create missing whiteouts, set opaque xattrs, and set impure xattrs. Global `status` records changed, abort, and unresolved inconsistency bits. A transient in-memory redirect list tracks duplicate origins.

Dependencies/integration: called by `fsck.c`; depends on `scan_dir` from `lib.c`, overlay xattr constants, path helpers, kernel-style list macros, and global user flags.

Risks: repair decisions are interactive unless auto/yes/no flags override. Redirect resolution is subtle and only supports xattr-capable layers. Incorrect repair can change overlay semantics, so mounted filesystems are blocked earlier.

Test signals: direct tests should create layered fixtures with orphan whiteouts, invalid redirect xattrs, duplicate redirects, missing impure xattrs, read-only lowers, and `-n`/`-y`/`-p` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/check.h -->
# sources/cloud-native/overlayfs-tools/check.h

Purpose: declares the filesystem scan/fix entry point used by the fsck executable.

Important APIs/types/functions: `int ovl_scan_fix(struct ovl_fs *ofs);`.

Control flow: callers pass a fully populated and opened overlay filesystem description. The implementation performs multi-pass validation and optional repair.

State and persistence: no header state; implementation may mutate upper/lower layers and global status according to flags.

Dependencies/integration: requires `struct ovl_fs` from `lib.h` to be visible before inclusion; used by `fsck.c`.

Risks: minimal header hides destructive behavior, so caller-side safeguards such as mount checks and read-only checks are essential.

Test signals: compile coverage plus `fsck.overlay` fixture tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/common.c -->
# sources/cloud-native/overlayfs-tools/common.c

Purpose: provides common output, allocation, duplication, and version helpers for overlayfs-tools.

Important APIs/types/functions: `print_debug`, `print_info`, `print_err`, `smalloc`, `srealloc`, `sstrdup`, `sstrndup`, and `version`. Uses global `program_name`.

Control flow: debug output is compiled only when `DEBUG` is defined; info prints to stdout; errors are prefixed with program name and printed to stderr. Allocation wrappers exit on failure after printing translated diagnostics.

State and persistence: no persistent data except reading `program_name`. It can terminate the process on allocation failure.

Dependencies/integration: used by both `overlay` and `fsck.overlay`; depends on `config.h` for package version and `common.h` for gettext macro.

Risks: allocation wrappers make memory failures fatal. `print_debug` signature is compiled even when empty, so format errors may be less visible without debug builds.

Test signals: version output and diagnostics are indirectly covered by CLI tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/common.h -->
# sources/cloud-native/overlayfs-tools/common.h

Purpose: shared declarations and macros for overlayfs-tools diagnostics, gettext integration, min/max helpers, and allocation wrappers.

Important APIs/types/functions: `_()` gettext macro, GNU-style `min`/`max`, printf-checked declarations for `print_err`, `print_info`, `print_debug`, memory helpers, and `version`.

Control flow: compile-time feature selection only; `USE_GETTEXT` toggles translation.

State and persistence: no state.

Dependencies/integration: included by most C files and provides a consistent utility layer across `overlay` and `fsck.overlay`.

Risks: `min`/`max` use GNU statement expressions and `typeof`, matching `gnu11` build mode but not strict ISO C. The fallback `__attribute__` guard may hide compiler checking on non-GNU compilers.

Test signals: build with Meson `c_std=gnu11` verifies macro compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/config.h -->
# sources/cloud-native/overlayfs-tools/config.h

Purpose: central static configuration for overlayfs-tools.

Important APIs/types/functions: defines `PACKAGE_VERSION` as `v0.1.0` and `MOUNT_TAB` as `/proc/mounts`.

Control flow: compile-time constants only.

State and persistence: no state. `MOUNT_TAB` controls where fsck/mount detection reads live mount information.

Dependencies/integration: included by common, fsck, mount, and related code; Meson also passes `OVERLAYFS_TOOLS_VERSION` separately for version output.

Risks: `PACKAGE_VERSION` may diverge from Meson project version; actual `version()` uses `OVERLAYFS_TOOLS_VERSION`, so this macro may be stale or unused. Hard-coded `/proc/mounts` is Linux-specific.

Test signals: version command and mount-detection tests expose configuration mismatches.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/fsck.c -->
# sources/cloud-native/overlayfs-tools/fsck.c

Purpose: command-line front end for `fsck.overlay`, responsible for option parsing, opening layer directories, basic safety checks, running scan/fix, and producing fsck-style exit codes.

Important APIs/types/functions: global `struct ovl_fs ofs`, `flags`, `status`; `ovl_open_dirs`, `ovl_clean_dirs`, `ovl_basic_check_layer`, `ovl_basic_check_workdir`, `ovl_basic_check`, `parse_options`, `fsck_exit`, and `main`.

Control flow: parses `-o lowerdir=...,upperdir=...,workdir=...` plus repair policy flags `-p`, `-n`, `-y`, opens all layer directories with fd-limit adjustment, checks whether any layer is mounted, validates xattr/read-only/workdir constraints, calls `ovl_scan_fix`, cleans fds/path allocations, then maps status bits to fsck return values.

State and persistence: may modify filesystem metadata through `ovl_scan_fix` unless `-n` or mounted-blocking prevents it. Global flags and status drive repair policy and exit code.

Dependencies/integration: uses mount parsing from `mount.c`, filesystem constants from `overlayfs.h`, scanning from `check.c`, xattr helpers from `lib.c`, and diagnostics from `common.c`.

Risks: option conflicts are fatal. Workdir/upperdir subdir checks use substring matching, which can false-positive on path prefixes. Fsck refuses mounted overlays unless no-change mode is used.

Test signals: fixture tests should cover option parsing, lower-only validation, mounted refusal, xattr unsupported layers, read-only layers, and exit status combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/fsck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/lib.c -->
# sources/cloud-native/overlayfs-tools/lib.c

Purpose: common fsck support library for prompting, xattr get/set/remove operations, and generic FTS directory scanning with callback hooks.

Important APIs/types/functions: `ask_question`, `get_xattr`, `set_xattr`, `remove_xattr`, `scan_entry_init`, `scan_check_entry`, and `scan_dir`.

Control flow: `ask_question` honors global repair-policy flags before falling back to interactive yes/no input. Xattr helpers open relative paths with `openat` and no symlink following, then perform fget/fset/fremove xattr operations. `scan_dir` uses `fts_open` with physical traversal, fills `scan_ctx`, counts files/directories, and invokes callbacks for whiteout, redirect, impurity, and impure checks on appropriate FTS events.

State and persistence: xattr helpers persist metadata mutations. `scan_dir` updates `scan_ctx.result` and transient `dirdata` stacks; prompt behavior reads global flags.

Dependencies/integration: used by `check.c` and `fsck.c`; depends on `path.c` for `basename2`, and on common allocation/printing helpers.

Risks: xattr helpers open directories read-only and no-follow, which is safer but may fail on unusual filesystem permissions. `set_xattr` tests `errno == EEXIST` after a call without first checking `ret`, so stale errno could be risky if not reset by libc behavior.

Test signals: unit fixtures for xattr existence/value, no-xattr filesystem, symlink handling, FTS callback ordering, and policy flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/lib.h -->
# sources/cloud-native/overlayfs-tools/lib.h

Purpose: declares fsck exit codes, global status/option flags, overlay layer data structures, scan context structures, and helper APIs.

Important APIs/types/functions: `struct ovl_layer`, `struct ovl_fs`, `struct scan_dir_data`, `struct scan_result`, `struct scan_ctx`, `struct scan_operations`, flag constants, `set_inconsistency`, `set_abort`, `set_changed`, `scan_dir`, `ask_question`, and xattr helpers.

Control flow: status helpers OR bits into caller-provided status. Callback structure defines the event hooks `scan_dir` will invoke.

State and persistence: data structures represent opened filesystem layers with paths, fds, stack index, and capability flags. No persistence in the header itself.

Dependencies/integration: shared contract between `fsck.c`, `check.c`, `lib.c`, and `mount.c`.

Risks: typo `OVL_ST_INCONSISTNECY` is part of the local API. Global flag/status constants make reentrancy unlikely. Struct ownership rules are implicit.

Test signals: compile coverage plus fsck behavior tests around every flag/status transition.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/list.h -->
# sources/cloud-native/overlayfs-tools/list.h

Purpose: provides a small Linux-kernel-style intrusive doubly linked list implementation for overlayfs-tools.

Important APIs/types/functions: `struct list_head`, `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`, `list_add`, `list_add_tail`, `list_del`, `list_del_init`, `list_empty`, `list_entry`, `list_for_each`, and `list_for_each_safe`.

Control flow: macros and static inline helpers manipulate embedded list nodes. `check.c` uses this for the redirect-origin tracking list.

State and persistence: state is embedded in caller-owned structs; no allocation or persistence.

Dependencies/integration: adapted from Linux kernel list API for C userspace.

Risks: no type safety beyond macro conventions. Deleting uninitialized or double-deleted entries corrupts memory. Requires including `<stdbool.h>` before use because `list_empty` returns `bool`.

Test signals: redirect duplicate tests exercise list add/find/delete/free flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/logic.c -->
# sources/cloud-native/overlayfs-tools/logic.c

Purpose: implements the `overlay` command actions `vacuum`, `diff`, `merge`, and `deref` by traversing an upperdir and comparing or transforming it relative to a lowerdir or mounted overlay view.

Important APIs/types/functions: xattr probes `is_opaque`, `is_redirect`, `is_metacopy`, `is_opaquedir`; comparison helpers `regular_file_identical` and `symbolic_link_identical`; traversal callbacks for vacuum/diff/merge/deref; generic `traverse`; public `vacuum`, `diff`, `merge`, and `deref`.

Control flow: `traverse` walks upperdir with FTS, maps each upper path to corresponding lower/mount path, stats lower, dispatches by file type, and allows callbacks to skip subtrees. Diff prints added/removed/modified/replaced entries. Vacuum emits shell commands to remove upper copies identical to lower. Merge emits commands to move/copy/remove lower and upper content. Deref emits commands to replace redirect/metacopy entries with real mounted content.

State and persistence: direct execution is avoided here; it writes shell commands to a script stream or prints diff output. Later `main.c` may execute generated scripts with `--force`.

Dependencies/integration: uses trusted overlay xattrs, FTS, shell command generation in `sh.c`, and global formatting flags.

Risks: redirect merge is intentionally unsupported and aborts. Special files generally fail. File content comparison uses stack buffers sized from filesystem block size. Diff semantics around opaque directories and brief/verbose modes are subtle.

Test signals: Meson test fixtures compare diff output in normal, verbose, and brief modes; additional tests should execute generated vacuum/merge/deref scripts on controlled overlays.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/logic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/logic.h -->
# sources/cloud-native/overlayfs-tools/logic.h

Purpose: declares the high-level overlay action functions used by the `overlay` CLI.

Important APIs/types/functions: extern flags `verbose`, `brief`, and `use_rsync`; functions `vacuum`, `diff`, `merge`, and `deref`.

Control flow: callers pass lower/upper or mount/upper directories and optional script stream. Functions return zero on success and nonzero on fatal traversal or unsupported input.

State and persistence: actions may write scripts or stdout output; filesystem mutations only happen if generated scripts are later executed.

Dependencies/integration: consumed by `main.c`, implemented by `logic.c`.

Risks: comments still say “three feature functions” though four are declared. Global flags make concurrent independent runs impossible.

Test signals: CLI tests exercise the exported actions through `overlay`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/logic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/main.c -->
# sources/cloud-native/overlayfs-tools/main.c

Purpose: command-line front end for the `overlay` utility, validating arguments and invoking diff/vacuum/merge/deref actions.

Important APIs/types/functions: `print_help`, `starts_with`, `is_mounted`, `check_mounted`, `directory_exists`, `directory_create`, `check_xattr_trusted`, and `main`; global flags `verbose`, `brief`, `ignore`, `force`, and `use_rsync`.

Control flow: parses lower/upper/mount/new-dir/options, resolves real paths, verifies lower and upper directories, checks ability to set `trusted.overlay.*` xattrs, warns/refuses if the overlay appears mounted for mutating actions, then runs the selected action. Mutating actions create a temporary shell script and either tell the user to run it or execute/delete it when `--force` is set.

State and persistence: may create new lower/upper backup directories, create generated shell scripts, and with force execute commands that mutate lower/upper trees. It writes a temporary xattr probe file in upperdir.

Dependencies/integration: calls `logic.c` actions and `sh.c` script generation; relies on `/proc/mounts` parsing and trusted xattr support.

Risks: mount detection uses string prefix matching and has complex negation that can false-positive/negative. Generated script execution uses `system`. Trusted xattr requirement means root or equivalent capability is needed even for diff.

Test signals: Meson tests cover diff variants; manual tests should cover force execution, mounted checks, new-dir backup behavior, and deref requirements.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/meson.build -->
# sources/cloud-native/overlayfs-tools/meson.build

Purpose: Meson build definition for overlayfs-tools executables and fixture-based tests.

Important APIs/types/functions: project `overlayfs-tools` version `2025.01`; builds `overlay` from `main.c`, `logic.c`, `sh.c`, `common.c`; builds `fsck.overlay` from fsck/check/mount/path/overlayfs support files; optional `musl-fts`; custom targets for fixture extraction and expected diff outputs; test `run_tests`.

Control flow: configures GNU11 builds, injects `OVERLAYFS_TOOLS_VERSION`, extracts test tarballs, sets trusted overlay xattrs in the upper fixture, generates normal/verbose/brief outputs with sudo, and compares through Python test runner.

State and persistence: build artifacts include executables and generated test directories/files in the build tree.

Dependencies/integration: supports glibc and musl by optionally linking `musl-fts`; requires sudo and setfattr-capable filesystem for tests.

Risks: tests requiring sudo and trusted xattrs may not run in restricted CI. `fsck_dep` tries to link `m` but code does not visibly use libm.

Test signals: `meson test run_tests` validates diff output against saved fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/mount.c -->
# sources/cloud-native/overlayfs-tools/mount.c

Purpose: parses overlay mount options, resolves lower/upper/work directories, scans live mounts, and detects whether a target overlay layer is currently mounted.

Important APIs/types/functions: `ovl_resolve_lowerdirs`, `ovl_get_dirs`, `ovl_free_opt`, `ovl_parse_opt`, `ovl_scan_mount_init`, `ovl_scan_mount_exit`, and `ovl_check_mount`.

Control flow: mount option strings are split with kernel-compatible helpers. Directory options are realpath-resolved; lowerdir lists are split on unescaped colons. Live mount scanning reads `/proc/mounts`, filters `overlay` entries, skips relative path mounts, resolves options, and compares every target lower/upper/work path against mounted entries.

State and persistence: no writes. Allocates and frees path arrays and mount entry structures.

Dependencies/integration: used by `fsck.c` for user option parsing and mounted-safety checks; depends on `overlayfs.c` split helpers and constants in `overlayfs.h`.

Risks: relative-path mounted overlays cannot be reliably checked and are skipped with a FIXME. Any one matching lower path marks the target mounted because fsck may modify lower layers.

Test signals: unit tests should cover escaped colons/commas, too many lower layers, relative live mounts, hard matches on lower/upper/work, and invalid paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/mount.h -->
# sources/cloud-native/overlayfs-tools/mount.h

Purpose: declares overlay mount-option parsing and live mount checking APIs.

Important APIs/types/functions: `struct ovl_config` with `lowerdir`, `upperdir`, `workdir`; `ovl_parse_opt`, `ovl_free_opt`, `ovl_get_dirs`, and `ovl_check_mount`.

Control flow: callers parse raw `-o` options into `ovl_config`, resolve paths into owned arrays/strings, then optionally check mounted status against a populated `ovl_fs`.

State and persistence: no persistence; ownership of allocated strings is shared by documented usage in implementation rather than explicit header comments.

Dependencies/integration: `fsck.c` consumes these APIs before opening and scanning layers.

Risks: header uses `struct ovl_fs` and `bool` without including their definitions; include order matters.

Test signals: compile and fsck option parsing tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/overlayfs.c -->
# sources/cloud-native/overlayfs-tools/overlayfs.c

Purpose: userspace copies of Linux overlayfs option splitting helpers.

Important APIs/types/functions: `ovl_split_lowerdirs` splits lowerdir lists on unescaped `:` and mutates separators to NUL; `ovl_next_opt` splits mount option strings on unescaped `,`.

Control flow: both helpers scan in place, skip escaped characters, terminate current token at separators, and return count or next token pointer.

State and persistence: mutates caller-provided strings only; no allocation.

Dependencies/integration: used by `mount.c` to parse user-supplied and `/proc/mounts` overlay options consistently with kernel syntax.

Risks: input strings are destroyed during parsing, so callers must duplicate if original text is needed. Escaping behavior must track kernel overlayfs semantics.

Test signals: unit cases for escaped separators, trailing escapes, empty options, and multi-layer lowerdir strings.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/overlayfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/overlayfs.h -->
# sources/cloud-native/overlayfs-tools/overlayfs.h

Purpose: defines overlayfs constants and declares option-splitting helpers shared by fsck and mount parsing.

Important APIs/types/functions: `OVERLAYFS_SUPER_MAGIC`, `OVERLAY_NAME`, `OVL_MAX_STACK`, option prefixes, trusted overlay xattr names, `ovl_split_lowerdirs`, and `ovl_next_opt`.

Control flow: constants guide mount detection, layer-count validation, and xattr reads/writes.

State and persistence: no state.

Dependencies/integration: included by `fsck.c`, `check.c`, `mount.c`, and `overlayfs.c`.

Risks: constants must stay aligned with Linux overlayfs. Only trusted xattr namespace is supported.

Test signals: fsck/check tests covering every xattr name and max stack boundary.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/overlayfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/path.c -->
# sources/cloud-native/overlayfs-tools/path.c

Purpose: implements path joining and base-relative path extraction helpers for overlayfs-tools.

Important APIs/types/functions: `joinname` and `basename2`.

Control flow: `joinname` normalizes leading `./`, handles empty/dot inputs, removes duplicate boundary slashes, allocates a new combined string, and returns `"."` for empty results. `basename2` strips a base directory prefix without modifying inputs and returns `"."` when path equals base.

State and persistence: `joinname` allocates memory that callers must free; `basename2` returns a pointer into the input path or a static dot string.

Dependencies/integration: used heavily by fsck lookup/redirect code and scan context initialization.

Risks: does not resolve `..`, middle duplicate slashes, or NULL input. `basename2` prefix matching is lexical, so callers must supply normalized paths.

Test signals: unit tests for root, dot, slash, mismatched prefix, exact prefix, and redirect path combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/path.h -->
# sources/cloud-native/overlayfs-tools/path.h

Purpose: declares lightweight path helpers.

Important APIs/types/functions: `joinname(const char*, const char*)` and `basename2(const char*, const char*)`.

Control flow: callers use `joinname` for allocated path construction and `basename2` for relative path views.

State and persistence: no header state; ownership is implementation-defined.

Dependencies/integration: consumed by fsck scanner and redirect lookup logic.

Risks: no NULL-safety or ownership annotations in the header.

Test signals: compile and path unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/path.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/sh.c -->
# sources/cloud-native/overlayfs-tools/sh.c

Purpose: generates safe shell scripts for the `overlay` utility actions.

Important APIs/types/functions: globals `vars` and `var_names`; `create_shell_script`, `quote`, `substitue`, and `command`.

Control flow: `create_shell_script` creates a 0700 temporary `.sh`, writes a bash header, exports quoted path variables, and optionally creates backup lower/upper trees when `LOWERNEW` or `UPPERNEW` are set. `quote` emits single-quoted shell strings with embedded quote escaping. `command` substitutes `%L`, `%U`, `%M`, `%N`-style variable prefixes into shell-safe references and appends a command line.

State and persistence: creates executable script files and, when run, the script may copy or mutate layer directories. The C code only writes scripts.

Dependencies/integration: called from `main.c` and `logic.c` callbacks to materialize vacuum/merge/deref operations.

Risks: function name `substitue` is misspelled but internal. Prefix substitution fails if a path does not start with the expected variable value. Backup copy commands in generated scripts are destructive to pre-existing `LOWERNEW`/`UPPERNEW` targets.

Test signals: tests should inspect generated scripts for quoting, prefix substitution, backup handling, and execution on paths containing quotes/spaces.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/sh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/sh.h -->
# sources/cloud-native/overlayfs-tools/sh.h

Purpose: declares shell-generation state and APIs for overlayfs-tools.

Important APIs/types/functions: enum indexes `LOWERDIR`, `UPPERDIR`, `MOUNTDIR`, `LOWERNEW`, `UPPERNEW`, `NUM_VARS`; extern `var_names` and `vars`; `create_shell_script`; `command`.

Control flow: callers populate `vars`, create a script, then emit formatted commands with path substitutions.

State and persistence: global `vars` controls all script substitution.

Dependencies/integration: used by CLI option parsing and action callbacks.

Risks: global mutable path state is not reentrant. The `command` format language is tiny and has no validation beyond substitution failure.

Test signals: generated script fixture tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/sh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/test_cases/run_tests.py -->
# sources/cloud-native/overlayfs-tools/test_cases/run_tests.py

Purpose: Meson test runner that builds overlayfs-tools test fixtures and compares generated diff output with expected files.

Important APIs/types/functions: `run_command(cmd)` wraps `subprocess.run(shell=True, check=True)` and exits with the failed return code; command list runs clean, fixture extraction, output generation, and expected generation.

Control flow: sequentially runs Ninja targets for clean/permanent/changes/diff/verbose/overlayed/brief expected/brief output, then runs three `diff -u` comparisons.

State and persistence: creates and removes build-tree fixture directories/files through Ninja targets; writes `diff.out`, `verbose.out`, `brief.out`, and `brief.expected`.

Dependencies/integration: invoked by Meson `test('run_tests', ...)`; assumes Ninja build directory and test fixtures from `meson.build`.

Risks: uses shell strings and sudo-dependent targets; failure stops at first command, which is simple but gives limited aggregate diagnostics.

Test signals: this is the primary automated signal for normal, verbose, and brief diff behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlayfs-tools/test_cases/run_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/ISSUE_TEMPLATE/bug_report.yaml -->
# sources/cloud-native/soci-snapshotter/.github/ISSUE_TEMPLATE/bug_report.yaml

Purpose: GitHub issue form for SOCI Snapshotter bug reports.

Important APIs/types/functions: YAML issue form fields for description, reproduction steps, expected results, host information, and additional context; default title prefix `[Bug]` and label `bug`.

Control flow: GitHub renders required textareas for description, expected results, and host information; optional context points lazy-loading reporters to debugging docs.

State and persistence: creates structured issue metadata in GitHub; no repository runtime state.

Dependencies/integration: integrated with GitHub Issues and repository labels/docs.

Risks: host information template is free-form, so versions may still be incomplete. Relative debug-doc link depends on GitHub issue template rendering behavior.

Test signals: manual issue creation or GitHub form preview validates fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/ISSUE_TEMPLATE/bug_report.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/ISSUE_TEMPLATE/config.yml -->
# sources/cloud-native/soci-snapshotter/.github/ISSUE_TEMPLATE/config.yml

Purpose: configures GitHub issue template behavior and discussion routing.

Important APIs/types/functions: `blank_issues_enabled: true` and a contact link named “Ask a question (GitHub Discussions)” targeting the project discussions page.

Control flow: GitHub shows the discussion link alongside issue templates and still permits blank issues.

State and persistence: affects GitHub UI only.

Dependencies/integration: relies on GitHub Discussions being enabled for `awslabs/soci-snapshotter`.

Risks: blank issues can bypass structured bug/feature templates. Stale discussion URL would misroute questions.

Test signals: repository issue creation UI preview.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/ISSUE_TEMPLATE/feature_request.yaml -->
# sources/cloud-native/soci-snapshotter/.github/ISSUE_TEMPLATE/feature_request.yaml

Purpose: GitHub issue form for feature requests.

Important APIs/types/functions: title prefix `[FEATURE]`, label `feature`, required description field, and optional solution/alternatives/context textareas.

Control flow: GitHub creates structured feature issues with the chosen labels and prompts.

State and persistence: stores user-provided feature request content in GitHub Issues.

Dependencies/integration: depends on the `feature` label existing or being creatable.

Risks: only the description is required, so acceptance criteria and alternatives may be omitted.

Test signals: GitHub issue form preview.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/ISSUE_TEMPLATE/feature_request.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/dependabot.yml -->
# sources/cloud-native/soci-snapshotter/.github/dependabot.yml

Purpose: configures Dependabot updates for Go modules, Docker base images, and GitHub Actions.

Important APIs/types/functions: daily gomod updates for `/` and `/cmd` with `[DNM]` commit prefix, patch-only allowance for `github.com/containerd/containerd/v2`, ignores for Kubernetes deps and self-dependency, Docker updates for root Dockerfile with Go base image major/minor ignored, and daily GitHub Actions updates.

Control flow: Dependabot opens PRs according to ecosystem schedules and filters.

State and persistence: creates dependency update pull requests; does not mutate code without merge.

Dependencies/integration: aligns with scripts that manually bump deps and CI dependency review.

Risks: daily cadence can create PR noise. Patch-only containerd policy avoids accidental compatibility jumps but may miss security fixes requiring minor upgrades. Comments indicate PRs are tracking-only and not intended for direct merge.

Test signals: Dependabot PR generation and dependency review workflow.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/dependency-review-config.yml -->
# sources/cloud-native/soci-snapshotter/.github/dependency-review-config.yml

Purpose: license allowlist configuration for GitHub dependency-review-action.

Important APIs/types/functions: `allow-licenses` includes Apache/BSD/MIT/ISC/Python/PostgreSQL/X11/Zlib/Golang patent license; `allow_dependencies_licenses` grants specific MPL-2.0 exceptions for HashiCorp packages.

Control flow: dependency review checks PR dependency changes against this policy and comments/fails when unapproved licenses appear.

State and persistence: no repository runtime state; enforces governance in PR checks.

Dependencies/integration: used by `.github/workflows/review-dependencies.yml`.

Risks: package URL identifiers must match GitHub dependency-review naming. License policy drift requires manual updates.

Test signals: PRs changing `go.mod`/`go.sum` exercise the review workflow.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/dependency-review-config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/new-pull-request-labels.yml -->
# sources/cloud-native/soci-snapshotter/.github/new-pull-request-labels.yml

Purpose: labeler configuration for new pull requests.

Important APIs/types/functions: maps changed file globs to labels `documentation`, `github_actions`, `go`, `testing`, `benchmarking`, and `dependencies`.

Control flow: `actions/labeler` applies or syncs labels based on changed files.

State and persistence: mutates PR labels in GitHub.

Dependencies/integration: consumed by `new-pull-requests.yml` under `pull_request_target`.

Risks: broad `.github/**` and `scripts/**` labeling as `github_actions` may over-label script-only changes. Label names must exist or be creatable by the action.

Test signals: opening PRs with representative file changes validates labels.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/new-pull-request-labels.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/benchmark-visualization.yml -->
# sources/cloud-native/soci-snapshotter/.github/workflows/benchmark-visualization.yml

Purpose: runs performance benchmarks, converts results to visualization data, and publishes benchmark history to GitHub Pages on main pushes.

Important APIs/types/functions: jobs `benchmark`, `download-and-convert-benchmark-result-to-visualization-data`, and `push-benchmark-result-gh-pages`; uses `make benchmarks-perf-test`, artifact upload/download, `scripts/visualization-data-converter.sh`, jq matrix generation, and `benchmark-action/github-action-benchmark`.

Control flow: push and selected PR changes build the project, run benchmark binaries, upload raw `results.json`, convert it into per-file JSON visualization data, then on push iterates those files to publish custom smaller-is-better benchmark data.

State and persistence: creates GitHub artifacts and updates gh-pages benchmark data on push.

Dependencies/integration: depends on Go setup, Makefile benchmark targets, converter script, jq, and GitHub token write/deployment permissions.

Risks: benchmarks run on shared GitHub runners and can be noisy. Matrix file paths are absolute workspace paths from conversion job but reused after artifact download, so path assumptions should be watched.

Test signals: PR workflow validates benchmark run/conversion without publishing; main push validates gh-pages publication.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/benchmark-visualization.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/build.yml -->
# sources/cloud-native/soci-snapshotter/.github/workflows/build.yml

Purpose: main build, unit, root-required, and integration CI workflow for SOCI Snapshotter.

Important APIs/types/functions: reusable `setup.yml` runner matrix; jobs `test`, `test-root`, and `integration`; Go versions `1.25.11` and `1.26.4`; containerd versions `1.7.32`, `2.0.9`, `2.2.4`, and `2.3.1`; Make targets `make`, `test-with-coverage`, `integration-with-coverage`, coverage display.

Control flow: triggered on main/release pushes and code-relevant PRs. Unit tests run across available runner OS labels and two Go versions. Root test runs snapshot package with `sudo -E`. Integration tests run a larger matrix over Go and containerd versions, installing gotestsum and platform-specific zlib static dependencies.

State and persistence: produces coverage data in workspace; no artifact upload here.

Dependencies/integration: depends on setup runner workflow, Makefile targets, Docker/containerd integration environment, and CodeBuild runners for awslabs.

Risks: high matrix size can be expensive. `SKIP_SYSTEMD_TESTS` is set only for `ubuntu-x86`. Future Go/containerd version changes require updates across workflows.

Test signals: this is the primary correctness gate for library, CLI, snapshot root tests, and integration behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/bump-deps.yml -->
# sources/cloud-native/soci-snapshotter/.github/workflows/bump-deps.yml

Purpose: scheduled/manual automation that runs repository dependency bump script and opens a PR.

Important APIs/types/functions: weekly Tuesday cron, workflow dispatch, Go setup, `./scripts/bump-deps.sh`, and `peter-evans/create-pull-request`.

Control flow: runs only for the upstream repository or manual dispatch, checks out code, sets Go version, runs bump script, and creates a signed-off PR labeled `dependencies`.

State and persistence: creates commits/branches/PRs through GitHub token write permissions.

Dependencies/integration: tied to repo scripts and Dependabot policy.

Risks: generated PR body says checks require close/reopen, so automated PRs may not be fully self-validating. Upstream repository guard prevents fork noise.

Test signals: scheduled run or manual dispatch producing a dependency PR.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/bump-deps.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/comparision-test.yml -->
# sources/cloud-native/soci-snapshotter/.github/workflows/comparision-test.yml

Purpose: scheduled/PR workflow for comparison benchmarks between SOCI and overlayfs.

Important APIs/types/functions: Go setup, `make`, `make benchmarks`, and `cat benchmark/comparisonTest/output/results.json`.

Control flow: runs every two days and on benchmark/Makefile/workflow PR changes. It builds the project, runs benchmark suite, and prints comparison results.

State and persistence: writes benchmark output under `benchmark/comparisonTest/output` in CI workspace.

Dependencies/integration: depends on Makefile benchmark targets and benchmark harness.

Risks: filename is misspelled `comparision-test.yml`, while PR path filter references `.github/workflows/comparison-test.yml`; changes to this workflow itself may not trigger the PR workflow. Benchmarks require sudo and stable host behavior.

Test signals: scheduled runs and benchmark output JSON.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/comparision-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/create-release-branch.yml -->
# sources/cloud-native/soci-snapshotter/.github/workflows/create-release-branch.yml

Purpose: orchestrates release branch creation and follow-up release maintenance PRs for licenses and docs.

Important APIs/types/functions: workflow dispatch inputs `major_minor_version` and `base_commit`; PR test job; scripts `create-release-branch.sh`, `build-third-party-licenses.sh`, and `update-version-in-docs.sh`; reusable workflows `create-third-party-licenses.yml` and `update-version-in-docs.yml`.

Control flow: PR runs dry-run validation and doc/license generation checks. Manual dispatch checks out main sparsely, validates version format, creates `release/<major.minor>` from requested base, outputs tag version, then calls downstream workflows with write permissions to create PRs.

State and persistence: on dispatch, creates a release branch and later PR branches for generated files.

Dependencies/integration: depends on GitHub token write permissions, release scripts, Go/go-licenses, and downstream workflows.

Risks: version validation prepends `v` in `VERSION` while input description says major.minor, so formatting expectations are strict. Sparse checkout in create job only includes branch script.

Test signals: PR dry run and manual workflow dispatch.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/create-release-branch.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/create-third-party-licenses.yml -->
# sources/cloud-native/soci-snapshotter/.github/workflows/create-third-party-licenses.yml

Purpose: generates and PRs `THIRD_PARTY_LICENSES` updates for release branches and validates license generation on PRs.

Important APIs/types/functions: supports workflow dispatch, workflow call, release branch pushes, and PRs; inputs `tag_name`; installs `go-licenses`; runs `scripts/build-third-party-licenses.sh`; creates PRs with `peter-evans/create-pull-request`.

Control flow: PRs only run test generation. Non-PR events determine `TAG_NAME` and `TARGET_BRANCH` from input or latest release API lookup for release branch pushes, check out the target branch, generate licenses, and open an automated PR.

State and persistence: creates/updates license files and PR branches; uses GitHub API reads for latest tag inference.

Dependencies/integration: called from release branch workflow and triggered on release branch pushes.

Risks: release API parsing uses grep/cut/awk on JSON and can select unexpected tags. It skips GitHub-action-authored push events to avoid automation loops.

Test signals: PR path validation and release-branch push/dispatch PR creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/create-third-party-licenses.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/new-pull-requests.yml -->
# sources/cloud-native/soci-snapshotter/.github/workflows/new-pull-requests.yml

Purpose: automatically labels newly opened or updated non-draft pull requests.

Important APIs/types/functions: `pull_request_target` trigger, permissions `contents: read` and `pull-requests: write`, `actions/labeler@v6`, config `.github/new-pull-request-labels.yml`, `sync-labels: true`.

Control flow: without checking out untrusted PR code, the labeler reads main-branch config and synchronizes labels on non-draft PRs.

State and persistence: mutates PR labels.

Dependencies/integration: secure pairing with label config and GitHub pull request metadata.

Risks: `pull_request_target` is safe here because no PR code is checked out, but future edits adding checkout/run steps would raise security risk. Draft PRs are ignored until state changes retrigger.

Test signals: PR label changes for known file patterns.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/new-pull-requests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/prebuild.yml -->
# sources/cloud-native/soci-snapshotter/.github/workflows/prebuild.yml

Purpose: pre-build quality gates for metadata, secrets, lint, YAML, shell scripts, and config generation.

Important APIs/types/functions: jobs `check`, `git-secrets`, `lint`, `yamllint`, `shellcheck`, and `config`; installs flatc binary and check tools; runs `check-ltag`, `check-dco`, `check-flatc`, git-secrets scan-history, golangci-lint in `.` and `cmd`, `yamllint .`, shellcheck in a container, and `make && ./scripts/check-config.sh`.

Control flow: triggered on main/release pushes and PRs. Jobs run independently on Ubuntu except shellcheck container.

State and persistence: no repository persistence; scans commit history and generated config in workspace.

Dependencies/integration: depends on script suite, `.golangci.yml`, `.yamllint.yml`, git-secrets repo, flatbuffers release artifact, and Makefile.

Risks: shell glob `. /**/*.sh` style may miss root-level scripts depending on shell behavior, though container shell likely expands recursive glob. Secret scan history can be slow.

Test signals: CI job statuses across lint/security/config gates.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/prebuild.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/releases.yml -->
# sources/cloud-native/soci-snapshotter/.github/workflows/releases.yml

Purpose: builds, validates, and drafts GitHub release artifacts for semver tags.

Important APIs/types/functions: jobs `setup`, `generate-artifacts`, `validate-artifacts`, and `create-release`; Make target `release`; script `verify-release-artifacts.sh`; artifact upload/download; `softprops/action-gh-release`.

Control flow: on tag push or release-related PRs, builds release artifacts across available runners, sets release tag and output names, creates dummy license/tag values for PR testing, uploads release artifacts, validates them per runner, and on tag push creates a draft GitHub release with merged assets.

State and persistence: creates release tarballs in workspace, GitHub artifacts, and draft release assets on tag pushes.

Dependencies/integration: uses setup matrix, Makefile release target, static library installation on AL2 ARM, and GitHub release permissions.

Risks: output names hard-code `linux-amd64` even matrix includes `al2-arm`, so naming should be verified against scripts. PR path tests use dummy tag and empty license file.

Test signals: PR workflow validates artifact generation/verification; tag push validates draft release creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/releases.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/review-dependencies.yml -->
# sources/cloud-native/soci-snapshotter/.github/workflows/review-dependencies.yml

Purpose: runs GitHub dependency review for Go dependency changes.

Important APIs/types/functions: pull_request trigger for `go.*` and `cmd/go.*`; `actions/dependency-review-action@v5`; config file `.github/dependency-review-config.yml`; `comment-summary-in-pr: always`.

Control flow: checks out PR code and invokes dependency review with license policy, writing PR comments.

State and persistence: comments on PRs and may fail checks; no code writes.

Dependencies/integration: paired with dependency review config and Go module files.

Risks: only Go module path changes trigger it; Docker/GitHub Actions dependency changes are governed elsewhere.

Test signals: PRs modifying `go.mod`/`go.sum` should produce dependency review comments.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/review-dependencies.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/setup.yml -->
# sources/cloud-native/soci-snapshotter/.github/workflows/setup.yml

Purpose: reusable workflow that chooses CI runner labels for SOCI Snapshotter workflows.

Important APIs/types/functions: workflow_call outputs `available-runners` and `runner-labels`; matrix entry with `use-codebuild`, CodeBuild runner names `ubuntu-x86` and `al2-arm`, fallback GitHub runner `ubuntu`.

Control flow: determines whether repository owner is `awslabs`; upstream uses CodeBuild labels, forks use Ubuntu GitHub-hosted runner. Outputs JSON arrays/maps for downstream workflow matrices.

State and persistence: no persistent state; prints matrix config.

Dependencies/integration: consumed by build and release workflows.

Risks: CodeBuild label naming embeds run id and attempt; downstream workflows depend on matching configured AWS CodeBuild projects. Forks get reduced platform coverage.

Test signals: downstream matrix expansion in build/release workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/setup.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/update-version-in-docs.yml -->
# sources/cloud-native/soci-snapshotter/.github/workflows/update-version-in-docs.yml

Purpose: validates and automates documentation version updates for SOCI releases.

Important APIs/types/functions: triggers workflow dispatch/call/release/pull_request/release-branch push; input `tag_name`; script `scripts/update-version-in-docs.sh`; creates PRs with `peter-evans/create-pull-request`.

Control flow: PRs sparsely check out docs and script, then assert an update with a dummy version. Non-PR events derive tag and target branch from input, GitHub release event, or release branch plus latest-release API lookup, check out docs/script, run update script, and open an automated PR.

State and persistence: edits docs in PR branches and creates pull requests.

Dependencies/integration: called by release branch workflow and release events; relies on docs paths `docs/eks.md` and `docs/getting-started.md`.

Risks: API parsing with grep/cut/awk can select wrong tags. Workflow skips GitHub-action-authored branch pushes to avoid loops. Only selected docs are sparse-checked out.

Test signals: PR assertion job and automated PR creation on release events or branch pushes.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.github/workflows/update-version-in-docs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.golangci.yml -->
# sources/cloud-native/soci-snapshotter/.golangci.yml

Purpose: golangci-lint v2 configuration for SOCI Snapshotter.

Important APIs/types/functions: enables `copyloopvar`, `misspell`, `revive`, `staticcheck`, `unconvert`, and `errorlint`; disables `errcheck`; configures staticcheck exclusions, revive unused-parameter rule suppression, generated lax exclusions, path exclusions, gofmt/goimports formatters, and 3-minute timeout.

Control flow: `prebuild.yml` runs golangci-lint against root and `cmd` working directories using this configuration.

State and persistence: no runtime state; affects lint pass/fail and formatter checks.

Dependencies/integration: pairs with `golangci/golangci-lint-action` and repo layout.

Risks: disabling `errcheck` can miss ignored error bugs. Excluding docs/images/out/script/third_party/builtin/examples reduces noise but can hide Go files under those paths.

Test signals: lint job statuses in CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.yamllint.yml -->
# sources/cloud-native/soci-snapshotter/.yamllint.yml

Purpose: yamllint configuration for repository YAML files.

Important APIs/types/functions: extends default; ignores trailing spaces in issue templates; disables document-start, comments, and line-length; permits truthy values `true`, `false`, and `on`.

Control flow: `prebuild.yml` runs `yamllint .` with this policy.

State and persistence: no runtime state.

Dependencies/integration: supports GitHub workflow and issue template syntax preferences.

Risks: disabling line length/comments reduces strictness. The truthy rule allows `on`, required for GitHub Actions, while still restricting other truthy spellings.

Test signals: yamllint CI job.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/.yamllint.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/Dockerfile -->
# sources/cloud-native/soci-snapshotter/Dockerfile

Purpose: multi-stage Dockerfile for SOCI Snapshotter integration/runtime test image with registry, containerd, runc, nerdctl, crictl, igzip, rapidgzip, and built SOCI binaries.

Important APIs/types/functions: build args for containerd/runc/nerdctl/crictl/igzip/rapidgzip versions; stages `registry`, `igzip-builder`, `rapidgzip-builder`, and `containerd-snapshotter-base`; copies `soci` and `soci-snapshotter-grpc` from `out/`; installs configs and systemd units.

Control flow: builder stages compile ISA-L static libraries and rapidgzip, with ARM-specific ISA-L/fcf-protection disables. Final Amazon Linux stage installs utilities, copies built binaries/configs/services, downloads containerd/runc/nerdctl/crictl release artifacts for target architecture, and prepares integration entrypoint/config paths.

State and persistence: image layers contain built dependencies, SOCI binaries, containerd tooling, systemd units, and config files.

Dependencies/integration: used by integration tests and Makefile/CI Docker build flows; depends on external GitHub releases and Amazon ECR public images.

Risks: network downloads are not checksum-verified. `dnf update && dnf upgrade` can reduce reproducibility. Static rapidgzip build has architecture-specific workarounds.

Test signals: Docker build success and integration tests using the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/Makefile -->
# sources/cloud-native/soci-snapshotter/Makefile

Purpose: central developer/CI build orchestration for SOCI Snapshotter binaries, flatbuffers, tests, coverage, integration tests, release artifacts, and benchmarks.

Important APIs/types/functions: targets `soci-snapshotter-grpc`, `soci`, `flatc`, `install`, `clean`, `tidy`, `vendor`, `gen-config`, `test`, `test-with-coverage`, `integration`, `integration-with-coverage`, `release`, `go-benchmarks`, `benchmarks-*`; variables for version/revision ldflags, static build tags, package lists, output/coverage dirs, benchmark binaries.

Control flow: default builds both commands. `soci-snapshotter-grpc` regenerates FlatBuffers first. Coverage targets compose Go build/test flags with `GOCOVERDIR`. Integration uses gotestsum with env gates. Release delegates to scripts. Benchmark targets build and run performance/comparison/stargz/parser tools.

State and persistence: writes binaries to `out/`, coverage to `cov/`, release artifacts to `release/`, generated FlatBuffer Go code, config files, and benchmark output. Clean removes these plus integration Docker leftovers.

Dependencies/integration: used by all GitHub workflows, Dockerfile, scripts, Go modules, flatc, Docker, and gotestsum.

Risks: static build ldflags and package-list shell commands are complex. Clean target includes Docker removal by name/reference. Generated FlatBuffer code can be stale if flatc version differs.

Test signals: CI invokes build, unit, coverage, integration, release, and benchmark targets.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/benchmarkTests.go -->
# sources/cloud-native/soci-snapshotter/benchmark/benchmarkTests.go

Purpose: benchmark workload functions comparing normal containerd overlayfs pulls/runs, SOCI lazy pulls/runs, and stargz lazy pulls/runs.

Important APIs/types/functions: `fatalf`, `PullImageFromRegistry`, `SociRPullPullImage`, `SociFullRun`, `OverlayFSFullRun`, `StargzFullRun`, `getContainerdProcess`, `getSociProcess`, and `getStargzProcess`.

Control flow: each benchmark starts isolated containerd and optional snapshotter processes, resets the benchmark timer around the measured flow, pulls images, creates containers/tasks, waits for a ready line, reports custom metrics (`pullDuration`, `unpackDuration`, `lazyTaskDuration`, `localTaskStats`), stops timers for cleanup, and tears down processes.

State and persistence: uses `/tmp` containerd/snapshotter roots, state dirs, and sockets; writes process logs under `./output`; deletes runtime state in process cleanup.

Dependencies/integration: depends on benchmark framework, containerd client, SOCI/stargz process starters elsewhere in benchmark package, image descriptors, and logrus/containerd logging.

Risks: closure use in callers must capture loop variables correctly. Benchmarks depend on external registries, host networking, root privileges, and ready-line correctness. Cleanup errors are mostly printed rather than fatal.

Test signals: Make benchmark targets and CI benchmark workflows produce result metrics.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/benchmarkTests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/comparisonTest/main.go -->
# sources/cloud-native/soci-snapshotter/benchmark/comparisonTest/main.go

Purpose: executable benchmark runner that compares OverlayFS full runs and SOCI full runs across configured image workloads.

Important APIs/types/functions: flags `-show-commit`, `-count`, and `-f`; uses `benchmark.GetCommitHash`, `GetDefaultWorkloads`, `GetImageList`, `framework.GetTestContext`, `BenchmarkTestDriver`, and `BenchmarkFramework.Run`.

Control flow: parses flags, chooses commit tag, loads default or JSON image descriptors, creates output directory/log file, builds a context with JSON logging, appends two benchmark drivers per image, and runs the framework to produce JSON results.

State and persistence: writes `../comparisonTest/output/benchmark_log` and `results.json`.

Dependencies/integration: built/run by Makefile `benchmarks-comparison-test` and CI comparison workflow.

Risks: loop variables `shortName` and `image` are captured by closures; with Go versions before per-iteration loop variable semantics this would make all drivers use the last image. Output dir creation does not clean existing files except log truncation.

Test signals: benchmark output JSON and log file; CI cat of results.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/comparisonTest/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/containerd_soci_config.toml -->
# sources/cloud-native/soci-snapshotter/benchmark/containerd_soci_config.toml

Purpose: minimal containerd config for benchmarks using SOCI snapshotter as a proxy plugin.

Important APIs/types/functions: TOML `version = 2`, debug level `DEBUG`, `[proxy_plugins.soci]` with type `snapshot` and socket address `/tmp/soci-snapshotter-grpc/soci-snapshotter-grpc.sock`.

Control flow: containerd loads this config when benchmark code starts containerd for SOCI flows.

State and persistence: no persistent state; directs containerd to the SOCI snapshotter socket.

Dependencies/integration: used by `getContainerdProcess` in benchmark tests and Make benchmark targets.

Risks: hard-coded `/tmp` socket must match SOCI process startup. Debug logging can be verbose.

Test signals: SOCI benchmark startup and containerd proxy plugin registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/containerd_soci_config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/containerd_stargz_config.toml -->
# sources/cloud-native/soci-snapshotter/benchmark/containerd_stargz_config.toml

Purpose: minimal containerd config for benchmarks using stargz snapshotter as a proxy plugin.

Important APIs/types/functions: TOML `version = 2`, debug level `DEBUG`, `[proxy_plugins.stargz]` with type `snapshot` and address `/tmp/containerd-stargz-grpc/containerd-stargz-grpc.sock`.

Control flow: containerd loads this file for Stargz benchmark flows and routes snapshot operations to the stargz socket.

State and persistence: no persistent state; configuration-only.

Dependencies/integration: used by `StargzFullRun` through `getContainerdProcess`.

Risks: hard-coded socket must match the stargz process. Debug logs may influence benchmark I/O.

Test signals: stargz benchmark run successfully creating containers with snapshotter `stargz`.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/containerd_stargz_config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/framework/containerd_utils.go -->
# sources/cloud-native/soci-snapshotter/benchmark/framework/containerd_utils.go

Purpose: framework utilities for starting/stopping containerd and driving container lifecycle operations during benchmarks.

Important APIs/types/functions: `ContainerdProcess`, `StartContainerd`, `StopProcess`, `PullImage`, `DeleteImage`, `CreateContainer`, `TaskDetails`, `CreateTask`, `RunContainerTaskForReadyLine`, `GetRemoteOpts`, `GetTestContext`, and `newClient`.

Control flow: `StartContainerd` launches a containerd subprocess with custom address/root/state/config and opens log files, then creates a client. Lifecycle helpers create containers/tasks with unique IDs, attach pipes, start tasks, watch stdout/stderr for a ready line or process exit/timeout, and provide cleanup closures that kill/delete tasks and remove roots/state/sockets.

State and persistence: creates `/tmp` roots/state/sockets and output log files, then removes them on stop. It also sets containerd namespace and logging context.

Dependencies/integration: used by all benchmark workloads; depends on containerd v2 client, cio, namespaces, logrus, and host `containerd` binary.

Risks: `StopProcess` kills without waiting. Timeout path in `RunContainerTaskForReadyLine` returns nil error even if ready line never appears. Pipe scanner goroutines may outlive briefly until cleanup closes pipes.

Test signals: benchmark success and absence of leftover processes/state; targeted tests should validate timeout semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/framework/containerd_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/framework/framework.go -->
# sources/cloud-native/soci-snapshotter/benchmark/framework/framework.go

Purpose: benchmark execution framework that repeatedly runs test drivers, gathers metrics, computes descriptive statistics, and writes JSON results.

Important APIs/types/functions: `BenchmarkFramework`, `BenchmarkTestStats`, `BenchmarkTestDriver`, `Run`, `calculateStats`, and `calculateTestStat`.

Control flow: initializes Go testing flags with one iteration per benchmark, loops through drivers, runs optional before hooks, calls `testing.Benchmark` the requested number of times, records total duration and custom extra metrics converted from milliseconds to seconds, computes standard deviation/mean/min/percentiles/max using `montanaflynn/stats`, runs optional after hook, marshals the framework to `results.json`.

State and persistence: accumulates metrics in memory and writes JSON under `OutputDir`.

Dependencies/integration: used by comparison/performance benchmark executables and visualization workflows.

Risks: missing custom metrics default to zero in `res.Extra`, which can hide benchmark functions that forgot to report metrics. `os.MkdirAll` uses file permission `0644`, which lacks execute bits for directories and may fail or create unusable dirs on some systems.

Test signals: benchmark result JSON schema consumed by visualization tooling; unit tests should cover stats with empty/one-item samples.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/framework/framework.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/framework/parser/file_access.go -->
# sources/cloud-native/soci-snapshotter/benchmark/framework/parser/file_access.go

Purpose: parses SOCI benchmark logs to summarize FUSE file access patterns relative to container task start time.

Important APIs/types/functions: package `bparser`; `FileAccessPatterns`, `SociLog`, `BaseOperation`, `Operation`, `ParseFileAccesses`, and `getTaskStartTime`.

Control flow: `ParseFileAccesses` obtains task start time from containerd logs, scans SOCI stderr JSON lines, filters messages equal to `FUSE operation`, groups by operation+path, records first access offset and count, totals operations by type, sorts operations by first access time, and writes per-image JSON under `file_access_logs`. `getTaskStartTime` scans containerd stderr for `/tasks/start` and parses the leading `time=` field.

State and persistence: reads `./output/soci-snapshotter-stderr` and `containerd-stderr`; writes `./output/file_access_logs/<image>_access_patterns`.

Dependencies/integration: intended for benchmark parser tooling and SOCI FUSE log format.

Risks: scanner assumes every SOCI log line is JSON and every containerd start line has a specific text format. If no task start is found, zero time is returned without explicit error. Keying by concatenated operation+path can theoretically collide.

Test signals: parser tests with representative log lines, malformed JSON, no start line, duplicate operations, and sort order.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/framework/parser/file_access.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/framework/utils.go -->
# sources/cloud-native/soci-snapshotter/benchmark/framework/utils.go

Purpose: registry pull helper utilities for benchmark containerd processes.

Important APIs/types/functions: `ContainerdProcess.PullImageFromRegistry` and `GetResolver`.

Control flow: `PullImageFromRegistry` adds platform remote opts plus a Docker resolver and calls containerd client pull. `GetResolver` parses the image reference, loads default Docker CLI config, extracts credentials for the hostname if present, configures Docker resolver hosts with those credentials, and uses an in-memory push tracker.

State and persistence: reads Docker credential config from the user environment; no writes.

Dependencies/integration: used by benchmark workloads pulling private/public images; depends on containerd remotes/docker config and Docker CLI config loading.

Risks: parse errors panic instead of returning errors. Credential callback returns the same username/password for any host passed to it, though values are selected from the parsed ref hostname. Auth helpers depend on local Docker config availability in CI.

Test signals: pull tests with public images, private registry credentials, invalid image refs, and missing Docker config.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/framework/utils.go -->
