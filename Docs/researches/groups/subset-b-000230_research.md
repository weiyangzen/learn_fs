# Research: subset-b-000230

This grouped report covers the Nydus smoke-test files and two `nydus-image` Rust modules assigned to subset B item `subset-b-000230`. Each section preserves the original source path and is bounded by reconciliation markers for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/cas_test.go -->
# sources/cloud-native/nydus/smoke/tests/cas_test.go

## Purpose
This Go smoke-test suite validates the Nydus chunk deduplication/CAS SQLite database side effects while mounting RAFS images with `nydusd`. It verifies both direct daemon startup with a dedup DB and API-driven submount lifecycle cleanup, with prefetch enabled and disabled.

## Important APIs, Types, And Functions
`CasTestSuite` exposes two dynamic suite generators. `TestCasTables` iterates `enable_prefetch=false,true` and calls `testCasTables`; `TestCasGcUmountByAPI` uses the same dimension and calls `testCasGcUmountByAPI`. `testCasTables` uses `texture.PrepareLayerWithContext`, sets `ctx.Runtime.ChunkDedupDb`, mounts through `tool.NewNydusdWithContext`, verifies the mounted tree, opens SQLite, checkpoints WAL, and asserts `Blobs` has one row and `Chunks` reaches thirteen rows. `testCasGcUmountByAPI` starts a generic `nydusd`, mounts an image through `/api/v1/mount`, verifies at a subpath, checks nonzero CAS rows, deletes the cache directory to mimic snapshotter cache cleanup, unmounts by API, and requires the CAS tables to be empty.

## Control Flow
The test flow is build synthetic texture layer, configure dedup DB path, run daemon, mount, walk/compare files, inspect DB, then unmount. The API GC variant first starts `nydusd` without a bootstrap, constructs the full per-mount config after the daemon is running, mounts `/mount` by API, then tests cleanup after `DELETE /api/v1/mount`.

## State And Persistence
The central persistent artifact is `cas.db` under the test work directory. It uses SQLite WAL behavior, so tests issue `PRAGMA wal_checkpoint(FULL)` before reads. The API GC test deletes `cache/` before unmount to simulate external snapshotter state loss and expects Nydus CAS tables to be garbage-collected on API unmount.

## Dependencies And Integration Points
This depends on `github.com/mattn/go-sqlite3`, `texture` layer builders, `tool.Nydusd`, and the local `nydusd` API socket. It also relies on Nydus creating tables named `Blobs` and `Chunks`, so schema naming is an integration contract with daemon-side CAS code.

## Risks
The fixed chunk count of thirteen is tightly coupled to the synthetic texture layer and packing behavior. Chunk insertion can lag behind filesystem reads, so the polling loop protects only `Chunks` in the direct mount test. The tests require working FUSE, SQLite driver availability, and sufficient privileges for the texture layer.

## Test Signals
Success signals include exact or nonzero CAS row counts, zero file-tree mismatches from `nydusd.Verify`, and zero rows after API unmount cleanup. Failures identify regressions in CAS population, WAL visibility, API submount cleanup, prefetch interaction, or file-serving correctness.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/cas_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/chunk_dedup_test.go -->
# sources/cloud-native/nydus/smoke/tests/chunk_dedup_test.go

## Purpose
This suite verifies runtime chunk deduplication across two independent mounts that share the same CAS database. It expects the second mount to issue fewer backend reads because metadata learned from the first mount can be reused.

## Important APIs, Types, And Functions
`ChunkDedupTestSuite` has `TestChunkDedup`, a dynamic generator with a single `iteration` value. It creates a temporary SQLite DB and passes it to `testRemoteWithDedup`. `testRemoteWithDedup` builds two separate texture layers and contexts, disables prefetch, points both contexts at the same `ChunkDedupDb`, mounts each with `tool.NewNydusdWithContext`, verifies file trees, fetches backend metrics, and compares read count and read amount.

## Control Flow
The first mount warms/populates the shared dedup DB while serving the synthetic file tree. The second mount repeats the same access pattern against a fresh workdir but the same DB. The final assertions compare `metrics.ReadCount` and `metrics.ReadAmountTotal`, requiring the first run to be greater than the second.

## State And Persistence
The shared DB path is created outside either Nydus workdir, then removed after the generator scope. Per-mount blob/cache/bootstrap data lives in each context workdir and is destroyed with deferred cleanup.

## Dependencies And Integration Points
The test depends on `nydusd` backend metrics from `/api/v1/metrics/backend`, `texture.PrepareLayerWithContext`, and consistent synthetic layer content. It integrates with runtime chunk dedup lookup/write paths through `ctx.Runtime.ChunkDedupDb`.

## Risks
The test is metric-sensitive: backend read counts may vary with prefetch, cache remnants, daemon implementation changes, or timing. It disables prefetch to reduce noise, but any non-determinism in verification order or cache sharing outside the DB can affect the comparison.

## Test Signals
Primary signals are no backend read errors for either mount and strictly lower read count/bytes for the second mount. These indicate dedup DB reuse rather than merely successful mounting.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/chunk_dedup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/commit_test.go -->
# sources/cloud-native/nydus/smoke/tests/commit_test.go

## Purpose
This suite validates committing a writable container based on a Nydus image and running the committed image through the Nydus snapshotter. It ensures files copied into the container's writable layer are preserved after `nydusify commit`.

## Important APIs, Types, And Functions
`CommitTestSuite` stores a root `*testing.T` because its dynamic generator prepares images before returning subtests. `TestCommitContainer` iterates `ubuntu:latest` over RAFS fs versions 5 and 6. `prepareImage` prepares a local registry source, converts it with `nydusify convert`, and returns the Nydus target plus committed target name. `TestCommitAndCheck` runs the image via `nerdctl --snapshotter nydus`, copies a generated `commit` file into `/root`, invokes `nydusify commit`, runs the committed image, and checks the file content with `nerdctl exec`. Helpers `checkFileContent` and `nerdctlExec` wrap command execution.

## Control Flow
The test first converts the base image, starts a long-lived shell container, mutates it by copying a file, commits the container to a new image, starts a second container from the committed image, and verifies the committed layer content.

## State And Persistence
State is external to the Go process: registry images, containerd/nerdctl containers, and temporary workdir files. The workdir is destroyed after the mutation step, while containers and images are removed through `tool.ClearContainer` defers.

## Dependencies And Integration Points
The test integrates with Docker/registry preparation, `nydusify convert`, `nydusify commit`, `nerdctl`, containerd, and the Nydus snapshotter. It also depends on `uuid` for isolated container names and `tool.PrepareImage` for registry naming.

## Risks
Commands are string-built and executed through shell wrappers, so image names and paths must remain shell-safe. The generator performs image conversion before the returned subtest executes, which can make failures appear during test enumeration rather than in a named subtest. The misspelled `commitedImage` parameter is cosmetic.

## Test Signals
The strongest signal is `stat` plus exact-content `grep` of `/root/commit` inside the committed container. Setup failures expose conversion, registry, snapshotter, or commit CLI regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/commit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/compatibility_test.go -->
# sources/cloud-native/nydus/smoke/tests/compatibility_test.go

## Purpose
This suite verifies cross-version compatibility among `nydus-image`, `nydusify`, `nydusd`, RAFS fs versions, and modern checker binaries. It reuses the main image conversion/check path while varying stable, legacy, and latest binaries.

## Important APIs, Types, And Functions
`CompatibilityTestSuite` stores `t` and a `preparedImages` cache. `TestConvertImages` requires `NYDUS_STABLE_VERSION`, builds a Cartesian matrix for image, RAFS version, nydus-image version, nydusify version, and nydusd version, and skips invalid legacy combinations. It resolves versioned binaries through `tool.GetBinary`, configures `tool.BinaryContext`, sets lz4 block compression, and delegates to `ImageTestSuite.TestConvertAndCopyImage` with copy disabled. `prepareImage` caches the registry-prepared image reference.

## Control Flow
For each valid matrix row, the generator resolves all binaries, builds a context that uses the selected converter and daemon but latest nydusify for checking, prepares the image once, then performs conversion and check in a subtest.

## State And Persistence
Prepared registry images are cached in memory for the suite. Each conversion gets a workdir from `ImageTestSuite` and creates target images in the registry/container runtime. No local persistent state is intentionally retained by this file.

