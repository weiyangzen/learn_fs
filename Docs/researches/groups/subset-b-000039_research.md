# subset-b-000039 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/tar_split.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-storage/src/tar_split.rs

Purpose: Implements tar-split metadata consumption for containers-storage layers. It reads gzip-compressed NDJSON tar-split streams, returns raw tar segments, and opens layer file contents as owned file descriptors so callers can reconstruct or stream layer tars without serializing file payloads into memory.

Important APIs and types: `TarSplitItem` exposes `Segment(Vec<u8>)` and `FileContent { fd, size, name }`. `TarSplitEntryRaw` is the serde-facing NDJSON shape; `TarSplitEntry::from_raw` validates type ids 1 and 2. `TarHeader::from_bytes` parses 512-byte tar headers with `tar_core` and exposes helpers for regular files, directories, links, and normalized names. `TarSplitFdStream::new`, `next`, `entry_count`, `open_file_in_chain`, parent-layer search helpers, and `verify_crc64` are the core runtime surface.

Control flow: `new` opens `overlay-layers/<layer>.tar-split.gz`, wraps it in `GzDecoder` and `BufReader`, reopens the `Layer`, and clones the storage root dir. `next` loops over metadata lines, decodes segment payloads directly, and for file entries with nonzero size opens the path from the current layer or lower layers. Parent lookup follows overlay `lower` files and `overlay/l/<link>` symlinks recursively with a depth cap of 500. If a CRC64 value is present, the file is read, checked, rewound, and then converted into an `OwnedFd`.

State and persistence: The stream keeps only the active layer handle, storage root `Dir`, reader position, and an entry counter. It reads persistent state from containers-storage overlay and overlay-layers directories but does not mutate storage. File descriptors transfer ownership to callers.

Dependencies and integration: Uses `cap_std` for capability-oriented path access, `flate2`, `serde_json`, `base64`, `crc`, `tar_core`, and local `Storage`/`Layer`/`StorageError`. It feeds `userns_helper` streaming and any caller needing file-descriptor-backed tar reconstruction.

Risks: Path names are normalized only by stripping leading `./`; malicious or malformed tar-split paths rely on `cap_std` directory confinement. Parent traversal treats any `TarSplitError` as branch-not-found in some recursive paths, which can hide non-not-found tar-split errors. CRC verification is full-file I/O and may be expensive. Symlink-target parsing for overlay links assumes `../<layer-id>/diff`. Non-UTF-8 tar header paths are rejected.

Test signals: Unit tests cover tar header type helpers and type-id deserialization, including invalid types. More integration coverage would need real overlay/tar-split fixtures, CRC mismatch cases, parent chain lookup, and malformed overlay links.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/tar_split.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/userns.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-storage/src/userns.rs

Purpose: Provides the permission-bypass probe used to decide whether rootless containers-storage access needs a helper running inside `podman unshare`.

Important APIs and types: The single public API is `can_bypass_file_permissions() -> bool`. It checks whether the current process is real root or has `CAP_DAC_OVERRIDE` in its effective capability set.

Control flow: The function first calls `rustix::process::getuid()` and returns true for UID 0. Otherwise it calls `rustix::thread::capabilities(None)` and checks `CapabilitySet::DAC_OVERRIDE`. Capability-query failure is nonfatal and falls through to false.

State and persistence: There is no persisted state. The result reflects current process credentials and effective capabilities at the moment of the call.

Dependencies and integration: Depends on `rustix` process and thread capability APIs. `StorageProxy::spawn` in `userns_helper.rs` uses this as a fast path to skip spawning a user namespace helper when the current process can already read restrictive overlay files.

Risks: It only tests DAC override style permission bypass. Other access-control systems, mount namespaces, LSM policy, or missing execute permissions on parent directories can still affect real file access. A transient capabilities error is treated as "cannot bypass", causing a helper spawn attempt.

Test signals: The unit test verifies deterministic repeated results and asserts root returns true. It does not emulate Linux capability combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/userns.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/userns_helper.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-storage/src/userns_helper.rs

