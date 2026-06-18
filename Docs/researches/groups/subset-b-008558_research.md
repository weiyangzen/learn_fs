# Group Research: subset-b-008558

Work item `subset-b-008558` covers Raft Engine failpoint tests and RocksDB GitHub Actions automation. Each section is wrapped for deterministic reconciliation into the mapped source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/test_engine.rs -->
# Research: sources/storage-engines/raft-engine/tests/failpoints/test_engine.rs

Purpose: Failpoint regression suite for Raft Engine core behavior under corrupted logs, failed purge/rewrite operations, recycling, multi-directory allocation, concurrent write grouping, listener callbacks, and sync edge cases.

Important APIs/types/functions: defines local helper `append`; tests `Engine::open`, `open_with_listeners`, `open_with_file_system`, `write`, `sync`, `fetch_entries_to`, `compact_to`, `purge_expired_files`, `purge_manager().must_rewrite_*`, `consistency_check`, `unsafe_repair`, `file_span`, `first_index`, and `last_index`. Uses `EventListener`, `FileId`, `FileBlockHandle`, `LogQueue`, `LogBatch`, `RaftLocalState`, `FailGuard`, `ObfuscatedFileSystem`, `ConcurrentWriteContext`, and `catch_unwind_silent`.

Control flow: each test builds an isolated temp directory, configures small file sizes or recovery modes, writes synthetic entries, injects failpoints at a precise storage layer, then drops and reopens the engine to validate recovery. Listener tests count log-file creation, append, memtable apply, and purge events. Rewrite tests force tiny rewrite batches and write failures through append-to-rewrite and rewrite-to-rewrite phases. Recycling tests create stale tails or simulated no-space conditions, then verify readable state and file spans after reopen.

State and persistence behavior: the suite intentionally persists log files, rewrite queues, memtables, compact markers, and recycled file metadata across engine drops. In-memory listener counters and failpoints are temporary, while the durable witness is the reopened engine's first/last indexes, fetched entries, file span, and repair/check results.

Dependencies and integration points: depends on `raft_engine::internals`, `raft_engine::env`, `kvproto::raft_serverpb::RaftLocalState`, `raft::eraftpb::Entry`, the local failpoint `util.rs` helpers, and the `fail` crate. It integrates with Raft Engine's test-only failpoints and optional `scripting` feature for `unsafe_repair`.

Risks: these tests are highly coupled to failpoint names and internal queue sequencing, so refactors can break tests without changing public API. Several assertions rely on sleeps to let paused writes reach specific phases. Some failures surface as panics because internal sync/write paths unwrap errors; this is deliberate but makes panic boundaries part of the contract. The `#[should_panic]` recycle stale-tail test documents a known issue rather than a desired success path.

Test signals: passing tests show that corrupted tails are tolerated or rejected according to recovery mode, partial rewrite failures do not lose committed entries, listeners see durable events, recycle/no-space paths remain readable, and `Engine::sync()` actually reaches the active log fsync path.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/test_engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/test_io_error.rs -->
# Research: sources/storage-engines/raft-engine/tests/failpoints/test_io_error.rs

Purpose: Focused failpoint tests for Raft Engine I/O failures: file open/read/write/sync/rotate/truncate/allocation/no-space errors, concurrent write failures, repair failures, and recycled-file allocation gaps.

Important APIs/types/functions: exercises `Engine::open_with_file_system`, `Engine::open`, `write`, `fetch_entries_to`, `get_message`, `file_span`, `unsafe_repair_with_file_system`, `purge_expired_files`, and optional `SwappyAllocator`. Uses `ObfuscatedFileSystem`, `FailGuard`, `ConcurrentWriteContext`, `generate_batch`, `MessageExtTyped`, and `catch_unwind_silent`.

Control flow: tests create temp engines, write baseline entries, enable one or more failpoints such as `default_fs::create::err`, `log_file::read::err`, `log_file::write::err`, `log_fd::sync::err`, `log_file::truncate::err`, `log_file::allocate::err`, and `log_fd::write::no_space_err`, then assert whether the public API returns `Err`, panics, or can recover after reopen. Rotate tests run both with and without restart after each injected failure.

State and persistence behavior: the file validates that partially written data is either ignored, overwritten, or recovered consistently depending on the failure point. Durable state is checked through reopened engines, fetched entry counts, first/last indexes, directory entry counts, and file spans. Some outstanding writes are explicitly not reverted after sync panic, and the tests document that behavior.

Dependencies and integration points: integrates failpoint-controlled filesystem behavior with the real engine write group, log writer, repair, recycle prefill, spill directory selection, and optional swap allocator. It shares typed Raft-entry helpers from `util.rs`.

Risks: exact failpoint scripts depend on low-level I/O call ordering and byte-splitting behavior; using `ObfuscatedFileSystem` is avoided in one concurrent test because it would split I/O differently. Panic-vs-error expectations encode current internal unwrap choices. No-space simulations cover selected retry paths but cannot fully model real disks.

Test signals: success means expected errors do not corrupt committed state, failed followers in concurrent write groups do not poison leaders, non-atomic writes can be reopened or overwritten safely, repair failures leave original data readable, recycled-file prefill gaps are supplemented, and no-space transitions between main and spill dirs behave as intended.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/test_io_error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/util.rs -->
# Research: sources/storage-engines/raft-engine/tests/failpoints/util.rs

Purpose: Shared failpoint-test utilities for Raft Engine tests, providing a typed Raft entry adapter, deterministic batch generation, silent panic capture, and a helper for forming concurrent write groups.

Important APIs/types/functions: `MessageExtTyped` implements `MessageExt<Entry = raft::eraftpb::Entry>` and returns `entry.index`. `generate_entries` builds indexed entries with optional data. `generate_batch` wraps generated entries into a `LogBatch`. `catch_unwind_silent` temporarily replaces the panic hook while running `panic::catch_unwind`. `ConcurrentWriteContext` owns an `Arc<Engine<FS>>` and spawned writer threads with `new`, `write`, `write_ext`, and `join`.

Control flow: `ConcurrentWriteContext::write_ext` installs `write_barrier::leader_exit` for the first thread, starts a no-op leader write to pause the write group, then adds follower closures that call into the same engine. `join` removes the barrier and joins all queued threads.

State and persistence behavior: helpers create in-memory batches and short-lived threads only. Persistent effects are made by the engine writes performed by callers. `catch_unwind_silent` restores the previous panic hook after the closure returns.

Dependencies and integration points: used by `test_engine.rs` and `test_io_error.rs`; depends on `raft_engine::{Engine, LogBatch, MessageExt}`, `raft::eraftpb::Entry`, `fail`, `std::sync::mpsc`, and `std::thread`.

