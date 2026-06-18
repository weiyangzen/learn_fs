# Group Research: subset-b-000237

This grouped report covers Nydus utility modules and OSTree build, documentation, packaging, and CI control files. Each source file has a source-path-preserving section delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/metrics.rs -->
## sources/cloud-native/nydus/utils/src/metrics.rs

### Purpose
This module centralizes Nydus runtime metrics for error events, storage backends, blob cache activity, and RAFS filesystem IO. It provides globally registered metric sets addressable by filesystem or backend id, plus atomic counters and JSON export helpers used by the HTTP metrics surface.

### APIs, Types, and Control Flow
Important public types are `StatsFop`, `InodeStatsCounter`, `InodeIoStats`, `AccessPattern`, `FsIoStats`, `FopRecorder`, `Metric`, `BasicMetric`, `BackendMetrics`, and `BlobcacheMetrics`. `FsIoStats::new()` registers an `Arc<FsIoStats>` in `FS_METRICS`, initializes default switches, and records global operation totals through `fop_update()`. Per-file accounting is enabled by toggles and initialized through `new_file_counter()`. `FopRecorder` is an RAII guard: `settle()` starts a failed operation by default, `mark_success()` records success and byte size, and `Drop` performs the final metrics update.

### State, Dependencies, and Integration
Global registries are `RwLock<HashMap<String, Arc<_>>>` values for filesystem, backend, and blobcache counters. Most numeric fields use relaxed `AtomicU64` counters through `BasicMetric`; mutable maps use `RwLock`; blobcache underlying file names use `Mutex<HashSet<String>>`. Export functions serialize with `serde_json` and return `nydus_api::http::MetricsError`. Integration points include `crate::logger::ErrorHolder`, `crate::InodeBitmap`, RAFS FUSE/virtiofs FOP accounting, backend read paths, and blobcache prefetch/cache-hit tracking.

### Risks and Test Signals
Counters are approximate under relaxed atomics, which is acceptable for metrics but not for sequencing. `AccessPattern::record_access_time()` uses a load-then-store race, so concurrent first reads can overwrite each other. `FopRecorder` counts failures if not marked successful, so early returns are handled but forgotten `mark_success()` calls skew results. Tests cover size and latency bucket selection, per-inode updates, access pattern idempotency, global export ambiguity with multiple ids, blobcache/backend lifecycle, duration saturation, and failure recording.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/mpmc.rs -->
## sources/cloud-native/nydus/utils/src/mpmc.rs

### Purpose
This module implements a lightweight asynchronous multi-producer multi-consumer queue for Nydus internal request flows. It combines a `Mutex<VecDeque<T>>` with `tokio::sync::Notify` instead of using a full channel type.

### APIs, Types, and Control Flow
`Channel<T>` exposes `new()`, `close()`, `send()`, `try_recv()`, async `recv()`, `flush_pending_prefetch_requests()`, `lock_channel()`, and `notify_waiters()`. `send()` rejects messages after close and returns the message to the caller for lifecycle recovery; otherwise it pushes to the queue and notifies one waiter. `recv()` creates a reusable notification future, enables it before checking the queue, returns `BrokenPipe` on close, awaits notification, and resets the future if another consumer won the race.

### State, Dependencies, and Integration
The persistent state is `closed: AtomicBool`, a `Notify`, and the pending `VecDeque`. The queue is in-memory only and has no durability. The flush method is tailored to prefetch cancellation: the predicate removes queued entries that should no longer run. `lock_channel()` exposes the raw mutex guard for callers that need to inspect or mutate the queue atomically with external state.

### Risks and Test Signals
`send()` checks `closed` before locking but does not recheck under the queue lock, so a close racing with send can leave messages queued after close. This may be acceptable if close means "wake and drain or fail eventually", but callers should know the semantics. Tests cover FIFO behavior, close rejection, flush retention/removal, explicit notify and locking access, async receive across a thread, and closed-channel `BrokenPipe` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/mpmc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/reader.rs -->
## sources/cloud-native/nydus/utils/src/reader.rs

### Purpose
This module provides two reader adapters: one for reading a fixed byte range from a file descriptor without moving the file cursor, and one for tracking buffered-reader position while optionally computing a SHA-256 digest of bytes read.

### APIs, Types, and Control Flow
`FileRangeReader::new()` captures a `File` raw fd, offset, and remaining size. Its `Read` implementation clamps reads to the remaining range, calls `nix::sys::uio::pread()`, then advances internal offset and decreases remaining size. `BufReaderInfo<R>` wraps `BufReader<R>` inside `Arc<Mutex<BufReaderState<R>>>`, where state contains `reader`, `pos`, and a `Sha256` hasher. `read()` updates position and feeds the hasher if digest calculation is enabled. `seek()` updates `pos` to the underlying reader position, and `Clone` shares the same reader state.

### State, Dependencies, and Integration
The raw fd in `FileRangeReader` depends on the original `File` outliving the reader. `BufReaderInfo` state is shared across clones, so clones serialize reads through one mutex and observe the same position/hash. Digest updates use `crate::digest::DigestHasher`; pread errors are converted through the local `last_error!()` macro.

### Risks and Test Signals
The lifetime marker in `FileRangeReader` helps express borrow intent, but the struct stores only the fd, so misuse through manual lifetime extension would be dangerous. Seeking after digest calculation does not rewind or reset the digest, so callers must disable digesting or avoid seeks when computing blob digests. Tests cover fixed-range reads, partial reads, position tracking, digest enable/disable behavior, seek position updates, and clone state sharing.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/singleflight.rs -->
## sources/cloud-native/nydus/utils/src/singleflight.rs

### Purpose
This module implements Go-style singleflight for async Rust: concurrent calls with the same key collapse to one executor future, and waiters receive the same cloned result.

### APIs, Types, and Control Flow
`Group` owns an `Arc<tokio::sync::Mutex<HashMap<String, CallState>>>`. `do_call()` locks the map, detects an existing `InFlight` watch receiver, removes stale cancelled receivers, or waits for the shared result. If no call is live, it inserts a `watch::Receiver<Option<Result<BoxedResult, String>>>`, drops the lock, awaits the user future, wraps the cloned `Result<T,E>` in a type-erased `Arc<ResultWrapper<T,E>>`, sends it to waiters, removes the key, and returns `CallResult { shared: false }`. `wait_for_result()` repeatedly inspects the watch value, downcasts to `ResultWrapper<T,E>`, maps function errors, or returns `Cancelled` when the sender is gone without a result. `forget()` removes an in-flight key to force a fresh call.

### State, Dependencies, and Integration
The state is transient and in-memory. Results require `T` and `E` to be `Clone + Send + Sync + 'static` because waiters receive cloned typed values from type-erased storage. The stale receiver path is important for integration with externally timed-out operations such as DNS resolution or HTTP connection attempts where the executor future can be dropped before publishing.

### Risks and Test Signals
Calling the same key with inconsistent result or error types yields `TypeMismatch`; this is a contract risk because the key namespace is not type-scoped. If `forget()` is used while an old executor is still running, old and new computations can overlap. Tests cover single and concurrent calls, independent keys, shared errors, sequential re-execution, custom result types, watch channel races, type mismatch, cancellation, externally aborted executor futures, waiting callers during cancellation, and repeated stale-entry recovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/singleflight.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/trace.rs -->
## sources/cloud-native/nydus/utils/src/trace.rs

