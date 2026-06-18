# subset-b-000036 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/varlink.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/varlink.rs

Purpose: this is the end-to-end integration suite for the `cfsctl` varlink RPC surface. It starts the real `cfsctl varlink` or `cfsctl oci varlink` process, connects over a temporary Unix socket, opens a composefs repository through `org.composefs.Repository.OpenRepository`, and then drives repository and OCI methods as an external client would. The file intentionally mixes `varlinkctl` calls for wire-level/systemd interop with zlink generated Rust proxy calls for typed reply and typed error validation.

Important APIs and helpers: `VarlinkService` owns the child process, socket path, repository handle, Tokio runtime, and socket tempdir. Its `Drop` implementation kills and waits on the child. `spawn` builds the service command, waits up to ten seconds for the socket, opens the repo, and creates a current-thread runtime for proxy calls. `open_repository` calls `varlinkctl` directly and parses the first non-empty JSON or JSON-SEQ line. `repository` and `oci` are CLI-entry wrappers. `inject_handle`, `call`, `call_raw`, `call_more`, `call_expect_err`, and `run` centralize handle injection, streaming `--more` parsing, and varlinkctl error handling. `proxy_inspect`, `proxy_image_objects`, `proxy_init_repository`, and `proxy_pull` exercise typed `OciProxy` and `RepositoryProxy` bindings, including streaming `PullProgress`.

Control flow: tests create temporary insecure repositories and fixtures, perform setup through CLI commands such as `create-image` or `oci pull`, spawn the varlink service, and assert JSON or typed replies. Repository coverage includes fsck for empty, healthy, metadata-only, and corrupted repos; GC dry-run behavior; image object listing and sorted object IDs; handle open/close invalidation; invalid open specs; invalid handles; unknown close; and `InitRepository` creation, idempotency, invalid algorithm, and typed proxy behavior. OCI coverage includes list/filter, check, inspect, tag/untag, compute-id parity with CLI, streaming pull over raw varlinkctl and zlink, bad-image pull failure, bootable-pull behavior, same-socket serving of Repository and Oci interfaces, and systemd-style `exec:` socket activation.

State and persistence: every test isolates repository storage under tempdirs produced by integration helpers. The service maintains repository handles in process memory; callers must pass a handle, and helper methods auto-inject the opened handle except for negative tests. Pull, tag, GC, fsck, inspect, and compute-id assertions validate persisted repository state by checking refs, manifests, config JSON, object IDs, and later calls after mutation. Socket activation is intentionally single-call because each `varlinkctl exec:` launch creates a fresh process and fresh handle table.

Dependencies and integration points: the suite depends on built `cfsctl`, systemd `varlinkctl`, zlink generated proxies from `composefs_ctl::varlink`, `serde_json`, `tokio`, `xshell`, and integration fixture helpers from `tests::cli`. It verifies the public RPC contract between the CLI service implementation and both generic varlink tooling and generated typed clients.

Risks: the suite is environment-sensitive: missing `varlinkctl`, unavailable built binaries, slow socket startup, or root/filesystem behavior can fail tests outside the code under test. Many assertions inspect raw JSON field names, so varlink schema changes require coordinated test updates. The child kill in `Drop` is robust for normal cases but does not inspect child exit status. The typed proxy tests reduce the risk of false positives where raw JSON only proves "some" reply shape.

Test signals: all functions are registered through `integration_test!`. The file gives high-value regression signals for handle semantics, JSON-SEQ streaming, typed error variants such as `NoSuchImage`, `NoSuchRef`, `InvalidSpec`, and `InvalidHandle`, one-socket multi-interface serving, repository mutation persistence, and socket activation wiring.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/varlink.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ioctls/Cargo.toml -->
## sources/cloud-native/composefs-rs/crates/composefs-ioctls/Cargo.toml

Purpose: this manifest defines the small `composefs-ioctls` crate, whose job is to isolate Linux ioctl bindings used by composefs. The package description and keywords identify two covered domains: fs-verity and loop devices.