Risks: the concurrent-write harness relies on sleeps and a specific failpoint to synchronize write groups, so it is sensitive to scheduler timing and write-barrier implementation changes. `catch_unwind_silent` mutates a process-global panic hook and should not be used around unrelated concurrent panic-sensitive tests.

Test signals: indirect signal comes from failpoint tests that use these helpers to verify batch contents, panic expectations, and concurrent write group behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/build-folly/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/build-folly/action.yml

Purpose: Composite GitHub Action that builds Folly and dependencies for RocksDB CI unless a prior `cache-folly` step reported a cache hit.

Important APIs/types/functions: input `cache-hit`; steps `Build folly and dependencies` and `Skip folly build`. The build step strips `/usr/lib/ccache` from `PATH` before running `make build_folly`.

Control flow: if `inputs.cache-hit != 'true'`, it reconstructs a clean PATH and invokes the make target; otherwise it prints a skip message.

State and persistence behavior: creates or updates the Folly getdeps install tree under paths discovered by the surrounding setup/cache actions. It does not itself upload artifacts; cache persistence is owned by `actions/cache`.

Dependencies and integration points: consumed by Folly-enabled PR and nightly jobs after `setup-folly`, `cache-getdeps-downloads`, and `cache-folly`. Depends on repository `folly.mk`, `make build_folly`, bash, and getdeps-prepared sources.

Risks: removing only `/usr/lib/ccache` may miss other ccache wrappers. Cache-hit is a string input, so callers must pass the exact cache output. A stale cache can skip a needed rebuild if the cache key misses an input.

Test signals: CI signal is whether Folly-enabled `make` or CMake jobs proceed past dependency setup and whether logs show either a real build or an intentional cache skip.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/build-folly/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/build-for-benchmarks/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/build-for-benchmarks/action.yml

Purpose: Composite action for preparing a Linux release build before benchmark execution.

Important APIs/types/functions: invokes local `pre-steps` and runs `make V=1 J=8 -j8 release`.

Control flow: setup/environment defaults are applied first, then a release build is compiled.

State and persistence behavior: produces RocksDB release build outputs in the checkout workspace. Benchmark data is produced later by `perform-benchmarks`.

Dependencies and integration points: used by `benchmark-linux.yml`; depends on GNU make, compiler toolchain, and the shared `pre-steps` action.

Risks: fixed `-j8` assumes runner capacity. It does not set up ccache, so benchmark build time can be high. Failures in `pre-steps` or release compilation block benchmark runs.

Test signals: successful benchmark workflow reaches `perform-benchmarks`; build logs show a completed `release` target.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/build-for-benchmarks/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/cache-folly/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/cache-folly/action.yml

Purpose: Composite action that caches the Folly getdeps install directory for debug Folly builds.

Important APIs/types/functions: output `cache-hit`; steps compute `FOLLY_MK_HASH`, compute `FOLLY_INSTALL_DIR` via `third-party/folly/build/fbcode_builder/getdeps.py show-inst-dir`, and call `actions/cache@v4` on the normalized installed directory.

Control flow: shell steps expose hash and install path through `GITHUB_OUTPUT`; the cache step uses runner OS/arch, container image, `folly.mk` hash, and `PORTABLE` mode in the key.

State and persistence behavior: persists the getdeps installed tree across CI runs. It does not cache source checkouts or download tarballs; those are handled elsewhere.

Dependencies and integration points: used before `build-folly` in Folly CI jobs. Depends on checked-out Folly sources from `setup-folly`, Python getdeps, `md5sum`, and `actions/cache`.

Risks: the action assumes the getdeps path contains `installed/folly` so the `sed` normalization is valid. Container image can be empty on non-container jobs, affecting key shape. It is only intended for debug Folly builds.

Test signals: `steps.cache-folly-build.outputs.cache-hit` drives whether `build-folly` runs; cache restore/save logs are the main validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/cache-folly/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/cache-getdeps-downloads/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/cache-getdeps-downloads/action.yml

Purpose: Composite action that caches getdeps download archives to reduce mirror flakiness and speed Folly dependency builds.

Important APIs/types/functions: output `cache-hit`; single `actions/cache@v4` step stores `/tmp/rocksdb-getdeps-cache` with restore prefixes keyed by OS and architecture.

Control flow: the cache action restores any matching rolling cache before later getdeps operations populate or reuse the directory.

State and persistence behavior: caches downloaded source archives under `/tmp`, not compiled artifacts. The key includes `github.run_id`, so exact-key hits are unlikely and restore keys carry most reuse.

Dependencies and integration points: used by Folly-enabled PR and nightly jobs before `setup-folly`/`build-folly`; relies on `folly.mk` and getdeps honoring the same download cache path.

Risks: run-id keys create continuous new caches and depend on GitHub cache eviction policy. A poisoned or partial restored cache could affect dependency builds if getdeps does not validate downloads.

Test signals: cache logs and fewer dependency download failures during Folly setup are the practical signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/cache-getdeps-downloads/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/increase-max-open-files-on-macos/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/increase-max-open-files-on-macos/action.yml

Purpose: Raises macOS file descriptor limits for RocksDB build and test jobs.

Important APIs/types/functions: composite action runs `sudo sysctl -w kern.maxfiles=1048576`, `sudo sysctl -w kern.maxfilesperproc=1048576`, and `sudo launchctl limit maxfiles 1048576`.

Control flow: a single bash step applies system-level settings before build/test commands run.

State and persistence behavior: changes runner kernel/session limits for the lifetime of the GitHub-hosted runner job; no repository state is modified.

Dependencies and integration points: used by macOS PR jobs and Java/macOS jobs before make or ctest. Depends on sudo access on macOS runners.

Risks: hosted runner policy changes could reject these sysctl/launchctl calls. Individual shells still often call `ulimit` afterward, so this action alone may not guarantee the soft limit.

Test signals: macOS logs should show successful sysctl/launchctl commands and later RocksDB tests should avoid EMFILE failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/increase-max-open-files-on-macos/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-gflags-on-macos/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/install-gflags-on-macos/action.yml

Purpose: Installs gflags on macOS CI runners through Homebrew.

Important APIs/types/functions: single bash step `HOMEBREW_NO_AUTO_UPDATE=1 brew install gflags`.

Control flow: package installation runs before macOS build/test jobs that configure RocksDB with gflags support.

State and persistence behavior: mutates the ephemeral runner's Homebrew installation only.

Dependencies and integration points: used by macOS PR and Java jobs. Integrates with make/CMake detection of gflags.

Risks: Homebrew package availability, bottle changes, or preinstalled conflicts can break CI. Auto-update is disabled for speed but can leave outdated metadata.

Test signals: later build/link steps and tools requiring gflags are the validation signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-gflags-on-macos/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-gflags/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/install-gflags/action.yml