### Purpose
This module provides build-time tracing helpers for Nydus image construction. It records timing points and event counters/descriptions under a global root tracer and exports a JSON summary map.

### APIs, Types, and Control Flow
`TraceClass` identifies timing and event classes and renders as JSON keys `consumed_time` and `registered_events`. `TracerClass` abstracts release to `serde_json::Value` and type-erased downcast access. `TimingTracerClass` stores point-name to elapsed seconds in a `Mutex<HashMap<String, f32>>`; `trace_timing()` wraps a closure and stores elapsed time if a timing tracer is registered. `EventTracerClass` stores `TraceEvent::Counter`, `Fixed`, or `Desc` values in an `RwLock<HashMap<_,_>>`. Macros `root_tracer!`, `register_tracer!`, `timing_tracer!`, and `event_tracer!` provide ergonomic global access.

### State, Dependencies, and Integration
`BUILDING_RECORDER` is a lazy global `BuildRootTracer` containing registered tracer classes. Event counters use `AtomicU64`, while insertion uses `RwLock` with double-check logic to avoid most races. The module depends on `serde`, `serde_json`, `thiserror`, and crate-exported macros, and is intended to be used across image build stages without plumbing tracer arguments everywhere.

### Risks and Test Signals
`register()` ignores duplicate registrations, so tests or repeated setup in one process can share prior global state. `trace_timing()` unwraps `duration_since`, which would panic on system clock anomalies. Event macro downcasts unwrap after class lookup; registering the wrong tracer type under a class would panic. Tests exercise concurrent event increments and timing inserts across threads, confirming the mutex/atomic combination produces expected counts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/trace.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/types.rs -->
## sources/cloud-native/nydus/utils/src/types.rs

### Purpose
This small Unix-specific utility module defines byte-size measurement for OS-native string/path values, avoiding confusion between character counts and filesystem byte representation.

### APIs, Types, and Control Flow
`ByteSize` exposes `byte_size(&self) -> usize`. Implementations for `OsString` and `OsStr` call Unix `OsStrExt::as_bytes().len()`. The `PathBuf` implementation delegates to `as_os_str().byte_size()`.

### State, Dependencies, and Integration
There is no runtime state or persistence. The module depends on `std::os::unix::ffi::OsStrExt`, making behavior explicitly Unix byte-oriented. It integrates with path validation, archive metadata sizing, or filesystem serialization code that needs byte lengths rather than Unicode scalar or display lengths.

### Risks and Test Signals
This trait is not portable to non-Unix targets as written. Consumers should not assume `PathBuf::byte_size()` includes a trailing separator; it measures the actual path buffer. Tests cover empty strings, ASCII strings, and incremental `PathBuf` construction through `/test/a`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/verity.rs -->
## sources/cloud-native/nydus/utils/src/verity.rs

### Purpose
This module computes SHA-256 Merkle tree layout and digest generation for data integrity verification. It maps digest pages into a file-backed region and produces the root digest used by verity-style verification.

### APIs, Types, and Control Flow
`MerkleTree::new()` currently asserts 4096 byte pages and SHA-256, computes 128 digests per page, and derives `max_levels` by repeatedly rounding data pages up by digests-per-page. Layout helpers return digest algorithm, max levels, pages and entries per level, entry index for a data page, byte base per level, and total digest pages. `VerityGenerator::new()` creates a tree, grows the target file if needed, and maps the digest region with `FileMapState` when there is more than one data page. `initialize()` fills every digest entry with `NON_EXIST_ENTRY_DIGEST`. `set_digest()` validates level, index, and digest size, with a special one-page root case. `generate_level_digests()` hashes lower-level digest pages into upper-level digest entries, and `generate_all_digests()` walks levels then returns the root.

### State, Dependencies, and Integration
State consists of `MerkleTree`, a `Mutex<FileMapState>`, and a cached `root_digest` for zero/one-page trees. It depends on `crate::digest::{Algorithm, RafsDigest, DigestData}`, `div_round_up`, and memory mapping helpers. Persistent effects include resizing and modifying the target verity data file region.

### Risks and Test Signals
Assertions restrict the implementation to SHA-256 and 4 KiB pages. Offset plus total-size overflow is checked, but mapped writes still rely on `FileMapState` safety. Level numbering is subtle: level 1 stores data-page digests, higher levels store digest-page digests, and level 0 is only a query helper. Tests cover layout boundaries from 0/1 pages to `u32::MAX`, invalid set operations, one/two/many entry roots, overflow/error paths, digest algorithm exposure, and initialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/verity.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.copr/Makefile -->
## sources/cloud-native/ostree/.copr/Makefile

### Purpose
This COPR-specific makefile builds a source RPM for OSTree in Fedora COPR infrastructure.

### APIs, Types, and Control Flow
The single `srpm` target installs git, marks all git directories safe for containerized builds, runs `ci/make-git-snapshot.sh`, downloads the Fedora rawhide `ostree.spec`, rewrites the spec `Version` from `git describe`, comments downstream patches, replaces `%autorelease`, builds an SRPM with `rpmbuild -bs`, and moves the output to `$outdir`.

### State, Dependencies, and Integration
It writes `ostree.spec`, spec backup files from `sed -ie`, build directories under `.build`, and an SRPM artifact. It integrates with COPR's expected `$outdir`, Fedora dist-git specs, and the repository's snapshot script.

### Risks and Test Signals
It relies on network access to src.fedoraproject.org and mutable rawhide spec content. `git config --global --add safe.directory '*'` is pragmatic in CI but broad. Test signal is a successful COPR SRPM build; failures will usually appear as missing spec, bad version substitution, or rpmbuild dependency/spec errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.copr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.gemini/config.yaml -->
## sources/cloud-native/ostree/.gemini/config.yaml

### Purpose
This config enables Gemini code review behavior for pull requests while suppressing noisy summaries.

### APIs, Types, and Control Flow
The YAML sets `have_fun: true`, enables `code_review`, uses a medium severity threshold, allows unlimited comments with `max_review_comments: -1`, and configures pull-request-opened behavior so `help` and `summary` are disabled but `code_review` is true.

### State, Dependencies, and Integration
There is no runtime state. The file integrates only with the Gemini review service and has an empty `ignore_patterns` list, so all files are reviewable unless the service applies its own defaults.

### Risks and Test Signals
The main risk is review-noise configuration drift: unlimited comments can be heavy on large PRs even with summary disabled. Test signal is external service behavior on PR open, not repository tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.gemini/config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/dependabot.yml -->
## sources/cloud-native/ostree/.github/dependabot.yml

### Purpose
This Dependabot config keeps git submodules and GitHub Actions dependencies fresh.

### APIs, Types, and Control Flow
It uses config `version: 2` and declares two update ecosystems: `gitsubmodule` at repository root on a daily schedule, and `github-actions` at repository root on a weekly schedule.

### State, Dependencies, and Integration
Dependabot opens PRs against dependency metadata; it does not update code at runtime. It integrates with the submodule commit-message gate in `ci/ci-commitmessage-submodules.sh`, which explicitly exempts Dependabot-authored submodule bumps from the manual `Update submodule: path` message requirement.