## Dependencies And Integration Points
The test depends on environment variables for versioned binaries such as `NYDUS_BUILDER_<version>` and `NYDUS_NYDUSD_<version>`, plus `NYDUS_STABLE_VERSION`. It integrates directly with the main `ImageTestSuite`, making image conversion behavior the compatibility contract.

## Risks
The scenario matrix can be large and slow. Legacy v0.1.0 rules are hard-coded, and future compatibility constraints may need updates. Because it calls into another suite method, failures can be reported under compatibility names while originating in image conversion/check mechanics.

## Test Signals
A passing matrix row proves the selected image builder, converter, checker, daemon, and RAFS version can produce and validate a Nydus image for `nginx:latest`. Skipped rows document known unsupported combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/compatibility_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/external_test.go -->
# sources/cloud-native/nydus/smoke/tests/external_test.go

## Purpose
This file smoke-tests Nydus external backend/model artifact support. It validates both library-level modctl metadata generation and binary `nydusify convert` modes for `modelfile` and `model-artifact` sources, then mounts and compares the resulting external-backed filesystem against a model context directory.

## Important APIs, Types, And Functions
Global environment-backed variables define model work/context directories, registry auth, and image reference. `proxy` models runtime external proxy settings. `walk` builds `tool.File` maps while skipping files larger than 128 MiB. `check` compares target files to source files. `verify` launches `nydusd` with an `ExternalBackendConfigPath` and compares mounted content. `packWithAttributes` packs a source directory with external blob attributes and returns internal/external blob digests. `parseReference` extracts registry host, repository path, and tag. `TestModctlExternal` generates `.nydusattributes`, backend metadata/config, builds an external bootstrap, checks it, rewrites runtime backend config, and mounts. `TestModctlExternalBinary` invokes `nydusify convert` using source-backend types `modelfile` and `model-artifact`. `convertAndCheck`, `buildFsViewer`, and `buildRuntimeExternalBackendConfig` pull bootstraps from converted images, check them, and inject runtime backend/proxy/auth configuration.

## Control Flow
Tests skip unless `NYDUS_MODEL_IMAGE_REF` is set. The library path either uses an existing `NYDUS_BOOTSTRAP`/`NYDUS_EXTERNAL_BACKEND_CONFIG` or generates external metadata, packs the model context into Nydus/external blobs, unpacks the bootstrap, checks it, rewrites backend runtime settings, and mounts. The binary path runs two subtests with different source backend types, then pulls and checks the produced bootstrap before mounting.

## State And Persistence
Temporary workdirs hold generated attributes, backend meta/config JSON, external blobs, bootstraps, and pulled artifacts. Runtime backend config is mutated in place by `buildRuntimeExternalBackendConfig` with auth, host, repo, timeout, proxy URL, and cache directory. Optional `NYDUS_ONLY_MOUNT=true` intentionally keeps the mount alive for five hours for debugging.

## Dependencies And Integration Points
This file integrates with `contrib/nydusify` packages (`modctl`, external backend handlers, parser, provider, viewer, checker tools), `snapshotter-converter`, `nydus-image check`, and `nydusd`. It requires external registry/model credentials and proxy/cache environment variables for real model artifacts.

## Risks
The tests depend heavily on external services, registry auth, local model directories, and large model contents. `walk` skips large files, so content verification is metadata-oriented for big artifacts. `convertAndCheck` uses `assert.NoError`, so later steps may run after an earlier command failure and produce secondary errors.

## Test Signals
Signals include successful external metadata generation, bootstrap extraction and `nydus-image check`, successful mount with external backend config, and file metadata/content comparison against `NYDUS_MODELCTL_CONTEXT_DIR` for non-huge files.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/external_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/hot_upgrade_test.go -->
# sources/cloud-native/nydus/smoke/tests/hot_upgrade_test.go

## Purpose
This suite tests direct `nydusd` FUSE hot upgrade mechanics without a full snapshotter. It simulates snapshotter supervision, transfers FUSE daemon state from an old process to a new upgrade-mode process, and verifies the filesystem remains accessible.

## Important APIs, Types, And Functions
`HotUpgradeTestSuite` contains `buildLayer`, `newNydusd`, and `TestHotUpgrade`. `buildLayer` packs a texture lower layer with RAFS v5/lz4 and merges it into a bootstrap. `newNydusd` creates a `tool.Nydusd` with a shared supervisor socket, optionally adds `--upgrade`, starts it, waits for `RUNNING` or `INIT`, then mounts the RAFS source by API at `/`. `TestHotUpgrade` creates a `supervisor.SupervisorSet`, starts old and new daemons, uses `FetchDaemonStates`, `SendFd`, `SendFd`, `Exit`, `Takeover`, and `StartByAPI`, then verifies the mounted file tree.

## Control Flow
The sequence is build image, start supervisor, start old daemon and mount, fetch old FUSE fd, start new daemon in upgrade mode, ask old daemon to exit, send saved state to new daemon, call takeover, wait for `RUNNING` or `READY`, fetch the new daemon state, start it by API when needed, and verify content.

## State And Persistence
The workdir contains blobs, bootstrap, config JSON files, per-daemon API sockets, and the supervisor socket. The live FUSE fd is state transferred through the supervisor rather than through disk. Workdir cleanup removes artifacts after unmounts.

## Dependencies And Integration Points
This integrates `containerd/nydus-snapshotter/pkg/supervisor`, `tool.Nydusd` daemon API helpers, `texture` layers, and `snapshotter-converter`. It exercises `/api/v1/daemon/fuse/sendfd`, `/api/v1/daemon/fuse/takeover`, `/api/v1/daemon/exit`, `/api/v1/daemon/start`, and `/api/v1/mount`.

## Risks
Timing and state transitions differ across old and new daemon versions, so the test allows `RUNNING` or `READY`. It assumes supervisor socket semantics and FUSE fd transfer work on the host. Deferred `Umount` on old and new daemons may race if takeover changes ownership.

## Test Signals
A passing test means old daemon served content, supervisor captured its state, new daemon accepted takeover, reached a serving state, and preserved file-tree semantics after hot upgrade.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/hot_upgrade_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/image_test.go -->
# sources/cloud-native/nydus/smoke/tests/image_test.go

## Purpose
This is the main smoke suite for image conversion, checking, copying, saving/loading, encryption flag handling, zran/OCI reference mode, batch conversion options, and chunkdict generation.

## Important APIs, Types, And Functions
`ImageTestSuite` stores `T` and a prepared-image cache. `TestConvertImages` builds a matrix over `nginx:latest`, fs versions 5/6, zran, batch size, and encryption, with skips for unsupported combinations. `TestConvertAndCopyImage` prepares a workdir, constructs `nydusify convert` arguments, runs `nydusify check`, and optionally calls `testNydusifyCopy`. `testNydusifyCopy` copies target-to-target, saves to `file://saved.tar`, loads back, and checks each result. `TestGenerateChunkdicts` prepares three Redis versions and calls `TestChundict`. `TestChundict` converts training images, generates a chunkdict image, converts a test image, and checks it. `prepareImage` caches registry-prepared source images.

## Control Flow
Conversion tests prepare a local registry image, create a unique Nydus target, convert with the selected flags, check against the original, then exercise copy/save/load/check if enabled. Chunkdict tests convert two training Redis images, generate a dictionary image from them, convert the third Redis image, and verify the result.

## State And Persistence
Each conversion uses a temporary workdir for builder/check/copy artifacts. Persistent external state includes registry images and pushed/copied Nydus images. `saved.tar` is written into the workdir and checked for existence before load.

## Dependencies And Integration Points
This depends on `nydusify`, `nydus-image`, `nydusd`, the local registry, Docker/registry preparation, and `tool.RunWithoutOutput`. It is a central integration point for the compatibility suite and performance preparation.

## Risks
Shell command construction is simple string concatenation. Matrix skip logic is an implicit feature-support map and must track CLI/runtime capabilities. The chunkdict conversion command currently does not pass the generated chunkdict reference to the later convert command in this file, so it mainly validates generation and normal conversion/check unless the CLI has implicit behavior elsewhere.

## Test Signals
Signals are successful CLI exit for convert/check/copy/save/load/chunkdict generate and existence of `saved.tar`. Checker success is the behavioral proof that converted images mount and match the source image.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/image_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/main_test.go -->
# sources/cloud-native/nydus/smoke/tests/main_test.go

## Purpose
This file defines package-level smoke-test setup and teardown. It ensures a registry port is available, optionally starts a local Docker registry, configures logging, runs all tests, and removes the registry container afterward.