Purpose: Installs Linux gflags development headers and library for CI jobs that need gflags.

Important APIs/types/functions: runs `sudo apt-get update -y && sudo apt-get install -y libgflags-dev`.

Control flow: one bash install step before build commands.

State and persistence behavior: mutates the ephemeral runner/container package state.

Dependencies and integration points: used by candidate ARM jobs and other non-container Linux paths where gflags is not preinstalled.

Risks: requires sudo and network package repositories. Container jobs that run as root might not need sudo, so portability depends on runner image.

Test signals: downstream CMake/make detection and tools such as `trace_analyzer` confirm gflags availability.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-gflags/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-jdk8-on-macos/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/install-jdk8-on-macos/action.yml

Purpose: Installs Liberica JDK 8 on macOS for RocksDBJava jobs.

Important APIs/types/functions: taps `bell-sw/liberica` and installs `liberica-jdk8` via Homebrew cask.

Control flow: two bash commands run before Java build/test steps set or use `JAVA_HOME`.

State and persistence behavior: installs a JDK into the ephemeral macOS runner; no repo state is written.

Dependencies and integration points: used by macOS Java and static Java workflows. Integrates with `make jtest`, `rocksdbjavastaticosx`, and JNI CMake/make targets.

Risks: cask names, tap availability, or Apple security policy changes can break installs. Jobs set `JAVA_HOME` to a fixed Liberica path, so package layout drift matters.

Test signals: `which java`, `java -version`, `javac -version`, and Java target success validate the action.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-jdk8-on-macos/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-maven/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/install-maven/action.yml

Purpose: Installs a pinned Maven distribution for Java PMD/site CI jobs.

Important APIs/types/functions: downloads `apache-maven-3.9.11-bin.tar.gz`, extracts it, appends `M2_HOME` to `GITHUB_ENV`, and appends the Maven bin directory to `GITHUB_PATH`.

Control flow: a single bash step performs download, extraction, and environment export.

State and persistence behavior: writes the Maven tree into the current workspace and updates job environment files for later steps.

Dependencies and integration points: used by `build-linux-java-pmd` in `pr-jobs.yml`; integrates with `make jpmd` and Maven-generated reports under `java/target`.

Risks: uses `--no-check-certificate`, reducing TLS validation. Archive URL availability and lack of checksum verification are supply-chain and reliability risks.

Test signals: later PMD job success and the presence of uploaded `pmd.xml` and Maven site artifacts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-maven/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/perform-benchmarks/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/perform-benchmarks/action.yml

Purpose: Runs RocksDB low-variance benchmark CI with fixed environment settings.

Important APIs/types/functions: invokes `./tools/benchmark_ci.py` with `--db_dir`, `--output_dir`, and `--num_keys 20000000`. Sets benchmark env such as `DURATION_RO`, `DURATION_RW`, `NUM_THREADS`, `MAX_BACKGROUND_JOBS`, cache and compression options, and `CI_TESTS_ONLY=true`.

Control flow: after a release build, the benchmark script executes read/write benchmark scenarios and writes outputs under `${{ runner.temp }}/benchmark-results`.

State and persistence behavior: creates benchmark database data under runner temp and report files under benchmark-results. Persistence beyond the job is handled by `post-benchmarks`.

Dependencies and integration points: used by `benchmark-linux.yml` after `build-for-benchmarks`. Depends on built RocksDB binaries, Python benchmark tooling, and `LD_LIBRARY_PATH=/usr/local/lib`.

Risks: benchmark stability depends on runner isolation, disk performance, and temp storage capacity. Fixed large key counts and durations make it expensive. Environment variables are implicit contract with `benchmark_ci.py`.

Test signals: successful script exit and generated `report.tsv`/benchmark artifacts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/perform-benchmarks/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/post-benchmarks/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/post-benchmarks/action.yml

Purpose: Uploads benchmark result artifacts and attempts to send a benchmark report to an external visualization endpoint.

Important APIs/types/functions: uses `actions/upload-artifact@v4.0.0` for `benchmark-results`; runs `benchmark_log_tool.py --tsvfile ... --esdocument ...`.

Control flow: artifact upload is required with `if-no-files-found: error`; the external report step disables immediate failure and ends with `true`, making visualization submission best-effort.

State and persistence behavior: persists benchmark files as GitHub artifacts and may write documents to an external Elasticsearch endpoint.

Dependencies and integration points: follows `perform-benchmarks` in `benchmark-linux.yml`; depends on `report.tsv`, Python tooling, network access, and the configured search endpoint.

Risks: external upload failures are intentionally hidden, so dashboards can silently miss data. The endpoint URL is embedded in workflow code.

Test signals: artifact upload success is hard CI signal; visualization ingestion must be checked in external systems/logs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/post-benchmarks/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/post-steps/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/post-steps/action.yml

Purpose: Shared post-job artifact collection for RocksDB CI.

Important APIs/types/functions: input `artifact-prefix`; uploads test results, `LOG`, failure logs copied from `t/*`, and `core.*` dumps with `actions/upload-artifact@v4.0.0`.

Control flow: normal uploads run after jobs; failure-log copy runs only on failure; core dump upload ignores missing files. Callers often wrap this action at the end of build/test jobs.

State and persistence behavior: reads workspace/test temp files and persists them as GitHub artifacts. It creates `${{ runner.temp }}/failure-test-logs` on failing runs.

Dependencies and integration points: used broadly by PR, nightly, weekly, macOS, Linux, ARM, and Folly jobs. Relies on `pre-steps` setting `GTEST_OUTPUT` into runner temp.

Risks: uploading `LOG` without `if-no-files-found` may warn/fail depending on action defaults if the file is absent. Copying `t/*` can be large on broad failures. Artifact names need unique prefixes for matrix jobs.

Test signals: artifact availability in failed/successful CI runs and lack of post-step masking failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/post-steps/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/pre-steps-macos/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/pre-steps-macos/action.yml

Purpose: macOS wrapper around the shared `pre-steps` composite action.

Important APIs/types/functions: contains one step using `./.github/actions/pre-steps`.

Control flow: delegates all setup to the generic pre-step action.

State and persistence behavior: same environment mutations as `pre-steps`, mainly `GITHUB_ENV` settings.

Dependencies and integration points: used by macOS jobs after macOS-specific package/ulimit setup.

Risks: Linux-oriented commands inside `pre-steps`, especially `apt-get install lld`, are allowed to fail with `|| true`, but still add noise and depend on shell compatibility.

Test signals: downstream macOS build/test jobs receiving common GTest/CTest environment variables.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/pre-steps-macos/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/pre-steps/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/pre-steps/action.yml

Purpose: Shared CI setup for RocksDB jobs: diagnostics, optional lld installation, test-output environment, and dependency download mirror variables.