### Risks and Test Signals
Submodule updates can affect vendored C/build behavior and should be covered by the full CI matrix. Actions updates can alter runner behavior. Test signals are Dependabot PR CI results and the submodule gate.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/labeler.yml -->
## sources/cloud-native/ostree/.github/labeler.yml

### Purpose
This file maps changed paths to GitHub PR labels for area triage.

### APIs, Types, and Control Flow
It declares `area/prepare-root` for `src/switchroot/**` and `src/boot`, and `area/rust-bindings` for `rust-bindings/**`. The GitHub labeler action consumes these glob mappings in the labeler workflow.

### State, Dependencies, and Integration
There is no repository runtime state. Integration is with `.github/workflows/labeler.yml` and the `actions/labeler` action running under `pull_request_target`.

### Risks and Test Signals
`pull_request_target` requires careful action configuration because it runs with target-repo permissions; this file is data-only but controls labeling. Missing globs cause under-labeling, not build failure. Test signal is correct labels on PRs touching those paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/labeler.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/bootc.yaml -->
## sources/cloud-native/ostree/.github/workflows/bootc.yaml

### Purpose
This GitHub Actions workflow validates OSTree behavior in bootc/container operating-system contexts across CentOS Stream 9 and 10.

### APIs, Types, and Control Flow
The workflow runs on `main` pushes, PRs to `main`, and manual dispatch. Concurrency cancels prior runs per workflow/ref. `unit-tests` checks out full history, sets up bootc on Ubuntu, runs `just unitcontainer` and `just unittest` for each stream, and uploads unit logs on failure. `integration` also enables libvirt, installs `tmt[provision-virtual]`, builds with `just build`, runs `just test-tmt` with a 40 minute timeout, and always archives `/var/tmp/tmt`.

### State, Dependencies, and Integration
It depends on `bootc-dev/actions/bootc-ubuntu-setup@main`, `just`, the repository `Justfile`, TMT plans, libvirt, and bootc images. Artifacts persist unit and TMT logs for debugging.

### Risks and Test Signals
Using an action from `@main` introduces upstream drift. The workflow is integration-heavy and sensitive to virtualization, package mirrors, and bootc image availability. Test signals are stream matrix success and uploaded logs on failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/bootc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/docs.yml -->
## sources/cloud-native/ostree/.github/workflows/docs.yml

### Purpose
This workflow builds API documentation, manpage HTML, Jekyll docs, and deploys GitHub Pages for non-PR runs.

### APIs, Types, and Control Flow
The `build` job runs inside the FCOS buildroot container, checks out the repo, marks it safe for git, installs dependencies, runs `./autogen.sh --enable-gtk-doc --enable-man --enable-man-html`, builds `apidoc` and `manhtml`, copies generated docs with `docs/prep-docs.sh`, builds the Jekyll site, and uploads a Pages artifact. The `deploy` job depends on `build`, skips PRs, requests Pages/id-token permissions, and calls `actions/deploy-pages`.

### State, Dependencies, and Integration
Outputs are `docs/_site` and GitHub Pages artifacts. Integration spans autotools, gtk-doc, XSLT manpage generation, Jekyll, and Pages deployment. Concurrency separates PR artifact names from production deploy artifacts.

### Risks and Test Signals
Docs build depends on buildroot image contents and gtk-doc/man tooling. PR artifacts are not deployed, limiting accidental publication. Test signal is successful build and Pages deployment URL for main branch runs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/docs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/labeler.yml -->
## sources/cloud-native/ostree/.github/workflows/labeler.yml

### Purpose
This workflow applies path-based labels to pull requests.

### APIs, Types, and Control Flow
It runs on `pull_request_target`, has one `triage` job on Ubuntu, grants `contents: read` and `pull-requests: write`, and invokes `actions/labeler@v4` using the repository labeler config.

### State, Dependencies, and Integration
The action updates PR labels through GitHub API state. It integrates with `.github/labeler.yml`.

### Risks and Test Signals
Because `pull_request_target` has elevated context, it should avoid checking out and running untrusted PR code; this workflow only runs an action, which is the expected safer shape. Test signal is expected labels appearing on PRs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/labeler.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/release.yml -->
## sources/cloud-native/ostree/.github/workflows/release.yml

### Purpose
This workflow sanity-checks release commits that modify `configure.ac`.

### APIs, Types, and Control Flow
It runs for PRs to `main` when `configure.ac` changes, but the job only proceeds when the PR label is `kind/release` or the title starts with `Release`. It checks out the PR head with recursive submodules and full history, runs `ci/ci-release-build.sh` at `HEAD`, then checks out `HEAD^` and runs the same sanity check.

### State, Dependencies, and Integration
It depends on git history being available and on the release-check script parsing `configure.ac`, commit messages, and symbol files. It mutates only the working checkout.

### Risks and Test Signals
The `github.event.label.name` expression may only be populated for labeled events, while the workflow trigger is plain `pull_request`; title matching is the fallback. The test signal is the script accepting both release and previous commit states, catching accidental `is_release_build` mismatches.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/rust.yml -->
## sources/cloud-native/ostree/.github/workflows/rust.yml

### Purpose
This workflow validates the Rust bindings for libostree under featureful, no-feature, live-C-library, and dependency-policy configurations.

### APIs, Types, and Control Flow
The `build` job runs in the FCOS buildroot, caches cargo dependencies, installs `just`, checks format, builds/tests with `CARGO_PROJECT_FEATURES=v2022_6`, runs clippy, and builds docs with warnings denied. `build-no-features` runs cargo tests without features. `build-git-libostree` checks out submodules/history, builds the C lib through `./ci/build.sh`, installs it from `target/c`, then tests Rust bindings against `LATEST_LIBOSTREE`. `cargo-deny` runs bans, sources, and license checks.

### State, Dependencies, and Integration
It integrates cargo, `just`, `rust-cache`, the C autotools build, and `cargo-deny`. Environment variables pin the default binding feature and latest C API feature currently exercised.

### Risks and Test Signals
Feature values must stay in sync with `Cargo.toml` and the C library's supported API. Cache/action pinning is mixed: rust-cache is commit-pinned, checkout versions vary. Test signals are cargo fmt/test/clippy/doc, no-feature compilation, live C-library integration tests, and cargo-deny policy success.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/rust.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/tests.yml -->
## sources/cloud-native/ostree/.github/workflows/tests.yml

### Purpose
This is the main C/autotools CI workflow for OSTree, covering style, minimal feature builds, Fedora builds, and a Linux distribution matrix.

### APIs, Types, and Control Flow
Jobs include `codestyle` for submodule commit-message policy, `clang-format` through `just clang-format-check`, `minimal` for a broad set of disabled optional dependencies, `build-c` for a Fedora-style build/install artifact, and a matrix `tests` job. The matrix spans Debian stable/testing, i386 Debian, Ubuntu rolling, feature variants for curl/libsoup/FUSE/static prepare-root/libsystemd/openssl/ed25519, and passes image-specific package/configure options into `ci/gh-install.sh` and `ci/gh-build.sh`.

### State, Dependencies, and Integration
It uses containerized runners, submodules, distro package managers, non-root builder users, a named volume mounted at `/test-tmp`, and uploaded install tarballs. It integrates the repository shell CI scripts with GitHub Actions matrix metadata.