Important configuration: the crate inherits edition, license, readme, repository, Rust version, version, and lints from the workspace. It has no default features and exposes an optional `loop-device` feature, allowing downstream crates to avoid compiling loop-device support unless needed. Runtime dependencies are deliberately minimal: `rustix` with the `fs` feature for fd, filesystem, and ioctl bindings, plus `thiserror` for typed error enums.

Control flow and integration: the manifest maps to `src/lib.rs`, which always exports `fsverity` and conditionally exports `loop_device`. The crate is meant to be a safe wrapper boundary around `unsafe` ioctl calls so consumers can forbid unsafe code while depending on these operations.

State and persistence behavior: the manifest itself has no persistent runtime state. Its feature gate controls whether loop-device ioctl code and its `/dev/loop-control` interaction become part of builds.

Dependencies and test signals: dev-dependencies are `tempfile` for filesystem-backed ioctl tests and `test-with` for path-gated tests such as `/dev/shm` behavior. The dependency set indicates tests interact with real filesystems and kernel ioctl responses rather than pure mocks.

Risks: this crate is highly platform-specific despite not declaring target gating in the manifest. Linux-only assumptions live in source modules and tests; non-Linux builds or environments without fs-verity/loop support may require cfg handling at higher layers. The optional loop feature prevents some exposure but does not make fs-verity portable.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ioctls/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/fsverity.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/fsverity.rs

Purpose: this module contains the low-level Linux fs-verity ioctl wrappers. It converts raw `FS_IOC_ENABLE_VERITY` and `FS_IOC_MEASURE_VERITY` calls into safe Rust functions and typed errors.

Important APIs and types: `EnableVerityError` classifies enable failures as I/O, unsupported filesystem, already enabled, writable-open conflict, or signature verification failure. `MeasureVerityError` classifies measure failures as I/O, verity missing, unsupported filesystem, invalid digest algorithm, or invalid digest size. `FsVerityEnableArg` mirrors `struct fsverity_enable_arg`, including signature pointer fields and reserved padding. `FsVerityDigest<const N>` mirrors `struct fsverity_digest` with a const generic digest byte array. Public functions are `fs_ioc_enable_verity`, `fs_ioc_enable_verity_with_sig`, and `fs_ioc_measure_verity<const N>`.

Control flow: `fs_ioc_enable_verity` delegates to the signature-aware function with `None`. `fs_ioc_enable_verity_with_sig` converts an optional byte slice into kernel size/pointer fields, builds version 1 enable args with no salt, and invokes `rustix::ioctl::Setter`. It maps specific `Errno` values (`NOTTY`, `OPNOTSUPP`, `EXIST`, `TXTBSY`, `KEYREJECTED`) into semantic errors. `fs_ioc_measure_verity` initializes the digest request with the expected algorithm and size, invokes `rustix::ioctl::Updater`, then validates the kernel-filled algorithm and size before returning the digest array.

State and persistence: enabling fs-verity changes persistent file metadata in the underlying filesystem and requires a read-only fd with no writable opens. Measuring does not mutate state but depends on existing fs-verity metadata. The wrapper does not cache anything and passes borrowed fds through `AsFd`.

Dependencies and integration: the module uses `rustix` for ioctl opcodes and errno, `std::io::Error` for fallback conversion, and `thiserror` for public error display. Higher-level repository code can use this crate while keeping unsafe code isolated here.

Risks: correctness depends on the C layout of the repr(C) structs and hard-coded ioctl numbers matching kernel headers. Signature and salt support is minimal: signatures can be supplied, but salt fields are always zero. The signature pointer is only valid for the duration of the syscall, which is appropriate for ioctl but must not become async. `OVERFLOW` during measure is converted into `InvalidDigestSize` with the kernel-reported size as `expected`, which is useful diagnostically but easy to misread.

Test signals: tests create temp files, reopen via `/proc/self/fd` read-only, and assert `VerityMissing` for regular files without fs-verity. `/dev/shm` gated tests assert unsupported filesystem behavior for both measure and enable. These tests exercise kernel error mapping but do not enable successful fs-verity on a supporting filesystem.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/fsverity.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/lib.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/lib.rs