Purpose: Implements a JSON-RPC plus fd-passing helper for rootless storage access. Parent processes spawn themselves through `podman unshare`; the child enters helper mode, opens otherwise unreadable files or storage layers, and returns file descriptors over a Unix socket.

Important APIs and types: Public request/result structs cover `openFile`, `listImages`, `getImage`, and `streamLayer`. `HelperError` wraps spawn, IPC, I/O, and RPC failures. `init_if_helper` is the required early-main entry point. `StorageProxy` manages child process lifecycle and RPC calls. `ProxiedLayerStream` yields `ProxiedTarSplitItem::{Segment, FileContent}` from streaming notifications.

Control flow: `StorageProxy::spawn` skips helper creation when `userns::can_bypass_file_permissions` returns true. Otherwise `spawn_helper_with_binary` creates a socketpair, runs `podman unshare env __CSTORAGE_USERNS_HELPER=1 <exe>`, and wires the child stdin to the socket. In helper mode, `init_if_helper` duplicates stdin, installs a parent-death signal, creates a current-thread Tokio runtime, and enters `run_helper_loop_async`. Requests are decoded with `jsonrpc_fdpass`; normal methods send one response, while `streamLayer` sends multiple `stream.segment` or `stream.file` notifications and a final response.

State and persistence: Runtime state is the child process, socket transport halves, monotonically increasing JSON-RPC ids, and stream completion flag. It reads containers-storage state through `Storage`, `Image`, `Layer`, and `TarSplitFdStream`; it does not persist mutations. `Drop` kills the child if still running.

Dependencies and integration: Integrates `podman`, `/proc/self/exe`, Unix socket fd passing via `jsonrpc_fdpass`, Tokio Unix streams, `rustix` fd/process helpers, and composefs-storage image/layer/tar-split modules. It is the privileged access path for APIs that need rootless overlay contents with restrictive permissions.

Risks: `podman` must be installed and `init_if_helper` must be called early by binaries using the library. `Drop` is forceful and may kill a helper with in-flight work. `openFile` opens arbitrary absolute paths passed by the parent, so caller trust boundaries matter. Streaming assumes ordered notifications on a single receiver; concurrent RPCs while streaming would need careful sequencing. Several `serde_json::to_value(...).unwrap()` calls can panic only if serialization of internal structs fails, but fuzzing does not cover this module.

Test signals: No local unit tests are visible in this file. Practical coverage should include helper spawn failure, graceful shutdown, fd-passing round trips, malformed RPC messages, stream ordering, and rootless integration with actual containers-storage.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/userns_helper.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/Cargo.toml -->
# sources/cloud-native/composefs-rs/crates/composefs/Cargo.toml

Purpose: Defines the `composefs` Rust library crate metadata, feature flags, dependencies, development dependencies, and workspace lints.

Important APIs and types: This manifest does not export Rust APIs, but it controls compile-time feature surfaces. Features are `pre-6.15` and `test` for `tempfile`, `rhel9` for pre-6.15 plus `composefs-ioctls/loop-device`, and `varlink` for optional `zlink-core`.

Control flow: Cargo resolves core dependencies for EROFS read/write, dumpfile parsing, hashing, async process support, serialization, and zerocopy layout handling. Optional dependencies are activated through features, while dev-dependencies enable capability-safe temp dirs, snapshots, property testing, and executable-gated tests.

State and persistence: The manifest persists crate configuration and participates in workspace inheritance for edition, license, readme, repository, rust-version, version, and lints.

Dependencies and integration: Runtime dependencies include `anyhow`, `composefs-ioctls`, `serde`, `serde_repr`, `fn-error-context`, `hex`, `log`, `once_cell`, `rustix`, `serde_json`, `sha2`, `thiserror`, `tokio`, `xxhash-rust`, `zerocopy`, `zstd`, `rand`, and `tokio-stream`. It integrates with optional `zlink-core` and feature-gated `tempfile`.

Risks: Feature names encode kernel or distribution assumptions; downstream builds must select compatible flags. `rand = 0.10.0` and `sha2 = 0.11.0` may imply newer APIs than older distributions carry. Optional feature coupling should stay aligned with code-level `cfg` gates.