### Risks and Test Signals
The matrix is sensitive to package names, seccomp behavior, Docker image freshness, and architecture runner quirks. Several checkout action versions are older. The key test signal is cross-distro `make check` success under non-overlayfs temp storage and with `MAKEFLAGS=-j2`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.packit.yaml -->
## sources/cloud-native/ostree/.packit.yaml

### Purpose
This Packit configuration builds and tests OSTree RPMs for pull requests across Fedora and CentOS Stream targets.

### APIs, Types, and Control Flow
It identifies upstream/downstream package names, release tag template `v{version}`, downloads Fedora's rawhide spec after clone, creates an archive through `ci/make-git-snapshot.sh`, patches the spec with `ci/packit-fix-spec.sh`, and prints spec/files for diagnostics. Jobs include `copr_build` and `tests`, both triggered by PRs, targeting x86_64 and aarch64 for CentOS Stream 9/10 and Fedora 43/44. The tests job runs TMT plan `/tmt/plans/integration` with `running_env=packit`.

### State, Dependencies, and Integration
Packit creates SRPM/RPM artifacts and COPR/TMT test state outside the repo. It integrates Fedora dist-git spec content, local archive/spec scripts, COPR builders, Testing Farm, and TMT.

### Risks and Test Signals
Spec download and target names are time-sensitive. Rawhide spec changes can break PR builds independent of source changes. Test signals are Packit COPR build completion and TMT integration success on each target architecture/distro pair.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.packit.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Cargo.toml -->
## sources/cloud-native/ostree/Cargo.toml

### Purpose
This manifest defines the `ostree` Rust crate, workspace membership, public bindings library, integration test, dependencies, and feature gates mirroring libostree API versions.

### APIs, Types, and Control Flow
The package is version `0.20.5`, edition 2021, Rust minimum 1.77.0, and exposes library `rust-bindings/src/lib.rs`. The workspace includes the root crate and `rust-bindings/sys`. Runtime dependencies include GLib/GIO bindings, `ostree-sys` via path package `ffi`, `bitflags`, `base64`, `hex`, `libc`, `once_cell`, and `thiserror`. The feature chain starts at `v2014_9` and incrementally enables later `ffi/v...` features through `v2025_3`; `dox` enables documentation support.

### State, Dependencies, and Integration
The manifest controls cargo package inclusion, excluding generated sys/gir config directories while including Rust binding sources. It integrates with `rust.yml`, docs.rs metadata, and the sys crate generated from C introspection.

### Risks and Test Signals
Feature chains are easy to break when adding versions: each later feature must include its predecessor and matching sys feature. The C and Rust latest-feature constants in CI must stay aligned. Test signals are cargo build/test/doc across default selected feature, no-feature mode, and live libostree integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Dockerfile -->
## sources/cloud-native/ostree/Dockerfile

### Purpose
This multi-stage Dockerfile builds OSTree from source, builds RPMs, assembles bootc-oriented test/rootfs images, and includes an integration-test binary.

### APIs, Types, and Control Flow
Stages include `buildroot` for dependency installation, `src` for full source, `binsrc` to remove tests for better cache reuse, `build` for autotools configure/make/install into `/out`, `rpmbuild` for SRPM and binary RPM rebuilds, `bin-and-test` for unit tests with built binaries, `integration-build` for the Rust bootc integration test binary, `rootfs` for RPM installation into the base image, and the final image that provisions cloudinit and regenerates initramfs with dracut.

### State, Dependencies, and Integration
It uses BuildKit cache mounts for ccache and cargo registries/git/target. It depends on CentOS bootc base images, DNF/RPM tooling, repository CI scripts, submodules, Rust/Cargo, dracut, and `hack/provision-derived.sh`.

### Risks and Test Signals
Base image drift can change package contents. The `rpm -Uvh --oldpackage` selection excludes devel/debug packages by grep and must continue to match generated RPM names. Network is disabled for some source/build steps to enforce cache correctness. Test signal is successful image build plus downstream `just` unit/integration workflows that consume these stages.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/GNUmakefile -->
## sources/cloud-native/ostree/GNUmakefile

### Purpose
This maintainer-oriented GNU make wrapper includes generated `Makefile` rules when configured, handles version freshness for dist/install targets, and gives a clear error before configure has run.

### APIs, Types, and Control Flow
If `Makefile` exists, it exports reproducible tar options, includes `Makefile` and `cfg.mk`, sets build-aux/autoreconf defaults, computes the current git-derived version for dist/install targets, and may run `_version` to regenerate configure output. If `Makefile` does not exist, the default goal errors with instructions to run `./configure`. It also appends recursive targets and marks conflicting multi-goal recursive invocations `.NOTPARALLEL`.

### State, Dependencies, and Integration
It reads `.tarball-version`, `build-aux/git-version-gen`, `cfg.mk`, and generated automake variables. `_version` removes `autom4te.cache` and `.version`, runs autoreconf, and rebuilds `Makefile`.

### Risks and Test Signals
Version freshness logic can unexpectedly trigger autoreconf for dist-like targets, which is intended for maintainers but can surprise simple build users. Test signals are successful `make dist`, `make install` warnings when versions mismatch, and a clear abort before configure.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/GNUmakefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-bash.am -->
## sources/cloud-native/ostree/Makefile-bash.am

### Purpose
This automake fragment installs Bash completion support for the `ostree` command.

### APIs, Types, and Control Flow
It sets `completionsdir` from `@BASH_COMPLETIONSDIR@` and installs `bash/ostree` as distributed completion data. It adds a distcheck configure override so test installs under a temporary prefix resolve the bash-completion directory under `${datadir}`.

### State, Dependencies, and Integration
There is no runtime state. It depends on configure substituting `BASH_COMPLETIONSDIR` and is included by top-level `Makefile.am`.

### Risks and Test Signals
The main risk is incorrect configure substitution or distro-specific completion paths. Test signal is `make distcheck` and package install content containing the completion file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-bash.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-boot.am -->
## sources/cloud-native/ostree/Makefile-boot.am

### Purpose
This fragment installs boot integration assets: dracut modules, mkinitcpio hooks, systemd units, tmpfiles rules, and GRUB generator scripts.

### APIs, Types, and Control Flow
Conditional blocks add dracut module/config files, mkinitcpio install/config files, and systemd unit data depending on `BUILDOPT_*` flags. If built-in grub2 mkconfig is disabled, it installs `grub2-15_ostree` as a package libexec script and creates a symlink in `$(sysconfdir)/grub.d` through an install hook; otherwise it installs the internal `ostree-grub-generator` under the OSTree boot script directory.

### State, Dependencies, and Integration
Install-time state is written under `/lib/dracut`, `/lib/initcpio`, `/etc`, `/lib/systemd/system`, `/lib/tmpfiles.d`, and `/etc/grub.d` depending on prefix/sysconfdir. It integrates with `INSTALL_DATA_HOOKS` from `Makefile-decls.am` and top-level dist packaging.

### Risks and Test Signals
Boot path conventions vary by distro, and the fragment intentionally avoids `$(libdir)` for dracut modules. Symlink creation must respect `DESTDIR`. Test signals include `make install`, distcheck configure flags, bootc tests, and boot/admin integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-boot.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-decls.am -->
## sources/cloud-native/ostree/Makefile-decls.am