Important APIs/types/functions: dumps soft/hard `ulimit`, runs `apt-get update -y && apt-get install -y lld 2>/dev/null || true`, and writes `GTEST_THROW_ON_FAILURE`, `GTEST_OUTPUT`, `SKIP_FORMAT_BUCK_CHECKS`, `GTEST_COLOR`, `CTEST_OUTPUT_ON_FAILURE`, `CTEST_TEST_TIMEOUT`, plus compression dependency download base URLs to `GITHUB_ENV`.

Control flow: diagnostics run first, package install is best-effort, environment variables are exported for all later steps.

State and persistence behavior: mutates only job environment and package state. Test result XML is directed to `${{ runner.temp }}/test-results/`.

Dependencies and integration points: used by most Linux/macOS CI jobs before make/ctest. Download base variables integrate with third-party dependency build scripts.

Risks: `apt-get` assumes Debian-like environments but errors are ignored. Quoted `GTEST_OUTPUT="xml:..."` writes literal quotes into the env value, which callers must tolerate. Mirror URL drift can break dependency fetches.

Test signals: logs show ulimits; test XML appears in runner temp; CTest failures include output due to exported env.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/pre-steps/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/setup-ccache/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/setup-ccache/action.yml

Purpose: Configures ccache and GitHub cache restore for RocksDB C/C++ CI builds.

Important APIs/types/functions: inputs `cache-key-prefix` and `portable`; exports `CCACHE_DIR`, `CCACHE_BASEDIR`, `CCACHE_NOHASHDIR`, `CCACHE_COMPILERCHECK`, `CCACHE_SLOPPINESS`, `CCACHE_MAXSIZE`, and optionally `PORTABLE=1`; restores `${{ github.workspace }}/.ccache`; installs ccache; adds libexec/wrapper dir to PATH; zeros stats and touches `.build_marker`.

Control flow: environment is prepared, cache is restored by branch/SHA prefixes, ccache is installed if missing, PATH is adjusted per OS, and a marker is created for later trimming.

State and persistence behavior: `.ccache` is restored and later saved by `actions/cache`; `.build_marker` marks files used during the current build for `ccache-trim.sh`.

Dependencies and integration points: paired with `teardown-ccache`; used throughout PR jobs. Integrates with compiler wrapper lookup and RocksDB `PORTABLE` build mode.

Risks: cache keys include branch/ref and SHA, so restore behavior depends on prefix ordering. Large sloppiness settings trade correctness for hit rate and must match compiler behavior. `PORTABLE=1` is skipped for Folly linked jobs when caller sets `portable: false`.

Test signals: ccache stats in teardown, cache restore logs, and build commands resolving compiler wrappers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/setup-ccache/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/setup-folly/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/setup-folly/action.yml

Purpose: Prepares Folly sources and Linux packages needed before building RocksDB with Folly.

Important APIs/types/functions: runs `make checkout_folly`; installs `patchelf` and `libaio-dev` with apt.

Control flow: source checkout happens first, then system packages are installed.

State and persistence behavior: populates `third-party/folly` and mutates ephemeral package state.

Dependencies and integration points: used by Folly PR/nightly jobs before `cache-folly` and `build-folly`. Depends on make targets and Debian package repositories.

Risks: checkout target and package availability are external failure points. No retry or cache logic exists in this action itself.

Test signals: existence of Folly source tree and successful later `make build_folly` or Folly-enabled CMake/make builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/setup-folly/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/setup-upstream/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/setup-upstream/action.yml

Purpose: Prepares an upstream remote and safe repository ownership for format-compatibility and source-check jobs.

Important APIs/types/functions: runs `chown $(whoami) . || true`, `git remote add upstream https://github.com/facebook/rocksdb.git`, `git fetch upstream`, and diagnostic `git status && git remote -v && env -i git branch`.

Control flow: ownership fix, remote setup, fetch, then diagnostics.

State and persistence behavior: mutates local git config/remotes and fetches upstream refs into the CI checkout.

Dependencies and integration points: used by `check-format-and-targets` and `nightly` format-compatible jobs that need full upstream history or branch behavior under `env -i`.

Risks: action name is incorrectly `build-folly`, which can confuse logs. `git remote add upstream` fails if remote already exists; no `|| true` is present there. Network fetch from GitHub is required.

Test signals: successful upstream fetch and `check_format_compatible.sh` running against expected history.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/setup-upstream/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/teardown-ccache/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/teardown-ccache/action.yml

Purpose: Post-build ccache cleanup and statistics reporting.

Important APIs/types/functions: checks `CCACHE_DIR`, runs `.github/scripts/ccache-trim.sh || true`, then `ccache -s || ...`; step is guarded with `if: always()`.

Control flow: if setup did not set `CCACHE_DIR`, it exits successfully; otherwise trims stale entries and prints stats.

State and persistence behavior: deletes unused ccache result/manifest files older than `.build_marker` and removes the marker. The remaining `.ccache` is what GitHub cache saves.

Dependencies and integration points: paired with `setup-ccache`; used by most ccache-enabled jobs.

Risks: trim failures are ignored, which preserves CI success but may allow cache growth. It assumes the script path exists and that ccache's file naming conventions match `ccache-trim.sh`.

Test signals: teardown logs show file count before/after trim and ccache stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/teardown-ccache/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/windows-build-steps/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/windows-build-steps/action.yml

Purpose: Composite Windows CI build/test action for RocksDB and RocksJava under Visual Studio.

Important APIs/types/functions: inputs `suite-run` and `run-java`; uses `microsoft/setup-msbuild`, `hendrikmuhs/ccache-action`, PowerShell ccache config, Chocolatey Liberica JDK install, Snappy source build, CMake configure with `WIN_CI`, `PORTABLE`, `SNAPPY`, `XPRESS`, `JNI`, MSBuild, `build_tools\run_ci_db_test.ps1`, Java `ctest`, and final ccache stats.

Control flow: configure msbuild/cache, install dependencies, build Snappy, configure RocksDB, build solution with high parallelism, run requested C++ suite shards, optionally run Java tests, and show cache stats.

State and persistence behavior: creates `thirdparty`, Snappy build outputs, CMake `build`, ccache content, and test outputs in the workspace. Nothing is committed.

Dependencies and integration points: used by PR and nightly Windows jobs with different `CMAKE_GENERATOR` and `CMAKE_PORTABLE` values. Integrates with Visual Studio, Chocolatey, CMake, CTest, Snappy, Java/JNI, and RocksDB PowerShell test runner.

Risks: many external tools and URLs can fail. The action uses fixed paths like `C:\a\rocksdb\rocksdb` for ccache base dir. `/m:32` can exceed actual CPU capacity but expects cache hits. Each PowerShell command needs explicit `$LASTEXITCODE` handling, so missing checks could hide errors.