## Important APIs, Types, And Functions
Constants define `defaultSnapshotter` and `defaultSnapshotterSystemSock`. `TestMain` reads or defaults `REGISTRY_PORT` to `5077`, starts `tool.NewRegistry` unless `DISABLE_REGISTRY` is set, sets log flags/output, runs `m.Run`, destroys the registry if started, and exits with the test code.

## Control Flow
The setup runs before any package test. Environment defaults are set first because image preparation helpers depend on `REGISTRY_PORT`. The registry lifetime encloses `m.Run`.

## State And Persistence
The file mutates process environment and starts a Docker `registry:2` container. The registry container ID is held in memory and removed after tests. If the process is killed before teardown, Docker cleanup relies on the container's `--rm` behavior only when it exits.

## Dependencies And Integration Points
It integrates all image-based suites with `tool.Registry` and Docker. The default snapshotter constants are reused by takeover/performance-related tests.

## Risks
Starting a registry is global package state and may conflict with an existing service on the chosen port. `DISABLE_REGISTRY` shifts responsibility to the caller to provide a reachable registry. The teardown always exits the process, so deferred cleanup in `TestMain` itself is not used.

## Test Signals
No direct assertions are present, but a successful setup permits registry-backed image tests to run. Failures surface as fatal environment setting errors or registry command failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/native_layer_test.go -->
# sources/cloud-native/nydus/smoke/tests/native_layer_test.go

## Purpose
This suite validates native layer packing, merging, mounting, overlay semantics, chunkdict use, parent bootstrap merge behavior, repeatable builds, multiple compressors/fs versions/cache modes, and amplify I/O settings.

## Important APIs, Types, And Functions
Constants name matrix parameters shared by other tests. `checkDigests` compares digest slices order-insensitively. `NativeLayerTestSuite.TestMakeLayers` builds a broad Cartesian matrix over daemon version, compressor, fs version, chunk size, cache type/compression, RAFS mode, prefetch, batch, encryption, amplify I/O, and dedup DB, with skip rules for unsupported combinations. `TestAmplifyIO` narrows the matrix around `AmplifyIO`. `TestMergeLayerWithParentBootstrap` verifies parent-bootstrap merge returns only new upper digest and mounts correct overlay content. `testMakeLayers` is the large scenario implementation for chunkdict, lower, upper, base, and parent-bootstrap flows.

## Control Flow
The main implementation creates a chunkdict layer and bootstrap, packs lower and upper layers using that dictionary, asserts repeated packing yields identical digests, merges and mounts lower and overlay layers, then builds base layers and merges later layers with `ParentBootstrapPath` and `ChunkDictPath` pointing at the base bootstrap. Each stage verifies expected blob digest sets and mounted file trees.

## State And Persistence
All test artifacts live in a temporary workdir: source directories, blobs, cache, bootstraps, and optional CAS DB path. File-tree state is recorded in `tool.Layer.FileTree` and then mutated by `Overlay` to model merged layer behavior.

## Dependencies And Integration Points
It depends on `snapshotter-converter` pack/merge APIs, `texture` layer builders, `tool.Verify`/`tool.Nydusd`, and versioned `nydusd` resolution. It exercises builder output determinism, chunkdict metadata, parent bootstrap reuse, and runtime mount compatibility.

## Risks
The matrix is large and may be expensive. Some options such as `/tmp/cas.db` are shared paths that can carry cross-test state if parallel tests collide. Texture layers create special files and set capabilities, requiring privileges and host support. Skip logic is critical for avoiding unsupported combinations.

## Test Signals
Digest equality checks prove merge result accounting and repeatable builds. `tool.Verify` proves mounted metadata/content match expected synthetic trees after lower, overlay, and parent-bootstrap merges.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/native_layer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/overlay_fs_test.go -->
# sources/cloud-native/nydus/smoke/tests/overlay_fs_test.go

## Purpose
This suite verifies Nydus writable overlay configuration by mounting a RAFS lower layer with an overlay upper/work directory, writing through the mount, and confirming the new file lands in the upperdir.

## Important APIs, Types, And Functions
`OverlayFsTestSuite.prepareTestEnv` creates a default context, packs a lower texture layer, merges it with `OCIRef=true`, verifies the read-only lower mount, and returns the context. `TestSimpleOverlayFs` builds a `tool.NydusdConfig` with overlay upper/work dirs and `Writable=true`, mounts, writes `test.txt` under the mount, reads it back through the mount, then reads the same file directly from `ctx.Env.OvlUpperDir`.

## Control Flow
The test first proves the lower image is valid through a normal mount. It then starts a writable overlay Nydus mount, writes a file through FUSE, verifies read-after-write via FUSE, and checks upperdir persistence.

## State And Persistence
Temporary workdir state includes lower source, blobs, bootstrap, cache, mount, overlay upper, and overlay work directories. The file `test.txt` is expected to persist in the upperdir after it is written through the mount.

## Dependencies And Integration Points
This integrates `tool.NewNydusdWithOverlay`, the overlay-specific config template in `tool/nydusd.go`, `snapshotter-converter`, and kernel overlay/FUSE behavior. It also uses `containerd/log` for deferred unmount logging.

## Risks
Writable overlay behavior requires host permissions and compatible kernel features. The preliminary lower verification adds time but helps isolate pack/merge issues from overlay failures. The test covers file creation but not deletion, rename, whiteout, or metadata mutation through the writable mount.

## Test Signals
The key signals are successful writable mount, exact `hello world` read through the mount, and identical content in the upperdir backing file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/overlay_fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/performance_test.go -->
# sources/cloud-native/nydus/smoke/tests/performance_test.go

## Purpose
This opt-in suite checks that a Nydus-converted container image stays within backend read-count and read-byte baselines for a supported workload. It targets regression detection for fs-version-5, fs-version-6, and zran modes.

## Important APIs, Types, And Functions
`PerformanceTestSuite` stores root `t`, converted image, and container name. `TestPerformance` reads `PERFORMANCE_TEST_MODE`, defaults to `fs-version-6`, configures the build context, selects `PERFORMANCE_TEST_IMAGE` or defaults to `wordpress:6.1.1`, validates support through `tool.SupportContainerImage`, converts the image with `prepareTestImage`, and calls `tool.RunContainerWithBaseline`. `prepareTestImage` prepares a registry image, creates a unique Nydus target, and uses `tool.ConvertImage`.

## Control Flow
The suite is skipped unless `PERFORMANCE_TEST` is set. When enabled it converts the workload once, starts the workload through the Nydus snapshotter, waits for the workload readiness URL, fetches backend metrics, and compares against mode-specific baselines.

## State And Persistence
Converted image references are stored on the suite struct and in the registry/container runtime. The conversion workdir is managed by `tool.ConvertImage`. Runtime metrics come from the Nydus daemon API socket under the snapshotter directory.

## Dependencies And Integration Points
It depends on containerd, nerdctl, nydus-snapshotter, local registry, `nydusify`, `nydus-image`, `nydusd`, and the baseline maps in `tool/container.go`.

## Risks
Performance baselines are environment-sensitive. CPU, network, cache warmth, image version drift, and snapshotter behavior can produce noise. The test only supports images with readiness or stdout recipes in `tool/container.go`.

## Test Signals
A pass means backend read bytes and read count are no more than 105% of the configured baseline for the selected mode after the container workload becomes ready.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/performance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/takeover_test.go -->
# sources/cloud-native/nydus/smoke/tests/takeover_test.go

## Purpose
This opt-in suite validates snapshotter-managed Nydus daemon recovery and hot upgrade while a container remains accessible. It covers daemon failover after kill, rolling upgrades caused by snapshotter restart, and snapshotter API-triggered daemon upgrade.

## Important APIs, Types, And Functions
Global state captures snapshotter name, test image, system socket, and candidate `nydusd` paths. `TakeoverTestSuit` stores context, converted test image, and `tool.SnapshotterClient`. `NewTakeoverTestSuit` prepares and converts the image. `TestFailover` runs a container, fetches daemon info, kills each daemon PID, waits, and checks workload access. `TestRestartSnapshotterHotUpgrade` alternates two `nydusd` paths in `/etc/nydus/config.toml` and restarts `nydus-snapshotter` repeatedly. `TestAPIHotUpgrade` sends an `UpgradeRequest` to the snapshotter system API. Helpers parse daemon version output, rewrite TOML config, remove containers/images, and check HTTP workload readiness.

