# subset-b-000035 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ctl/src/varlink.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-ctl/src/varlink.rs

Purpose: implements the `cfsctl` varlink RPC server and typed proxy definitions. It exposes `org.composefs.Repository` always and `org.composefs.Oci` behind the `oci` feature so callers can use structured replies and fd passing instead of parsing CLI text.

Important APIs/types/functions: `CfsctlService` owns a `HashMap<u64, HandleEntry>` of open repositories plus a monotonic handle counter. `OpenRepo` erases the concrete digest type into SHA-256/SHA-512 variants. Wire reply types include `FsckReply`, `GcReply`, `ImageObjectsReply`, `OpenRepositoryReply`, `InitRepositoryReply`, `MountParams`, and `MountReply`; error enums are `RepositoryError` and, with OCI, `oci::OciError`. Core helpers are `do_open`, `resolve_selector`, `run_fsck`, `run_gc`, `run_image_objects`, `run_mount`, `run_init_repository`, and OCI helpers for list, fsck, inspect, tag, untag, compute-id, pull, and mount. `try_activated_listener`, `serve_activated`, and `serve` integrate with systemd-style socket activation or explicit Unix-socket binding. `proxy` defines zlink-generated Rust client traits.

Control flow: clients call `InitRepository` or `OpenRepository`, receive a handle, then call operations with that handle. Each operation resolves the handle, matches SHA-256/SHA-512, and calls the corresponding generic repository or OCI helper. The zlink service macro has two compile-time variants: Repository-only without `oci`, and a combined Repository/Oci implementation when `oci` is enabled because method dispatch is generated from one impl block. OCI `Pull` is a streaming `more` method: it parses local-fetch/storage options, clones the repository `Arc`, spawns a Tokio task, forwards progress through an unbounded channel, and ends with a terminal `completed` frame.

State and persistence: no repository is opened at server startup. Server state is only the process-local handle table and handle counter; persistent changes happen through `Repository` methods that create metadata, objects, streams, image refs, OCI tags, boot images, GC deletions, or mounts. Handles are not reclaimed on disconnect yet, although each `HandleEntry` records an optional owner for a future cleanup hook. `run_init_repository` creates parent directories before initializing metadata. Mount methods return detached mount fds via varlink fd passing.

Dependencies and integration points: depends on `composefs`, `composefs_oci`, `composefs_boot`, `zlink`, `tokio`, `libsystemd`, `rustix`, `serde`, and the surrounding `cfsctl` CLI helpers such as `open_repo_at`, `resolve_hash_type`, `resolve_oci_image`, and `resolve_oci_config`. Integration-test consumers use both external `varlinkctl` and the generated `proxy` traits. The socket-activation path must not write protocol-breaking data to stdout.

Risks: the handle table can leak repositories for clients that disconnect without `CloseRepository`. `next_handle` is monotonic and unchecked for overflow, though practical impact is low. `MountParams` maps fd-count mistakes to `InvalidSpec`; OCI mount converts that to `InternalError`, losing specificity. The pull progress channel is unbounded, so a very slow client can accumulate frames. `parse_local_fetch` silently maps unknown values to disabled, which is forward-compatible but can hide caller typos. OCI and Repository error names differ intentionally; cross-interface callers must handle both.

Test signals: integration tests for the varlink module are imported from `tests/mod.rs` via `pub mod varlink`, while CLI tests cover the same repository/OCI semantics through subprocesses. Key behavior to verify includes invalid handles, selector validation, fd-return mounts, streaming pull terminal-frame behavior, activated socket startup, and typed proxy compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-ctl/src/varlink.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-erofs-debug/Cargo.toml -->
## sources/cloud-native/composefs-rs/crates/composefs-erofs-debug/Cargo.toml

Purpose: declares the unpublished `composefs-erofs-debug` binary crate, described as an EROFS image debugging tool.