### Purpose
This fragment initializes shared automake variables and helper hook targets used by all other non-recursive make fragments.

### APIs, Types, and Control Flow
It resets common accumulators such as `AM_CPPFLAGS`, `AM_CFLAGS`, `SUBDIRS`, `BUILT_SOURCES`, `CLEANFILES`, install program/script/library lists, introspection lists, schema lists, and OSTree boot install variables. It includes `buildutil/glib-tap.mk` to initialize test handling. It defines aggregate hook targets `install-data-hook: $(INSTALL_DATA_HOOKS)` and `all-local: $(ALL_LOCAL_RULES)`.

### State, Dependencies, and Integration
It is included early by top-level `Makefile.am`, so later fragments append to initialized variables. The hook accumulators let fragments add install/all behavior without overriding each other.

### Risks and Test Signals
Ordering matters: including this after fragments would erase their additions. Test signals are automake generation, successful hook chaining, and tests being recognized through `glib-tap.mk`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-decls.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-libostree-defines.am -->
## sources/cloud-native/ostree/Makefile-libostree-defines.am

### Purpose
This fragment defines the public libostree header set shared by the library build and gtk-doc API documentation.

### APIs, Types, and Control Flow
`libostree_public_headers` lists the installed C API headers such as `ostree.h`, repo/sysroot/deployment APIs, remote/repo-finder APIs, signing APIs, blob reader APIs, and kernel args. `libostree_public_built_headers` identifies generated `src/libostree/ostree-version.h`.

### State, Dependencies, and Integration
The header lists feed `Makefile-libostree.am` installation variables and `apidoc/Makefile.am` gtk-doc scanning inputs. The generated header requires configure/builddir awareness.

### Risks and Test Signals
Forgetting to add a new public header here can omit it from installation and docs. Adding a private header here can expose unsupported API. Test signals include install tree inspection, gtk-doc completeness, and Rust/sys binding generation expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-libostree-defines.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-libostree.am -->
## sources/cloud-native/ostree/Makefile-libostree.am

### Purpose
This large automake fragment builds and installs the core `libostree-1.la` library plus helper `libbupsplit.la`, generated enum files, introspection artifacts, pkg-config metadata, and install hooks.

### APIs, Types, and Control Flow
It includes public header definitions, declares `libbupsplit.la`, installs public headers under `ostree-1`, generates `ostree-enumtypes.{h,c}` using `glib-mkenums`, and populates `libostree_1_la_SOURCES` with repository, sysroot, deployment, bootloader, static-delta, repo-finder, signing, blob-reader, compression, checksum, and utility sources. Conditional sections add libarchive, TLS cert interaction, Avahi, GPGME or dummy GPG result, curl/libsoup fetchers, libmount, SELinux, systemd, composefs, and introspection support. Link flags use a released symbol version script and hidden visibility with `_OSTREE_PUBLIC`.

### State, Dependencies, and Integration
Build artifacts include generated enum sources, GIR/typelib files, `ostree-1.pc`, and installed `trusted.gpg.d` README plus `/etc/ostree/remotes.d` creation through an install hook. It links against `libotutil`, `libotcore`, `libglnx`, `libbsdiff`, crypto, zlib, lzma, GLib/GIO, and optional feature libraries.

### Risks and Test Signals
Feature conditionals must stay consistent with `configure.ac`; adding sources without matching CFLAGS/LIBADD can break only certain distros. Symbol files are ABI gates. Test signals include full matrix builds, introspection builds, symbol tests, installed headers, and package linker checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-libostree.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-man.am -->
## sources/cloud-native/ostree/Makefile-man.am

### Purpose
This fragment generates and installs OSTree man pages and optional HTML manpage output from DocBook XML sources.

### APIs, Types, and Control Flow
Under `ENABLE_MAN`, it defines `man1`, `man5`, and `man8` file lists, conditionally adding FUSE and GPGME pages. It maps them to automake `*_MANS`, defines `manhtml_files`, adds a convenience `manhtml` target under `ENABLE_MAN_HTML`, and provides XSLT rules for `.1`, `.5`, `.8`, and `man/html/*.html` generation using `xsltproc --nonet`.

### State, Dependencies, and Integration
Generated man and HTML files are added to `CLEANFILES`; XML sources and the HTML stylesheet are distributed. It integrates with docs workflow and top-level `make manhtml`.

### Risks and Test Signals
The comment notes new man pages must also be referenced in index XML. Network use is disabled through `--nonet`, so local stylesheets/catalogs must be available. Test signal is successful `make manhtml`, `make dist`, and docs workflow.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-man.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-ostree.am -->
## sources/cloud-native/ostree/Makefile-ostree.am

### Purpose
This fragment builds the `ostree` command-line binary and its subcommand source graph.

### APIs, Types, and Control Flow
It adds `ostree` to `bin_PROGRAMS`, lists main command sources, generated `parse-datetime.c` from yacc, admin subcommands, remote subcommands, optional GPG signing/import/list sources, optional pull/cookie sources for curl/libsoup, and optional libarchive flags. Shared command CFLAGS include libotutil/libostree/ostree include paths and `PKGLIBEXECDIR`; shared LDADD links `libglnx`, `libotutil`, `libostree-1`, GLib/GIO, bsdiff, and systemd.

### State, Dependencies, and Integration
The generated parser is written under `src/ostree/parse-datetime.c` and cleaned. The binary links to the library built by `Makefile-libostree.am` and is consumed by tests through symlinks in `Makefile-tests.am`.

### Risks and Test Signals
Subcommand source registration is manual, so adding a builtin requires updating this file and likely man/tests. Fetcher conditionals must match library fetcher availability. Test signals are CLI build, parser regeneration, command help tests, and broad shell integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-ostree.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-otcore.am -->
## sources/cloud-native/ostree/Makefile-otcore.am

### Purpose
This fragment builds the private `libotcore.la` helper library for core boot/signature functionality shared by OSTree components.

### APIs, Types, and Control Flow
It adds `libotcore.la` to `noinst_LTLIBRARIES` and compiles `otcore.h`, ed25519 verification, prepare-root support, and SPKI verification sources. It notes a partial circular dependency because the library uses includes from libostree.

### State, Dependencies, and Integration
It links GLib/GIO, GPGME when configured, systemd, crypto libraries, and optionally composefs. It is linked by switchroot helpers, tests, and libostree paths that need these core helpers.

### Risks and Test Signals
The CFLAGS line includes `$(OT_DEP_CRYPTO_LIBS)` where CFLAGS might be expected, which may be intentional or a latent build hygiene issue depending on configure output. Conditional composefs linkage must match source usage. Test signals are prepare-root, signature verification, and otcore unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-otcore.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-otutil.am -->
## sources/cloud-native/ostree/Makefile-otutil.am

### Purpose
This fragment builds the private `libotutil.la` utility library used by libostree, CLI tools, and tests.

### APIs, Types, and Control Flow
It adds checksum, filesystem, keyfile, option parsing, Unix, variant, GIO, tool, and JSON writer utility sources. Under `USE_GPGME`, it adds GPG utility and zbase32 sources. CFLAGS include libglnx/libotutil include paths, locale directory, GLib/GIO/GPGME/crypto/systemd flags, and LIBADD mirrors those dependencies.