Test signals: successful MSBuild, `run_ci_db_test.ps1`, optional Java CTest, and ccache stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/windows-build-steps/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/build-ai-review-comment.js -->
# Research: sources/storage-engines/rocksdb/.github/scripts/build-ai-review-comment.js

Purpose: Shared Node helper that formats AI review output into a consistent Markdown PR comment.

Important APIs/types/functions: exports `buildAiReviewComment({icon, headerTitle, triggerLine, responseBody, footerLines})`, returning a joined Markdown string with heading, trigger line, body, separators, and an expandable details footer.

Control flow: pure formatting only; it builds an array of lines and joins with newline characters.

State and persistence behavior: no state, filesystem, or network access.

Dependencies and integration points: required by `parse-claude-review.js` and `parse-codex-review.js`, which are invoked from `ai-review-analysis.yml`.

Risks: does not sanitize body/footer markdown, which is acceptable for generated comments but means callers control all rendered content. Uses an info emoji in the summary, so consumers expecting ASCII-only output should not reuse it unchanged.

Test signals: indirect through parser scripts and posted PR comment shape; there is no direct unit test for this helper.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/build-ai-review-comment.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/ccache-trim.sh -->
# Research: sources/storage-engines/rocksdb/.github/scripts/ccache-trim.sh

Purpose: CI script that trims ccache to entries accessed or created during the current build.

Important APIs/types/functions: requires `CCACHE_DIR`; uses `.build_marker`; counts files named `*R` or `*M`, deletes result/manifest files not newer than the marker, removes empty directories, runs `ccache -c`, prints before/after counts, and deletes the marker.

Control flow: exits early if marker is absent; otherwise performs cleanup under `set -e` with best-effort directory cleanup and counter recalculation.

State and persistence behavior: mutates the ccache directory by deleting stale result and manifest files. It intentionally does not touch local build outputs.

Dependencies and integration points: called by `teardown-ccache/action.yml` after `setup-ccache` creates the marker. Depends on ccache's on-disk file suffixes and `find`.

Risks: intended only for CI; local shared ccache use could lose useful entries. Future ccache storage layout changes could make the file pattern incomplete or dangerous. If the marker timestamp is wrong, it can over-trim or under-trim.

Test signals: teardown log line `ccache-trim: before -> after` and subsequent cache size/stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/ccache-trim.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/compute-test-shard.sh -->
# Research: sources/storage-engines/rocksdb/.github/scripts/compute-test-shard.sh

Purpose: Computes a round-robin subset of RocksDB test binaries for a CI shard.

Important APIs/types/functions: CLI `compute-test-shard.sh <shard_index> <num_shards>`; runs `make -s list_all_tests`, filters `_test` binaries, sorts them, forces `db_test` first, uses awk modulo assignment, writes `subset=...` to `GITHUB_OUTPUT`, and prints shard summary.

Control flow: generate total sorted list, reorder heavyweight `db_test`, select lines where `(NR - 1) % nshards == shard`, then expose the space-separated list.

State and persistence behavior: writes temporary files under `/tmp` and one GitHub step output; no repository changes.

Dependencies and integration points: intended for GitHub Actions jobs that build/run only `ROCKSDBTESTS_SUBSET`; depends on the Makefile's `list_all_tests` target.

Risks: no validation that shard index is within range or integer. Uses fixed `/tmp` filenames, so concurrent invocations in one runner could collide. Round-robin by sorted name is simple but not duration-aware.

Test signals: output summary with first/last/included counts and downstream shard jobs receiving the expected subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/compute-test-shard.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/parse-claude-review.js -->
# Research: sources/storage-engines/rocksdb/.github/scripts/parse-claude-review.js

Purpose: Parses Claude Code execution logs and converts them into a standardized AI review/comment Markdown body.

Important APIs/types/functions: exports `parseClaude({executionFile, conclusion, meta})`; internal `getTriggerLine` chooses manual/auto early/auto late text; `getLastAssistantText` recovers substantial assistant text from logs; uses `build-ai-review-comment.js`.

Control flow: reads and parses a JSON execution log, finds the `type === 'result'` message, handles success, generic error, `error_max_turns`, partial fallback, empty output, and parse exceptions, then builds a comment with Claude-specific footer commands.

State and persistence behavior: reads the execution file only and returns text; it does not write comments itself.

Dependencies and integration points: called by `ai-review-analysis.yml` in Claude auto/manual paths after `anthropics/claude-code-base-action`. The produced file is uploaded and later posted by `ai-review-comment.yml`.

Risks: assumes the execution log is a JSON array with Claude action message schema. It truncates recovered text to 50k chars but successful results are not truncated here. It embeds generated output directly into PR comments.

Test signals: successful parser step writes `claude-review-comment.md`; failure modes show parse/error messages in the posted artifact.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/parse-claude-review.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/parse-codex-review.js -->
# Research: sources/storage-engines/rocksdb/.github/scripts/parse-codex-review.js

Purpose: Parses Codex CLI review artifacts and builds the standardized Codex PR comment body.

Important APIs/types/functions: exports `parseCodex({responseFile, recoveryFile, findingsFile, logFile, exitCode, meta})`; helpers `getTriggerLine`, `readIfPresent`, and `tailFile`; uses `build-ai-review-comment.js`.

Control flow: prefers a recovery file, then direct final response, then incremental `review-findings.md`, otherwise tails the execution log and emits failure text. It chooses partial/success/warning icon based on `meta.isPartial` and numeric exit code.

State and persistence behavior: only reads artifact files and returns Markdown. It caps log tail at 12k characters to avoid enormous comments.

Dependencies and integration points: invoked by shared AI review workflow after Codex auto/manual runs and optional recovery. Output is posted by the comment workflow.

Risks: missing `OPENAI_API_KEY` paths can still lead to parser output depending on generated files. Direct responses are not size-capped. Exit-code parsing defaults to failure if absent.

Test signals: generated `codex-review-comment.md`, parser fallback text when review fails, and uploaded Codex logs for diagnosis.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/parse-codex-review.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/post-pr-comment.js -->
# Research: sources/storage-engines/rocksdb/.github/scripts/post-pr-comment.js

Purpose: Shared GitHub API utility for creating, updating, pruning, deleting, or superseding PR comments by marker.

Important APIs/types/functions: exports async `postPrComment` with `github`, `context`, `core`, `prNumber`, `body`, `marker`, optional `legacyMarkers`, `prunePrefix`, `preserveLatest`, `obsoleteMarker`, and `obsoleteTitle`. Internal helpers list comments, sort by activity time/id, identify obsolete comments, build obsolete bodies, delete comments, and supersede comments.