Purpose: this is the crate root for `composefs-ioctls`. It documents the crate as the unsafe boundary for Linux ioctls used by composefs and exposes safe Rust modules to downstream crates.

Important APIs and modules: `fsverity` is always public. `loop_device` is public only when the `loop-device` feature is enabled. `test_utils` is private and compiled only for this crate's tests. `test_utils_pub` is public but hidden from docs so integration tests in other crates can reuse the unsafe test helper without making production APIs depend on it.

Control flow: there is no runtime control flow here; the file is a module export and safety policy boundary. It sets `#![deny(unsafe_code)]` at crate root, forcing all unsafe operations to live in submodules that explicitly allow unsafe code, such as the ioctl implementations and test helpers.

State and persistence: no runtime state. Feature flags control the exported module graph.

Dependencies and integration: the crate-level docs provide an example of enabling and measuring fs-verity. The primary integration point is downstream composefs code that needs fs-verity or loop-device functionality without weakening its own unsafe policy.

Risks and test signals: accidental unsafe in the crate root or non-allowed modules is rejected by the lint. The hidden public test module is a deliberate API escape hatch; because it is public, downstream users could technically depend on it despite doc hiding, so changes should still consider semver impact within the workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/loop_device.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/loop_device.rs

Purpose: this feature-gated module wraps Linux loop-device ioctls for creating a loop device backed by an existing file, mainly for mounting composefs images on kernels that need loop indirection.

Important APIs and types: `flags` exposes `LO_FLAGS_READ_ONLY`, `LO_FLAGS_AUTOCLEAR`, `LO_FLAGS_PARTSCAN`, and `LO_FLAGS_DIRECT_IO`. `LoopConfig` and `LoopInfo64` mirror kernel loop configuration structs. `LoopCtlGetFree` is a custom `rustix::ioctl::Ioctl` implementation because `LOOP_CTL_GET_FREE` returns the loop number in the syscall return value rather than through an argument pointer. Public functions are `loopify` and `loopify_with_flags`.

Control flow: `loopify` calls `loopify_with_flags` with read-only, autoclear, and direct-I/O defaults. `loopify_with_flags` opens `/dev/loop-control`, invokes `LOOP_CTL_GET_FREE`, rejects negative results, opens `/dev/loopN`, builds a `LoopConfig` with the backing fd raw number, 4096-byte block size, and requested flags, then invokes `LOOP_CONFIGURE`. The returned `OwnedFd` owns the opened loop device; autoclear means the kernel detaches when the last fd closes if that flag is used.

State and persistence: this mutates kernel loop-device state by binding a backing file to a free loop device. Persistence is kernel-managed and normally bounded by the lifetime of open fds when autoclear is set. The function does not write repository state and does not maintain user-space bookkeeping.

Dependencies and integration: uses `std::fs::OpenOptions`, fd traits, and `rustix::ioctl`. It is exported only behind the crate's `loop-device` feature, keeping the default ioctl surface limited to fs-verity.

Risks: struct layout and ioctl constants are hard-coded and must match Linux headers. The code assumes `/dev/loop-control` and `/dev/loopN` naming. `fd.as_raw_fd() as u32` would be problematic only for extremely large fd numbers. Direct-I/O default may not work for all backing files or filesystems. This operation usually needs privileges or device access; tests account for permission failure.

Test signals: `test_loopify_not_root` creates a 4 KiB temp file and calls `loopify`, asserting non-root users get an error rather than a panic. It is a smoke test for code path safety, not a privileged success test.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/loop_device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/test_utils.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/test_utils.rs

Purpose: this private test-only module re-exports unsafe-capable test utilities from `test_utils_pub` for internal crate tests.

Important APIs: it exposes whatever `crate::test_utils_pub::*` provides, currently the `CommandExt` trait for adding a pre-exec sleep to `std::process::Command`.

Control flow, state, and dependencies: there is no logic besides re-export. The module is compiled under `#[cfg(test)]` from `lib.rs`, allows unsafe code and unused imports, and keeps unsafe test support outside the crate root's `deny(unsafe_code)` policy.

Integration points: internal tests can import `crate::test_utils::*` without depending directly on the hidden public module. The split allows other workspace integration tests to use the same helper via `test_utils_pub` while keeping this module private.