Test signals: Dev-dependencies indicate snapshot, property, async, and external executable tests. The fuzz crate depends on this package by path.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/fuzz/Cargo.toml -->
# sources/cloud-native/composefs-rs/crates/composefs/fuzz/Cargo.toml

Purpose: Configures the cargo-fuzz harness crate for `composefs`.

Important APIs and types: Declares package `composefs-fuzz`, `publish = false`, `cargo-fuzz = true`, its own workspace boundary, dependency on `libfuzzer-sys`, and path dependency on the parent `composefs` crate.

Control flow: Cargo exposes three binaries: `read_image`, `debug_image`, and `generate-corpus`. The first two are libFuzzer targets with tests/docs/bench disabled; the third is a normal corpus generator binary.

State and persistence: The manifest persists fuzz target registration and isolates the fuzz crate from the parent workspace, as required by cargo-fuzz.

Dependencies and integration: Integrates with `cargo fuzz`, LLVM libFuzzer through `libfuzzer-sys`, and the local `composefs` crate. Corpus generation writes under the fuzz crate's `corpus` directories.

Risks: The fuzz crate is intentionally not published and should remain outside normal workspace release semantics. Target names and paths must stay synchronized with files under `fuzz_targets/`.

Test signals: The existence of registered targets is itself a coverage signal for EROFS reader/debug panic resistance. `generate-corpus` seeds both fuzz targets with structured images.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/fuzz/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/fuzz/fuzz_targets/debug_image.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/fuzz/fuzz_targets/debug_image.rs

Purpose: Fuzz target for the EROFS debug dumper.

Important APIs and types: Imports `composefs::erofs::debug::debug_img` and calls it from `fuzz_target!(|data: &[u8]| ...)`, writing output to `io::sink()`.

Control flow: Every arbitrary byte slice is passed to `debug_img`. Return values are ignored; the invariant is that malformed input returns errors rather than panicking.

State and persistence: Stateless. It allocates only whatever the debug path allocates for parsing/traversal and does not write output because the writer is a sink.

Dependencies and integration: Depends on `libfuzzer_sys`, `std::io`, and the `composefs` debug module. It pairs with the corpus generated by `generate_corpus.rs`.

Risks: It only checks panic freedom for the debug entry point. It does not assert textual output stability, semantic correctness, or performance under large inputs. Because output is discarded, formatting regressions require separate tests.

Test signals: Strong signal for panic safety in `debug_img`, especially around zerocopy parsing, image traversal, overlapping segment detection, and malformed directory/xattr data.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/fuzz/fuzz_targets/debug_image.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/fuzz/fuzz_targets/read_image.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/fuzz/fuzz_targets/read_image.rs

Purpose: Fuzz target for EROFS image reading and high-level conversion APIs.

Important APIs and types: Uses `Image`, `InodeHeader`, `InodeOps`, `collect_objects`, `erofs_to_filesystem`, and `dumpfile::write_dumpfile`. The helper `exercise_image` walks as many reachable reader APIs as possible.

Control flow: The target tries `Image::open`; invalid images are ignored. For valid openings, it reads superblock fields, root inode metadata, xattrs, inline data, inode blocks, data blocks, directory entries, child inodes, object collection, and optional filesystem conversion followed by dumpfile serialization.

State and persistence: Stateless and in-memory. No corpus mutation is performed by the target itself; libFuzzer owns input generation.

Dependencies and integration: Integrates reader, fs-verity SHA-256 object collection, tree conversion, and dumpfile serialization, creating broader coverage than a parser-only target.

Risks: Traversal loops over entries and blocks from untrusted images; the reader must enforce bounds to avoid panics or excessive work. The target intentionally ignores errors, so it detects crashes but not missed validation or incorrect conversion.

Test signals: Excellent panic-safety signal for reader methods, xattr iteration, inline data handling, directory block parsing, block addressing, high-level conversion, and dumpfile writer interaction.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/fuzz/fuzz_targets/read_image.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/fuzz/generate_corpus.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/fuzz/generate_corpus.rs