Control flow: validates input, ensures the marker is embedded, lists comments, updates an exact marker match if present, creates a fresh comment if update is absent or races with 404, then prunes related legacy/prefix comments while preserving the newest active comments.

State and persistence behavior: mutates GitHub issue comments through REST API calls. It does not write local files.

Dependencies and integration points: used by clang-tidy and AI review comment workflows through `actions/github-script`. Works with marker schemes from `ai-review-comment.yml`.

Risks: concurrent workflows can race between list/update/create/prune; the code handles 404 but still relies on ordering heuristics. Superseding preserves original bodies inside details, which can create very large comments. Marker collisions across bots would cause unintended updates.

Test signals: unit tests in `post-pr-comment.test.js` cover create/update, legacy migration, 404 races, and concurrent newer-comment supersession.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/post-pr-comment.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/post-pr-comment.test.js -->
# Research: sources/storage-engines/rocksdb/.github/scripts/post-pr-comment.test.js

Purpose: Node test suite for `post-pr-comment.js` comment creation, update, legacy migration, 404 handling, and supersession logic.

Important APIs/types/functions: uses `node:test`, `node:assert/strict`, `postPrComment`, constants `OBSOLETE_MARKER` and `OBSOLETE_TITLE`, harness helpers `makeComment`, `createHarness`, `createCore`, `escapeRegExp`, and `assertObsoleteComment`.

Control flow: each test builds an in-memory fake Octokit/context/core, calls `postPrComment` with different marker/pruning options, then asserts recorded update/create/delete calls and final fake comments. One test injects a new newer comment during the second pagination to simulate concurrent workflow behavior.

State and persistence behavior: all state is in-memory fake comments and call logs. No real GitHub API or filesystem is used.

Dependencies and integration points: validates the script used by `clang-tidy-comment.yml` and `ai-review-comment.yml`; runnable with modern Node's built-in test runner.

Risks: harness abstracts away pagination parameters, REST response details, rate limits, and permission failures. It does not test every branch, such as missing body/prNumber or delete-without-obsolete-title.

Test signals: `node --test .github/scripts/post-pr-comment.test.js` should pass and confirm stable comment marker behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/post-pr-comment.test.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/ai-review-analysis.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/ai-review-analysis.yml

Purpose: Reusable workflow implementing shared Claude/Codex PR analysis for automatic and manual AI review/query requests.

Important APIs/types/functions: `workflow_call` inputs select provider, display name, slash commands, artifact/comment filenames, default/selected/classifier/recovery models, thinking budget, dispatch PR number, and authorized users. Jobs are `auto-review` and `manual-review`. Major steps gather PR info, gate early reviews, avoid duplicate review artifacts, checkout base repo, install Codex, generate prompts/diffs, classify complexity, run Claude or Codex, recover partial findings, build comments through parser scripts, and upload artifacts/logs.

Control flow: auto mode runs on `pull_request_target` for same-repo PRs after a checks threshold or on `workflow_run` fallback after PR CI success. It skips stale SHAs and existing comments. Manual mode accepts `workflow_dispatch` or authorized issue comments containing review/query commands, resolves PR metadata, builds either review or query prompts, and runs the chosen provider with optional model/budget overrides.

State and persistence behavior: writes temporary diff/prompt files, review outputs, execution logs, metadata files (`pr_number.txt`, `trigger_type.txt`, `head_sha.txt`, etc.), and uploads short-retention artifacts consumed by the comment workflow. It does not post comments directly.

Dependencies and integration points: called by `claude-review.yml` and `codex-review.yml`; depends on GitHub REST via `actions/github-script`, `actions/checkout`, `actions/setup-node`, `@openai/codex`, `anthropics/claude-code-base-action`, parser scripts, prompt files under `claude_md`, and repository PR CI workflow names.

Risks: Codex runs with `--dangerously-bypass-approvals-and-sandbox`; the workflow limits that to read-only analysis and same-repo early triggers, but it is still arbitrary command execution on the runner. Diff truncation can miss issues. Early-review gate can skip reviews due to CI timing. Secrets must be present for provider execution. Manual authorization is a hardcoded JSON list.

Test signals: uploaded provider result artifact, execution log artifacts, skip reasons in logs, generated comment markdown, and successful downstream comment workflow posting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/ai-review-analysis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/ai-review-comment.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/ai-review-comment.yml

Purpose: Reusable workflow that downloads AI review artifacts and posts/updates PR comments, plus reactions for manual requests or failures.

Important APIs/types/functions: `workflow_call` inputs `provider`, `result_artifact_name`, and `comment_file`; jobs `comment`, `failure-notice`, and `unauthorized-notice`. Uses `actions/download-artifact`, sparse checkout of `.github/scripts`, `post-pr-comment.js`, and GitHub reactions API.

Control flow: on successful analysis workflow runs, downloads the result artifact, reads metadata, chooses marker strategy for auto vs manual comments, and posts via shared script. Manual requests get a rocket reaction. Failed analysis runs can add a confused reaction to the triggering comment if metadata exists.

State and persistence behavior: mutates PR issue comments and reactions through GitHub API. Reads downloaded artifact files only.

Dependencies and integration points: called by `claude-review-comment.yml` and `codex-review-comment.yml` on provider workflow completion. Requires `pull-requests: write` and `issues: write`.

Risks: artifact download can fail silently due to `continue-on-error`, causing no comment. Auto marker includes workflow run id and prunes old provider auto comments, so marker bugs can leave duplicates. The unauthorized notice only logs skipped workflows.

Test signals: PR comments with provider-specific markers, obsolete comment collapse for older auto reviews, and reactions on manual trigger comments.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/ai-review-comment.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/benchmark-linux.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/benchmark-linux.yml

Purpose: Manually triggered benchmark workflow for RocksDB Linux benchmark runs.

Important APIs/types/functions: workflow name `facebook/rocksdb/benchmark-linux`; trigger `workflow_dispatch`; job `benchmark-linux` uses checkout, `build-for-benchmarks`, `perform-benchmarks`, and `post-benchmarks`.

Control flow: only runs for `github.repository_owner == 'facebook'`, builds release binaries, runs benchmark script, uploads and posts benchmark results.

State and persistence behavior: creates build outputs, benchmark DB/temp data, benchmark result artifacts, and optional external visualization documents.

Dependencies and integration points: composes the three benchmark actions in this subset. Depends on GitHub runner temp storage and benchmark tooling in the repository.

Risks: schedule is commented out as temporarily disabled, so benchmarks require manual dispatch. Uses `ubuntu-latest` with a FIXME to return to self-hosted, so performance comparability is limited.

Test signals: successful manual workflow with `benchmark-results` artifact and benchmark report TSV.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/benchmark-linux.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/clang-tidy-comment.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/clang-tidy-comment.yml