### State, Dependencies, and Integration
The library is non-installed and linked into libostree and command/test binaries. It centralizes common helpers so higher-level fragments do not duplicate utility source lists.

### Risks and Test Signals
Utility behavior has broad blast radius: changes can affect CLI parsing, repository IO, checksums, and tests. Conditional GPG sources must match GPGME availability. Test signals include utility-specific C tests and any libostree/CLI build using these helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-otutil.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-switchroot.am -->
## sources/cloud-native/ostree/Makefile-switchroot.am

### Purpose
This fragment builds and installs early-boot switchroot helpers: `ostree-prepare-root`, `ostree-remount`, and optionally `ostree-system-generator`.

### APIs, Types, and Control Flow
It initializes prepare-root sources and flags, installs `ostree-remount` under boot programs when systemd is enabled or as a check program otherwise, and supports a static prepare-root path using `STATIC_COMPILER` and `ostree-prepare-root-static.c`. The normal path builds `ostree-prepare-root.c` with GLib/GIO, crypto, libotcore, libotutil, and libglnx. SELinux, composefs, systemd, and systemd+libmount conditionals add CPPFLAGS/LIBADD and the systemd generator target.

### State, Dependencies, and Integration
Installed programs land under `$(prefix)/lib/ostree` and systemd generator directories when enabled. These binaries are boot-critical and integrate with boot unit files from `Makefile-boot.am` and bootc/container tests.

### Risks and Test Signals
Static prepare-root exists for systems without populated `/lib`; wrong linkage can break boot. Feature macros must reflect runtime mount behavior. Test signals include switchroot tests, bootc integration, ASAN/unit builds, and installed boot asset checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-switchroot.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-tests.am -->
## sources/cloud-native/ostree/Makefile-tests.am

### Purpose
This fragment declares OSTree's test environment, shell and C test suites, installed-test support, helper binaries, test data, and test-specific build/link rules.

### APIs, Types, and Control Flow
It adds TAP driver assets to distribution, configures `AM_TESTS_ENVIRONMENT` with uninstalled source/build paths, fatal GLib warnings, typelib/library paths, local PATH, feature flags, and proxy/VFS overrides. It lists large sets of installed-or-uninstalled shell tests for pull, deploy, admin, static delta, signing, xattrs, composefs, concurrency, and more. Conditional sections add ed25519, SPKI, GPGME, FUSE, libsoup, GJS, Avahi, libarchive, and installed-test data. It builds helper/test programs such as bloom, repo-finder, varint, checksum, lzma, PEM, bsdiff, otcore, and trivial HTTPD. Symlink-stamp rules expose built binaries under `tests/`.

### State, Dependencies, and Integration
It integrates with `buildutil/glib-tap.mk`, `Makefile-ostree.am`, libostree/libotutil/libotcore, installed-test packaging, and GNOME desktop testing. Install hooks create installed-test symlinks and ASAN-adjusted `libtest.sh`.

### Risks and Test Signals
The file is a central CI surface: missing a test in the right variable can exclude it from `make check` or installed tests. Environment variables intentionally constrain GLib behavior; changing them can cause nondeterminism. Test signal is the suite itself, plus installed-test runners and distro matrix jobs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-tests.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile.am -->
## sources/cloud-native/ostree/Makefile.am

### Purpose
This is the top-level non-recursive automake file that assembles OSTree's build graph from fragments, global flags, bundled dependencies, release targets, and distribution helpers.

### APIs, Types, and Control Flow
It includes `Makefile-decls.am`, sets path/version defines, warning flags, distcheck configure defaults, gitignore files, and package dependency variables. It conditionally includes introspection make rules and the `apidoc` subdir. It includes generated libglnx and bsdiff fragments, then project fragments for otutil, otcore, libostree, CLI, switchroot, tests, boot, manpages, and bash completion. Release targets create git tags, embedded-dependency tarballs, and a `dist-then-build` smoke build from a generated dist archive.

### State, Dependencies, and Integration
It coordinates generated files, submodules, `EXTRA_DIST`, `CLEANFILES`, install hooks, and recursive doc builds. Release tarball logic archives the current revision, submodules, and selected embedded dependencies.

### Risks and Test Signals
Include order is critical because fragments append to variables initialized early. Release-tarball logic shells through git and tar and depends on submodule state. Test signals are autoreconf/configure, full make, distcheck-like builds, embedded tarball generation, and package CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/apidoc/Makefile.am -->
## sources/cloud-native/ostree/apidoc/Makefile.am

### Purpose
This gtk-doc makefile builds the libostree API reference from public headers and C sources.

### APIs, Types, and Control Flow
It includes public header definitions, sets `DOC_MODULE=ostree`, points `DOC_MAIN_SGML_FILE` at `ostree-docs.xml`, scans `src/libostree`, configures gtk-doc scan/mkdb options, computes header and C globs, lists private headers to ignore, and generates `version.xml` from `$(VERSION)`. It includes the standard `gtk-doc.make`, distributes `version.xml` and section files, and adds generated doc files to gitignore metadata.

### State, Dependencies, and Integration
Generated state includes gtk-doc XML/HTML artifacts and `version.xml`. It integrates with top-level docs subdir inclusion, `Makefile-libostree-defines.am`, `gtkdocize`, and the docs GitHub workflow.

### Risks and Test Signals
The ignore list must be maintained to avoid documenting private headers. `HFILE_GLOB` spans source and build dirs for generated version headers. Test signal is `make -C apidoc` under `--enable-gtk-doc` and docs workflow success.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/apidoc/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/apidoc/ostree-docs.xml -->
## sources/cloud-native/ostree/apidoc/ostree-docs.xml

### Purpose
This DocBook root document defines the structure of the generated OSTree API reference.

### APIs, Types, and Control Flow
It declares DocBook 4.3, loads `version.xml` as an entity, sets the book title/release info, and creates an API Reference chapter with XInclude entries for generated XML pages such as core, repo, mutable-tree, sysroot, signing, bootconfig parser, deployment, diff, kernel args, remote, repo finder, and version docs. It also includes the full API index and annotation glossary with fallbacks.

### State, Dependencies, and Integration
It is consumed by gtk-doc through `apidoc/Makefile.am`. Its includes depend on gtk-doc scan output under `xml/`.

### Risks and Test Signals
Missing XIncludes produce incomplete docs or build failures depending on gtk-doc behavior. New public API sections may need manual inclusion here. Test signal is successful API docs generation and review of generated index coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/apidoc/ostree-docs.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/autogen.sh -->
## sources/cloud-native/ostree/autogen.sh

### Purpose
This bootstrap script prepares the autotools build system from a source checkout and optionally runs configure.

### APIs, Types, and Control Flow
It resolves `srcdir`, enters it, verifies `autoreconf`, creates `m4`, runs `gtkdocize` if available or writes a minimal `gtk-doc.make` stub if not, initializes `libglnx` and `bsdiff` submodules when missing, generates `.am.inc` files from submodule make fragments with computed-path substitutions, symlinks `libglnx.m4` into `buildutil`, runs `autoreconf --force --install --verbose`, returns to the original directory, and runs `configure "$@"` unless `NOCONFIGURE` is set.

