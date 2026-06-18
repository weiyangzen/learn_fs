# subset-b-000038 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/skopeo.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-oci/src/skopeo.rs

### Purpose
This module is the OCI image pull path for `composefs-oci`. It opens an image reference through `containers-image-proxy`/skopeo, fetches manifests, configs, and blobs, imports layer content into a composefs `Repository`, and records config and manifest splitstreams with named references to their dependent layers. It also contains the local OCI layout fast path and the delta artifact path.

### Important APIs, Types, and Functions
`PullResult<ObjectID>` carries manifest digest/verity and config digest/verity, with `into_config()` and `into_manifest()` compatibility helpers. The content type constants identify splitstreams: `TAR_LAYER_CONTENT_TYPE`, `OCI_CONFIG_CONTENT_TYPE`, `OCI_MANIFEST_CONTENT_TYPE`, and `OCI_BLOB_CONTENT_TYPE`. `ImageOp` owns the repository, proxy, opened image, reporter, and transport. `ImageOp::new()` validates write access, applies containers-storage-specific skopeo/podman handling, and opens the image. `ensure_layer()` imports or reuses a layer. `ensure_config_with_layers()` imports or reuses config and all referenced layers. `pull()` stores the manifest and detects delta artifacts. `ProxyBlobReader` adapts skopeo blob access for delta import. Public entry points are `pull_image()` and backward-compatible `pull()`.

### Control Flow
`pull_image()` first ensures the repo is writable and parses `imgref`. `oci:` references bypass skopeo and call `oci_layout::import_oci_layout`; all other transports construct `ImageOp` and call `pull()`. `ImageOp::pull()` fetches raw OCI manifest bytes, parses them, dispatches delta artifacts to `pull_delta()`, otherwise imports config and layers, then writes a manifest splitstream if missing. `ensure_config_with_layers()` first checks for an existing config splitstream; on cache hit it reads named layer refs back from the config stream. On miss it downloads the config, extracts diff IDs, sorts layer downloads by descending size, limits concurrency with `available_parallelism()`, imports layers in parallel, then writes a config splitstream with named refs keyed by diff ID. `ensure_layer()` checks the repository for an existing layer stream. Missing tar layers are downloaded, progress-wrapped, decompressed, and passed to `import_tar_async`; non-tar artifact blobs are stored raw and wrapped in an `OCI_BLOB_CONTENT_TYPE` stream. After pull, `pull_image()` calls `ensure_oci_composefs_erofs()` for container images and tags artifacts directly.

### State and Persistence
Persistent state is the composefs repository: objects, stream IDs, stream content IDs, named stream references, image tags, and generated EROFS references. Layer content IDs are derived from diff IDs, config content IDs from config digests, and manifest content IDs from manifest digests. Cache hits short-circuit network and storage work. Delta blobs are temporarily copied to repo tmpfiles before apply.

### Dependencies and Integration Points
This file integrates `containers-image-proxy`, skopeo/podman, `tokio`, composefs repository APIs, `layer` import helpers, OCI image tagging/manifests, delta import, progress reporting, and OCI layout import. It handles transport quirks for rootless `containers-storage:` and digest references.

### Risks
Correctness depends on proxy driver futures being awaited so skopeo validates content. Parallel layer sorting returns task indexes from sorted order, but final layer refs are reconstructed by diff ID, which avoids order corruption unless duplicate diff IDs appear. Existing config streams must contain all named layer refs or cache hit reconstruction fails. Non-tar artifacts intentionally skip tar import and EROFS generation. Rootless containers-storage behavior relies on external podman/skopeo availability.

### Test Signals
No tests live in this file, but behavior is covered indirectly by OCI image construction, layout import, layer import, manifest/tagging, delta, and repository tests elsewhere. The main test indicators are cache reuse, config named-ref reconstruction, non-tar artifact handling, local OCI layout fast path, delta import, and rootless containers-storage reference normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/skopeo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/tar.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-oci/src/tar.rs

### Purpose
This module converts tar layer byte streams into composefs splitstreams and reads those splitstreams back into structured tar entries. It preserves tar bytes closely enough for OCI diff ID verification while moving large regular file content into external fs-verity objects.