Purpose: Posts or updates a PR comment containing clang-tidy results from the separate clang-tidy workflow.

Important APIs/types/functions: triggered by completed `workflow_run` for workflow `clang-tidy`; job downloads `clang-tidy-result`, reads `clang-tidy-comment.md` and `pr_number.txt`, and calls `post-pr-comment.js` with marker `<!-- clang-tidy-bot -->`.

Control flow: only handles pull_request-origin workflow runs. If artifact download succeeds and files exist, it posts/updates the comment.

State and persistence behavior: mutates PR comments through GitHub API; downloaded artifacts are temporary.

Dependencies and integration points: pairs with `clang-tidy.yml`; requires sparse checkout of scripts and `pull-requests: write`.

Risks: if artifact is missing or the workflow was a push run, no comment is posted. Uses one stable marker, so every new clang-tidy result replaces the old bot comment.

Test signals: PR comment appears or updates after clang-tidy workflow completion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/clang-tidy-comment.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/clang-tidy.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/clang-tidy.yml

Purpose: Runs clang-tidy on changed files for push and pull_request events and uploads a comment artifact.

Important APIs/types/functions: job `clang-tidy` uses a RocksDB Ubuntu 24.1 container, checkout depth 2, diff-base calculation, `apt-get install clang-tidy-21`, CMake compile commands generation with clang-21, `tools/run_clang_tidy.py` with GitHub annotations/summary/comment output, and artifact upload.

Control flow: skips new branch pushes with all-zero `github.event.before`; otherwise determines base SHA, builds `compile_commands.json`, runs clang-tidy on changed files with `continue-on-error`, saves PR number for PR events, uploads artifacts, and finally fails the job if clang-tidy found issues.

State and persistence behavior: creates `build/compile_commands.json`, symlink `compile_commands.json`, `clang-tidy-comment.md`, `pr_number.txt`, and the uploaded `clang-tidy-result` artifact.

Dependencies and integration points: paired with `clang-tidy-comment.yml`; depends on CMake, clang-21, `tools/run_clang_tidy.py`, and the container image.

Risks: repository-owner guard prevents fork owners from running this workflow. Push diff base handling can skip or mis-scope unusual histories. CMake config cost is paid even for small diffs.

Test signals: annotations, step summary, uploaded comment artifact, and final failure when issues are found.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/clang-tidy.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/claude-review-comment.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/claude-review-comment.yml

Purpose: Provider-specific wrapper that posts Claude review comments using the shared AI comment workflow.

Important APIs/types/functions: triggered by completed workflow `Claude Code Review`; job `review-comment` calls `./.github/workflows/ai-review-comment.yml` with provider `claude`, artifact `claude-review-result`, and comment file `claude-review-comment.md`.

Control flow: delegates all logic to the reusable comment workflow and inherits secrets.

State and persistence behavior: no direct state beyond delegated comment/reaction mutations.

Dependencies and integration points: pairs with `claude-review.yml` and shared `ai-review-comment.yml`.

Risks: workflow name coupling means renaming the analysis workflow breaks trigger matching. Permissions must include both pull request and issue write.

Test signals: Claude analysis completion results in posted or updated Claude PR comments.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/claude-review-comment.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/claude-review.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/claude-review.yml

Purpose: Provider-specific wrapper exposing Claude Code Review triggers and inputs while delegating implementation to shared AI analysis.

Important APIs/types/functions: triggers on `workflow_run` of `facebook/rocksdb/pr-jobs`, same-repo `pull_request_target`, `issue_comment`, and `workflow_dispatch`. Inputs include PR number, Claude model choice, and thinking budget. Calls `ai-review-analysis.yml` with provider `claude`, commands `/claude-review` and `/claude-query`, default model `claude-opus-4-6`, classifier/recovery `claude-sonnet-4-6`.

Control flow: skips fork PRs on the early `pull_request_target` path and otherwise delegates to reusable workflow.

State and persistence behavior: state is produced by the called reusable workflow as artifacts/logs, not directly here.

Dependencies and integration points: pairs with `claude-review-comment.yml`, `ai-review-analysis.yml`, and the PR jobs workflow name.

Risks: hardcoded model choices and workflow names can drift. Same-repo condition protects early trigger, while fork reviews rely on workflow_run fallback.

Test signals: dispatch/manual/comment/auto triggers produce Claude review result artifacts and downstream comments.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/claude-review.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/codex-review-comment.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/codex-review-comment.yml

Purpose: Provider-specific wrapper that posts Codex review comments through the shared AI comment workflow.

Important APIs/types/functions: triggered by completed `Codex Code Review`; calls `ai-review-comment.yml` with provider `codex`, artifact `codex-review-result`, and comment file `codex-review-comment.md`.

Control flow: all logic is delegated to the reusable comment workflow.

State and persistence behavior: no direct local state; delegated workflow mutates PR comments/reactions.

Dependencies and integration points: pairs with `codex-review.yml`.

Risks: trigger depends on exact analysis workflow name. Permission scope must allow issue and pull-request writes.

Test signals: Codex result artifacts become PR comments with Codex markers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/codex-review-comment.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/codex-review.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/codex-review.yml

Purpose: Provider-specific wrapper exposing Codex Code Review triggers and model inputs while using shared AI analysis.

Important APIs/types/functions: triggers on `workflow_run` of `facebook/rocksdb/pr-jobs`, same-repo `pull_request_target`, `issue_comment`, and `workflow_dispatch`. Inputs include PR number, Codex model choice (`gpt-5.5`, `gpt-5.3-codex`, `gpt-5.2-codex`) and thinking budget. Calls shared analysis with commands `/codex-review` and `/codex-query`.

Control flow: skips early pull_request_target for fork PRs; reusable analysis handles auto/manual/query branches.

State and persistence behavior: artifacts and logs are produced in the called workflow, including Codex output/recovery files.

Dependencies and integration points: pairs with `codex-review-comment.yml`, shared analysis, OpenAI API secret, and Codex CLI installation.

Risks: Codex CLI execution in shared workflow bypasses approvals/sandbox, so trust boundary depends on trigger restrictions. Model list can go stale. Workflow name coupling to PR jobs controls auto review.

Test signals: Codex review artifacts/logs and downstream PR comments.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/codex-review.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/nightly-candidate.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/nightly-candidate.yml

Purpose: Manual holding workflow for nightly jobs that are currently broken or not ready for the main nightly schedule.

Important APIs/types/functions: workflow name currently matches `facebook/rocksdb/nightly`; trigger `workflow_dispatch`; job `build-linux-arm-test-full` installs gflags and runs `make V=1 J=4 -j4 check` on `arm64large`.