Important APIs/types/functions: the manifest has package metadata inherited from the workspace for edition, license, readme, repository, Rust version, and version. Runtime dependencies are `clap` with a minimal feature set (`std`, `help`, `usage`, `derive`) and the workspace `composefs` crate.

Control flow: Cargo builds a single default binary from `src/main.rs`; no custom bin/test targets are declared here. Workspace lint settings apply through `[lints] workspace = true`.

State and persistence: the manifest itself has no runtime state. It configures a local diagnostic tool that reads EROFS images and emits deterministic debug output.

Dependencies and integration points: the tool integrates tightly with `composefs::erofs::debug::debug_img` and `clap::Parser`. `publish = false` keeps it internal to the repository.

Risks: because this crate is unpublished and minimal, regressions are most likely to come from changes to the `composefs` debug API or workspace lints. The reduced clap feature set is intentional but means shell completions/color/env support are absent unless added.

Test signals: no crate-local tests are declared. Confidence comes from workspace builds and any tests that compare EROFS/debug output or use the tool manually for deterministic diffs.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-erofs-debug/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-erofs-debug/src/main.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-erofs-debug/src/main.rs

Purpose: command-line utility that dumps an entire EROFS image in a detailed, deterministic, diff-friendly format for inspection and comparison.

Important APIs/types/functions: `Args` derives `clap::Parser` and carries one `PathBuf` field, `image`. `main` opens the path, reads the whole file into a `Vec<u8>`, and calls `composefs::erofs::debug::debug_img(&mut stdout, &data)`.

Control flow: parse CLI arguments, open the image, read it fully, then stream the debug renderer to stdout. Failures use `expect` for file open/read and `unwrap` for debug rendering, making this a diagnostic tool rather than a polished user-facing CLI.

State and persistence: it only reads the image and writes stdout. It does not mutate the repository or image.

Dependencies and integration points: depends on `clap` for argument parsing and `composefs::erofs::debug::debug_img` for all domain-specific parsing/rendering. The deterministic output is useful alongside image determinism tests and EROFS writer comparisons.

Risks: reads the whole image into memory, so very large images can be expensive. Panic-style errors are acceptable for debugging but poor for automation expecting structured failures. Correctness is entirely delegated to the `debug_img` parser.

Test signals: no tests are local to this file. Existing mkcomposefs determinism tests and any manual byte-diff investigations are the main consumers of the behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-erofs-debug/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-fuse/Cargo.toml -->
## sources/cloud-native/composefs-rs/crates/composefs-fuse/Cargo.toml

Purpose: declares the `composefs-fuse` library crate, a FUSE backend for exposing composefs trees from a repository.

Important APIs/types/functions: package metadata is workspace-inherited. Dependencies are `anyhow`, workspace `composefs`, `fuser` with ABI 7.31, `log`, and `rustix` with `fs` and `mount` features.

Control flow: Cargo builds the library from `src/lib.rs`; there are no binary targets in this manifest. The crate intentionally uses low-level mount APIs, so its dependency list is small but system-facing.

State and persistence: the manifest configures a runtime library that opens `/dev/fuse`, creates a FUSE mount object, and serves read-only file content from composefs repository objects.

Dependencies and integration points: integrates with Linux FUSE, rustix fsopen/fsconfig/fsmount APIs, and the core `composefs` tree/repository model. Consumers are expected to open `/dev/fuse`, call `mount_fuse`, then call `serve_tree_fuse`.

Risks: platform support is Linux-specific. The `fuser` ABI feature pins kernel protocol expectations. Mount behavior requires appropriate privileges or userns/fuse configuration, and changes in `rustix` mount wrappers can affect this crate.

Test signals: privileged mount integration tests exercise the higher-level `cfsctl mount` path, which depends on composefs mount behavior. Direct unit coverage for this FUSE crate is not present in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-fuse/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-fuse/src/lib.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-fuse/src/lib.rs

Purpose: implements a read-only FUSE filesystem view over a `composefs::tree::FileSystem`, serving external file data from a `Repository`.