### Important APIs, Types, and Functions
`split_async()` is the async tar-to-splitstream writer. `get_entry()` reads one logical tar entry from a `SplitStreamReader`. `TarItem<ObjectID>` models directory, leaf content, and hardlink entries. `TarEntry<ObjectID>` combines absolute path, `Stat`, and `TarItem`, and implements `Display` using dumpfile writers. Helpers include `pax_mtime_nsec()` for subsecond PAX mtime parsing, `receive_and_finalize_object()` for blocking tmpfile finalization, `stream_large_file()` for background external object streaming, and `make_absolute_path()` for tar path normalization.

### Control Flow
`split_async()` uses `tar_core::Parser` as a sans-IO tar parser and a `BytesMut` buffer. It reads enough bytes for the parser, handles global extensions inline, rejects sparse entries, and handles end-of-archive by preserving extra GNU record padding through EOF. For normal entries it writes headers and extension bytes inline, computes storage size rounded to 512 bytes, and chooses a content strategy. Regular files larger than `INLINE_CONTENT_MAX_V0` are streamed through an mpsc channel into a blocking task that writes a repository tmpfile and finalizes it as an external object; the splitstream builder records the external handle and then stores tar padding inline. Smaller files and non-file entries keep content and padding inline. `get_entry()` accumulates header blocks until `tar_core` emits a parsed entry, reads the stored payload from the splitstream as inline or external, maps tar entry types to composefs leaf content, extracts xattrs and PAX nanoseconds, and returns absolute paths.

### State and Persistence
The module persists splitstreams and external content objects in the composefs repository. Large file object writes use tmpfiles, fs-verity finalization, and object store methods surfaced through `ImportStats`. The splitstream stores tar metadata, small payloads, padding, and external object references, preserving byte-exact archive reconstruction through `SplitStreamReader::cat()`.

### Dependencies and Integration Points
It depends on `tar-core` parsing, `bytes`, `tokio` async IO and mpsc, `rustix::fs::makedev`, composefs splitstream/repository/tree/dumpfile types, and OCI import stats. It is called by layer import paths such as `skopeo.rs` for tar media types.

### Risks
The parser rejects sparse entries, so images using sparse tar extensions are unsupported. Large file streaming must consume exactly the file content before parsing continues; channel failure handling explicitly awaits the writer task because continuing would corrupt parser alignment. `actual_size as usize` can be risky on platforms where huge tar entries exceed addressable memory. `get_entry()` assumes external chunks only represent regular/continuous files and enforces inline/external threshold invariants. Path normalization strips leading and trailing slashes and maps bare root to an empty path, which is a deliberate composefs convention.

### Test Signals
The file has extensive tests: PAX mtime parsing, absolute path normalization, empty tar, GNU record padding preservation, small/large threshold behavior, byte-exact round trips, special filenames, GNU long names and long links, USTAR prefix handling, multiple large external files, long path and hardlink table tests, property tests across path lengths, hardlink targets, file sizes, and tar byte round trips. An ignored benchmark exercises large tar split throughput.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/tar.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/test_util.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-oci/src/test_util.rs

### Purpose
This file provides test utilities for building deterministic OCI images and filesystems from composefs dumpfile strings. It is the fixture layer for integration and unit tests that need realistic multi-layer container images, bootable OS images, SELinux policy content, xattrs, deduplication behavior, and generated EROFS references.

### Important APIs, Types, and Functions
`dumpfile_to_tar()` converts composefs dumpfile lines into tar bytes. `create_multi_layer_image()` imports each dumpfile layer, builds OCI config and manifest objects, stores config splitstreams with named layer refs, and writes a tagged manifest. `TestImage` returns manifest digest, manifest verity, and config digest. The builder API is `OsImage` with `minimal()`, `bootable()`, `with_selinux()`, `with_layer()`, `build_oci()`, and `build_filesystem()`. Compatibility helpers include `create_base_image()`, `create_bootable_image()`, `create_test_oci_image()`, `create_test_bootable_oci_image()`, `ensure_erofs_for_image()`, and test-only `build_oci_layout()`.

### Control Flow
`dumpfile_to_tar()` parses each non-empty dumpfile line, skips root, strips leading slash for tar paths, collects xattrs, and creates directory, regular file, or symlink tar entries. Inline regular files use literal content; external dumpfile regular files get deterministic pseudo-random bytes seeded by size. Xattrs are encoded by `append_with_xattrs()` as PAX `SCHILY.xattr.*` records before the real entry. `create_multi_layer_image()` hashes tar bytes for diff IDs, imports each layer through `crate::import_layer()`, builds an OCI image config with ordered diff IDs, writes a config splitstream referencing layer verities, builds the manifest descriptors, hashes the manifest JSON, and calls `write_manifest()`. `OsImage::layer_strings()` assembles base, boot, version-specific, shared, SELinux, and caller-provided layers before delegating to the multi-layer builder.