Purpose: Generates valid seed EROFS images for fuzz targets, covering distinct filesystem shapes and format versions.

Important APIs and types: Defines `Dir` and `Inode` aliases over `Sha256HashValue`, helper constructors `stat`, `dir_stat`, `file_stat`, `empty_root`, `insert_dir`, `push_all_versions`, and Linux `makedev`. Uses `ValidatedFileSystem`, `mkfs_erofs`, and `mkfs_erofs_versioned`.

Control flow: `main` builds a vector of named image bytes. For each logical filesystem, `push_all_versions` emits V2, V1, and V0 variants. Fixtures include empty root, inline and external files, symlink, FIFO, character/block devices, socket, nested dirs, many entries, xattrs, mixed types, hardlinks, large inline data, deep nesting, nonzero mtimes, and large uid/gid. It creates corpus directories for `read_image` and `debug_image`, writes every seed to both, and prints a size summary.

State and persistence: Writes corpus files under `crates/composefs/fuzz/corpus/<target>/<seed>`. The generated bytes reflect writer behavior at generation time, so corpus updates can track intentional format changes.

Dependencies and integration: Integrates the generic tree model, fs-verity hash values, EROFS writer, and fuzz target directory layout. It can be run through the manifest path or repository task runner.

Risks: Uses `unwrap`/panic on corpus write failures, appropriate for a developer tool but not a library API. The corpus is only as broad as the manually listed cases and does not include corrupt images; libFuzzer mutation provides that.

Test signals: The selected seeds exercise inline/external data, special file types, xattrs, hardlinks, directory layouts, mtime/uid/gid edge cases, and all supported format versions.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/fuzz/generate_corpus.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/dumpfile.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/dumpfile.rs

Purpose: Serializes `FileSystem` trees to composefs dumpfile text and rebuilds trees from parsed dumpfile entries. It bridges the internal tree model, dumpfile syntax, hardlink semantics, and EROFS validation.

Important APIs and types: Public writer APIs are `write_directory`, `write_leaf`, `write_hardlink`, `write_dumpfile`, `dump_single_dir`, and `dump_single_file`. Reader/conversion APIs are `add_entry_to_filesystem`, `dumpfile_to_filesystem`, and `dumpfile_to_validated_filesystem`. `DumpfileWriter` tracks hardlinks and nlink counts during traversal.

Control flow: Serialization writes root and sorted directory entries recursively. `write_entry` emits path, size, mode, nlink, uid/gid, rdev, mtime, payload, content, digest, and xattrs. It uses sentinel-aware escaping for normal fields and raw escaping for xattr key/value pairs. Leaf serialization distinguishes inline regular files, external fs-verity objects, devices, fifos, sockets, and symlinks. For repeated `LeafId`s, the first occurrence is serialized normally and later occurrences become hardlink lines. Parsing requires the first non-empty line to be root, then inserts entries into parent directories, resolving hardlinks through a path-to-`LeafId` map.

State and persistence: The module writes dumpfile bytes to supplied writers and builds in-memory `FileSystem` values from strings. It does not manage files directly. Temporary state includes hardlink maps, nlink maps, and buffered output.

Dependencies and integration: Depends on `dumpfile_parse::{Entry, Item}`, `generic_tree`, `tree`, `fsverity`, `rustix::fs::FileType`, and EROFS writer validation. It is exercised by the EROFS fuzz target when reader conversion succeeds.

Risks: Dumpfile parsing currently accepts `&str`, so non-UTF-8 dumpfile bytes cannot round-trip through `dumpfile_to_filesystem`. Parent directories must appear before children. External regular entries require a digest. Hardlinked whiteout character devices are rejected because composefs cannot represent them correctly.

Test signals: Unit tests cover simple conversion, hardlinks, dash symlink target round trips, xattr empty/dash round trips, hardlink writer round trips, hardlinked whiteout rejection, escape behavior, and proptest round trips for SHA-256/SHA-512 filesystem specs.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/dumpfile.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/dumpfile_parse.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/dumpfile_parse.rs