Important APIs/types/functions: public entry points are `open_fuse`, `FuseMountOptions::set_allow_other`, `mount_fuse`, and `serve_tree_fuse`. Internal structures are `InodeMap`, `InodeRef`, `OpenHandle`, and `TreeFuse`. `InodeMap` assigns stable FUSE inode numbers eagerly from directories and leaf IDs so hardlinked leaves share inode numbers. `InodeRef` converts composefs metadata into `fuser::FileAttr`.

Control flow: callers open `/dev/fuse`, create a detached FUSE mount with `mount_fuse`, and then run a blocking `fuser::Session` through `serve_tree_fuse`. On lookup/readdir, `TreeFuse` registers inodes and caches attributes. `open` accepts only regular files; external files become object fds via `repo.open_object`, and inline files become in-memory byte slices. `read` serves either `pread` from the object fd or slices inline data. Symlinks, xattrs, directory listing, getattr, release, and statfs are implemented; mutation operations are absent.

State and persistence: runtime state is per-session maps for inode references, cached attrs, open handles, and a file-handle counter. The crate does not write repository content. `mount_fuse` creates a read-only FUSE mount object with `default_permissions`, optional `allow_other`, fixed root mode/user/group, and the supplied device fd.

Dependencies and integration points: bridges `fuser` callbacks to `composefs` tree types and `rustix` fd/mount syscalls. It relies on `composefs::repository::Repository` object lookup and `FileSystem::nlinks` for hardlink counts. Higher-level mount commands can use this when kernel composefs mounting is unavailable or when serving from userspace is desired.

Risks: `read` casts negative offsets to `u64`/`usize`, relying on FUSE not to issue invalid negative offsets; defensive checks would be safer. Directory inode identity uses raw directory pointers, valid only because the tree is immutably borrowed for the session lifetime. Attribute TTL is very long, which is fine for immutable trees but wrong if a future mutable mode is added. `blocks` is hard-coded to 1 and `statfs` returns zeros, so disk-usage semantics are approximate. Serving is blocking and single-session; callers must handle threading/lifetime.

Test signals: privileged CLI mount tests validate visible filesystem content, overlay upper/work behavior, bootable OCI mount differences, and plain mount sanity. Direct FUSE-specific xattr, hardlink inode, statfs, and error-path coverage is not shown in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-fuse/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-http/Cargo.toml -->
## sources/cloud-native/composefs-rs/crates/composefs-http/Cargo.toml

Purpose: declares the `composefs-http` library crate for HTTP downloading of composefs repositories.

Important APIs/types/functions: package metadata is workspace-inherited. Runtime dependencies are `anyhow`, `bytes`, workspace `composefs`, `hex`, `reqwest` with `zstd`, `sha2`, and `tokio`. Dev dependency is `similar-asserts`.

Control flow: the library is asynchronous and built from `src/lib.rs`. The dependency set points to a downloader that fetches HTTP resources, stores them in composefs repositories, and verifies hashes.

State and persistence: the manifest configures code that writes downloaded objects into a local repository but does not itself define persistence.

Dependencies and integration points: integrates with `reqwest`/Tokio for network IO, `composefs` repository and splitstream APIs, and SHA-256 verification. The `zstd` feature suggests support for compressed HTTP responses through reqwest.

Risks: version changes in reqwest/Tokio can affect async behavior and defaults. This crate likely needs network/integration tests because correctness depends on HTTP status handling, symlink content types, and concurrent downloads.

Test signals: no direct tests are present in this subset. Verification should include recursive splitstream fetching, object checksum mismatch handling, and progress events.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-http/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-http/src/lib.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-http/src/lib.rs

Purpose: provides an async downloader that fetches a named splitstream and all referenced splitstreams/objects from an HTTP endpoint into a composefs repository, verifying fs-verity IDs and SHA-256 splitstream body checksums.