### State, Dependencies, and Integration
It mutates build support files, submodule checkout state, `gtk-doc.make`, generated include fragments, and autotools outputs. CI commonly uses `NOCONFIGURE=1 ./autogen.sh` before configure.

### Risks and Test Signals
Missing gtk-doc degrades docs generation but permits bootstrap through a stub. Submodule initialization requires git/network unless already present. Test signal is successful autoreconf/configure and subsequent make.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/build-aux/vc-list-files -->
## sources/cloud-native/ostree/build-aux/vc-list-files

### Purpose
This gnulib helper script lists version-controlled files for one or more directories across several VCS backends.

### APIs, Types, and Control Flow
It supports `--help`, `--version`, and `-C SRCDIR`. For each directory, it detects `.git`, `.hg`, `.bzr`, CVS, or `.svn`, then emits relative file paths using the corresponding VCS command. The git path uses `git ls-tree -r HEAD:"$dir"` and filters regular-file entries; other backends use `hg locate`, `bzr ls`, `cvsu` or `awk` over CVS entries, and `svn list -R`.

### State, Dependencies, and Integration
It reads VCS metadata and writes only stdout/stderr. It integrates with maintainer checks and `cfg.mk` exclusion rules.

### Risks and Test Signals
The script uses `eval` to compose pipelines, so quoting is inherited from old gnulib conventions and should not be extended casually. Git symlinks are intentionally ignored. Test signal is correct file listing under git for maintainer rules.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/build-aux/vc-list-files -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/buildutil/glib-tap.mk -->
## sources/cloud-native/ostree/buildutil/glib-tap.mk

### Purpose
This make fragment adapts GLib-style TAP tests to automake, supporting both in-tree and installed tests.

### APIs, Types, and Control Flow
It sets `AM_TESTS_ENVIRONMENT`, `LOG_DRIVER` to `tap-driver.sh`, and `LOG_COMPILER` to `tap-test`. It initializes test variables for installed, uninstalled, dist, data, scripts, programs, and libtool libraries. It builds `TESTS` from runnable uninstalled test programs/scripts, computes aggregate lists for all test artifacts, adds distributed scripts/data to `EXTRA_DIST`, chooses `check_*` or `noinst_*` based on `ENABLE_ALWAYS_BUILD_TESTS`, and under `ENABLE_INSTALLED_TESTS` installs test programs/scripts/data and generates `.test` metadata files.

### State, Dependencies, and Integration
Generated `.test` metadata is added to `CLEANFILES`. It integrates with `Makefile-tests.am`, automake parallel test harness, GLib test environment variables, and installed-test runners.

### Risks and Test Signals
The variable taxonomy is broad; placing a file in the wrong variable changes whether it is run, installed, or distributed. Test signal is automake recognizing the expected tests and installed-test metadata generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/buildutil/glib-tap.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/buildutil/tap-driver.sh -->
## sources/cloud-native/ostree/buildutil/tap-driver.sh

### Purpose
This automake TAP driver executes a test command, parses TAP output, writes per-test logs and `.trs` metadata, and prints decorated summary lines.

### APIs, Types, and Control Flow
Shell option parsing requires `--test-name`, `--log-file`, `--trs-file`, then passes the command output and final exit status into an embedded awk program. The awk parser tracks planned tests, result numbers, TODO/SKIP directives, bailout, comments, expected failures, colorization, merge behavior, and exit status. It reports PASS/FAIL/XFAIL/XPASS/SKIP/ERROR, determines whether recheck or global log copy is needed, and writes automake metadata fields to the `.trs` file.

### State, Dependencies, and Integration
It writes the log file via fd 3 and `.trs` metadata. It uses `AM_TAP_AWK` or awk and is invoked by `glib-tap.mk` as the automake `LOG_DRIVER`.

### Risks and Test Signals
The parser is old but nuanced; small changes can break automake semantics around late plans, unplanned tests, expected failures, and exit-status handling. Test signal is correct `make check` reporting, especially for skipped tests, failing TAP, bailout, and recheck behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/buildutil/tap-driver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/buildutil/tap-test -->
## sources/cloud-native/ostree/buildutil/tap-test

### Purpose
This wrapper runs one GLib test binary in TAP mode inside an isolated temporary directory.

### APIs, Types, and Control Flow
It derives the test source directory and basename from `$1`, creates `TEST_TMPDIR` under `/var/tmp` by default, marks it with `.testtmp`, runs the binary with `-k --tap` under `timeout` with ABRT and a 600 second base timeout multiplied by `TEST_TIMEOUT_FACTOR`, then cleans the tempdir based on `TEST_SKIP_CLEANUP` policy.

### State, Dependencies, and Integration
It creates and usually deletes a temporary directory. It integrates with `glib-tap.mk` as `LOG_COMPILER`, ensuring tests run away from the source/build tree and can use user xattrs unavailable on tmpfs.

### Risks and Test Signals
The cleanup guard prevents deleting arbitrary paths, but failures with `TEST_SKIP_CLEANUP=err` intentionally leave directories for debugging. Test signal is TAP output consumed by `tap-driver.sh` and timeout failures represented in automake logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/buildutil/tap-test -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/cfg.mk -->
## sources/cloud-native/ostree/cfg.mk

### Purpose
This maintainer-check configuration customizes gnulib/maint.mk source checks and version-control file exclusions for OSTree.

### APIs, Types, and Control Flow
It exports `VC_LIST_EXCEPT_DEFAULT` to exclude Rust bindings, docs, git.mk, support directories, gettext header, changelogs, and buildutil from default checks. It skips many generic maintainer checks that do not fit the project. It defines two custom syntax checks prohibiting trailing colons in `glnx_prefix_error()` and `glnx_throw_errno_prefix()` messages, a `show-vc-list-except` helper, and always-exclude regexes for metadata/compressed/signature files.

### State, Dependencies, and Integration
It is included by `GNUmakefile` and works with maintainer check machinery plus `build-aux/vc-list-files`.

### Risks and Test Signals
Skipping checks reduces noise but can hide portability/style issues. Custom regexes are grep-based and may produce false positives/negatives. Test signal is maintainer `make syntax-check` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/cfg.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/build-check-sanitized.sh -->
## sources/cloud-native/ostree/ci/build-check-sanitized.sh

### Purpose
This CI script builds OSTree with ASAN/UBSAN and runs unit tests.

### APIs, Types, and Control Flow
It enables strict shell options, sources `ci/libbuild.sh`, disables ASAN leak detection because of known global leaks, calls `build --disable-gtk-doc --with-curl --with-openssl --enable-sanitizers`, then runs `make check`.

### State, Dependencies, and Integration
It mutates the build tree through the shared `build` helper and writes normal test/build logs. It integrates with sanitizer-capable compilers and CI environments.

### Risks and Test Signals
Leak detection is disabled, so this catches memory errors/UB but not leaks. Test signal is sanitizer-clean `make check`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/build-check-sanitized.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/build-check.sh -->
## sources/cloud-native/ostree/ci/build-check.sh

### Purpose
This CI script installs dependencies, builds OSTree, runs unit and installed tests, and optionally performs a clang rebuild for stricter warnings.