### State and Persistence
The utilities write into a composefs test repository: imported layer streams, config stream, manifest stream, optional tag refs, generated EROFS objects, and optional boot image objects. They also create temporary OCI layout directories for tests. Shared layer constants intentionally produce identical content across boot image versions so GC and deduplication behavior can be tested.

### Dependencies and Integration Points
The file integrates `composefs::dumpfile_parse`, repository APIs, `containers_image_proxy` OCI spec builders, `sha2`, `tar`, `tar_core` PAX builder, `rand`, `ocidir`, `cap-std-ext`, `composefs_boot` transform tests, and crate-local image/layer/boot helpers.

### Risks
These helpers panic on malformed fixture input, which is acceptable for tests but not production. Path and xattr handling assumes UTF-8 dumpfile paths and xattr keys. The fake external content is deterministic by size, so same-sized external files can have identical generated content unless differentiated elsewhere. The module bypasses full pull paths, so tests using it should call `ensure_erofs_for_image()` when they need mountable image refs.

### Test Signals
Tests validate dumpfile-to-tar conversion for directories, files, executables, and symlinks; creation of base and bootable images; SELinux layer inclusion; custom layer injection into a merged filesystem; bootable filesystem shape; and GC behavior when versioned boot images share most layers but differ in kernel/initramfs/modules/UKI layers.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/test_util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-setup-root/Cargo.toml -->
## sources/cloud-native/composefs-rs/crates/composefs-setup-root/Cargo.toml

### Purpose
This manifest defines the `composefs-setup-root` binary crate, an initramfs setup tool for composefs-based boot. It participates in the workspace and inherits edition, license, readme, repository, Rust version, version, and lints.

### Important APIs, Types, and Functions
As a Cargo manifest, its important API surface is feature and dependency selection. Features are `default = ["pre-6.15"]`, `rhel9 = ["composefs/rhel9"]`, and `pre-6.15 = ["composefs/pre-6.15"]`. The default feature selects compatibility behavior for kernels before 6.15.

### Control Flow
Cargo resolves this crate as a binary package. Feature flags flow into the Rust code via `cfg!(feature = "pre-6.15")`, changing whether the new root is mounted early or after submount setup. `rhel9` and `pre-6.15` propagate to the `composefs` workspace crate.

### State and Persistence
The manifest itself has no runtime persistence. It determines which dependencies are built into the setup tool and therefore which mount/repository behavior is available at early boot.

### Dependencies and Integration Points
Runtime dependencies include `anyhow`, `fn-error-context`, `clap`, `composefs`, `composefs-boot`, `env_logger`, `hex`, `rustix`, `serde`, and `toml`. `similar-asserts` is used for tests. The dependency set reflects a low-level boot utility: command-line parsing, TOML config parsing, digest parsing, composefs repository/mount APIs, boot command line parsing, and Linux mount syscalls through `rustix`.

### Risks
Defaulting to `pre-6.15` materially changes mount sequencing and can hide newer floating-tree behavior unless disabled. The crate uses low-level mount APIs, so dependency feature changes can affect initramfs footprint and syscall availability. `env_logger` is present but the current code does not configure much logging.

### Test Signals
The manifest exposes only `similar-asserts` as a dev dependency. The Rust tests in `src/main.rs` focus on command-line digest parsing rather than mount behavior, which is difficult to unit-test without privileged/kernel-specific environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-setup-root/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-setup-root/src/main.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-setup-root/src/main.rs

### Purpose
This binary is an early-boot root filesystem setup tool. It reads the composefs image address from the kernel command line, mounts the composefs root image or a test root filesystem, overlays or bind-mounts mutable subdirectories, preserves old `/sysroot` when present, and replaces the initramfs `/sysroot` with the composed root.

### Important APIs, Types, and Functions
Config types are `MountType`, `RootConfig`, `MountConfig`, and `Config`, parsed from TOML. `Args` defines CLI/test options for command, sysroot path, config path, root-fs override, cmdline override, and target. Helpers include `open_dir()`, `ensure_dir()`, `bind_mount()`, `mount_tmpfs()`, `overlay_state()`, `overlay_transient()`, `open_root_fs()`, `mount_composefs_image()`, `mount_subdir()`, `gpt_workaround()`, `parse_image_address()`, `setup_root()`, and `main()`.