Risks and test signals: because this file is only a re-export, risk is low. Its value is organizational: it preserves the unsafe boundary and avoids duplicating `pre_exec` helper code in tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/test_utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/test_utils_pub.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/test_utils_pub.rs

Purpose: this hidden public module provides test helpers that require unsafe code, especially for fork/exec scenarios where tests need a process to pause between fork and exec.

Important APIs: `CommandExt` defines `pre_exec_sleep(&mut self, delay: Duration) -> &mut Self`. The implementation for `std::process::Command` calls Unix `CommandExt::pre_exec` and sleeps in the callback before returning `Ok(())`.

Control flow: callers build a `Command`, invoke `pre_exec_sleep`, and then spawn/exec normally. In the child process after fork and before exec, the callback sleeps for the requested duration. The method returns `&mut Self` for builder chaining.

State and persistence: no persistent state. The only side effect is delaying the child process during the unsafe pre-exec window, useful for tests that need fd races or lifetime timing.

Dependencies and integration: depends on `std::os::unix::process::CommandExt`, `std::process::Command`, and `Duration`. It is exported as `#[doc(hidden)]` by the crate root so other crate tests can reuse it while production APIs stay focused.

Risks: `pre_exec` callbacks run in a restricted post-fork context where many operations are unsafe in multi-threaded programs. Sleeping is intentionally simple, but this helper should remain test-only. Non-Unix targets are not supported because the module imports Unix process extensions.

Test signals: there are no tests in this file; its correctness is exercised indirectly by tests that need fork timing.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/test_utils_pub.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/Cargo.toml -->
## sources/cloud-native/composefs-rs/crates/composefs-oci/Cargo.toml

Purpose: this manifest defines `composefs-oci`, the crate that imports OCI/container images into composefs repositories, manages OCI metadata, supports containers-storage and optional boot image generation, and exposes test/varlink-adjacent feature surfaces.

Important configuration: default features include `containers-storage`. `test` enables tar generation, rand, and `composefs/test`. `boot` enables `composefs-boot`. `containers-storage` enables optional `composefs-storage` (`cstorage`), `base64`, and the cstorage user namespace helper. `varlink` enables `zlink-core` and `composefs/varlink`. Core dependencies include `composefs`, `containers-image-proxy`, `ocidir`, `cap-std-ext`, async/tokio utilities, compression libraries, serde/serde_json, sha2/hex, rustix, tar parsing crates, progress/tracing support, and optional storage/boot helpers.

Control flow and integration: feature selection determines which import paths are available. The modules in this work item use these dependencies for OCI layout imports, skopeo/proxy pulls, containers-storage direct/proxied imports, tar splitting, delta reconstruction, filesystem construction, and boot-image metadata rewriting.

State and persistence behavior: the manifest does not persist runtime state, but dependencies reveal that runtime code writes composefs splitstreams/objects, OCI config and manifest streams, image refs, referrers, and optional boot EROFS objects into repositories.

Test signals: dev-dependencies include `cap-tempfile`, `similar-asserts`, `composefs` test features, `composefs-boot`, `once_cell`, `proptest`, `tempfile`, and `tar`, indicating broad unit and integration coverage for tar round trips, filesystem semantics, generated images, boot handling, and property-style tests.

Risks: the default `containers-storage` feature pulls in platform- and environment-sensitive local storage behavior. Optional features must stay aligned with cfg usage in source files. Compression and OCI parsing libraries are security-sensitive because many code paths process untrusted image content.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/boot.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-oci/src/boot.rs

Purpose: this module manages derived bootable EROFS images for OCI container images. A boot image is stored as metadata linked from the OCI config/manifest, with special filtering to avoid circular references and capture boot resources.

Important APIs: `generate_boot_image` is compiled with the `boot` feature and idempotently creates a boot EROFS image for a manifest. `boot_image` returns an existing boot EROFS object ID, if present. `remove_boot_image` removes the boot image reference from OCI metadata while leaving the actual EROFS object for repository GC.