Important APIs/types/functions: public API is `DownloadOptions { progress }` and `download(url, name, repo, opts) -> Result<(String, ObjectID)>`. Internal `Downloader` owns a `reqwest::Client`, repository `Arc`, base `Url`, and progress reporter. Key methods are `fetch`, `ensure_object`, `open_splitstream`, and `ensure_stream`. `INITIAL_CONCURRENT_REQUESTS` limits object fetch fan-out to 100.

Control flow: `download` builds a `Downloader` and calls `ensure_stream`. `ensure_stream` fetches `streams/<name>`; if the HTTP `Content-Type` is `text/x-symlink-target`, bytes are treated as an object pathname, otherwise the body is stored directly as an object. It recursively walks splitstream named refs, downloading missing splitstream objects, then collects all non-splitstream object refs. Object downloads run through a bounded `JoinSet` queue. After all objects are present, every splitstream is concatenated through `SplitStreamReader::cat` and verified against its recorded body checksum. Progress events report splitstream fetch messages, object started/progress/done, and verification messages.

State and persistence: downloaded objects are persisted through `Repository::ensure_object_async`; existing objects are reused. No remote state is mutated. The returned tuple is the top-level stream content digest (`sha256:...`) and fs-verity object ID.

Dependencies and integration points: depends on HTTP URL layout conventions: `streams/<name>` and `objects/<object-pathname>`. It uses `SplitStreamReader` to discover nested stream refs and object refs, `DigestWrite<Sha256>` to verify reconstructed stream content, and `composefs::progress` for observability.

Risks: symlink detection depends solely on exact content type; servers with charset parameters or different metadata will be treated as direct object data. Splitstream recursion is sequential except object fetches, and verification is also sequential. `ensure_object` considers any `open_object` error as absence, which can mask permission/corruption errors until later. Concurrent fetch count is fixed rather than configurable. Error messages include expected/measured digest information but all failures collapse to `anyhow::Error`.

Test signals: useful tests would serve synthetic HTTP repositories with nested splitstreams, duplicate refs with conflicting body hashes, object fs-verity mismatches, direct-vs-symlink stream responses, HTTP failures, and progress counts. This subset does not include direct tests for the crate.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-http/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/Cargo.toml -->
## sources/cloud-native/composefs-rs/crates/composefs-integration-tests/Cargo.toml

Purpose: declares the unpublished integration-test harness crate for composefs-rs.

Important APIs/types/functions: `autobins = false` and `autotests = false` prevent Cargo defaults. `src/main.rs` is declared both as a `[[bin]]` named `cfsctl-integration-tests` and a `[[test]]` with `harness = false`, allowing container image execution and nextest/libtest-mimic discovery. `src/cleanup.rs` is a separate `test-cleanup` binary.

Control flow: tests are registered through code, not Cargo test discovery. Dependencies include CLI/test helpers (`xshell`, `libtest-mimic`, `linkme`, `paste`, `tempfile`), serialization (`serde`, `serde_json`), archive/layout tools (`tar`, `ocidir`), repository crates (`composefs`, `composefs-oci`, `composefs-ctl` with `oci`), `tokio`, `rustix`, and `zlink`.

State and persistence: tests create temporary repositories, containers-storage images, loop-mounted filesystems, podman containers/images, and OCI layouts. The cleanup binary removes labeled podman resources.

Dependencies and integration points: this crate intentionally verifies behavior through the `cfsctl` CLI for most checks, while using library helpers for fixture setup and typed varlink tests. It is excluded from workspace default members per comments and is expected to run through `just test-integration` or VM workflows.

Risks: tests are highly environment-sensitive: podman, skopeo, bcvk, user namespaces, root privileges, fs-verity-capable ext4, XFS reflinks, network access, and old binary paths can all affect execution. Because `src/main.rs` is both bin and test, warnings around shared source are expected.

Test signals: the manifest itself shows broad coverage intent: host-safe CLI tests, privileged mount/verity tests, containers-storage import tests, network digest stability tests, old-format migration tests, and varlink protocol tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/cleanup.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/cleanup.rs