### Control Flow
`main()` parses CLI args, runs `gpt_workaround()` best-effort, then calls `setup_root()`. `setup_root()` reads optional TOML config, opens sysroot, obtains cmdline text, parses a SHA-512 composefs digest first and falls back to legacy SHA-256 on invalid length, then obtains `new_root` either by bind-cloning `--root-fs` or mounting a composefs image from `sysroot/composefs`. It clones the current sysroot, optionally mounts early for `pre-6.15`, optionally overlays the whole root transiently, attempts to mount old sysroot under the new root, opens per-image state under `state/deploy/<image_addr>`, mounts `etc` and `var` according to config/defaults, and on newer kernels detaches and replaces `/sysroot`.

### State and Persistence
Persistent state is outside the binary: composefs repository under sysroot, image-specific state under `state/deploy/<digest>`, overlay `upper` and `work` directories, and `/run/systemd/volatile-root` symlink from the GPT workaround. Transient mode uses tmpfs-backed overlay state. `overlay_state()` intentionally creates `upper` as 0755 so merged directory permissions do not block non-root services.

### Dependencies and Integration Points
The code integrates `rustix` mount/fs syscalls, composefs repository and mount APIs, overlayfs mount compatibility helpers, `composefs_boot::cmdline`, `clap`, `serde`/`toml`, and digest types for SHA-256/SHA-512. It depends on kernel mount API behavior, overlayfs, EROFS/composefs support, and systemd GPT auto-root behavior.

### Risks
Most behavior requires privileges and early-boot filesystem state, so unit coverage is necessarily narrow. Mount sequencing differs by `pre-6.15`; mistakes can leave abandoned mounts or fail to replace sysroot. The `cmd` and `target` args are currently parsed but not used in `setup_root()`, suggesting testing hooks or future behavior may be incomplete. `gpt_workaround()` ignores errors, which is deliberate best-effort behavior but can hide integration issues. The image digest length dispatch assumes SHA-512 is 128 hex and SHA-256 is 64 hex.

### Test Signals
The included test verifies invalid command lines fail, SHA-256 legacy digests still parse, and SHA-512 digests parse and round-trip to hex. Mount, overlay, config, and state behavior are not unit-tested here because they require kernel and privilege conditions.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-setup-root/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-splitfdstream/Cargo.toml -->
## sources/cloud-native/composefs-rs/crates/composefs-splitfdstream/Cargo.toml

### Purpose
This manifest defines the unpublished `composefs-splitfdstream` library crate, which implements a binary format for streams that mix inline bytes with external file descriptor references.

### Important APIs, Types, and Functions
Cargo metadata names the crate, description, keywords, and `publish = false`. The runtime dependency is `rustix` with `fs` and `std` features. Dev dependencies are `proptest` and `tempfile`. Workspace lints are enabled.

### Control Flow
The manifest keeps the crate small and independent. Tests pull in property testing and temporary files, while production only needs standard IO and `rustix` support for fd-relative/positional reads used in test-only reconstruction helpers.

### State and Persistence
No runtime state is defined by the manifest. It controls whether the stream format implementation is included as a private workspace crate and ensures it is not published independently.

### Dependencies and Integration Points
`rustix` provides low-level file descriptor IO support used by the library's test adapters. `proptest` is important because the stream format has many chunk ordering and boundary cases. `tempfile` supports external fd reconstruction tests.

### Risks
Because `publish = false`, downstream users should depend on it through the workspace, not crates.io. The crate has no serde or async dependencies, which keeps the wire format implementation simple but means higher-level fd passing protocols must be implemented elsewhere.

### Test Signals
The manifest enables extensive unit and property tests in `src/lib.rs`, including arbitrary chunk sequence round trips, external fd reconstruction, same-fd reuse, bounds errors, and inline size limit checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-splitfdstream/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-splitfdstream/src/lib.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-splitfdstream/src/lib.rs

### Purpose
This library implements the splitfdstream wire format: a sequential binary stream where chunks are either inline bytes or references to external file descriptors. It is useful for passing mostly inline metadata plus large externally supplied payloads over fd-passing transports.

### Important APIs, Types, and Functions
`MAX_INLINE_CHUNK_SIZE` caps inline chunk reads at 256 MiB. `Chunk<'a>` is `Inline(&'a [u8])` or `External(u32)`. `SplitfdstreamWriter<W>` provides `new()`, `write_inline()`, `write_external()`, and `finish()`. `SplitfdstreamReader<R>` provides `new()`, `into_inner()`, and `next_chunk()`. Test-only helpers include `ReadAtReader`, `SplitfdstreamAsRead`, and `reconstruct()`.