## Control Flow
`TestTakeover` skips unless `TAKEOVER_TEST=true`, initializes defaults and paths, chmods the new daemon binary, creates the suite, and runs it synchronously. Each case starts the same converted image, perturbs daemon or snapshotter state, waits for recovery, and probes the workload URL.

## State And Persistence
The test mutates host state: it writes `/etc/nydus/config.toml`, restarts a systemd service, kills daemon PIDs, creates/removes containers, and pushes/removes images. Snapshotter daemon information is fetched from the configured Unix system socket.

## Dependencies And Integration Points
This depends on root permissions, systemd, nydus-snapshotter, containerd/nerdctl, `tool.SnapshotterClient`, `containerd/nydus-snapshotter/config`, and TOML marshaling. It exercises `/api/v1/daemons` and `/api/v1/daemons/upgrade` on the snapshotter controller.

## Risks
This is host-invasive and not safe for generic CI without isolation. The hard-coded default config path and `/usr/local/bin/nydusd` fallback are deployment-specific. Fixed five-second waits may be too short or unnecessarily long depending on host load.

## Test Signals
Signals are continued successful HTTP access to the workload after daemon kill, after repeated snapshotter restarts with alternating daemon paths, and after snapshotter upgrade API invocation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/takeover_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/golang/entrypoint.sh -->
# sources/cloud-native/nydus/smoke/tests/texture/golang/entrypoint.sh

## Purpose
This shell entrypoint drives the Go language texture container smoke check. It changes to the mounted source directory and runs the Go program provided by `main.go`.

## Important APIs, Types, And Functions
The script has two commands: `cd /src` and `go run main.go`. It has no functions or arguments.

## Control Flow
When invoked by `tool.runCmdStdoutContainer`, the shell starts in the container, enters `/src`, compiles/runs the Go file with `go run`, and exits with the Go command status.

## State And Persistence
No persistent state is written intentionally. Go may create build cache state in the container depending on its environment.

## Dependencies And Integration Points
It is mounted into Go-capable container images by `tool/container.go` for the `golang` recipe. It assumes `/src/main.go` exists and the image has `go` in `PATH`.

## Risks
The script has no shebang and no strict shell flags. It relies on the caller invoking `sh /src/entrypoint.sh`. If `cd /src` fails, the next command still runs unless the shell exits due to caller settings, which it does not here.

## Test Signals
A zero exit from `go run main.go` proves the mounted source was readable and the Go runtime could execute the texture program.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/golang/entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/golang/main.go -->
# sources/cloud-native/nydus/smoke/tests/texture/golang/main.go

## Purpose
This tiny Go program is a language texture payload used by container smoke tests to validate source mounts and command execution inside Go images.

## Important APIs, Types, And Functions
It defines package `main`, imports `log`, and implements `main()` which logs `hello`.

## Control Flow
Program startup enters `main`, writes a timestamped log line to stderr/stdout according to Go logger defaults, and exits successfully.

## State And Persistence
It does not read or write files, network, or persistent process state.

## Dependencies And Integration Points
It is executed by `texture/golang/entrypoint.sh`, which is mounted into the container by `tool/container.go` for `golang` images.

## Risks
The signal is minimal: it proves compilation and execution, not complex filesystem behavior. Logger output formatting may differ from plain `hello`, but the harness only requires command success.

## Test Signals
The relevant signal is a successful `go run main.go` exit from the container.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/golang/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/java/Main.java -->
# sources/cloud-native/nydus/smoke/tests/texture/java/Main.java

## Purpose
This Java texture program is used by container smoke tests to validate that a mounted Java source file can be compiled and executed inside a Java-capable image.

## Important APIs, Types, And Functions
It defines class `Main` with `public static void main(String[] args)` and prints `hello` using `System.out.println`.

## Control Flow
The JVM enters `Main.main`, writes one line to stdout, and exits.

## State And Persistence
The source file itself is read by `javac`. Runtime state is transient, though compilation creates `Main.class` in `/src`.

## Dependencies And Integration Points
It is compiled and run by `texture/java/entrypoint.sh`, which is mounted for the `amazoncorretto` recipe in `tool/container.go`.

## Risks
The program is intentionally minimal and cannot detect nuanced filesystem issues beyond source readability and class file write support in the mounted directory.

## Test Signals
A successful `javac Main.java` followed by `java Main` indicates the mounted source directory is accessible and executable in the Java container.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/java/Main.java -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/java/entrypoint.sh -->
# sources/cloud-native/nydus/smoke/tests/texture/java/entrypoint.sh

## Purpose
This entrypoint compiles and runs the Java texture program in container smoke tests.

## Important APIs, Types, And Functions
It runs `cd /src`, `javac Main.java`, and `java Main`. There are no functions or parameters.

## Control Flow
The caller runs the script under `sh`. It changes to the mounted source directory, compiles `Main.java`, then launches the resulting class.

## State And Persistence
Compilation writes `Main.class` in `/src`. Because `/src` is a host-mounted texture directory, this can leave a generated class file unless cleaned outside this script.

## Dependencies And Integration Points
The script is selected for `amazoncorretto` images by `tool/container.go`, requiring a JDK with `javac` and `java`.

## Risks
No `set -e` means a failed `cd` or `javac` may not stop the script before the next command, although final nonzero status should still surface if `java Main` fails. Writing `Main.class` into the mounted source tree can dirty local state.

## Test Signals
Successful script exit verifies the Java toolchain can read/write/execute the mounted texture payload.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/java/entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/layer.go -->
# sources/cloud-native/nydus/smoke/tests/texture/layer.go

## Purpose
This package creates synthetic filesystem layers for Nydus smoke tests. The layers intentionally include regular files, large files, sparse files, directories, hardlinks, symlinks, special files, non-ASCII and long names, whiteouts, opaque markers, and xattrs to stress pack/merge/mount behavior.

## Important APIs, Types, And Functions
`LayerMaker` is a callback for customizing a `tool.Layer`. `LargerFileMaker` returns a callback that adds a large random file. `MakeChunkDictLayer` creates files useful for dictionary content. `MakeLowerLayer` creates the broad lower-layer fixture. `MakeThinLowerLayer` creates a privilege-light layer without special files for UFFD tests. `MakeUpperLayer` creates overlay updates, whiteouts, an opaque directory, and a capability xattr. `MakeMatrixLayer` creates small named files for parent-bootstrap matrix tests. `PrepareLayerWithContext` creates a default context, workdir, lower layer, OCI/RAFS blob pair, merges a bootstrap, and returns both context and layer.

## Control Flow
Most functions allocate a new `tool.Layer`, call `Create*` helpers to populate files, apply optional makers, and return the layer. `PrepareLayerWithContext` additionally packs via `PackRef`, merges with `tool.MergeLayers`, asserts the original OCI digest is returned, and sets `ctx.Env.BootstrapPath`.

## State And Persistence
The functions write real files, directories, links, sparse files, device nodes/FIFO, xattrs, blobs, and bootstraps under the caller-provided workdir. `MakeUpperLayer` and `MakeLowerLayer` call `setcap`, altering security xattrs on test files.

## Dependencies And Integration Points
This package depends on `tool.Layer`, `snapshotter-converter`, OpenContainers digests, `syscall`, and host `setcap`. It feeds most test suites, so its exact file set is an implicit contract for CAS counts, file-tree verification, overlay behavior, and chunkdict content.

## Risks
Special file creation and `setcap` require privileges/capabilities. The path with emoji and Chinese characters intentionally uses Unicode, which can reveal encoding/path handling issues but may be host-sensitive. Large random files increase disk and time cost.

## Test Signals
There are no direct tests in this file, but downstream `tool.Verify`, digest checks, CAS row counts, and mount comparisons all depend on these fixtures being constructed as expected.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/node/index.js -->
# sources/cloud-native/nydus/smoke/tests/texture/node/index.js

## Purpose
This Node.js texture starts a simple HTTP server used by container smoke tests that wait for a URL readiness signal.

## Important APIs, Types, And Functions
It imports Node's `http` module, creates a server callback that responds with status 200, content type `text/plain`, and body `hello\n`, then listens on port 80.

## Control Flow
When run as `node /src/index.js`, the process starts a long-lived HTTP server. Each request receives the same static response.

## State And Persistence
It keeps in-memory server state and binds port 80. It writes no files.

## Dependencies And Integration Points
`tool/container.go` uses it for the `node` recipe, mounting `tests/texture/node` to `/src` and passing `node /src/index.js` as container args. Readiness is checked by HTTP GET to `http://localhost:80`.