Purpose: Parses and displays individual composefs dumpfile entries and wraps `composefs-info dump` execution.

Important APIs and types: `Xattr`, `Xattrs`, `Mtime`, `Entry`, and `Item` model dumpfile records. Core parsing helpers are `unescape_limited`, `unescape_to_osstr`, `unescape_to_path`, `unescape_to_path_canonical`, `Xattr::parse`, `Mtime::from_str`, and `Entry::parse`. `Entry::filter_special`, `Item` accessors, `Display` impls, `DumpConfig`, and `dump` are the integration surface.

Control flow: `Entry::parse` splits space-delimited fields, canonicalizes absolute paths, parses octal mode and hardlink prefix, and dispatches by `rustix::fs::FileType`. Hardlinks ignore all metadata except payload target. Regular entries become inline content or external object references depending on payload. Symlink targets are not canonicalized, but path length is bounded. Xattrs are parsed from `key=value`, size-limited, and sorted for deterministic output. `dump` spawns `composefs-info dump`, streams stdout lines through `Entry::parse`, filters overlay special xattrs, and reports stderr if the command fails.

State and persistence: Parser state is per-line. `dump` launches an external process and consumes a supplied image `File`; it does not persist changes itself.

Dependencies and integration: Depends on `anyhow`, `rustix::fs::FileType`, `MAX_INLINE_CONTENT`, `SYMLINK_MAX`, and external `composefs-info`. `dumpfile.rs` consumes `Entry` and `Item` for filesystem construction.

Risks: The parser uses simple space splitting, making escaping correctness critical. Display for xattr values still uses standard escaping, noted as slightly divergent from C, while the higher-level writer avoids that path. External command integration depends on `composefs-info` availability. A diagnostic uses `found={keylen}` for an oversized value, likely a minor message bug.

Test signals: Tests cover unescaping limits, canonical path rejection, xattr parsing and length limits, parse/display idempotence, directory size canonicalization, hardlink metadata canonicalization, xattr ordering, expected failures, and executable-gated `mkcomposefs` round trips including filters.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/dumpfile_parse.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/erofs/composefs.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/erofs/composefs.rs

Purpose: Defines composefs-specific EROFS overlay metadata for fs-verity metacopy digests.

Important APIs and types: `OverlayMetacopy<H: FsVerityHashValue>` is a `repr(C)` zerocopy struct with private version, length, flags, digest algorithm fields and public `digest`. `new`, `valid`, and private field accessors provide construction and validation.

Control flow: `new` fills version 0, struct length, flags 0, digest algorithm from the hash type's kernel id, and clones the digest. `valid` checks that all metadata fields match the expected current encoding for hash type `H`.

State and persistence: This is an on-disk/xattr binary layout type. It has no runtime state beyond struct contents and is intended to be serialized/deserialized by zerocopy.

Dependencies and integration: Depends on `zerocopy` derives and `FsVerityHashValue`. It is used by EROFS writer/reader code that encodes overlayfs metacopy xattrs containing fs-verity digests.

Risks: The `len` field is `u8`, so layout growth beyond 255 bytes would require a format change. Validation is type-specific; digest algorithm mismatch is rejected. Because fields are private, external callers cannot forge metadata except through raw bytes.

Test signals: No tests in this file; coverage should come from EROFS xattr/metacopy writer-reader tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/erofs/composefs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/erofs/debug.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/erofs/debug.rs

Purpose: Provides debug formatting and whole-image inspection for composefs EROFS images, including structure dumps, path attribution, padding/unknown-region reporting, and space statistics.

Important APIs and types: Exposes `dump_unassigned` and `debug_img`. Implements `Debug` for format headers, reader inodes, xattrs, directory blocks, and data blocks. Internal `SegmentType` and `ImageVisitor` classify and traverse image regions.

Control flow: `debug_img` opens an `Image`, uses `ImageVisitor::visit_image` to walk from the root inode iteratively, then emits all visited segments in offset order. The visitor records header, superblock, inodes, shared xattrs, inline and external directory blocks, and data blocks, deduplicating by byte offset to handle hardlinks and cycles. Gaps between known segments are dumped as zero padding or unknown hexdump. At the end it prints per-segment and padding transition size percentages.