### Control Flow
Writers encode each inline chunk as a negative signed 64-bit little-endian prefix followed by that many bytes. Empty inline chunks are skipped. External chunks encode the fd index as a non-negative signed 64-bit little-endian prefix and carry no inline payload. Readers attempt to read an 8-byte prefix; any `UnexpectedEof` while reading the prefix is treated as clean stream end. Negative prefixes allocate/read an inline buffer after enforcing the 256 MiB maximum. Non-negative prefixes yield `Chunk::External(prefix as u32)`. Test reconstruction reads inline data directly and external data from the selected file, using `pread` wrappers so repeated references to the same fd start at offset zero each time.

### State and Persistence
Runtime state is limited to the wrapped reader/writer and the reader's reusable inline buffer. The stream format has no header, footer, checksum, or embedded external length, so external chunk size is defined by the referenced fd content as interpreted by the receiver.

### Dependencies and Integration Points
The production implementation uses only `std::io`. Test-only code uses `rustix::io::pread`, file descriptors, `tempfile`, and `proptest`. Higher layers are expected to pass the stream fd and external fds out of band; this crate only serializes references.

### Risks
Partial prefix reads return `Ok(None)`, so truncated streams shorter than 8 trailing bytes are accepted as EOF. External indexes are encoded from `u32`, but reader casts any non-negative `i64` to `u32`, so malformed prefixes above `u32::MAX` would wrap rather than error. Because external chunks contain no length, reconstruction reads whole files; callers needing subranges need a higher-level protocol. Inline chunks allocate a buffer of the declared size, bounded by 256 MiB.

### Test Signals
Tests cover empty streams, inline-only, external-only, mixed/interleaved chunks, boundary sizes, fd index zero and max u32, skipped empty inline chunks, many small chunks, alternating patterns, truncated prefix/data handling, inline limit enforcement, reconstruction with external fds, out-of-bounds external refs, large external files, repeated fd references, `into_inner()`, and property tests for arbitrary chunk sequences and read-adapter equivalence.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-splitfdstream/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/Cargo.toml -->
## sources/cloud-native/composefs-rs/crates/composefs-storage/Cargo.toml

### Purpose
This manifest defines the `composefs-storage` library crate, which provides read-only access to containers-storage overlay driver data and tar-split reconstruction support.

### Important APIs, Types, and Functions
The package metadata names storage, overlay, Podman, and Buildah keywords. Feature `userns-helper` enables optional `jsonrpc-fdpass`, `tokio`, and `tracing` support. Default features are empty. The manifest also enables workspace lints.

### Control Flow
Cargo builds the base storage library with capability-oriented filesystem access, OCI parsing, JSON/TOML parsing, compression, CRC, and tar-core support. Enabling `userns-helper` adds async networking/fd-passing dependencies for helper/proxy behavior without imposing them on default builds.

### State and Persistence
The manifest has no runtime state, but its dependency choices define the crate's access model: read-only overlay storage inspection, layer/image metadata parsing, tar-split gzip/zstd processing, and optional user namespace helper communication.

### Dependencies and Integration Points
Key dependencies are `cap-std` and `cap-std-ext`, `oci-spec`, `serde_json`, `toml`, `tar-core`, `flate2`, `zstd`, `crc`, `sha2`, `rustix`, `thiserror`, and optional `jsonrpc-fdpass`/`tokio`/`tracing`. This shows integration with containers-storage layouts, OCI metadata, compressed tar-split files, Linux permission/capability checks, and optional fd proxying.

### Risks
The crate defaults to no helper feature, so rootless storage access requiring helper/proxy support must opt in. Multiple parser/compression dependencies increase attack surface for untrusted storage metadata, making the fd-relative and read-only design important. Version differences in containers-storage layout can affect runtime behavior more than the manifest can express.

### Test Signals
The manifest supplies `tempfile` for filesystem-layout tests in `storage.rs` and `layer.rs`. Other module tests use only normal test dependencies and validate config parsing, manifest parsing, whiteout/opaque handling, and discovery parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/config.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-storage/src/config.rs

### Purpose
This module parses containers-storage `storage.conf`-style TOML data into Rust structures. It captures the configured driver, primary root, runtime root, additional image stores, and additional layer store settings.