Control flow: `generate_boot_image` first calls `boot_image`; if one exists, it returns it. Otherwise it delegates to `ensure_oci_composefs_erofs_boot` and expects a container image to produce an EROFS object. `boot_image` delegates to `composefs_boot_erofs_for_manifest`. `remove_boot_image` opens the manifest as an `OciImage`, rejects non-container images, returns early if no boot ref exists, preserves raw config JSON, rewrites config with no boot image through `write_config_raw`, reads raw manifest JSON, and calls `oci_image::rewrite_manifest` with the new config verity and existing layer refs.

State and persistence: generation writes or reuses an EROFS object and updates OCI config/manifest splitstreams so the manifest points at the boot image. Removal rewrites metadata to drop that ref, but object cleanup is deferred to `repo.gc()`. Tags remain associated with the OCI image when metadata is rewritten.

Dependencies and integration: integrates with `composefs::Repository`, `FsVerityHashValue`, `OciDigest`, crate-level EROFS helpers, and `oci_image::OciImage`. With tests, it uses `composefs-boot` to inspect boot resources and `TestRepo` fixtures from `test_util`.

Risks: manifest/config rewriting must preserve enough raw JSON and refs to keep the OCI image valid. Removing a boot ref changes config and manifest verities, so any caller caching old verities must refresh. The `expect` in `generate_boot_image` assumes a container image should always produce boot EROFS once the boot path is requested; non-container or malformed content would panic if lower layers violate that assumption.

Test signals: boot-feature tests cover absent boot images, generation, idempotency, removal, removal idempotency, GC preservation while tagged, GC collection after untag, OCI preservation after boot removal, and boot content differences/resources for both classic kernel/initramfs and UKI-like fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/boot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/cstor.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-oci/src/cstor.rs

Purpose: this module imports images directly from local containers-storage into composefs repositories, avoiding redundant data copies where possible. It supports privileged/direct access and rootless/proxied access through a helper that can read storage files and pass fds back.

Important APIs and types: `import_from_containers_storage` is the async public entry point and returns manifest/config digest+verity pairs plus `ImportStats`. `init_if_helper` is re-exported from `cstorage`. Internal paths are `import_from_containers_storage_direct`, `import_from_containers_storage_proxied`, `finalize_import`, `import_layer_direct`, `import_layer_proxied`, `process_file_content`, `discover_storage_paths`, and `parse_containers_storage_ref`. `CstorImportResult` aliases the manifest/config result tuple, and `ZERO_PADDING` preserves tar block alignment.

Control flow: the public function branches on `can_bypass_file_permissions`. Direct mode runs blocking work in `tokio::task::spawn_blocking`, discovers or opens configured stores, finds the image, gets storage layer IDs and config diff_ids, checks counts, imports or reuses each layer stream, and finalizes. Rootless mode rejects explicit storage paths, spawns a `StorageProxy`, discovers paths, searches via the proxy, imports/reuses each layer by streaming proxied tar-split items, shuts down the proxy, reopens metadata directly, and finalizes. Both layer import paths write tar headers/segments inline, process file-content fds through `process_file_content`, and account for padding after file content because tar-split associates padding with the following segment.

State and persistence: layer splitstreams are written under content IDs derived from diff_ids. Large files become external composefs objects by reflink, hardlink, copy, or already-present detection; small files and tar metadata are inlined. `finalize_import` writes config and manifest splitstreams with named refs to layer verities, ensures or links the composefs EROFS image, tags the manifest if requested, and re-reads config/manifest verities because EROFS generation may rewrite metadata.

Dependencies and integration: uses `composefs::Repository`, `ImportContext`, `ObjectStoreMethod`, `INLINE_CONTENT_MAX_V0`, `cstorage` image/layer/proxy/tar-split APIs, base64 for config metadata lookup, OCI content-type constants from skopeo, progress reporting, and crate-level identifier and EROFS helpers.

Risks: storage discovery is environment-dependent and rootless proxy mode currently does not support explicit storage roots/additional stores. The import assumes storage layer count matches config diff_ids. Tar-split padding handling is subtle and must stay consistent with the normal tar importer. Zero-copy mode can fail if reflink or hardlink is unavailable. File descriptor ownership is transferred into `std::fs::File`, so each fd must be unique and positioned/readable as expected.