Control flow: only runs for repository owner `facebook`; checkout, pre-steps, install gflags, full check, post-steps.

State and persistence behavior: produces build/test outputs and artifacts through `post-steps`; no persistent repo state.

Dependencies and integration points: related to `nightly.yml` but separated for failing/broken candidates.

Risks: workflow name duplicates the main nightly name, which can confuse workflow_run triggers and UI. Requires an `arm64large` self-hosted label that may be unavailable.

Test signals: manual dispatch success indicates the ARM full test candidate may be ready for promotion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/nightly-candidate.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/nightly.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/nightly.yml

Purpose: Scheduled and manual nightly RocksDB CI covering long-running, platform-specific, Folly, Windows, ARM, examples, and fuzz build lanes.

Important APIs/types/functions: triggers daily at `0 9 * * *` and `workflow_dispatch`; jobs include format compatibility, non-shm Linux check, clang21 ASAN/UBSAN with Folly, CMake/release Folly builds, Windows AVX2, ARM full/crash tests, examples, fuzzers, and Folly-lite CMake.

Control flow: each job is guarded to `github.repository_owner == 'facebook'`; most jobs checkout, run shared pre-steps and specialized dependency setup, execute make/CMake/ctest commands, then upload post-step artifacts.

State and persistence behavior: produces build directories, test temp data, crash-test files, swapfile on ARM crash job, and artifacts. No commits or durable repo changes.

Dependencies and integration points: shares actions from this subset (`pre-steps`, `setup-folly`, `cache-folly`, `build-folly`, `windows-build-steps`, `post-steps`) and exercises repository scripts such as `check_format_compatible.sh`, fuzz Makefiles, and crash tests.

Risks: long-running nightly jobs depend on self-hosted labels, container images, external package managers, and large `/dev/shm`/swap resources. One Folly ASAN job manually disables ccache wrappers, which is fragile. ARM crash job mutates system swap and shm.

Test signals: daily green nightly workflow, uploaded artifacts/logs, and coverage of paths too expensive for PR CI.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/nightly.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/pr-jobs-candidate.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/pr-jobs-candidate.yml

Purpose: Manual staging workflow for PR jobs that are failing or not ready for the main PR workflow.

Important APIs/types/functions: workflow_dispatch only; jobs `build-linux-arm` and `build-linux-arm-cmake-no_test_run` on `arm64large`; uses checkout, `pre-steps`, `install-gflags`, make/CMake commands, Java environment setup, and `post-steps`.

Control flow: owner-guarded jobs run ARM make or CMake build variants manually.

State and persistence behavior: creates build outputs and artifacts only.

Dependencies and integration points: mirrors jobs that may later move into `pr-jobs.yml`; depends on ARM self-hosted runners and JDK path `/usr/lib/jvm/java-8-openjdk-arm64`.

Risks: candidate jobs are explicitly broken or unstable. Hardcoded runner labels and Java paths can block execution.

Test signals: manual green candidate runs justify promotion into regular PR CI.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/pr-jobs-candidate.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/pr-jobs.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/pr-jobs.yml

Purpose: Main RocksDB PR/push CI workflow aggregating fast checks and broad build/test coverage across Linux, macOS, Windows, Java, sanitizers, Folly, ARM, and formatting.

Important APIs/types/functions: top-level `ONLY_JOB` override; `config` job exports it. Jobs include `check-format-and-targets`, core Linux `make check`, CMake MinGW, Folly make/CMake, benchmark CMake shards, encrypted env no compression, release builds, clang/gcc no-test builds, unity/header checks, mini crash tests, ASAN/UBSAN/TSAN shards, alternate namespace static build, macOS make/CMake/Java variants, Windows VS2022 matrix, Java/PMD, and ARM subset build. Uses many composite actions from this subset.

Control flow: jobs run on push/pull_request but are owner-gated to `facebook` unless `ONLY_JOB` is set. Matrix jobs shard tests by CTest or selected suite lists. Shared setup/post actions wrap most jobs; ccache setup/teardown surrounds compiler-heavy lanes.

State and persistence behavior: creates build directories, ccache directories, test temp outputs, PMD/Maven artifacts, failure logs, core dumps, and uploaded GitHub artifacts. No repository commits are made.

Dependencies and integration points: central integration point for local actions (`pre-steps`, `setup-ccache`, `teardown-ccache`, `post-steps`, Folly/cache actions, macOS installers, Windows build action), repository Make/CMake targets, container images, self-hosted runner labels, GitHub artifacts, and downstream AI review `workflow_run` triggers.

Risks: a single workflow contains many independent lanes, so syntax errors can block all PR signal. Owner gating prevents fork runner hangs but reduces fork-local validation. Many jobs depend on specific labels/images/tool versions. `ONLY_JOB` is powerful but requires editing workflow env. High parallelism and large artifacts can stress runners.

Test signals: required PR checks, matrix shard results, uploaded test artifacts, ccache stats, and downstream workflow_run consumers such as AI review wrappers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/pr-jobs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/weekly.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/weekly.yml

Purpose: Weekly long-running RocksDB Valgrind CI workflow.

Important APIs/types/functions: scheduled at `0 9 * * 0` plus manual dispatch; job `build-linux-valgrind` runs with `timeout-minutes: 840`, 16-core Ubuntu runner, RocksDB Ubuntu 22.1 container, shared pre-steps, `make V=1 -j20 valgrind_test`, and post-steps.

Control flow: owner-gated weekly job checks out the repo, applies common environment, runs Valgrind tests, then uploads artifacts.

State and persistence behavior: creates Valgrind/test outputs and post-step artifacts. No durable repo state.

Dependencies and integration points: complements PR/nightly workflows with expensive memory-check coverage.

Risks: very long timeout and Valgrind overhead can consume runner capacity. Container/toolchain drift can affect reports. Failures may be delayed until weekly cadence.

Test signals: weekly Valgrind pass/fail and uploaded logs for memory diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/weekly.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.lgtm.yml -->
# Research: sources/storage-engines/rocksdb/.lgtm.yml

Purpose: LGTM/CodeQL-style extraction configuration for RocksDB C++ indexing.

Important APIs/types/functions: YAML `extraction.cpp.index.build_command: make static_lib`.

Control flow: external analysis service reads this file and builds `static_lib` to observe compilation for indexing.

State and persistence behavior: no runtime state in repository; analysis workers create build outputs externally.

Dependencies and integration points: integrates RocksDB with LGTM code analysis and the repository Makefile.

Risks: if `make static_lib` no longer captures important compile units or needs dependencies unavailable in the analysis environment, code intelligence quality drops. LGTM service support may have changed over time, so the file may be legacy.

Test signals: successful external C++ extraction/indexing; locally, `make static_lib` remains a rough compatibility signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.lgtm.yml -->