### Important APIs, Types, and Functions
`StorageConfig` has fields `driver`, `root`, `run_root`, `image_stores`, and `layer_stores`, all deserialized with defaults. `AdditionalLayerStore` has `path` and `with_reference`. `StorageConfig::from_toml()` wraps `toml::from_str`.

### Control Flow
There is no complex runtime control flow. Callers pass TOML text to `from_toml()`, serde fills missing fields with defaults, and nested `[[layer_stores]]` entries deserialize into `AdditionalLayerStore` values.

### State and Persistence
The module does not read files itself and stores no global state. It creates an in-memory configuration value from caller-provided content. Path fields are `PathBuf`s and can represent system, user, or additional store locations.

### Dependencies and Integration Points
It depends on `serde::Deserialize`, `toml`, and `PathBuf`. The parsed data is intended to feed storage discovery/opening code, though the current `storage.rs` also has environment/default-root discovery paths.

### Risks
The module does not validate driver values, path existence, or overlay support; it only parses. The documentation examples show `[storage]` tables, but the struct shape as written expects fields at the current TOML level unless callers deserialize a containing type elsewhere. Empty defaults can hide missing configuration unless validation is done by the caller.

### Test Signals
Tests cover basic parsing of `driver` and `root`, and parsing a `[[layer_stores]]` entry with `with_reference = true`. There are no tests for `[storage]` nesting, `image_stores`, `run_root`, invalid TOML, or validation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/error.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-storage/src/error.rs

### Purpose
This module defines the storage crate's error model and result alias. It centralizes user-facing failure categories for storage discovery, image/layer lookup, link resolution, tar-split processing, IO, and JSON parsing.

### Important APIs, Types, and Functions
`pub type Result<T> = std::result::Result<T, StorageError>` is the crate result alias. `StorageError` derives `thiserror::Error` and includes `RootNotFound(PathBuf)`, `InvalidStorage(String)`, `LayerNotFound(String)`, `ImageNotFound(String)`, `LinkReadError(String)`, `TarSplitError(String)`, `Io(std::io::Error)`, and `JsonParse(serde_json::Error)`.

### Control Flow
The enum is consumed throughout the storage crate via `?`, manual mapping, and `From` conversions for IO and JSON. More specific variants are used when lookup or validation semantics matter, while lower-level failures are wrapped in `Io`, `InvalidStorage`, or `LinkReadError`.

### State and Persistence
The module has no persistence. It preserves contextual data in variant payloads, such as missing root paths, missing layer/image IDs, and invalid storage messages.

### Dependencies and Integration Points
It depends on `thiserror`, `PathBuf`, `std::io`, and `serde_json`. It is re-exported from `lib.rs` and used by `config`, `image`, `layer`, `storage`, and tar-split/userns modules.

### Risks
Many call sites wrap structured IO failures into string-bearing `InvalidStorage` or `LinkReadError`, which is readable but less machine-actionable. `JsonParse` has a `From` impl, but some JSON parse sites deliberately map to `InvalidStorage` to add file context, so consumers should not rely on every JSON failure using the same variant.

### Test Signals
There are no direct tests for this file. It is exercised indirectly by storage validation tests, image/layer lookup tests, JSON parsing paths, and tar-split error propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/image.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-storage/src/image.rs

### Purpose
This module represents and reads images from containers-storage `overlay-images/<image-id>/`. It provides raw and parsed manifest access, config access from base64-keyed metadata files, diff ID extraction, storage layer ID resolution, metadata reads, and image name lookup.

### Important APIs, Types, and Functions
`Image` stores an image ID and a `cap_std::fs::Dir` handle to its image directory. Public methods include `open()`, `id()`, `read_manifest_raw()`, `manifest()`, `config()`, `layers()`, `storage_layer_ids()`, `read_metadata()`, `image_dir()`, and `names()`. `ImageJsonEntry` models `overlay-images/images.json` entries with `id` and optional `names`.

### Control Flow
`Image::open()` strips a leading `sha256:` prefix, opens `overlay-images`, then opens the image ID directory or returns `ImageNotFound`. `read_manifest_raw()` preserves exact manifest bytes; `manifest()` parses JSON. `config()` constructs the key `sha256:<id>`, base64-encodes it, reads the corresponding `=<key>` metadata file, and parses `ImageConfiguration`. `layers()` extracts rootfs diff IDs from config and strips `sha256:` prefixes. `storage_layer_ids()` resolves all diff IDs across a slice of `Storage` values, allowing layers to span additional stores. `names()` scans `images.json` for matching ID and returns stored names.