Test signals: this file has a direct unit test for `parse_containers_storage_ref`. Broader validation likely comes from integration paths that pull containers-storage images and compare with normal OCI imports. Progress events (`Started`, `Skipped`, `Done`, `Message`) give runtime observability for skipped existing layers and imported byte counts.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/cstor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/delta.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-oci/src/delta.rs

Purpose: this module detects and applies `oci-delta` artifacts. A delta artifact embeds the target manifest/config and changed layer blobs, reconstructing omitted layers from an already-present source image in the composefs repository.

Important APIs and types: `MEDIA_TYPE_DELTA`, `is_delta_artifact`, `DeltaBlobReader`, `import_delta`, and `delta_layer_descriptors` are the main integration points. Internal state includes `SourceImage`, `ComposeFsDataSource`, `CurrentFile`, `OciHasher`, `HashingWriter`, `DeltaLayer`, and `ParsedDelta`. Tar-diff parsing uses opcodes for data, open, copy, add-data, and seek plus size limits for filenames and add-data payloads.

Control flow: `parse_delta_manifest` reads artifact annotations, finds embedded target manifest/config blobs and layer mappings by `io.github.containers.delta.*` annotations, fetches and parses the embedded target JSON, and returns a `ParsedDelta`. `import_delta` exits early if the target manifest already exists. Otherwise it extracts target diff_ids, verifies the source config stream exists and has an EROFS image ref, parses that source EROFS into a filesystem, and processes target layers in parallel with a semaphore. Changed layers are fetched through `DeltaBlobReader`, reconstructed in blocking tasks with `reconstruct_layer`, then imported through the normal layer importer. Reused layers must already be present. Finally, it writes target config and manifest splitstreams using raw embedded bytes and returns a normal `PullResult`.

Tar-diff behavior: `tar_patch_apply` verifies the magic header, wraps the stream in a zstd decoder, reads varint-sized op records, and writes reconstructed tar bytes. `OP_OPEN` selects a source file from the source EROFS, `OP_COPY` copies bytes from it, `OP_ADD_DATA` adds byte-wise deltas to source data, and `OP_SEEK` moves the source cursor. `reconstruct_layer` hashes reconstructed uncompressed tar bytes and rejects diff_id mismatches.

State and persistence: delta import reads existing source config, source EROFS, existing layer streams, and source objects. It writes reconstructed changed layers as normal tar splitstreams, writes target config and manifest splitstreams, and returns stats for imported/skipped layers. It does not tag images directly in this module; callers perform normal pull/tag handling.

Dependencies and integration: integrates with OCI layout and skopeo paths through `DeltaBlobReader`, with `composefs::erofs::reader` for source filesystem access, with `crate::import_layer`, `write_config_raw`, and `oci_image::rewrite_manifest`, and with progress reporters for apply-delta progress.

Risks: delta application is security-sensitive because it parses untrusted binary patch streams and compressed data. Size limits protect filenames and add-data records, and diff_id verification protects final layer integrity, but CPU/memory pressure remains possible. Reused layers and source EROFS must be present; otherwise the delta is not applicable. Parallel tasks fetch and write layers concurrently, so repository operations must remain safe under that concurrency.

Test signals: unit tests cover uvarint normal, overflow, and truncated cases. End-to-end tests conditionally require `oci-delta` and sometimes `skopeo`; they build source/target/delta OCI layouts, import source, import delta, import target directly, and compare manifest/config digests. Idempotent delta pull is also tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/delta.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/image.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-oci/src/image.rs

Purpose: this module converts OCI layer tar entries into a composefs filesystem tree, including container overlay semantics such as whiteouts, hardlinks, symlinks, and deterministic OCI transformations.

Important APIs: `process_entry` applies a single `TarEntry<ObjectID>` to a mutable `FileSystem<ObjectID>`. `create_filesystem` opens an OCI config splitstream, iterates its layer diff_ids in order, reads each layer splitstream, and builds the final filesystem. Internal tests include helpers for synthetic tar creation and assertions over dumpfile output.