State and persistence: All state is in-memory: visited segment map, traversal stack, path lists, and statistics maps. Output is written to the supplied writer; input image bytes are not modified.

Dependencies and integration: Depends on EROFS `format` and `reader` modules, `zerocopy::FromBytes`, and `anyhow`. Fuzz target `debug_image.rs` continuously tests this entry point against arbitrary data.

Risks: Debug code traverses untrusted image structures, so bounds checks in reader APIs are critical. The visitor includes conflict detection for overlapping segments but still must avoid excessive traversal; iterative stack avoids call-stack overflow. Debug output is not a stable machine API unless explicitly treated as such.

Test signals: Direct tests are absent, but `debug_image` fuzzing targets panic resistance. The implementation also contains comments referencing a prior recursion depth problem that was addressed by iterative traversal.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/erofs/debug.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/erofs/format.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/erofs/format.rs

Purpose: Defines the zerocopy EROFS and composefs on-disk ABI: headers, constants, mode/file type encoding, format versions, feature flags, inode layouts, xattr structures, and directory entry headers.

Important APIs and types: Key exports include `BLOCK_BITS`, `BLOCK_SIZE`, `FormatError`, `FormatField`, `InodeLayout`, `DataLayout`, mode constants, `FileType`, `FileTypeField`, `ModeField`, `FormatVersion`, `FormatEpoch`, `FormatConfig`, `ComposefsHeader`, `Superblock`, `CompactInodeHeader`, `ExtendedInodeHeader`, `InodeXAttrHeader`, `XAttrHeader`, xattr constants/prefixes, and `DirectoryEntryHeader`.

Control flow: This file is mostly declarative, but conversions are important. `FormatField` maps raw bits to inode layout and fallible data layout. `InodeLayout | DataLayout` builds a `FormatField`. `FileTypeField` maps raw directory entry values to `FileType`, defaulting unknown values to `Unknown`. `FileType | permissions` constructs raw mode fields. `FormatVersion::epoch` collapses V0/V1 to compact-inode epoch 1 and V2 to extended-inode epoch 2. `FormatConfig::versions` yields default first and sorted extras excluding duplicates.

State and persistence: These structs are persisted directly in image bytes via `repr(C)` and little-endian `zerocopy` integer wrappers. `FormatConfig` is persisted in metadata JSON and controls which image format variants are generated.

Dependencies and integration: Depends on `zerocopy`, `serde`, and `serde_repr`. Reader, writer, debug, corpus generation, and repository metadata all consume these definitions.

Risks: This file is ABI-sensitive; field order, widths, and endianness cannot change casually. Unknown feature flags and unsupported xattr prefix differences matter for compatibility with C `mkcomposefs`, especially V0/V1. V1 deliberately skips `lustre.` prefix matching for C compatibility. `FileType::Unknown` must be handled by readers rather than passed into mode construction.

Test signals: Unit tests cover `FormatConfig` single/multi/dedup behavior, ordering, epoch mapping, and composefs version field values. Broader layout correctness is indirectly tested by reader/writer round trips and fuzz seeds.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/erofs/format.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/erofs/mod.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/erofs/mod.rs

Purpose: Module root for composefs EROFS support.

Important APIs and types: Re-exports submodules by declaring `composefs`, `debug`, `format`, `reader`, and `writer`.

Control flow: There is no runtime control flow. Rust module resolution uses this file to make the EROFS submodules available as `composefs::erofs::*`.

State and persistence: No state. It defines namespace structure only.

Dependencies and integration: Integrates the composefs-specific overlay metadata, debug utilities, on-disk format definitions, reader, and writer into one public module tree.

Risks: Public module declarations expose these submodules to crate users; renaming or hiding them would be an API change. Keeping reader/writer available here enables fuzz targets and callers to use stable paths.

Test signals: No direct tests are needed beyond compile coverage from imports throughout the crate and fuzz targets.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/erofs/mod.rs -->