Purpose: small cleanup binary for integration-test leftovers in podman.

Important APIs/types/functions: `main` uses `std::process::Command` and `INTEGRATION_TEST_LABEL` from the integration-test library. It runs `podman ps -a --filter label=... -q` and `podman images --filter label=... -q`, then removes matching containers/images.

Control flow: print start message, collect container IDs, remove each with `podman rm -f`, collect image IDs, remove each with `podman rmi -f`, print completion. Command failures are ignored unless the initial listing command itself cannot be spawned, in which case the section is skipped.

State and persistence: mutates local podman state by deleting containers and images with the integration-test label. It does not touch composefs repositories or temp directories.

Dependencies and integration points: used by developers/CI to clean resources created by tests that label podman objects with `composefs-rs.integration-test=1`.

Risks: cleanup is label-scoped, so tests must consistently apply the label or resources remain. It ignores command failures, which is convenient for best-effort cleanup but can hide permission or podman availability problems. Image removal with repeated IDs may be harmless but noisy.

Test signals: no direct tests. Effectiveness is visible after integration test runs by checking that labeled podman resources are gone.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/cleanup.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/lib.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/lib.rs

Purpose: shared integration-test infrastructure: registration metadata, test macro, cfsctl path discovery, test image settings, repository setup, and podman fixture helpers.

Important APIs/types/functions: `TestFn`, `IntegrationTest`, distributed slice `INTEGRATION_TESTS`, and macro `integration_test!` implement registration. Constants/functions include `INTEGRATION_TEST_LABEL`, `get_cfsctl_path`, `get_primary_image`, `get_all_images`, `create_test_repository`, `build_test_image`, and `cleanup_test_image`.

Control flow: modules call `integration_test!(function)` to insert metadata into the linkme slice. The runner later reads `INTEGRATION_TESTS`. `get_cfsctl_path` checks `CFSCTL_PATH`, target release/debug binaries, then `/usr/bin/cfsctl`. `create_test_repository` opens a tempdir fd and initializes an insecure SHA-256 repository. `build_test_image` writes a temporary Containerfile, builds a CentOS-based image with small/large files, symlink, `/boot`, and `/sysroot`, then reads the image ID from an iid file.

State and persistence: creates temporary repositories and podman images. Podman images may outlive tests unless explicitly cleaned. The repository helper returns `Arc<Repository<Sha256HashValue>>` for async/library tests.

Dependencies and integration points: uses `linkme`/`paste` for distributed registration, `tempfile`, `rustix`, `composefs_oci` re-exported composefs types, and podman. It supports both CLI subprocess tests and library-level setup for containers-storage imports.

Risks: distributed slices require unsafe allowance. `build_test_image` depends on network/base image availability and podman behavior. The test label constant is not embedded in the sample Containerfile shown here, so cleanup only applies where tests label podman resources elsewhere. Path discovery can accidentally pick stale target binaries if multiple builds exist.

Test signals: this file is foundational; if registration or cfsctl path resolution breaks, all integration modules fail. It also standardizes the minimal image used by cstor/bootable tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/main.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/main.rs

Purpose: custom integration-test runner using `libtest_mimic`, plus host-safe helpers shared by test modules.

Important APIs/types/functions: `cfsctl()` resolves the binary path from `CFSCTL_PATH`, workspace target release/debug, or `/usr/bin/cfsctl`. `create_test_rootfs(parent)` creates a simple rootfs fixture with `/usr/bin/hello`, `/usr/lib/readme.txt`, and `/etc/hostname`. `main` initializes containers-storage helper mode, converts registered `IntegrationTest`s to `libtest_mimic::Trial`s, and runs them.

Control flow: `main` first calls `composefs_oci::cstor::init_if_helper()` because this binary may be re-executed under `podman unshare` as a containers-storage helper. It parses libtest-style arguments, maps each distributed test to a trial closure returning formatted errors, and exits with libtest status.