## Risks
Binding port 80 may require container privileges and can conflict with other host-network tests because containers run with `--net=host`. The server has no error handling for listen failures.

## Test Signals
The readiness signal is a successful HTTP response from localhost port 80 after the Nydus-backed container starts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/node/index.js -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/python/entrypoint.sh -->
# sources/cloud-native/nydus/smoke/tests/texture/python/entrypoint.sh

## Purpose
This one-line shell script is the Python texture entrypoint for container smoke tests.

## Important APIs, Types, And Functions
It invokes `python -c 'print("hello")'`.

## Control Flow
The caller runs the script under `sh`; Python starts, prints `hello`, and exits.

## State And Persistence
No persistent state is written.

## Dependencies And Integration Points
`tool/container.go` mounts this file for the `python` recipe and executes it as `sh /src/entrypoint.sh`. It assumes `python` exists in the image.

## Risks
Images that expose only `python3` would fail. The script does not validate mounted file contents beyond its own readability.

## Test Signals
Successful script exit proves the Python runtime starts from the Nydus-backed container environment.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/python/entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/ruby/entrypoint.sh -->
# sources/cloud-native/nydus/smoke/tests/texture/ruby/entrypoint.sh

## Purpose
This one-line shell script is the Ruby texture entrypoint for container smoke tests.

## Important APIs, Types, And Functions
It invokes `ruby -e "puts \"hello\""`.

## Control Flow
The caller runs the script under `sh`; Ruby starts, prints `hello`, and exits.

## State And Persistence
No persistent state is written.

## Dependencies And Integration Points
`tool/container.go` mounts this file for the `ruby` recipe and executes it as `sh /src/entrypoint.sh`. It assumes `ruby` exists in the image.

## Risks
The script is intentionally minimal and validates only interpreter startup plus basic mounted script access.

## Test Signals
Successful script exit proves the Ruby runtime starts from the Nydus-backed container environment.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/texture/ruby/entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/builder.go -->
# sources/cloud-native/nydus/smoke/tests/tool/builder.go

## Purpose
This helper wraps `nydus-image check` for smoke tests that need to validate generated bootstraps outside the higher-level `nydusify check` path.

## Important APIs, Types, And Functions
`CheckOption` contains `BuilderPath`. `CheckBootstrap` builds arguments `check --log-level error --bootstrap <path> -v`, runs the builder with `exec.CommandContext`, sends stdout/stderr to a logrus module writer, and returns errors to the caller.

## Control Flow
The function constructs CLI args, logs them at debug level, runs the command, logs failures with context, and returns nil on success.

## State And Persistence
It does not write files directly; it reads the bootstrap and emits log output.

## Dependencies And Integration Points
It integrates smoke tests with the `nydus-image` binary and is used by external backend tests after bootstrap generation/pull.

## Risks
It uses `context.Background` without timeout, so a hung builder can hang the test. It assumes `BuilderPath` is executable and compatible with the bootstrap format.

## Test Signals
Successful return is a bootstrap structural validation signal from `nydus-image check -v`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/container.go -->
# sources/cloud-native/nydus/smoke/tests/tool/container.go

## Purpose
This helper centralizes container workload recipes and metrics collection for Nydus snapshotter smoke/performance tests.

## Important APIs, Types, And Functions
`ContainerMetrics` stores E2E time, conversion time, backend reads, and image size. `RunArgs` describes readiness URL, command args, optional bind mount, and baseline metric maps. `urlWait` contains long-running HTTP workloads such as `wordpress` and `node`; `cmdStdout` contains one-shot language runtime workloads. `SupportContainerImage` and `GetRunArgs` query recipes. `runURLWaitContainer` starts `nerdctl run -d --net=host` and polls `WaitURL`. `runCmdStdoutContainer` runs an interactive command script. `RunContainerWithBaseline` runs Nydus and enforces read baselines. `RunContainer` returns runtime metrics. `RunContainerSimple` starts a workload with optional cleanup. `ClearContainer` removes the container and image. `getContainerBackendMetrics` connects to a discovered nydusd API socket and decodes backend metrics. `searchAPISockPath` finds the first daemon socket directory under the snapshotter socket root.

## Control Flow
Recipes are selected by image repo name stripped from the full reference. Workload launch either waits for an HTTP endpoint or waits for command completion. For Nydus snapshotter runs, metrics are fetched from the daemon API socket after workload launch.

## State And Persistence
The helper creates/removes containers and images through `nerdctl`. It may mount repository texture directories into containers. Metrics are read from live daemon state and not persisted by this helper.

## Dependencies And Integration Points
It requires `sudo nerdctl`, containerd, Nydus snapshotter, host networking, HTTP readiness, and Nydus daemon API socket layout under `/var/lib/containerd/io.containerd.snapshotter.v1.nydus/socket`.

## Risks
Host-network port 80 can conflict across parallel tests. `searchAPISockPath` picks the first directory and may choose the wrong daemon if multiple instances exist. ClearContainer removes images as well as containers, which can affect shared image cache. Baselines are environment-sensitive.

## Test Signals
Signals include successful workload readiness/completion, backend metrics availability, and read-count/read-byte comparisons against baselines.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/context.go -->
# sources/cloud-native/nydus/smoke/tests/tool/context.go

## Purpose
This file defines the shared smoke-test context model for binaries, build options, runtime options, and per-test filesystem paths.

## Important APIs, Types, And Functions
`BinaryContext` stores paths and feature flags for builder, daemon, nydusify, and checker binaries. `BuildContext` stores fs version, compressor, chunk size, OCI ref flags, batch size, and encryption. `RuntimeContext` stores cache, mount, RAFS mode, prefetch, amplify I/O, and dedup DB settings. `EnvContext` stores work, blob, cache, mount, bootstrap, and overlay dirs. `Context` embeds those groups. `DefaultContext` initializes binaries from environment/defaults and conservative build/runtime defaults. `PrepareWorkDir` creates a temp workdir tree. `Destroy` removes it.

## Control Flow
Tests call `DefaultContext`, optionally mutate fields, then `PrepareWorkDir` before building images or daemons. `PrepareWorkDir` chooses `WORK_DIR` or `os.TempDir`, creates all subdirectories, and writes paths into `ctx.Env`.

## State And Persistence
The main state is a temporary directory containing blobs, cache, mountpoint, overlay upper/work dirs, and bootstraps. `Destroy` recursively removes the workdir.

## Dependencies And Integration Points
This integrates with `tool.GetBinary`, all pack/convert/daemon helpers, and environment variables such as `NYDUS_BUILDER`, `NYDUS_NYDUSD`, `NYDUS_NYDUSIFY`, and `WORK_DIR`.

## Risks
`Destroy` ignores removal errors. Defaults such as fs version 6, zstd, blobcache, direct mode, prefetch enabled, and amplify I/O shape many tests unless overridden. Mount directories must be unmounted before removal.

## Test Signals
There are no direct assertions beyond directory creation. Failures usually surface as missing binary fatal errors or `require.NoError` from `PrepareWorkDir`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/file.go -->
# sources/cloud-native/nydus/smoke/tests/tool/file.go

## Purpose
This helper captures filesystem metadata and content digests for comparing source layers with Nydus-mounted trees.

## Important APIs, Types, And Functions
`File` stores path, size, mode, rdev, symlink target, uid, gid, xattrs, and digest hash. `GetXattrs` lists and reads xattrs with lget semantics. `NewFile` uses `os.Lstat`, symlink reads, `syscall.Stat_t`, xattrs, and SHA256 digesting for regular files. `Compare` normalizes directory size to zero and asserts structural equality with `require.Equal`.

## Control Flow
Layer builders and verifiers call `NewFile` while walking source or mount trees. Comparisons are pairwise by target path.

## State And Persistence
The helper only reads filesystem state. It records an in-memory snapshot of metadata and content digests.

## Dependencies And Integration Points
It depends on Linux stat fields, `github.com/pkg/xattr`, OpenContainers digest, and `testify/require`. It is foundational for `tool.Layer.recordFileTree`, `tool.Nydusd.Verify`, and external backend comparison.

## Risks
It assumes `stat.Sys()` is `*syscall.Stat_t`, making it Unix/Linux-specific. Xattr availability and permission to read `security.*` xattrs can vary. Directory size normalization avoids filesystem-specific directory sizes but only inside `Compare`.