### State and Persistence
The module is read-only. Persistent state lives in containers-storage: manifest files, base64-prefixed metadata files, and `images.json`. Open `Dir` handles maintain capability-scoped access to image directories.

### Dependencies and Integration Points
It uses `base64`, `cap_std`, `oci_spec::image`, `serde_json`, and crate `Storage`/`StorageError`. It integrates with `Storage::resolve_diff_ids()` and is used by storage listing, image lookup, layer lookup, and size calculation paths.

### Risks
Config metadata lookup assumes the config key is based on `sha256:<image-id>`, which follows the documented layout but can fail for layout variants. `layers()` returns normalized diff IDs without `sha256:`, while `resolve_diff_ids()` re-adds the prefix; callers must understand the distinction between OCI diff IDs and storage layer IDs. `storage_layer_ids()` ignores stores whose `layers.json` cannot be read, which helps multi-store fallback but can hide broken stores if another store resolves all layers. `names()` returns empty if the image directory exists but the index lacks the ID.

### Test Signals
The local test validates OCI manifest JSON parsing. Runtime behavior is also indirectly covered by storage tests and any integration tests using real or mocked containers-storage layouts. There are no direct tests for config metadata base64 lookup, multi-store resolution, or names lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/image.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/layer.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-storage/src/layer.rs

### Purpose
This module models containers-storage overlay layers. It opens layer directories, exposes diff content, reads short link IDs and lower parent links, resolves parent chains, and detects overlay whiteout and opaque-directory markers.

### Important APIs, Types, and Functions
`Layer` stores full layer ID, layer directory handle, diff directory handle, short link ID, and parent link IDs. Public methods include `open()`, `id()`, `link_id()`, `parent_links()`, `parents()`, `layer_dir()`, `diff_dir()`, `layer_chain()`, `open_file()`, `open_file_std()`, `metadata()`, `read_dir()`, `has_whiteout()`, and `is_opaque_dir()`. Internal helpers `read_link()` and `read_lower()` parse layer metadata files.

### Control Flow
`Layer::open()` opens `overlay/<id>`, `diff/`, reads `link`, and parses optional `lower`. `read_lower()` treats missing `lower` as a base layer and otherwise parses colon-separated `l/<link-id>` references. `parents()` maps parent link IDs through `Storage::resolve_link()`. `layer_chain()` walks from self through all parents breadth-first by appending opened parent layers until exhaustion or `MAX_DEPTH = 500`. File operations delegate to the `diff_dir` handle. `has_whiteout()` checks `.wh.<filename>` in root or a parent directory. `is_opaque_dir()` checks `.wh..wh..opq` in root or a target directory, returning false for missing directories.

### State and Persistence
The module reads persistent overlay storage state: `overlay/<layer-id>/diff`, `link`, `lower`, whiteout files, and opaque markers. It stores only open directory handles and parsed metadata in memory.

### Dependencies and Integration Points
It uses `cap_std::fs::Dir`, crate `Storage`, and `StorageError`. It is used by storage layer retrieval, tar-split reconstruction, chain traversal, and any direct layer file access logic.

### Risks
The layer chain traversal has a depth cap but no explicit visited set, so cycles below 500 entries will eventually hit the depth error rather than reporting a cycle. `read_lower()` silently ignores lower components without `l/`, which may hide malformed lower files. Whiteout checks are existence-based and do not validate marker file type. Path inputs are passed to `cap_std` APIs, so capability scoping helps, but callers still need to avoid semantic confusion from unusual relative paths.

### Test Signals
Tests cover lower-file parsing, mock layer opening, whiteout detection in root/subdirectories/nested directories/nonexistent parents/multiple files, opaque marker detection in root/subdirectories/normal dirs/nonexistent/nested paths, coexistence of whiteout and opaque markers, and the `.wh..wh.` edge case that is a whiteout for `.wh.` rather than an opaque marker.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/layer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/lib.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-storage/src/lib.rs

### Purpose
This is the public facade for the `composefs-storage` crate. It documents the read-only, capability-based approach to containers-storage overlay access and re-exports the crate's primary modules and types.

### Important APIs, Types, and Functions
Modules exported are `config`, `error`, `image`, `layer`, `storage`, `tar_split`, and `userns`, plus feature-gated `userns_helper`. Re-exports include `AdditionalLayerStore`, `StorageConfig`, `Result`, `StorageError`, `Image`, `Layer`, `LayerMetadata`, `Storage`, `TarHeader`, `TarSplitFdStream`, `TarSplitItem`, `can_bypass_file_permissions`, optional helper/proxy types, and OCI `Descriptor`, `ImageConfiguration`, and `ImageManifest`.