Control flow: `process_entry` treats entries with no filename as root metadata updates and requires them to be directories. Other entries become an `Inode`: directories allocate nested `Directory`, leaf content goes into the filesystem leaf table, and hardlinks resolve the target leaf ID from the current filesystem. It splits the destination path, interprets filenames beginning with `.wh.` as overlayfs whiteouts, clears directories for `.wh..wh..opq`, removes named entries for normal whiteouts, or merges the inode normally. `create_filesystem` opens config through `crate::open_config`, uses named refs from config splitstream to find layer verities, optionally validates layer checksums when config verity is not trusted, streams tar entries through `crate::tar::get_entry`, applies each entry, transforms the filesystem for OCI consistency, compacts orphan leaves, and debug-asserts fsck.

State and persistence: this module primarily constructs in-memory `FileSystem` state from repository streams and object refs. It reads repository config/layer streams and external objects indirectly through splitstream parsing. It does not commit an EROFS image itself; callers later commit or inspect the filesystem.

Dependencies and integration: depends on `composefs::tree` structures, `Repository`, fs-verity object IDs, `DigestWrite`/SHA-256 for optional layer checksum validation, OCI digest types, tar item types, and the skopeo tar layer content type. It is called by higher-level OCI EROFS generation and boot logic.

Risks: whiteout semantics are easy to regress, especially exact `.wh..wh..opq` matching, root-directory behavior, hardlink target resolution, and replacement ordering. When `config_verity` is absent, validation is intentionally expensive because named refs are not trusted. The filesystem transformation step affects final image IDs; changes need compatibility scrutiny.

Test signals: tests cover base image tar round-trip with directories, inline/external regular files, symlinks, hardlinks, replacement ordering, and entry counts. Many focused tests exercise file whiteouts, nonexistent whiteouts, directory whiteouts, root whiteouts, nested whiteouts, opaque directory clearing, recreate-after-whiteout, multiple and double whiteouts, unusual `.wh.` names, and clearing subdirectories. These are strong behavioral guards for overlay merging.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/image.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/layer.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-oci/src/layer.rs

Purpose: this module contains shared async layer import helpers for OCI image paths. It normalizes media type handling, decompression, tar splitstream import, and raw blob storage.

Important APIs: `is_tar_media_type` identifies supported tar layer media types, including gzip/zstd and non-distributable variants. `decompress_async` wraps an async reader in the appropriate decoder or buffered reader. `import_tar_async` imports an already-decompressed tar stream into a repository splitstream using the OCI tar layer content type. `store_blob_async` writes arbitrary raw bytes to a repository object and finalizes it.

Control flow: `decompress_async` first wraps the input in a `BufReader`, then returns a boxed `AsyncRead` using no decompressor for plain layers, `GzipDecoder` for gzip layers, `ZstdDecoder` for zstd layers, or an error for unsupported media. `import_tar_async` delegates to `tar::split_async` with the repository and `TAR_LAYER_CONTENT_TYPE`. `store_blob_async` creates a repository temp object fd, converts it to a Tokio file, streams all bytes with `tokio::io::copy`, flushes, converts back to std, and calls `finalize_object_tmpfile`.

State and persistence: tar import persists a splitstream and any external objects created by `split_async`; raw blob storage persists a single repository object and returns its object ID, byte size, and storage method. The module itself has no cache.

Dependencies and integration: depends on `async-compression`, `tokio`, `containers-image-proxy` media types, composefs repository APIs, shared IO buffer capacity, and `crate::tar`. It is used by OCI layout, skopeo, and delta paths to keep layer import behavior consistent.

Risks: callers must pass decompressed streams to `import_tar_async`; passing compressed data there would create invalid splitstreams. `decompress_async` boxes readers with lifetimes tied to the input, so caller ownership must remain correct. Unsupported media types are rejected here unless higher-level code stores them as non-tar blobs through `store_blob_async`.

Test signals: this module has no local tests in the file. Coverage is indirect through OCI layout/pull/delta tests and tar round-trip tests that import layers and then read back entries or compose filesystems.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/layer.rs -->