State and persistence: `create_test_rootfs` writes a temporary fixture tree. The runner itself only executes tests; persistent state is produced by individual tests.

Dependencies and integration points: bridges the library registration slice to the test executable. It is both a Cargo test target and standalone binary, matching the manifest. The rootfs deliberately includes a 128 KiB file to force external object storage for `image-objects`/dump tests.

Risks: path discovery assumes the crate is two parents below workspace root. Re-exec helper initialization must run before argument handling. Tests are plain functions, so filtering and exact matching depend on libtest-mimic names from `IntegrationTest::new`.

Test signals: all integration tests flow through this file. Failures in `cfsctl()` or registration show up as immediate harness failures rather than domain-specific errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/cli.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/cli.rs

Purpose: host-safe CLI integration suite for `cfsctl --insecure` and no-repo commands. It avoids root, fs-verity, and network requirements while checking core repository, OCI, fsck/gc, and mkcomposefs behavior.

Important APIs/types/functions: helper `init_insecure_repo` initializes V2 legacy EROFS repositories for pinned digest stability; `create_oci_layout` builds a deterministic minimal OCI layout with one layer and a hardlink; `corrupt_one_object` mutates repository object data for fsck tests. Constants include `OCI_LAYOUT_COMPOSEFS_ID`, composefs/EROFS magic bytes, and superblock offset.

Control flow: each function creates tempdirs, resolves `cfsctl`, runs commands through `xshell::cmd`, and asserts stdout/stderr/JSON/filesystem effects. Covered flows include GC empty/after-create/dry-run, image creation/idempotence/object listing, repository init metadata/algorithm/idempotence/conflicts/reset, hash auto-detection and mismatch failures, fsck healthy/corrupt/broken refs, OCI images/pull/inspect/layer/compute-id/tag/untag/gc, no-repo compute/dump behavior, and `mkcomposefs` byte-level output.

State and persistence: tests create temp repositories, rootfs fixtures, OCI layout directories, EROFS images, and intentionally corrupted object/ref states. They rely on tempdir cleanup. Repository metadata tests inspect `meta.json`, `objects`, `streams`, and `images`.

Dependencies and integration points: exercises public CLI behavior, not library internals, with JSON parsed by `serde_json`, tar output parsed by `tar`, dumpfile output parsed by `composefs_oci::composefs::dumpfile_parse`, and optional comparison to the C `mkcomposefs` binary if present.

Risks: pinned image IDs make EROFS writer changes visible but also require intentional updates when formats change. Many assertions inspect human-oriented output substrings, so output wording changes can break tests. The minimal OCI layout tests a controlled case, not registry/network pulls. The C mkcomposefs comparison is skipped when unavailable, so CI coverage depends on environment.

Test signals: this is the broadest fast regression suite for CLI semantics. Strong signals include deterministic image IDs, JSON schema expectations, nonzero fsck exit behavior, old-format migration hint presence, reset metadata preserving objects while removing streams/images, and mkcomposefs magic/determinism/hardlink behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/cstor.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/cstor.rs

Purpose: containers-storage import tests. They verify that `composefs_oci` and `cfsctl oci pull --local-fetch` correctly import podman/containers-storage images, preserve content equivalence, and use caching/zero-copy paths.

Important APIs/types/functions: `copy_image_to_separate_store` copies a podman image to a standalone overlay store using skopeo and optional `podman unshare`. Tests include cstor-vs-skopeo equivalence, idempotent import, import with reference, additional image store, and bootable containers-storage pull.

Control flow: tests use `require_privileged` or `require_userns` to run locally when possible or dispatch to a VM. They build a synthetic image via `build_test_image`, create temp repositories, pull through `composefs_oci::pull` or external `cfsctl`, and compare config digests, layer refs, import stats, OCI refs, inspect fields, and CLI output.

State and persistence: creates podman images, separate overlay stores, temp repositories, OCI directory copies, and `STORAGE_OPTS`-scoped pulls. Cleanup is explicit for some images via `cleanup_test_image`, while tempdirs handle repositories/stores.