### Control Flow
There is no runtime control flow beyond module loading and feature-gated exports. The file enforces clippy denials for stdout/stderr in non-test library code, which guides diagnostics toward returned errors or logging rather than direct printing.

### State and Persistence
This facade stores no state. It defines the crate boundary through which callers access persistent containers-storage data via `Storage`, `Image`, `Layer`, and tar-split stream types.

### Dependencies and Integration Points
The crate facade integrates internal modules with external consumers and re-exports OCI spec types to reduce dependency friction. Optional `userns-helper` exports expose fd-passing proxy support only when the feature is enabled.

### Risks
The public API exposes low-level storage concepts directly, so semver changes in module types can affect consumers. The module docs mention SQLite database access, but the current researched files use JSON metadata and directory layouts rather than SQLite, so documentation may be partially stale. Feature-gated exports require consumers to compile with matching features before helper types are available.

### Test Signals
No direct tests exist in this facade. Its test signal is successful compilation of downstream module tests and doctest-like examples that use `Storage::discover()` and common re-exports.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/storage.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-storage/src/storage.rs

### Purpose
This module provides the main read-only `Storage` handle for containers-storage overlay roots. It opens and validates storage roots, discovers default and additional image stores, resolves overlay links and diff IDs, lists/finds images, opens image layers, reads layer metadata, and computes image size.

### Important APIs, Types, and Functions
`Storage` wraps a capability-scoped root `Dir`. Public methods include `open()`, `discover()`, `discover_all()`, `from_root_dir()`, `root_dir()`, `resolve_link()`, `list_images()`, `get_image()`, `get_image_layers()`, `find_image_by_name()`, `resolve_diff_ids()`, `resolve_diff_id()`, `get_layer_metadata()`, and `calculate_image_size()`. Internal helpers include `default_search_paths()`, `validate_storage()`, `additional_image_stores_from_env()`, `parse_additional_image_stores()`, `extract_layer_id_from_link()`, and `read_layer_entries()`. Data structs are internal `LayerEntry` and public `LayerMetadata`.

### Control Flow
`open()` opens a root path with ambient authority and validates required directories: `overlay`, `overlay-layers`, and `overlay-images`. `discover()` tries `$CONTAINERS_STORAGE_ROOT`, rootless XDG/home paths, and `/var/lib/containers/storage`. `discover_all()` combines primary discovery with valid `STORAGE_OPTS=additionalimagestore=<path>` entries. Link resolution reads `overlay/l/<link-id>` symlink targets and extracts the second-to-last component from `../<layer-id>/diff`. Image listing opens every directory under `overlay-images`. Name lookup scans `images.json` for exact names, suffix matches with slash boundary, and short names with implicit `:latest`. Diff ID resolution parses `overlay-layers/layers.json` once, builds a normalized digest map, and returns same-length `Option<String>` results. Image size calculation resolves layers and sums available `diff_size` values with saturating addition.

### State and Persistence
The module is read-only over persistent containers-storage directories and JSON files: `overlay`, `overlay/l`, `overlay-layers/layers.json`, `overlay-images`, and `overlay-images/images.json`. It stores only a root directory handle in memory. Environment variables affect discovery but are not mutated.

### Dependencies and Integration Points
It uses `cap_std` for fd-relative operations, standard environment/path/io APIs, `serde_json`, and crate `Image`, `Layer`, and `StorageError`. It integrates with `image.rs` for image opening and diff ID extraction, and with `layer.rs` for layer opening and metadata.

### Risks
Validation only checks required directories, not `layers.json` or `images.json`, so later calls can fail after `open()` succeeds. `discover()` silently skips invalid existing paths and reports a generic failure if none work. Additional image stores from `STORAGE_OPTS` silently skip inaccessible paths. `extract_layer_id_from_link()` is string-based and assumes the usual `../<layer-id>/diff` target shape. Name suffix matching is convenient but can be ambiguous if multiple names share suffixes. `calculate_image_size()` ignores layers with missing `diff_size`.

### Test Signals
Tests cover default search path generation, minimal storage validation with required directories, and parsing additional image stores from `STORAGE_OPTS` including empty, single, multiple, nonexistent, and unrelated options. There are no direct tests for `images.json` name matching, symlink target parsing, diff ID resolution, layer metadata, or size calculation.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-storage/src/storage.rs -->