## Test Signals
A failed comparison pinpoints metadata/content drift between source and mounted Nydus files.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/image.go -->
# sources/cloud-native/nydus/smoke/tests/tool/image.go

## Purpose
This helper manages local registry image preparation and simple image conversion for smoke tests.

## Important APIs, Types, And Functions
`Registry` stores the Docker registry container ID. `NewRegistry` runs `docker run -d -it --rm -p <REGISTRY_PORT>:5000 registry:2`. `Destroy` removes that container. `PrepareImage` maps a source to `localhost:<port>/<source>`, reuses it if already pullable, otherwise tags/pulls/pushes it. `ConvertImage` prepares a workdir and runs `nydusify convert` with context-selected fs version and optional OCI ref.

## Control Flow
Package setup starts the registry. Tests call `PrepareImage` to ensure a source image exists in the local registry, then call `ConvertImage` for Nydus targets when needed.

## State And Persistence
State includes a Docker registry container and pushed image tags in that registry. `ConvertImage` creates and destroys a workdir but leaves target image state in the registry/runtime.

## Dependencies And Integration Points
It integrates Docker, registry:2, `nydusify`, `nydus-image`, and the shared `Context`. It is used by image, commit, compatibility, performance, and takeover tests.

## Risks
Image references are embedded in shell commands without escaping. `PrepareImage` assumes target pull failure means it should tag/pull/push. Registry cleanup removes the container, losing pushed images after the package test run.

## Test Signals
Signals are successful Docker pull/tag/push and successful `nydusify convert` command exit.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/iterator.go -->
# sources/cloud-native/nydus/smoke/tests/tool/iterator.go

## Purpose
This file implements a small Cartesian-product iterator used to generate dynamic smoke-test scenarios with optional environment and code-based skips.

## Important APIs, Types, And Functions
`DescartesItem` wraps a map of dimension values and exposes `Exists`, `GetString`, `GetBool`, `GetUInt64`, and deterministic `Str`. `DescartesIterator` stores cursors, value lists, dimension-name mapping, optional skip closure, and cached next item. `Dimension` appends a dimension and initializes cursor state. `Skip` registers skip logic. `HasNext`, `Next`, `calNext`, `haveNext`, `noNext`, and `clearNext` drive iteration. `isIgnoredByEnv` implements `SKIP_CASES` filtering of `key=value` pairs.

## Control Flow
The iterator increments cursors like a mixed-radix counter, builds a `DescartesItem`, rejects it if `SKIP_CASES` or the skip closure matches, caches the next valid item, and returns it to generator closures. `Str` sorts keys so subtest names are stable.

## State And Persistence
Iterator state is in memory only. The `SKIP_CASES` environment variable influences scenario selection globally.

## Dependencies And Integration Points
All dynamic test suites use this to produce `test.Generator` cases. It integrates with `tool/test/suite.go`, which executes the generated cases.

## Risks
`isIgnoredByEnv` assumes every comma-separated entry contains `=`, so malformed `SKIP_CASES` can panic. Typed getters use unchecked type assertions. `Dimension` resets `c.cursors[0] = -1`, which works for the intended construction pattern but is fragile if dimensions are manipulated after iteration starts.

## Test Signals
No direct tests are present here. Downstream subtest names and scenario coverage are the visible signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/layer.go -->
# sources/cloud-native/nydus/smoke/tests/tool/layer.go

## Purpose
This helper models and materializes synthetic OCI layers, packs them into Nydus blobs, merges them into bootstraps, and computes expected file trees for verification.

## Important APIs, Types, And Functions
`Layer` stores `workDir` and `FileTree`. Creation helpers write files, large random files, sparse files, dirs, symlinks, hardlinks, special files, xattrs, whiteouts, and opaque markers. `TargetPath` maps absolute paths to layer-relative names. `Pack` streams an OCI tar through `converter.Pack` to a Nydus native blob. `PackWithAttributes` writes both internal and external blobs. `PackRef` creates an optional gzip OCI blob and corresponding RAFS/zran blob. `Overlay` mutates expected file trees according to OCI whiteout/opaque semantics. `recordFileTree` walks the source tree into `FileTree`. `ToOCITar` uses `archive.Diff`. `MergeLayers` opens blob readers and calls `converter.Merge`.

## Control Flow
Tests populate a layer, pack it to blobs, merge one or more blob digests into a bootstrap, then mount and compare against `FileTree`. Overlay tests mutate the lower `FileTree` with an upper layer to derive expected merged state.

## State And Persistence
This file writes real layer contents under `workDir`, blob files named by digest under `blobDir`, and temporary bootstraps. It renames temp blobs atomically to digest hex names. `FileTree` is an in-memory metadata snapshot.

## Dependencies And Integration Points
It depends on `snapshotter-converter`, containerd archive/content local readers, OpenContainers digest, xattr, Unix syscalls, and `tool.File`. It bridges synthetic test data to real Nydus builder/merge behavior.

## Risks
`Overlay` adds upper files inside a loop over lower files, which may fail to add files when the lower tree is empty and is sensitive to map mutation during iteration. Special files and xattrs need privileges. Random large files make digests non-stable across different layer creations, though repeatability is checked on the same layer contents.

## Test Signals
Digest outputs from `Pack`/`PackRef` and `MergeLayers`, plus later file-tree comparisons, are the main signals. Failures identify packing, merge accounting, or expected-tree modeling issues.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/nydusd.go -->
# sources/cloud-native/nydus/smoke/tests/tool/nydusd.go

## Purpose
This is the central `nydusd` test harness. It generates daemon configs, starts FUSE and UFFD modes, mounts/unmounts images, exercises daemon APIs, fetches metrics/config, and verifies mounted file trees.

## Important APIs, Types, And Functions
Metric structs model daemon JSON responses. `NydusdConfig` contains mount, backend, cache, API, hot-upgrade, overlay, and UFFD fields. `Nydusd` wraps an HTTP client, `exec.Cmd`, wait channel, and config. Config templates cover regular and overlay modes. `makeConfig`, `newNydusd`, `NewNydusd`, `NewNydusdUffd`, `NewNydusdWithOverlay`, and `NewNydusdWithContext` construct daemons. Lifecycle methods include `Run`, `Mount`, `Shutdown`, `Umount`, `MountByAPI`, `UmountByAPI`, `WaitStatus`, `StartByAPI`, `SendFd`, `Takeover`, and `Exit`. Metrics/config methods fetch global, files, backend, latest files, access pattern, blobcache, inflight, and hot-reload config endpoints. `Verify` and `VerifyByPath` walk mounted trees and compare `tool.File` snapshots. Package function `Verify` mounts a context and verifies it.

## Control Flow
Construction writes a config JSON when needed, builds command args, and creates an HTTP client that dials the Unix API socket. `Run` starts the process and waits in a goroutine. Mount paths either start the daemon and wait for `RUNNING`, or post a mount config to the API. Verification walks the mounted directory and performs two-way expected/actual checks.

## State And Persistence
The harness writes config files into workdirs, creates Unix sockets, launches daemon processes, mounts FUSE filesystems, and may unmount lazily. It reads daemon API state and metrics but does not persist them. UFFD mode maps to sockets rather than FUSE mountpoints.

## Dependencies And Integration Points
It integrates tests with `nydusd` CLI, Unix-domain HTTP API, FUSE mount lifecycle, snapshotter hot-upgrade endpoints, UFFD subcommand, overlay config, and JSON metric schemas.

## Risks
`time.Sleep(2s)` after process start is a coarse readiness delay. Several API methods ignore HTTP status codes and only return transport errors. `defer resp.Body.Close()` inside `WaitStatus` loop can accumulate until the function returns. Lazy unmount and process exit timing can be host-sensitive.

## Test Signals
Signals include daemon state transitions, successful API calls, metric JSON decoding, and exact mounted file-tree comparisons. This harness amplifies failures from most smoke suites.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/nydusd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/snapshotter.go -->
# sources/cloud-native/nydus/smoke/tests/tool/snapshotter.go

## Purpose
This helper provides a small HTTP-over-Unix-socket client for the nydus-snapshotter system controller API used by takeover tests.

## Important APIs, Types, And Functions
`SnapshotterClient` wraps `http.Client`. `DaemonInfoFromSnapshotter` models daemon details including ID, PID, API socket, supervisor path, references, mountpoints, resource metrics, and RAFS instances. `UpgradeRequest` models upgrade API input. `NewSnapshotterClient` creates a Unix-socket transport. `request` marshals an optional JSON body, sends a request, reads the response, and enforces 2xx status. `GetNydusDaemonInfos` calls `GET /api/v1/daemons`. `Upgrade` calls `PUT /api/v1/daemons/upgrade`.