### APIs, Types, and Control Flow
It sources `libbuild.sh`, runs `ci/build.sh`, creates a results directory, executes `make check`, moves `test-suite.log` and `config.log`, runs `make install`, then if clang is available and not blocked by a GLib macro issue, cleans the tree, switches `CC=clang`, and rebuilds. A helper copies logs and GNOME desktop testing results to `$ARTIFACTS` or the repo root. If `gnome-desktop-testing-runner` exists, it clones/builds a newer runner, installs it, traps artifact copy, and runs installed tests.

### State, Dependencies, and Integration
It modifies build/install outputs, may `git clean -dfx` the repo and submodules, and writes artifact logs. It depends on `libbuild.sh`, clang, git, make, and optionally GNOME desktop testing.

### Risks and Test Signals
The destructive clean is appropriate for CI but unsafe for dirty local work unless intentional. Network clone of gnome-desktop-testing can fail. Test signals are unit `make check`, install success, clang build, and installed-test runner results.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/build-check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/build-rpm.sh -->
## sources/cloud-native/ostree/ci/build-rpm.sh

### Purpose
This script creates an OSTree source RPM and rebuilds binary RPMs in the current directory.

### APIs, Types, and Control Flow
It sources `libbuild.sh`, installs buildroot/rpmbuild/git dependencies when running as root, initializes submodules if needed, defaults Fedora builds to curl unless soup or no-curl is configured, enables exclusive installed tests when curl/soup and a desktop testing runner are available, runs `make -f ci/Makefile.dist-packaging srpm PACKAGE=libostree DISTGIT_NAME=ostree`, installs build dependencies if root, and rebuilds the SRPM with `ci/rpmbuild-cwd`, printing any `config.log` on failure.

### State, Dependencies, and Integration
It writes SRPM/RPM artifacts and build directories in the current tree. It integrates with Fedora packaging, `libbuild.sh`, package managers, and RPM build tooling.

### Risks and Test Signals
Non-root runs assume dependencies are already installed. Fedora default feature injection can surprise callers relying on implicit no-curl builds. Test signal is successful `rpmbuild --rebuild` and generated binary RPMs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/build-rpm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/build.sh -->
## sources/cloud-native/ostree/ci/build.sh

### Purpose
This shared CI build script installs dependencies, chooses default configure options, hardens compiler flags, and performs a normal build.

### APIs, Types, and Control Flow
It rejects a `0000` umask, runs `ci/installdeps.sh`, adds Fedora default `--with-curl` unless soup/no-curl is requested, adds composefs and openssl for RHEL/Fedora-like systems, enables exclusive installed tests when curl/soup and a desktop testing runner are present, exports warning-as-error CFLAGS, and calls `build --enable-gtk-doc ${CONFIGOPTS:-}` from `libbuild.sh`.

### State, Dependencies, and Integration
It depends on `/etc/os-release` variables sourced by `libbuild.sh`, package installation helpers, autotools, and compiler toolchains. It mutates the build tree under the helper's target directory.

### Risks and Test Signals
The shell pattern `*--with-curl*|--with-soup*` appears asymmetric and may not match all soup-containing option strings as intended. Warning-as-error can expose distro compiler drift. Test signal is successful configured build with docs enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/ci-commitmessage-submodules.sh -->
## sources/cloud-native/ostree/ci/ci-commitmessage-submodules.sh

### Purpose
This CI gate ensures commits that change submodule pointers explicitly say which submodule was updated.

### APIs, Types, and Control Flow
It sources `libbuild.sh`, accepts an optional head commit, creates a guarded tempdir, ensures git exists, copies the repository to avoid recloning submodules, iterates commits in `origin/main..HEAD`, rejects non-empty merge commits, records changed files and commit logs, checks out each commit, initializes submodules, and for each changed submodule requires the commit message to contain `Update submodule: <path>` unless the author is Dependabot.

### State, Dependencies, and Integration
It uses temp copies, git logs/diffs/checkouts, and submodule metadata. It integrates with the `codestyle` GitHub Actions job and Dependabot submodule updates.

### Risks and Test Signals
It assumes `origin/main` exists and that copying the repo preserves enough metadata. The grep for author is simple and tied to Dependabot log formatting. Test signal is CI failure on accidental submodule pointer changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/ci-commitmessage-submodules.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/ci-release-build.sh -->
## sources/cloud-native/ostree/ci/ci-release-build.sh

### Purpose
This script verifies that release-build mode in `configure.ac` matches the commit title and symbol-file state.

### APIs, Types, and Control Flow
It writes the selected commit message to `log.txt`, removes temporary files on exit, and checks `configure.ac` for `is_release_build=yes`. In release mode it builds a small `version.m4` file from `m4_define` version macros, evaluates `package_version`, requires the commit message to start with `Release $V`, and ensures `src/libostree/libostree-devel.sym` no longer references `LIBOSTREE_$V`. In non-release mode it rejects commit titles that look like releases.

### State, Dependencies, and Integration
It reads git commit messages, `configure.ac`, and symbol files, and writes temporary `version.m4`/`log.txt`. It integrates with `release.yml`.

### Risks and Test Signals
Parsing relies on m4 macro layout in `configure.ac` and commit title conventions. Test signal is release PR CI confirming release flag/version/title/symbol consistency at both HEAD and HEAD parent.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/ci-release-build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/codestyle.sh -->
## sources/cloud-native/ostree/ci/codestyle.sh

### Purpose
This script performs source-structure style checks that do not require building OSTree.

### APIs, Types, and Control Flow
It optionally runs `cargo fmt --check` for every discovered `Cargo.toml` when cargo is installed. It then runs grep-based static analysis for prohibited patterns, currently `glnx_fd_close`, excluding the script itself.

### State, Dependencies, and Integration
It reads the git working tree and may invoke cargo. It integrates with local developer checks and CI style jobs.

### Risks and Test Signals
The `find -iname Cargo.toml` loop can include nested crates and assumes each manifest can be formatted independently. Grep-based checks are simple but can flag comments or examples. Test signal is a clean style check with actionable failure messages.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/codestyle.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/flatpak.sh -->
## sources/cloud-native/ostree/ci/flatpak.sh

### Purpose
This integration script builds Flatpak against the just-built OSTree and runs Flatpak's test suite to catch API or behavior regressions.

### APIs, Types, and Control Flow
It pins `FLATPAK_TAG=1.4.1`, builds OSTree through `ci/build.sh` without installing first, clones Flatpak recursively at that tag into a tempdir, applies an OSTree GPG error compatibility patch, installs Flatpak build dependencies, installs the just-built OSTree over the packaged version with `make install`, builds Flatpak using the shared `build` helper, traps cleanup to move `test-suite.log` back to the OSTree checkout, and runs `make -j 8 check`.

### State, Dependencies, and Integration
It writes a temp Flatpak checkout, installs packages and OSTree into the CI system, and captures Flatpak test logs. It depends on network access to GitHub, distro package managers, Flatpak build dependencies, and the repository patch file.

### Risks and Test Signals
The pinned old Flatpak tag is intentional for API compatibility but may become harder to build on newer distros. Installing OSTree over system packages is CI-oriented. Test signal is Flatpak's automake test suite passing with this OSTree build.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/flatpak.sh -->