Dependencies and integration points: requires podman, skopeo, containers-storage, user namespaces, and sometimes the VM path from `privileged.rs`. It exercises `LocalFetchOpt::IfPossible`, OCI tagging/ref layout under `streams/refs/oci`, additional image store handling, and boot image generation.

Risks: environment-dependent and slower than host tests. Skopeo/containers-storage behavior may differ by version. A documented TODO notes cstor vs skopeo config verity can differ due to layer ref ordering even when content is equivalent. Additional image store testing mutates the default store by removing the original image, so cleanup/order matters.

Test signals: validates critical import invariants: matching config digests/layer refs across cstor and skopeo paths, second import copying zero objects, reference names appearing in OCI refs, `STORAGE_OPTS=additionalimagestore=...` support, and bootable pull producing `composefs_boot_erofs`.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/cstor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/digest_stability.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/digest_stability.rs

Purpose: table-driven digest stability suite for OCI-to-composefs conversion across pinned real container images, EROFS writer versions, and bootable transformations.

Important APIs/types/functions: `ContainerImage` records labels, mirror/upstream refs, expected V2/V1 plain IDs, and optional V2/V1 bootable IDs. Constants cover UBI10, centos-bootc, debian-bootc, and Ubuntu resolute. Helpers include `skip_network`, `pull_image`, `try_pull_image`, `compute_id`, `compute_id_v1`, `try_expand_var`, and `check_digest_equivalence`.

Control flow: `test_oci_container_digest_stability` skips if `COMPOSEFS_SKIP_NETWORK` is set, then for each image initializes a V2 insecure repo, pulls from GHCR mirror with upstream fallback, computes V2 plain/bootable IDs and V1 plain/bootable IDs, and asserts exact expected hashes plus plain-vs-bootable/V1-vs-V2 differences. `check_digest_equivalence` pulls an image into podman, imports from containers-storage, mounts/examines an on-disk container root, compares bootable digests, and emits dumpfile diffs on mismatch.

State and persistence: creates temp repositories, pulls registry images, creates podman containers, mounts containers, writes temporary dumpfiles on mismatch, and may remount `/var` tmpfs larger in VM environments.

Dependencies and integration points: requires network unless skipped, `cfsctl`, podman, registry mirrors/upstreams, privileged VM support for equivalence tests, and digest behavior from OCI import, EROFS V1/V2 writers, boot transforms, and on-disk rootfs reading.

Risks: exact digest pins are intentionally brittle: any legitimate format, metadata, tar-split, boot transform, or fixture image change requires updating expected values. Network/mirror availability can make tests flaky, though upstream fallback helps. The centos bootc equivalence path is intentionally skipped due to known directory mtime divergence tracked upstream.

Test signals: very high-value regression coverage for reproducibility. It catches silent EROFS writer output changes, OCI metadata reconstruction changes, bootable transform differences, and mismatch between containers-storage and on-disk digest paths. Dumpfile diff capture is a strong diagnostic signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/digest_stability.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/mod.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/mod.rs

Purpose: module index for the integration test suite, grouped by execution environment and feature area.

Important APIs/types/functions: exports submodules `cli`, `cstor`, `digest_stability`, `old_format`, `privileged`, and `varlink`.

Control flow: Rust module loading causes each submodule's `integration_test!` registrations to be linked into the distributed slice. There is no runtime logic in this file.

State and persistence: none directly.

Dependencies and integration points: ties `src/main.rs`'s `mod tests;` to all test categories. The presence of `varlink` means varlink tests are part of the same harness even though that file is outside this subset.

Risks: adding a new test file without listing it here means its registrations are not compiled. Removing or renaming a module silently drops that suite from the harness.

Test signals: coverage organization is explicit: fast host CLI, containers-storage, network digest stability, old-format compatibility, privileged kernel/mount behavior, and varlink RPC.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/old_format.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/old_format.rs