## Control Flow
Tests instantiate the client with the system socket path, call typed methods, and receive decoded daemon state or errors.

## State And Persistence
The client itself is stateless aside from connection pooling. It reads live snapshotter state and sends upgrade commands that mutate daemon fleet state.

## Dependencies And Integration Points
It integrates with nydus-snapshotter's controller API over a Unix socket and is used by `takeover_test.go`.

## Risks
The request helper typo in error text is harmless. The client has a fixed 30-second timeout. API schema changes will break JSON decoding or tests relying on fields such as PID.

## Test Signals
Successful daemon info fetch and upgrade request completion are prerequisite signals for snapshotter takeover/hot-upgrade tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/test/suite.go -->
# sources/cloud-native/nydus/smoke/tests/tool/test/suite.go

## Purpose
This package implements a lightweight reflection-based test-suite runner with static test methods, dynamic generators, and optional synchronous execution.

## Important APIs, Types, And Functions
`Option`, `options`, `Sync`, `Case`, and `Generator` define the mini-framework. `Run` validates that the suite is a pointer, applies options, reflects over exported methods whose names start with `Test`, and dispatches either static methods with signature `func(*testing.T)` or dynamic methods returning `Generator`. `runTest` wraps `t.Run` and calls `t.Parallel` unless sync is requested. `runDynamicTest` pulls generated cases until nil and names unnamed cases with a counter.

## Control Flow
Every suite entrypoint calls `test.Run(t, &Suite{})`. Reflection scans methods once. Dynamic generators produce one subtest at a time, enabling Cartesian matrices without registering all cases manually.

## State And Persistence
The framework stores only per-run option flags and generator counters. Test state lives in suite structs or closures.

## Dependencies And Integration Points
It integrates with Go's `testing` package and all smoke-test suites in this subset. It avoids external test frameworks while supporting parallelism.

## Risks
Reflection signature matching is strict and silent for unsupported methods. Parallel execution means suite fields shared across cases must be concurrency-safe; several suites cache prepared images and rely on external command serialization implicitly. Dynamic generators may perform expensive setup before returning the subtest closure.

## Test Signals
Subtest names and parallel/sync behavior are the visible outputs. Failures are reported through normal Go testing subtests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/test/suite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/uffd_client.go -->
# sources/cloud-native/nydus/smoke/tests/tool/uffd_client.go

## Purpose
This Linux-only helper implements a test client for Nydus UFFD block-device mode. It connects to the daemon's Unix socket, negotiates device stats and handshakes, manages a userfaultfd-backed memory mapping, handles zerocopy page-fault responses, and exposes read/verification helpers.

## Important APIs, Types, And Functions
Constants define protocol message types, policy IDs, syscall/ioctl numbers, and EROFS magic. Protocol structs model VMA regions, handshake, blob ranges, page-fault responses, stat request/response. `UffdClient` stores socket, userfaultfd, mmap slice, device metadata, policy, region, worker synchronization, and close state. Syscall helpers include `sysUserfaultfd`, `createUserfaultfd`, `uffdRegister`, `uffdWake`, `sendWithFd`, and `recvWithFd`. `NewUffdClient` connects and requests stats. `Handshake` creates/registers mmap memory and sends the userfaultfd via SCM_RIGHTS. `zerocopyWorker` maps blob fds into the region on page-fault responses. `ReadAt`, `Close`, `VerifyErofsMagic`, `VerifyNonZero`, `closeFds`, `isTemporaryError`, and `ExportDiskImage` provide test-facing operations.

## Control Flow
A test creates the client, reads device size/block size from a stat exchange, handshakes in copy or zerocopy mode, then reads from the mapped memory. In zerocopy mode a goroutine receives page-fault responses and maps file descriptors at requested offsets before waking userfaultfd waiters. Close signals the worker, closes the socket, unmaps memory, and closes fds.

## State And Persistence
The client creates kernel userfaultfd state, an anonymous mmap region rounded to 2 MiB alignment, Unix socket connections, and transient file descriptor transfers. `ExportDiskImage` writes a raw disk image using `nydus-image export --block`.

## Dependencies And Integration Points
It depends on Linux userfaultfd, Unix SCM_RIGHTS, architecture-specific syscall numbers, Nydus UFFD protocol JSON, `nydusd uffd`, and `nydus-image export`. It is used by `uffd_test.go`.

## Risks
The build tag restricts this to Linux, but userfaultfd may be disabled by kernel policy. Unsafe mmap slicing and fixed syscall numbers are inherently platform-sensitive. Zerocopy worker silently ignores malformed responses or mmap failures, which can later appear as read/verification failures.

## Test Signals
Signals include successful stat response, handshake, EROFS magic reads, nonzero/expected data reads, and clean resource shutdown.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/uffd_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/util.go -->
# sources/cloud-native/nydus/smoke/tests/tool/util.go

## Purpose
This file provides shell command wrappers, binary path resolution, and image repository parsing for smoke tests.

## Important APIs, Types, And Functions
`defaultBinary` maps environment keys to default executable names. `RunWithCombinedOutput`, `Run`, `RunWithoutOutput`, and `RunWithOutput` execute shell commands through `sh -c` with different output handling and assertion behavior. `GetBinary` resolves versioned environment variables like `NYDUS_BUILDER_v1_2_3`, falls back to unversioned vars or defaults for `latest`, and fails tests if required binaries are absent. `ImageRepo` strips registry/path and tag to get the repository name used for workload recipes.

## Control Flow
Tests construct command strings and pass them to these helpers. Binary lookup normalizes dots to underscores in version strings and chooses the right environment key before falling back.

## State And Persistence
The helpers execute external commands that can mutate system state, but this file itself stores only the default binary map.

## Dependencies And Integration Points
It integrates all smoke tests with shell commands, Docker, nerdctl, nydusify, nydus-image, nydusd, and environment-based binary selection.

## Risks
All command helpers use `sh -c`, so callers must avoid unsafe strings. `Run` and `RunWithoutOutput` use `assert.Nil`, which records failures but may allow callers to continue. `RunWithOutput` panics on command failure instead of returning a testing assertion.

## Test Signals
Command exit status and captured output are the direct signals. Binary resolution failures are fatal test failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/tool/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/uffd_test.go -->
# sources/cloud-native/nydus/smoke/tests/uffd_test.go

## Purpose
This suite validates Nydus `nydusd uffd` block-device mode lifecycle, restart behavior, error handling for missing bootstraps, and data correctness in zerocopy and copy policies.

## Important APIs, Types, And Functions
`UffdTestSuite` stores `T`. `buildLayer` creates a RAFS v6 thin layer and bootstrap without special files. `TestUffdDaemonLifecycle` starts `nydusd uffd`, waits for `RUNNING`, and checks socket creation. `TestUffdDaemonRestart` starts, shuts down, removes the leftover socket, and starts again on the same path. `TestUffdDaemonMissingBootstrap` expects invalid bootstrap startup not to reach `RUNNING`. `TestUffdZerocopyDataVerification` and `TestUffdCopyDataVerification` export a reference disk image when possible, start UFFD daemon, connect `tool.UffdClient`, handshake with the selected policy, verify EROFS magic, and call `verifyDataAtOffsets`. `verifyDataAtOffsets` reads aligned offsets across the device and compares to exported disk bytes when available.

## Control Flow
Each case prepares a temp context and bootstrap, starts UFFD daemon through `tool.NewNydusdUffd`, waits or expects failure, then optionally uses `UffdClient` to trigger page faults by reading mapped memory. Data verification samples start, interior, and tail offsets.

## State And Persistence
The workdir contains blobs, bootstrap, UFFD socket, API socket, and optional `disk.raw` export. UFFD client state includes mmap and userfaultfd resources cleaned by `Close`.

## Dependencies And Integration Points
This integrates `texture.MakeThinLowerLayer`, `snapshotter-converter`, `tool.NydusdUffd`, `tool.UffdClient`, kernel userfaultfd, and `nydus-image export --block`.

## Risks
The tests are Linux/kernel-feature dependent and may require userfaultfd permissions. Export failure downgrades verification to EROFS magic and accessible reads, reducing coverage. Missing-bootstrap test waits for the full `WaitStatus` timeout before passing unless the API fails earlier.

## Test Signals
Signals include daemon state, socket existence, restart on reused path after manual unlink, expected failure for invalid bootstrap, successful UFFD handshakes, EROFS magic match, and sampled data equality with exported raw disk when available.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/uffd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/zran_layer_test.go -->
# sources/cloud-native/nydus/smoke/tests/zran_layer_test.go

## Purpose
This suite verifies zran/OCI-reference layer packing and mounting for gzip and non-gzip OCI blobs with cache compression and prefetch combinations.

## Important APIs, Types, And Functions
`ZranTestSuite.TestMakeLayers` iterates `gzip`, `cache_compressed`, and `enable_prefetch`. `testMakeLayers` prepares a context, creates a lower texture layer, packs it with `PackRef` to produce original OCI and RAFS blob digests, merges with `OCIRef=true`, asserts the merge returns the original OCI digest, sets the bootstrap path, and verifies the mount.

## Control Flow
For each scenario the test builds a lower layer, packs the OCI-reference RAFS blob, merges it into a bootstrap that references original OCI content, then mounts through `nydusd` and compares the file tree.

## State And Persistence
Temporary state includes source layer, OCI blob, RAFS blob, bootstrap, cache, and mount directory. The gzip flag changes how the original OCI blob is stored.

## Dependencies And Integration Points
It depends on `texture.MakeLowerLayer`, `tool.Layer.PackRef`, `tool.MergeLayers`, `snapshotter-converter`, and `tool.Verify`. It exercises Nydus zran/OCI reference mode in builder and runtime.

## Risks
The texture layer includes special files and large random data, requiring host support. The expected digest assertion differs from native mode: the returned digest must be the original OCI digest, not the RAFS blob digest.

## Test Signals
Signals are correct merge digest accounting and successful mounted file-tree verification for all gzip/cache/prefetch combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/zran_layer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/deduplicate.rs -->
# sources/cloud-native/nydus/src/bin/nydus-image/deduplicate.rs

## Purpose
This Rust module implements chunk deduplication metadata persistence and chunkdict generation for `nydus-image`. It stores blob/chunk metadata from RAFS bootstraps in SQLite, validates bootstrap version compatibility, updates build context from parent bootstraps, and implements dictionary selection algorithms based on cross-image clustering and version-level exponential smoothing.

## Important APIs, Types, And Functions
`DatabaseError` wraps SQLite and poisoned mutex errors. `Database` abstracts table creation, inserts, and lookups. `SqliteDatabase` owns `ChunkTable` and `BlobTable`. `get_fs_version`, `check_bootstrap_versions_consistency`, and `update_ctx_from_parent_bootstrap` inspect bootstraps and mutate `BuildContext`. `Deduplicate<SqliteDatabase>::new` opens file or in-memory DB. `save_metadata` loads a bootstrap, creates tables, inserts blob info, walks the RAFS tree, and records each chunk with image reference and version. `Algorithm<SqliteDatabase>` loads chunks and runs `chunkdict_generate`. Algorithm helpers include `fill_chunkdict`, `exponential_smoothing`, `distance`, `divide_by_image`, `divide_set`, misspelled `dbsacn`, `expand_cluster`, `aggregate_chunk`, `deduplicate_image`, and `deduplicate_version`. `Table` abstracts SQL table operations. `ChunkTable`, `BlobTable`, `CustomString`, and `DataPoint` support storage and ordering. The test module covers ordering, table CRUD/paging, and algorithm behavior.

## Control Flow
Metadata ingestion loads RAFS metadata, extracts blob infos, creates SQLite tables if needed, inserts blob rows, builds a `Tree` from the bootstrap, walks DFS, and inserts chunk rows associated with the relevant blob ID. Generation loads all chunks, builds image-cluster dictionaries, builds per-version dictionaries, combines them, logs size, computes noise images, then expands selected chunks to include all chunks from any selected blob plus blob metadata.

## State And Persistence
The module persists two SQLite tables: `chunk` with image/version/blob/digest/crc/size/offset fields and `blob` with blob ID, sizes, compressor, and metadata chunk-info offsets/sizes. Table connections are protected by `Arc<Mutex<Connection>>`. In-memory DB mode is supported only when the URL is exactly `:memory:`.

## Dependencies And Integration Points
It depends on `nydus_rafs` for bootstrap/superblock/tree traversal, `nydus_builder` for `BuildContext`, conversion type, and chunkdict info structs, `nydus_storage::BlobInfo`, `nydus_api::ConfigV2`, and `rusqlite`. It is tied to `nydus-image` chunkdict CLI behavior and to smoke tests that inspect CAS/Chunks/Blobs counts.

## Risks
`SqliteDatabase::new` panics if the path exists but is not a file. `ChunkTable` and `BlobTable` open separate SQLite connections; in-memory mode creates separate private databases for chunk and blob tables, which is safe only because they are used independently. The DBSCAN implementation uses `min_points=10`, repeated O(n^2) distance scans, and mutates reusable `data_point` across radii, making large datasets expensive and behavior sensitive. `CustomString` ordering compares only extracted numeric sequences, so nonnumeric version distinctions can collapse in ordering. `chunkdict_generate` currently supports only `"exponential_smoothing"` by name even though image clustering is also invoked inside that path.

## Test Signals
Unit tests validate table insertion/listing/paging, version-string numeric ordering, distance calculation, train/test division, DBSCAN clustering, aggregate chunk selection, image deduplication, version deduplication, and smoothing output. Runtime smoke signals include CAS table population and chunkdict generation paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/deduplicate.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/inspect.rs -->
# sources/cloud-native/nydus/src/bin/nydus-image/inspect.rs

## Purpose
This Rust module implements an interactive/request-mode RAFS bootstrap inspector for `nydus-image`. It can show filesystem metadata, list directories, change directories, stat files and chunks, list blobs and prefetch entries, resolve chunks by blob offset, and check inodes.

## Important APIs, Types, And Functions
`RafsInspector` stores request mode, `RafsSuper`, bootstrap reader, current directory inode, parent inode stack, and a RAFS v6 file-to-parent map. `new` loads a bootstrap with `RafsSuper::load_from_file`. Command methods include `cmd_stats`, `cmd_list_dir`, `cmd_change_dir`, `cmd_stat_file`, `cmd_list_blobs`, `cmd_list_prefetch`, `cmd_show_chunk`, and `cmd_check_inode`. Traversal helpers include `generate_file_parents`, `path_from_ino`, `walk_dir`, and `walk_dir_inner`. `stat_single_file` prints inode attributes; `get_file_name` handles v6 hardlink naming; `get_blob_id_by_index` maps blob indices to IDs. `ExecuteError` models control/error results. `Executor::execute` parses commands and dispatches. `Prompt::run` provides the REPL loop and optional JSON output handling.

## Control Flow
The inspector loads RAFS metadata once, then commands read from that in-memory metadata and the bootstrap reader as needed. Directory navigation updates `cur_dir_ino` and `parent_inodes`. Commands that need full paths or v6 hardlink parents lazily build `file_parents` by walking from root. The prompt loops on stdin, executes commands, prints text output or serializes JSON values in request mode, and exits on `q`/`exit`.

## State And Persistence
Persistent source data is the bootstrap file. Runtime mutable state includes current directory inode, parent stack, cached file parent mapping, and a mutex-protected bootstrap reader used for prefetch table reads. The inspector itself does not modify the bootstrap.

## Dependencies And Integration Points
It depends on `nydus_rafs` metadata traits, `RafsIoReader`, `nydus_storage::BlobChunkInfo`, `nydus_api::ConfigV2`, serde JSON, and Unix permission formatting. It is a CLI-facing module in `nydus-image` and consumes RAFS v5/v6 metadata conventions.

## Risks
`Executor::execute` parses `chunk` offset with `unwrap`, so invalid chunk arguments can panic unlike `icheck`. `cmd_change_dir` prints "`name is `" with an empty reason when a child is absent. Several methods print directly even in paths that return `Option<Value>`, so request-mode JSON coverage is partial. `path_from_ino` and hardlink handling require full-tree walks and can be expensive on large images.

## Test Signals
No unit tests are present in this file. Functional signals are successful command execution against known bootstraps: sane stats, correct directory navigation/listing, blob and prefetch tables, inode resolution including v6 hardlinks, and chunk lookup by compressed offset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/src/bin/nydus-image/inspect.rs -->