Purpose: backward-compatibility test for reading and auto-upgrading old-format composefs-rs repositories created by an older `cfsctl`.

Important APIs/types/functions: `cfsctl_old` reads `CFSCTL_PATH_OLD`; `have_skopeo` checks skopeo availability; `test_read_old_format_repo` performs the compatibility scenario.

Control flow: skip if the old binary path or skopeo is absent. Otherwise copy busybox into an OCI layout, use old `cfsctl` to pull into a repo without modern metadata, assert new `cfsctl --no-upgrade` rejects it, then run new `cfsctl` without `--no-upgrade` and verify auto-upgrade writes `meta.json`, lists the image, dumps `/bin/sh`, runs GC, and passes `oci fsck --json`.

State and persistence: creates a temp OCI layout and old-format temp repository; auto-upgrade mutates the repository by adding modern metadata.

Dependencies and integration points: requires an externally built old binary from a documented revision, skopeo, Docker Hub access for busybox, and current `cfsctl`. It validates splitstream compatibility and metadata migration.

Risks: optional by environment, so it may not run in normal CI. It pulls `busybox:latest`, which is less reproducible than digest-pinned fixtures. Auto-upgrade behavior must be coordinated with `--no-upgrade` guarantees.

Test signals: high signal for migration: old repo rejection under `--no-upgrade`, successful default auto-upgrade, dump compatibility, GC preservation, and OCI fsck integrity.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/old_format.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/privileged.rs -->
## sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/privileged.rs

Purpose: privileged integration tests for root, fs-verity, kernel mounts, overlay upper layers, bootable OCI mounts, read-only repositories, and filesystem-specific containers-storage zero-copy behavior.

Important APIs/types/functions: environment gates are `require_privileged`, `require_privileged_with_memory`, `require_userns`, and `userns_works`. Filesystem fixtures are `VerityTempDir` for ext4+verity and `LoopTempDir` for ext4/XFS loop mounts. Test helpers include `create_oci_layout_with_large_files`, `copy_oci_to_cstor`, `init_insecure_repo_at`, `cstor_pull`, and `cstor_pull_with_algorithm`.

Control flow: non-root tests re-exec inside a bcvk VM when `COMPOSEFS_TEST_IMAGE` is set; otherwise they fail with setup guidance. Tests initialize secure or insecure repositories on loop-mounted filesystems, run `cfsctl` mount/init/pull commands, inspect mounted content, unmount resources, and assert import stats. The cstor filesystem tests iterate SHA-256/SHA-512 and local-fetch auto/zerocopy across ext4 hardlink and XFS reflink expectations.

State and persistence: creates sparse filesystem images, formats/mounts loop devices, initializes repositories, creates OCI test images, creates overlay stores, performs kernel mounts and bind mounts, writes through overlay upperdirs, and unmounts in `Drop` or explicit cleanup.

Dependencies and integration points: requires root or VM, ext4 verity, optional XFS reflink tools, podman, skopeo, unshare, mount/umount, `composefs_oci::test_util`, and `cfsctl`. It validates integration between repository verity policy, OCI boot transforms, mount plumbing, overlayfs, containers-storage local fetch, hardlinks, and reflinks.

Risks: tests are resource- and privilege-heavy. Cleanup relies on successful unmounts; failures can leave mounts behind until process exit or manual cleanup. XFS coverage skips when `mkfs.xfs` is missing. Read-only bind-mount tests must unmount before assertions to avoid leaked read-only state. The VM path depends on `BCVK_PATH`, `COMPOSEFS_TEST_IMAGE`, and memory sizing. Assertions on import stats assume filesystem/link behavior remains stable.

Test signals: strongest coverage for production-like behavior: secure repo without `--insecure`, verity-required metadata, insecure metadata rejection under `--require-verity`, bootable OCI mount content differences, upperdir read-only/read-write semantics, read-only repo error clarity, ext4 hardlink fallback, XFS reflink use, and both hash algorithms under local-fetch modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/privileged.rs -->
