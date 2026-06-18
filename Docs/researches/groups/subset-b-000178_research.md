# Research Group subset-b-000178

This grouped report covers the requested Moby daemon internal files. Each section is bounded by source-path markers for reconciliation into one source-tree-aligned research document per source file.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/xfer/transfer.go -->
## sources/cloud-native/moby/daemon/internal/distribution/xfer/transfer.go

Purpose: Implements the shared transfer scheduler used by layer download/upload managers. It deduplicates in-flight work by key, fans progress to multiple watchers, limits active transfers, supports inactive jobs that should not consume a concurrency slot, and cancels orphaned transfers when all watchers release.

Important APIs and types: `DoNotRetry` and `IsDoNotRetryError` classify non-retriable failures. `watcher` owns release/signal/running channels. The internal `transfer` interface is implemented by `xfer`. `doFunc` is the non-blocking transfer factory contract. `transferManager` exposes `setConcurrency` and `transfer`.

Control flow: `newTransfer` creates a background context deliberately decoupled from client cancellation. `broadcast` drains the main progress channel, stores `lastProgress`, notifies watchers, handles sync pings, and closes `running` when progress ends. `watch` registers a watcher and starts a goroutine that writes the last progress event without duplicates until released or finished. `release` removes the watcher, cancels the transfer if no watchers remain, waits for the watcher goroutine, and closes `releasedChan` after manager closure. `transferManager.transfer` reuses an existing non-cancelled transfer, otherwise queues or starts work based on `concurrencyLimit`, launches broadcast, and removes the transfer from the map when done or inactive.

State and persistence: State is in memory only: maps of active transfers and watchers, last progress, active count, waiting start channels, and cancellation state. There is no disk persistence.

Dependencies and integration: Depends on daemon progress output, `context`, `sync`, `runtime.Gosched`, and `pkg/errors.As`. Upload/download managers build on this scheduler.

Risks: The correctness depends on channel ordering and watcher release pairing. A forgotten `release` leaks watcher references and can keep transfers tracked. The broadcaster sync channel avoids missing progress during detach, but any changes here risk subtle race regressions. `concurrencyLimit == 0` means unlimited, which callers must understand. Type assertions in callers assume factory-returned transfers have the expected concrete wrapper.

Test signals: `transfer_test.go` exercises basic progress delivery, concurrency limits, inactive slot release, watcher release cancellation, watching a finished transfer, and duplicate transfer deduplication.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/xfer/transfer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/xfer/transfer_test.go -->
## sources/cloud-native/moby/daemon/internal/distribution/xfer/transfer_test.go

Purpose: Validates the internal transfer scheduler and progress watcher machinery.

Important tests and helpers: Test-local `makeXferFunc` factories create `newTransfer` instances and progress goroutines. `TestTransfer` confirms progress flows to consumers and reaches the final value. `TestConcurrencyLimit` uses `atomic.Int32` to prove active transfers never exceed the limit. `TestInactiveJobs` closes `inactive` after progress so queued jobs can start before the original goroutine fully exits. `TestWatchRelease` attaches several watchers to one long-running transfer, releases them one by one, and expects transfer cancellation plus closed `released`/`done` channels. `TestWatchFinishedTransfer` verifies watchers created after completion can be released safely. `TestDuplicateTransfer` starts five requests with the same key and confirms the transfer factory runs once while all watchers see progress.

Control flow and state: The tests use unbuffered channels and timed sleeps to exercise scheduling interleavings. Consumers drain progress channels into maps or close notifications to avoid blocking writer goroutines.

Dependencies and integration: Uses the daemon `progress` package and Go atomics. It tests unexported types in-package.

Risks covered: Duplicate work, progress loss, cancelled-transfer reuse, active slot accounting, and watcher lifecycle leaks. Residual risk remains around rare races not reached by timing-based tests; running with `-race` is valuable for this package.

Persistence: None; all state is test-local memory.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/xfer/transfer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/xfer/upload.go -->
## sources/cloud-native/moby/daemon/internal/distribution/xfer/upload.go

Purpose: Provides `LayerUploadManager`, a blocking push helper that schedules layer uploads, deduplicates layers by descriptor key, reports progress, retries transient failures, and records remote descriptors back onto all input descriptors.

Important APIs and types: `maxUploadAttempts` is 5. `LayerUploadManager` wraps `transferManager` and `waitDuration`. `UploadDescriptor` supplies `Key`, display `ID`, `DiffID`, `Upload(ctx, progress)`, and `SetRemoteDescriptor`. `uploadTransfer` embeds `transfer` plus the uploaded remote descriptor and final error.

Control flow: `Upload` marks each descriptor as "Preparing", skips duplicate keys in a per-call map, starts or joins transfer-manager work with `makeUploadFunc`, defers watcher release, waits for all unique upload transfers or caller context cancellation, then copies remote descriptors to every original layer entry. `makeUploadFunc` creates an `uploadTransfer`, waits for the concurrency `start` channel, emits "Waiting" if queued, calls `descriptor.Upload` with the transfer context, and retries failures unless the transfer context was cancelled, the error is `DoNotRetry`, or `maxUploadAttempts` is reached. Retry delay counts down in five-second increments scaled by attempt number and uses the configurable tick duration.

State and persistence: Runtime-only state includes remote descriptors, errors, retry counters, and transfer-manager slots. Persistence is delegated to registries through `UploadDescriptor.Upload`; this file does not write disk.

Dependencies and integration: Integrates with Docker distribution descriptors, daemon layer IDs, progress output, containerd logging, and `transfer.go`.

Risks: Direct type assertion `err.(DoNotRetry)` misses wrapped `DoNotRetry`; `IsDoNotRetryError` would handle wrapping. Retry countdown messages rely on a small pluralization map. The caller context only controls the blocking wait; actual upload cancellation comes from transfer context cancellation triggered by watcher release.

Test signals: `upload_test.go` covers successful concurrent uploads, deduplication by repeated diff ID, retry success, and caller cancellation returning `context.Canceled`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/xfer/upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/xfer/upload_test.go -->
## sources/cloud-native/moby/daemon/internal/distribution/xfer/upload_test.go

Purpose: Tests `LayerUploadManager` behavior against mocked upload descriptors.

Important APIs and helpers: `mockUploadDescriptor` implements `UploadDescriptor`, tracks current uploads with `atomic.Int32`, returns display/key data from `diffID`, and can fail a configurable number of times through `simulateRetries`. `uploadDescriptors` returns six descriptors including a duplicate key and one descriptor that fails once before succeeding.

Control flow: Mock `Upload` increments/decrements the active counter, errors if concurrency exceeds `maxUploadConcurrency`, emits progress from 0 to 10 with delays, honors context cancellation, optionally simulates a retry, and returns an empty distribution descriptor on success. `TestSuccessfulUpload` sets a millisecond retry tick and expects the complete upload call to return nil while draining progress. `TestCancelledUpload` cancels the caller context shortly after start and expects `context.Canceled`.

State and persistence: No persistent state. The test checks in-memory concurrency and progress behavior.

Dependencies and integration: Uses Docker distribution descriptors, daemon `layer.DiffID`, daemon progress output, Go atomics, and context cancellation.

Risks covered: Over-concurrency, retry path, duplicate descriptor keys, and cancellation while uploads are in progress. The mock `SetRemoteDescriptor` is a no-op, so descriptor propagation is not asserted.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/xfer/upload_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filedescriptors/filedescriptors_linux.go -->
## sources/cloud-native/moby/daemon/internal/filedescriptors/filedescriptors_linux.go

Purpose: Counts file descriptors used by the current daemon process on Linux.

Important API: `GetTotalUsedFds(ctx context.Context) int` returns the count or `-1` on failure/cancellation.

Control flow: The function starts a containerd tracing span, builds `/proc/<pid>/fd`, and first tries the Linux 6.2 fast path where `stat.Size` on the proc fd directory contains the open descriptor count. If unavailable, it opens the directory and repeatedly calls `Readdirnames(100)`, checking `ctx.Done()` between batches. It logs and returns `-1` on open/read errors or cancellation. The slow path includes the descriptor for the opened `/proc/<pid>/fd` directory itself.

State and persistence: Reads kernel procfs state only. No persistence.

Dependencies and integration: Uses `x/sys/unix.Stat`, `os.Getpid`, containerd tracing/logging, and procfs. Useful for daemon diagnostics and resource monitoring.

Risks: Procfs semantics are Linux-version dependent. The fallback count can differ from the fast path by one because it opens the fd directory. Returning `-1` instead of an error requires callers to handle sentinel values.

Test signals: `filedescriptors_linux_test.go` benchmarks allocations/performance but does not assert correctness.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filedescriptors/filedescriptors_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filedescriptors/filedescriptors_linux_test.go -->
## sources/cloud-native/moby/daemon/internal/filedescriptors/filedescriptors_linux_test.go

Purpose: Provides a benchmark for Linux fd counting.

Important API: `BenchmarkGetTotalUsedFds` loops over `GetTotalUsedFds(context.Background())` and reports allocations.

Control flow and state: It does not set up fd fixtures or validate counts; it measures whichever fast or slow path the current kernel supports.

Dependencies and integration: Uses Go benchmark support and the Linux implementation in-package.

Risks and gaps: This is performance coverage only. It will not detect off-by-one behavior between fast and slow paths, procfs read errors, or cancellation handling.

Persistence: None.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filedescriptors/filedescriptors_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filedescriptors/filedescriptors_unsupported.go -->
## sources/cloud-native/moby/daemon/internal/filedescriptors/filedescriptors_unsupported.go

Purpose: Supplies the non-Linux build of fd counting.

Important API: `GetTotalUsedFds(context.Context) int` always returns `-1`.

Control flow and state: No branching or state. The `//go:build !linux` tag keeps it out of Linux builds.

Dependencies and integration: Maintains a common package API for platforms where procfs fd counting is unsupported, including Windows.

Risks: Callers must treat `-1` as unsupported/failure rather than a valid count. No tests are present for this build-tag path.

Persistence: None.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filedescriptors/filedescriptors_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filters/errors.go -->
## sources/cloud-native/moby/daemon/internal/filters/errors.go

Purpose: Defines the package-specific invalid filter error used by filter parsing and validation.

Important API/type: `invalidFilter` carries a filter name and optional values. `Error` formats messages such as `invalid filter` or `invalid filter 'dangling=[bad]'`. `InvalidParameter` marks the error for Docker error classification.

Control flow: Formatting appends the filter name when present and uses `fmt.Sprintf` for values. The marker method is empty and exists for interface detection.

State and persistence: Error values are transient. No persistence.

Dependencies and integration: Integrated by `parse.go` for invalid JSON, unknown filter names, and invalid boolean values. Tests assert both direct type detection and wrapping compatibility through `errors.Is`-style helpers.

Risks: The type is unexported, so external callers rely on marker interfaces and errdefs classification rather than concrete matching. Value slice ordering may be map-dependent unless tests sort expected/actual values.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filters/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filters/example_test.go -->
## sources/cloud-native/moby/daemon/internal/filters/example_test.go

Purpose: Documents `Args.MatchKVList` behavior as an executable Go example.

Important test: `ExampleArgs_MatchKVList` builds label filters for `image=foo` and `state=running`, then prints results for a missing filter key, nil sources, matching sources, and mismatching values.

Control flow and state: The example uses `NewArgs` and `Arg`, then calls `MatchKVList` with different source maps. The `// Output:` block verifies the user-facing semantics.

Dependencies and integration: Runs as a Go example test and documents package behavior for generated docs.

Risks covered: Confirms the "no values for key means no filtering" behavior and the "filter set with no sources fails" behavior. It does not cover key-only labels, multiple fields, or malformed values.

Persistence: None.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filters/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filters/parse.go -->
## sources/cloud-native/moby/daemon/internal/filters/parse.go

Purpose: Provides the daemon filter argument model: a map from filter keys to set-like string values, with JSON serialization, matching helpers, validation, and cloning.

Important APIs/types: `Args` owns `fields map[string]map[string]bool`. `KeyValuePair`, `Arg`, and `NewArgs` construct filters. Serialization APIs are `MarshalJSON`, `ToJSON`, `FromJSON`, and `UnmarshalJSON`. Query/mutation APIs include `Keys`, `Get`, `Add`, `Del`, `Len`, `Contains`, `Clone`, `Validate`, and `WalkValues`. Matching APIs are `MatchKVList`, `Match`, `ExactMatch`, `UniqueExactMatch`, `FuzzyMatch`, and `GetBoolOrDefault`.

Control flow: `FromJSON` first unmarshals the current map-of-map format, then falls back to legacy map-of-slice format and converts with `deprecatedArgs`; invalid input returns `invalidFilter`. Empty filter sets serialize to `{}` at JSON level and to an empty string through `ToJSON`. Matching semantics generally treat missing/empty filter values as "do not filter." `Match` first checks exact match and then regex matches each value, ignoring invalid regex patterns. Boolean parsing accepts only `0`, `1`, `false`, and `true`; missing values return the provided default.

State and persistence: State is in the `Args.fields` map. JSON is the persistence/interchange representation. `Clone` deep-copies nested maps to avoid shared mutation.

Dependencies and integration: Used throughout daemon APIs that accept filter query parameters. Depends on `encoding/json`, `regexp`, `strings`, and Go `maps.Copy`.

Risks: Map iteration order is nondeterministic for `Keys`, `Get`, `WalkValues`, and error value display. Regex matching treats filter values as regexes, so user-provided expressions can be expensive or surprising. `UnmarshalJSON` on a zero `Args` value requires valid map allocation from JSON; direct mutation on an uninitialized `Args{}` via `Add` would panic, so callers should use `NewArgs`.

Test signals: `parse_test.go` covers JSON formats, matching variants, add/delete, validation, walking, clone independence, and boolean parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filters/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filters/parse_test.go -->
## sources/cloud-native/moby/daemon/internal/filters/parse_test.go

Purpose: Provides broad behavioral coverage for the filters package.

Important tests: JSON tests cover current map-of-map format, empty filters, `ToJSON`, invalid JSON, legacy map-of-slice compatibility, and wrapped invalid filter errors. Matching tests cover `MatchKVList`, regex matching through `Match`, exact and unique exact matching, prefix fuzzy matching, and contains. Mutation tests cover `Add`, `Del`, `Len`, `Clone`, and `WalkValues`. `TestValidate` checks unknown keys. `TestGetBoolOrDefault` covers truthy/falsy values, invalid values, conflicts, sorting of expected value slices, and wrapped errors.

Control flow and state: Tests frequently instantiate `Args` with map literals to exercise internal states directly, in addition to using `NewArgs`.

Dependencies and integration: Uses `gotest.tools/v3/assert` and cmp helpers. It tests unexported `invalidFilter` by staying in package.

Risks covered: Legacy compatibility, nil/empty behavior, invalid regex handling, exact matching semantics, and value conflicts. Gaps include randomized map order, very large regex patterns, and concurrent access; `Args` is not synchronized.

Persistence: Tests JSON as the external persistence/interchange form.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/filters/parse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/fstype/fstype.go -->
## sources/cloud-native/moby/daemon/internal/fstype/fstype.go

Purpose: Defines filesystem magic constants and a cross-platform `GetFSMagic` wrapper.

Important APIs/types: `FsMagic` is a `uint32`. Constants enumerate known filesystem IDs including aufs, btrfs, extfs, overlayfs, xfs, zfs, fuse, tmpfs, and `FsMagicUnsupported`. `FsNames` maps IDs to human-readable names. `GetFSMagic(rootpath)` delegates to the platform implementation.

Control flow and state: The file is pure definitions plus one delegation function. `FsNames` is mutable package-level state but is intended as a constant lookup table.

Dependencies and integration: Used by daemon storage/driver code that needs to branch or report based on backing filesystem type. Platform-specific logic lives in `fstype_linux.go` and `fstype_unsupported.go`.

Risks: Filesystem magic values must stay accurate. Unknown filesystems are not automatically present in `FsNames`. Because `FsNames` is exported mutable state, accidental writes could affect diagnostics or behavior.

Test signals: No tests are listed for this package in the requested set.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/fstype/fstype.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/fstype/fstype_linux.go -->
## sources/cloud-native/moby/daemon/internal/fstype/fstype_linux.go

Purpose: Linux implementation of filesystem type detection.

Important API: `getFSMagic(rootpath string) (FsMagic, error)` calls `unix.Statfs` and returns `FsMagic(buf.Type)`.

Control flow and state: One syscall-backed function. It returns `0` plus the syscall error on failure.

Dependencies and integration: Depends on `golang.org/x/sys/unix` and is reached through `GetFSMagic` in `fstype.go`.

Risks: Requires the path to exist and be statfs-readable. Callers must decide how to handle unknown magic values not present in `FsNames`.

Persistence: Reads filesystem metadata only. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/fstype/fstype_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/fstype/fstype_unsupported.go -->
## sources/cloud-native/moby/daemon/internal/fstype/fstype_unsupported.go

Purpose: Non-Linux implementation of filesystem magic detection.

Important API: `getFSMagic(rootpath string) (FsMagic, error)` returns `FsMagicUnsupported, nil`.

Control flow and state: Build-tagged with `//go:build !linux`; no runtime branching.

Dependencies and integration: Keeps the public `GetFSMagic` API usable on unsupported platforms.

Risks: Returning nil error for unsupported detection makes platform support distinguishable only through the magic value. Callers must not treat `FsMagicUnsupported` as a real filesystem.

Persistence: None. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/fstype/fstype_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/idtools/idtools.go -->
## sources/cloud-native/moby/daemon/internal/idtools/idtools.go

Purpose: Defines a small daemon-local identity value.

Important type: `Identity` holds either Unix `UID`/`GID` or Windows `SID`, with the comment specifying that both modes should not be used at once.

Control flow and state: Data-only struct, no methods.

Dependencies and integration: Used wherever daemon internals need to pass identity data across platform-specific code without importing a broader idtools package.

Risks: The exclusivity invariant is documented but not enforced by constructors or validation. Zero values can mean root/root on Unix or unset depending on context.

Persistence and tests: No persistence logic and no tests in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/idtools/idtools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/cache/cache.go -->
## sources/cloud-native/moby/daemon/internal/image/cache/cache.go

Purpose: Implements builder image cache resolution against local children and optional `--cache-from` image histories.

Important APIs/types: `ImageCacheStore` abstracts image lookup, parent metadata, image creation, built-locally metadata, and child enumeration. `New` returns either `LocalImageCache` or history-based `ImageCache`. `LocalImageCache.GetCache` checks direct local children. `ImageCache.Populate`, `GetCache`, `restoreCachedImage`, `isParent`, `getLayerForHistoryIndex`, `isValidConfig`, `isValidParent`, and `getLocalCachedImage` implement cache matching and restoration.

Control flow: `New` builds a local cache, then resolves each `cacheFrom` ref with `GetByRef`, skipping missing refs but propagating context cancellation/deadline. `ImageCache.GetCache` first tries local child cache and only accepts it if the child belongs to one populated cache source. If that fails, it compares each source image against the requested parent history/rootfs and command config. Exact next-step hits return the target ID and possibly set parent metadata. Partial matches synthesize a restored cache image with one more history entry and layer diff ID.

State and persistence: In-memory `sources` list and store-backed parent/built-local/image creation metadata. `restoreCachedImage` may persist a new image through `store.Create` and `SetParent`.

Dependencies and integration: Used by the classic builder cache interface. Integrates daemon image, layer DiffID, OCI platform matching, container config comparison, logging, and ref lookup.

Risks: `isParent` is recursive and assumes parent metadata eventually terminates. `getLayerForHistoryIndex` indexes `RootFS.DiffIDs` with minimal validation. Config matching uses `strings.Join(cfg.Cmd, " ")`, which can lose argument boundaries. Cache restoration mutates `rootFS := parent.RootFS` by appending to the same pointer, so store implementations must tolerate this or callers must avoid reusing parent objects unsafely.

Test signals: `compare_test.go` covers lower-level config/platform matching; this file has no direct tests in the requested set.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/cache/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/cache/compare.go -->
## sources/cloud-native/moby/daemon/internal/image/cache/compare.go

Purpose: Supplies cache matching helpers for platform and container config comparison.

Important APIs: `comparePlatform(builderPlatform, imagePlatform)` wraps `containerd/platforms.Only(...).Match` but special-cases Windows OS version matching. `compare(a, b *container.Config)` compares relevant container config fields while intentionally ignoring container-specific fields such as Image, Hostname, Domainname, and MacAddress.

Control flow: For Windows, if both OS values are windows and both versions have at least three dot-separated parts, it rewrites the image platform version to share the builder major/minor and builder build/revision before invoking the platform matcher; this effectively ignores build/revision compatibility. Config comparison checks nil, slice/map lengths, ordered slice entries, map key/value presence, booleans, strings, stop timeout pointer/value equality, and detailed healthcheck fields.

State and persistence: Pure functions. No persistence.

Dependencies and integration: Used by `getLocalCachedImage` to decide whether a locally built child can satisfy a builder cache request.

Risks: Slice order is significant for Env, Cmd, Entrypoint, Shell, OnBuild, and healthcheck test. The Windows version rewrite is subtle and only meaningful under the platform matcher behavior active on Windows. New fields added to `container.Config` must be considered manually.

Test signals: `compare_test.go` exercises many same/different config cases and platform matching including Windows version behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/cache/compare.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/cache/compare_test.go -->
## sources/cloud-native/moby/daemon/internal/image/cache/compare_test.go

Purpose: Tests cache comparison helpers.

Important tests: `TestCompare` builds same/different `container.Config` pairs covering ignored fields, user, stdin flags, env, command, labels, exposed ports, entrypoints, volumes, and count mismatches. `TestPlatformCompare` checks architecture, OS, ARM variants, and Windows OS version compatibility.

Control flow and state: The config test iterates maps of pointer pairs and fails fast on unexpected compare results. Platform OSVersion cases are skipped when not running on Windows because containerd's platform matcher only compares OSVersion on Windows.

Dependencies and integration: Uses API `container.Config`, network port parsing, OCI platform structs, runtime GOOS, and `gotest.tools` assertions.

Risks covered: Regressions in ignored fields, ordered slice matching, map membership/value matching, ARM variant compatibility, and Windows major/minor semantics. Gaps include stop timeout, healthcheck, shell, onbuild, and labels with nil vs empty map distinctions beyond length checks.

Persistence: None.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/cache/compare_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/fs.go -->
## sources/cloud-native/moby/daemon/internal/image/fs.go

Purpose: Implements a filesystem-backed `StoreBackend` for image configuration blobs and per-image metadata.

Important APIs/types: `DigestWalkFunc`, `StoreBackend`, and `fs`. Public constructor `NewFSStoreBackend` calls `newFSStore`. Methods are `Walk`, `Get`, `Set`, `Delete`, `SetMetadata`, `GetMetadata`, and `DeleteMetadata`. Constants define `content` and `metadata` subdirectories.

Control flow: Initialization creates `content/sha256` and `metadata/sha256`. `Set` rejects empty data, computes `digest.FromBytes`, and atomically writes content to `content/<algo>/<encoded>`. `Get` reads and verifies content digest. `Walk` enumerates canonical sha256 content entries, validates digest filenames, logs and skips invalid entries, and stops on callback error. Metadata methods require the content to exist before reading/writing sidecars under `metadata/<algo>/<encoded>/<key>`. `Delete` removes metadata then content.

State and persistence: Persistent state is disk files under the backend root. A RW mutex serializes backend operations in-process. Atomic writer reduces torn content/metadata writes.

Dependencies and integration: Used by `image.Store` as durable storage for image config JSON and metadata such as parent, lastUpdated, and builtLocally.

Risks: Only canonical sha256 is walked/created by initialization. Metadata keys are used as path components with no extra sanitization in this file. Digest verification catches content corruption but means every `Get` reads full content.

Test signals: `fs_test.go` covers invalid roots, get/set digest verification, empty set rejection, metadata, walking, deletion, and callback errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/fs_test.go -->
## sources/cloud-native/moby/daemon/internal/image/fs_test.go

Purpose: Tests filesystem-backed image store backend behavior.

Important tests: `TestFSGetInvalidData` corrupts content after `Set` and expects verification failure. `TestFSInvalidSet` creates a directory where a content file should be. `TestFSInvalidRoot` makes conflicting files at root/content/metadata paths. `TestFSMetadataGetSet` covers multiple IDs and keys plus missing content errors. `TestFSInvalidWalker` verifies invalid digest filenames are skipped. `TestFSGetSet` validates known and random sha256 digests. Additional tests cover unset keys, empty data rejection, delete behavior, full walk, and stopping on callback error.

Control flow and state: Tests use `t.TempDir`, direct filesystem mutation, and independent digest calculation for random content.

Dependencies and integration: Exercises `NewFSStoreBackend` and `StoreBackend` methods with `gotest.tools` assertions and OpenContainers digest.

Risks covered: Disk layout conflicts, atomic writes surfacing errors, corruption detection, metadata dependence on existing content, and walker resilience. It does not cover concurrent access or metadata key path traversal.

Persistence: Uses temporary on-disk roots and verifies durable file effects within the test process.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/image.go -->
## sources/cloud-native/moby/daemon/internal/image/image.go

Purpose: Defines the daemon image configuration model, image IDs, V1 compatibility fields, rootfs/history relationship, JSON behavior, and exporter interface.

Important APIs/types: `ID` wraps `digest.Digest`; `V1Image` contains legacy Docker image fields; `Image` embeds `V1Image` and adds content-addressable parent ID, `RootFS`, `History`, OS details, cached raw JSON, computed ID, and optional containerd `Details`. Methods expose raw JSON, ID, run config, base arch/variant/OS, platform, and custom marshal behavior. `ChildConfig`, `NewImage`, `NewChildImage`, `Clone`, `History`, `NewHistory`, `Exporter`, and `NewFromJSON` are the core helpers.

Control flow: `NewFromJSON` unmarshals config, requires a `RootFS`, stores immutable raw JSON, and leaves `computedID` to callers. `MarshalJSON` marshals through an alias then re-marshals a `map[string]*RawMessage` to stabilize top-level key order. `NewChildImage` clones or creates rootfs, appends non-empty layers, creates a history entry from the container command, and copies selected platform fields. `Clone` shallow-copies an image, clones rootfs, updates legacy ID and computed ID.

State and persistence: Image config is persisted as JSON by image stores and tar exporters. `rawJSON` preserves original bytes for content-addressable IDs and export.

Dependencies and integration: Integrates container config types, daemon layer DiffID, OCI platform/history descriptors, and digest IDs.

Risks: `Clone` assumes `RootFS` is non-nil. `Platform` returns raw Architecture/OS fields, while `OperatingSystem` and `BaseImgArch` default missing values to runtime; callers must choose the right one. Key-order stabilization depends on JSON map marshal ordering.

Test signals: `image_test.go` covers JSON parsing, missing RootFS, key order, ID helpers, OS defaulting, and child image rootfs copy behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/image_os.go -->
## sources/cloud-native/moby/daemon/internal/image/image_os.go

Purpose: Validates that an image operating system matches the daemon host OS.

Important API: `CheckOS(os string) error` compares the supplied OS to `runtime.GOOS` case-insensitively and returns `errdefs.InvalidParameter` on mismatch.

Control flow and state: A single string comparison with no persistent state.

Dependencies and integration: Used by image store restore/create and tar export save/load to reject unsupported platform images before retaining layers or importing configs.

Risks: Empty OS does not match any normal runtime GOOS; other code often defaults missing OS through `Image.OperatingSystem`, so direct callers must pass the normalized value. The error message is intentionally generic.

Tests: No dedicated tests in this subset; coverage is indirect through image store and tar export paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/image_os.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/image_test.go -->
## sources/cloud-native/moby/daemon/internal/image/image_test.go

Purpose: Tests core image model helpers.

Important tests: `TestNewFromJSON` checks raw JSON preservation. `TestNewFromJSONWithInvalidJSON` requires the RootFS key. `TestMarshalKeyOrder` confirms stable top-level key order for selected fields. `TestImage` verifies ID string helpers, runtime OS defaulting, and run config access. `TestImageOSNotEmpty` verifies explicit OS wins. `TestNewChildImageFromImageWithRootFS` checks diff ID append, author/comment/config propagation, OS assignment, history append, and parent rootfs copy rather than mutation.

Control flow and state: Uses static sample JSON and a parent rootfs/history fixture.

Dependencies and integration: Uses container configs, daemon layer DiffID, runtime GOOS, and `go-cmp`/`gotest.tools`.

Risks covered: Missing RootFS rejection, raw JSON content, key order, and child image mutation boundaries. Gaps include empty-layer child behavior, nil RootFS clone behavior, and platform OS feature/version propagation details.

Persistence: Validates the JSON representation consumed by image stores and exporters.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/image_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/rootfs.go -->
## sources/cloud-native/moby/daemon/internal/image/rootfs.go

Purpose: Models an image root filesystem as a list of layer DiffIDs and computes chain IDs.

Important APIs/types: `TypeLayers` is the supported rootfs type. `RootFS` has JSON fields `type` and `diff_ids`. `NewRootFS`, `Append`, `Clone`, and `ChainID` are the methods.

Control flow: `Append` appends a diff ID in layer order. `Clone` copies the type and uses `slices.Clone` for DiffIDs. `ChainID` delegates to OCI `identity.ChainID` to compute the top layer chain digest from all diff IDs.

State and persistence: RootFS is persisted inside image config JSON. The order of `DiffIDs` is semantically significant.

Dependencies and integration: Used by image creation, layer store lookups, tar load/save, and builder cache. Depends on daemon layer digest aliases and OpenContainers identity.

Risks: `Append` mutates the receiver; callers sharing a RootFS pointer can accidentally mutate parent images. Empty DiffIDs produce an empty chain ID.

Test signals: Covered indirectly by image and store tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/rootfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/store.go -->
## sources/cloud-native/moby/daemon/internal/image/store.go

Purpose: Provides the daemon image store over a `StoreBackend` and layer reference manager. It creates, restores, searches, deletes, and tracks parent/child image relationships.

Important APIs/types: `Store` is the public interface. `LayerGetReleaser` abstracts layer retention. Internal `imageMeta` stores the retained top layer and child set. `store` keeps maps, a digest prefix set, backend, and layer store.

Control flow: `NewImageStore` calls `restore`. Restore walks backend digests, loads each image, checks OS, retains the rootfs chain layer when present, adds it to the digestset and image map, then does a second pass to reconstruct children from parent metadata. `Create` parses config JSON, rejects impossible history/rootfs layer counts, writes config through `fs.Set`, checks duplicates, validates OS, retains the rootfs layer, inserts metadata, and adds the digest to the lookup set. `Search` resolves partial IDs with `digestset`. `Get` reads config, parses it, sets computed ID, and hydrates parent metadata when present. `Delete` removes child parent metadata, unlinks from parent, removes digestset and backend content, and releases retained layer. Metadata helpers persist parent, lastUpdated, and builtLocally values. `Children`, `Heads`, `Map`, and `Len` expose in-memory views.

State and persistence: Durable state is image JSON plus metadata keys in `StoreBackend`. In-memory state is protected by an RW mutex and includes retained layer references. Layer persistence and reference counts live in `layer.Store`.

Dependencies and integration: Integrates with digestset, daemon image model, layer store, errdefs, logging, and filesystem backend.

Risks: `Create` writes config before validating layer existence, so failed layer retention can leave untracked backend content. `Delete` ignores backend delete errors. Children metadata is removed when parent is deleted, flattening child relationships. `imagesMap` calls `Get` while holding an RLock, so backend latency occurs under lock.

Test signals: `store_test.go` covers create validation, restore, search, add/delete, parent reset, lastUpdated, and length/map behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/store_test.go -->
## sources/cloud-native/moby/daemon/internal/image/store_test.go

Purpose: Tests image store lifecycle and metadata behavior.

Important tests: `TestCreate` rejects missing RootFS. `TestRestore` seeds backend content including invalid JSON, restores two valid images, checks parent/children/heads/search and not-found behavior. `TestAddDelete` creates parent/child images, sets parent, deletes parent, and verifies child remains with parent metadata cleared. `TestSearchAfterDelete` ensures digestset removal. `TestDeleteNotExisting` checks not-found classification. `TestParentReset` moves a child from one parent to another. `TestGetAndSetLastUpdated` checks zero default and persisted timestamp. `TestStoreLen` checks map length after several creates.

Control flow and state: `defaultImageStore` uses a temporary FS backend and `mockLayerGetReleaser` that returns nil layers. Tests use static JSON configs and known digest expectations.

Dependencies and integration: Uses containerd errdefs matching, daemon layer metadata interfaces, and `gotest.tools`.

Risks covered: Invalid restore entries are skipped, parent metadata reconstruction, partial ID lookup, delete cleanup, and metadata writes. Gaps include actual layer retention/release behavior, OS mismatch, builtLocally metadata, and create failures after backend writes.

Persistence: Exercises temporary on-disk backend state and in-memory restored state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/tarexport/load.go -->
## sources/cloud-native/moby/daemon/internal/image/tarexport/load.go

Purpose: Implements Docker image archive load/import from a tar stream into image store, layer store, and reference store.

Important APIs/functions: `(*tarexporter).Load`, `untar`, `setParentID`, `loadLayer`, `setLoadedTag`, `safePath`, `parentLink`, `validatedParentLinks`, and `checkValidParent`.

Control flow: `Load` creates a temp directory, untars input with context-aware reads, opens `manifest.json`, rejects missing/null/invalid manifests, iterates manifest entries, reads config safely inside temp root, validates image JSON and host OS, applies optional platform matcher, checks manifest layer count against RootFS DiffIDs, then for each layer either reuses an existing chain layer or loads it from the archive. `loadLayer` opens the layer file sequentially, optionally wraps it in a progress reader, decompresses it, and registers it with descriptor support when available. After layers are present, `Load` creates the image, tags repo tags, records load events, validates parent links across the loaded set, and writes either loaded image names or IDs.

State and persistence: Writes layer data into `layer.Store`, image config into `image.Store`, tag mappings into `refstore.Store`, and emits image events. Temporary extraction state is removed at return.

Dependencies and integration: Uses chroot archive extraction, symlink-safe path resolution, compression, progress/stream formatting, distribution descriptors for foreign layers, tracing, and platform matching configured in `tarexport.go`.

Risks: Archive safety depends on `safePath` and `chrootarchive.Untar`. Load is all-or-partial; earlier layers/images/tags may remain if a later entry fails. Only loaded-set parent links are restored. Existing layer reuse trusts `lss.Get` and then checks DiffID.

Test signals: No dedicated load tests in this subset; behavior is coupled to image/layer store tests and external integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/tarexport/load.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/tarexport/os_path.go -->
## sources/cloud-native/moby/daemon/internal/image/tarexport/os_path.go

Purpose: Provides `mkdirAllWithChtimes`, a modified `os.MkdirAll` that preserves timestamps on directories it creates.

Important API: `mkdirAllWithChtimes(path, perm, atime, mtime)` recursively creates missing parent directories and calls daemon `system.Chtimes` on each newly-created directory.

Control flow: It fast-paths existing directories, returns `ENOTDIR` if the target exists as a non-directory, computes the parent path manually in the style of Go stdlib, recurses when the parent is not just the volume name, calls `os.Mkdir`, tolerates races where the directory appears, and applies atime/mtime.

State and persistence: Creates directories on disk and mutates filesystem timestamps. Used by tar save paths for reproducible archive metadata.

Dependencies and integration: Used by `save.go` when writing OCI blobs and metadata. Depends on daemon `system.Chtimes`.

Risks: Based on copied stdlib logic, so future path semantics changes need manual sync. Timestamp application can fail on filesystems/platforms with limited time support.

Tests: No direct tests in this subset; failures would surface through tar export save paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/tarexport/os_path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/tarexport/save.go -->
## sources/cloud-native/moby/daemon/internal/image/tarexport/save.go

Purpose: Implements Docker image archive save/export, including Docker `manifest.json`, legacy `repositories`, and OCI layout/index/blob content.

Important APIs/types: `imageDescriptor` records refs, layer DiffIDs, image config, and retained top layer. `saveSession` tracks output dir, selected images, saved layer descriptors, and saved legacy configs. Key methods are `Save`, `parseNames`, `takeLayerReference`, `releaseLayerReferences`, `save`, `writeTar`, `saveImage`, `saveConfigAndLayer`, and `saveConfig`.

Control flow: `Save` resolves requested names/IDs into image descriptors and retains top layers, deferring release. `parseNames` handles digest references, canonical sha256-looking names, bare repository names with all tags, tagged refs, duplicate tags, and invalid refs. `takeLayerReference` loads image config, checks host OS and optional platform, and retains the rootfs top layer. `save` creates a temp dir, loops images, calls `saveImage`, builds Docker manifest entries and OCI manifest/index descriptors, writes legacy repositories when tags exist, writes `manifest.json`, `oci-layout`, `index.json`, fixes timestamps, and tars the directory with `CopyCtx`. `saveImage` walks RootFS layers, creates legacy V1 IDs/configs for compatibility, writes actual image config as an OCI blob, and records layer order. `saveConfigAndLayer` writes legacy config if needed, gets layer tar stream, tees through a digest calculator, writes the layer blob, records descriptor metadata, and warns if the layer DiffID does not match tar digest.

State and persistence: Temporary export tree is written to disk and streamed to caller. The function retains/releases layer references but does not mutate image store except for event logging. Cached `savedLayers` prevents duplicate layer writes.

Dependencies and integration: Integrates image store, layer store, refstore, OCI specs, Docker distribution descriptors, archive/compression, sequential file IO, tracing, events, and context-aware copy.

Risks: Empty image export is not implemented. Partial writes in temp dir are cleaned, but caller output stream may receive partial tar data on late errors. The untagged OCI index branch checks global manifest descriptor length, so multiple untagged images after tagged images need careful review. Descriptor reuse for foreign layers depends on layer implementing `distribution.Describable`.

Tests: No direct tests in this subset; lower-level layer/image tests cover some dependencies.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/tarexport/save.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/tarexport/tarexport.go -->
## sources/cloud-native/moby/daemon/internal/image/tarexport/tarexport.go

Purpose: Defines shared tar export/load types and constructs the image exporter.

Important APIs/types: Constants `manifestFileName` and `legacyRepositoriesFileName`; `manifestItem` models Docker archive manifest entries with config path, repo tags, layer paths, optional parent, and optional foreign layer source descriptors. `tarexporter` holds image store, layer store, reference store, event logger, and optional platform matcher. `LogImageEvent` abstracts event logging. `NewTarExporter` returns an `image.Exporter`.

Control flow: Constructor stores dependencies and creates a strict platform matcher when a platform is supplied.

State and persistence: The struct is long-lived dependency state; load/save methods perform the actual persistence.

Dependencies and integration: Bridges the daemon image exporter interface to image/layer/ref stores and OCI/containerd platform matching.

Risks: All dependencies are interfaces or concrete stores expected to be non-nil; constructor does not validate them. Platform matching is strict, which can exclude images if metadata is incomplete.

Tests: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/tarexport/tarexport.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/v1/imagev1.go -->
## sources/cloud-native/moby/daemon/internal/image/v1/imagev1.go

Purpose: Generates legacy V1 image IDs for backwards-compatible Docker archive save output.

Important APIs: `CreateID(v1Image, layerID, parent)` and helper `rawJSON`.

Control flow: `CreateID` clears the legacy image ID, marshals the V1 image, unmarshals into a map so it can inject `layer_id` and optional `parent`, marshals the map again, logs the generated JSON at debug level, and returns `digest.FromBytes(configJSON)`. `rawJSON` marshals a value and returns a `*json.RawMessage`, or nil on marshal failure.

State and persistence: The generated digest becomes legacy config identity in saved archives. No state is retained in memory.

Dependencies and integration: Called by tar export `saveImage` for every layer in an image. Depends on daemon image/layer types and OpenContainers digest.

Risks: Map marshal ordering and injected compatibility fields determine the digest; any JSON behavior change can alter legacy IDs. The FIXME notes slight incompatibility with RootFS logic.

Tests: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/image/v1/imagev1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/ioutils/copy.go -->
## sources/cloud-native/moby/daemon/internal/ioutils/copy.go

Purpose: Provides context-aware reader/copy helpers for long-running stream operations.

Important APIs/types: `CopyCtx(ctx, dst, src)` wraps `io.Copy` and returns early on context cancellation. `NewCtxReader(ctx, r)` wraps reads with context checks. `readerCtx` implements `Read`.

Control flow: `CopyCtx` wraps `src`, starts `io.Copy` in a goroutine, and races copy completion against `ctx.Done()`. On cancellation it returns `-1, ctx.Err()` without closing the writer and without waiting for the copy goroutine. `readerCtx.Read` checks `ctx.Err()` before and after the underlying `Read`, returning context error if cancellation is observed.

State and persistence: No persistent state. It can leave a goroutine blocked if the underlying reader or writer blocks after cancellation, as documented.

Dependencies and integration: Used by tar load/save and archive handling to make stream operations cancellable at API boundaries.

Risks: Goroutine lifetime is intentionally not guaranteed after cancellation. If underlying IO ignores cancellation and blocks forever, resources may remain. Partial bytes read concurrently with cancellation are discarded by returning zero and context error from `readerCtx`.

Test signals: `copy_test.go` validates that `CopyCtx` returns promptly when a blocking reader is paired with a cancelled context.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/ioutils/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/ioutils/copy_test.go -->
## sources/cloud-native/moby/daemon/internal/ioutils/copy_test.go

Purpose: Tests that `CopyCtx` responds to context cancellation even when the source reader blocks.

Important test/helper: `blockingReader.Read` sleeps for one second and returns no data. `TestCopyCtx` creates a context with a 5 ms timeout, calls `CopyCtx` in a goroutine, and requires it to finish within 100 ms.

Control flow and state: The test does not inspect returned byte count or error; it only validates liveness.

Dependencies and integration: Uses `bytes.Buffer`, context timeouts, and time-based select.

Risks covered: The primary cancellation path in `CopyCtx`. It does not assert the documented `-1` byte count, context error, or goroutine cleanup behavior after return.

Persistence: None.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/ioutils/copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/empty.go -->
## sources/cloud-native/moby/daemon/internal/layer/empty.go

Purpose: Defines the canonical empty layer implementation and digest.

Important APIs/types: `DigestSHA256EmptyTar` is the sha256 digest of a 1024-byte empty tar stream. `EmptyLayer` is a singleton `*emptyLayer`. `IsEmpty(diffID)` checks for the empty layer digest.

Control flow: `TarStream` creates an in-memory tar writer, closes it to emit an empty tar, and returns a read closer. `TarStreamFrom` only supports an empty parent ID. Metadata, parent, size, diff size, chain ID, and diff ID methods return fixed empty-layer values.

State and persistence: No mutable persistence. The digest value is part of image/layer compatibility semantics and is used to avoid adding empty history layers to RootFS.

Dependencies and integration: Used by image child creation and layer APIs as a no-content layer.

Risks: The digest must remain aligned with the tar writer output. `TarStreamFrom` returns a generic error for non-empty parent.

Test signals: `empty_test.go` verifies IDs, nil parent, zero sizes, empty metadata, and tar digest.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/empty.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/empty_test.go -->
## sources/cloud-native/moby/daemon/internal/layer/empty_test.go

Purpose: Tests the empty layer singleton.

Important test: `TestEmptyLayer` checks chain ID, diff ID, parent, size, diff size, metadata, tar stream creation, and digest of the produced tar stream.

Control flow and state: Copies the tar stream into a canonical digest hash and compares it to `DigestSHA256EmptyTar`.

Dependencies and integration: Uses `io.Copy` and OpenContainers digest. It exercises the `Layer`-like methods on `EmptyLayer`.

Risks covered: Accidental changes to the empty tar representation or fixed metadata. It does not test `TarStreamFrom` error behavior or `IsEmpty`.

Persistence: None.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/empty_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/filestore.go -->
## sources/cloud-native/moby/daemon/internal/layer/filestore.go

Purpose: Provides filesystem metadata persistence for layer store state, including read-only layer metadata, tar-split data, writable mount metadata, and orphan cleanup discovery.

Important APIs/types: `fileMetadataStore`, `fileMetadataTransaction`, `newFSMetadataStore`, path helpers, `StartTransaction`, transaction setters (`SetSize`, `SetParent`, `SetDiffID`, `SetCacheID`, `SetDescriptor`, `TarSplitWriter`, `Commit`, `Cancel`), getters (`GetSize`, `GetParent`, `GetDiffID`, `GetCacheID`, `GetDescriptor`, `TarSplitReader`), mount metadata setters/getters, `getOrphan`, `List`, `Remove`, `RemoveMount`, and `isValidID`.

Control flow: Transactions write into `root/tmp` using `atomicwriter.WriteSet` and commit atomically to `root/<algorithm>/<encoded>`. Layer metadata files are simple text or JSON sidecars: `size`, `parent`, `diff`, `cache-id`, `descriptor.json`, and `tar-split.json.gz`. Tar-split writer can gzip input. Mount metadata lives under `root/mounts/<mount>/`. `List` enumerates valid layer digest directories and mount directories. `getOrphan` finds directories ending `-removing`, validates the encoded digest prefix, reads cache ID, and returns lightweight `roLayer` values for cleanup. `Remove` removes only matching `-removing` metadata folders for a given chain/cache pair.

State and persistence: All state is durable files under layerdb. The store itself has no lock; callers coordinate.

Dependencies and integration: Used by `layer_store.go` for restore, register, release, mount save, tar reconstruction, and cleanup. Depends on gzip, JSON, distribution descriptors, atomic writer, and digest parsing.

Risks: Metadata corruption causes restore failures. `isValidID` constrains mount/init IDs to 64 lower-hex chars with optional `-init`, which may reject unexpected graphdriver IDs. `TarSplitWriter` close wrapper ignores the gzip close error ordering by returning only file close after calling `wc.Close`.

Test signals: `filestore_test.go` covers transaction failure, orphan detection, and mount/init ID validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/filestore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/filestore_test.go -->
## sources/cloud-native/moby/daemon/internal/layer/filestore_test.go

Purpose: Tests filesystem metadata store edge cases.

Important helpers/tests: `randomLayerID` creates deterministic test digests. `newFileMetadataStore` creates temp roots. `TestCommitFailure` creates a file where the algorithm directory should be and expects `ENOTDIR`. `TestStartTransactionFailure` creates a file at `tmp`, expects transaction start failure, then removes it and verifies a transaction can be canceled. `TestGetOrphan` creates committed metadata, then renames the layer directory to a `-removing` name and expects orphan discovery. `TestIsValidID` covers valid 64-character lower-hex IDs, `-init`, too short/long, uppercase, non-hex, empty, and suffix-only strings.

Control flow and state: Tests mutate on-disk metadata directly to simulate failure and cleanup states.

Dependencies and integration: Uses `stringid.GenerateRandomID`, OpenContainers digest, syscall errors, and temp directories.

Risks covered: Atomic transaction parent conflicts, orphan layer cleanup discovery, and mount ID validation. Gaps include descriptor JSON, tar-split reader/writer, metadata getters, `List`, and `Remove`.

Persistence: Strong focus on layerdb disk layout.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/filestore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer.go -->
## sources/cloud-native/moby/daemon/internal/layer/layer.go

Purpose: Defines the layer store package contracts for read-only layers, writable layers, metadata, store operations, and common errors.

Important APIs/types: Errors include `ErrLayerDoesNotExist`, `ErrLayerNotRetained`, `ErrMountDoesNotExist`, `ErrMountNameConflict`, and `ErrMaxDepthExceeded`. `ChainID` and `DiffID` alias digest. Interfaces include `TarStreamer`, `Layer`, `RWLayer`, `Store`, and `DescribableStore`. `Metadata`, `MountInit`, and `CreateRWLayerOpts` describe lifecycle metadata and mount creation options. `ReleaseAndLog` releases a layer and logs cleanup metadata.

Control flow: Mostly declarations. `ReleaseAndLog` calls `Store.Release`, logs errors, and logs each removed layer metadata entry.

State and persistence: Interfaces abstract persistent graphdriver/layerdb state implemented elsewhere. `Metadata` reports removed layer state after release.

Dependencies and integration: This is the main boundary used by image store, tar export/import, distribution transfer, builder cache, and graphdriver integrations.

Risks: Interface contracts rely on callers balancing `Get/Register/CreateRWLayer` references with `Release/ReleaseRWLayer`. Misbalanced calls can leak layers or trigger retained-reference errors. `ReleaseAndLog` intentionally swallows release errors after logging.

Test signals: Many layer tests validate concrete implementations against these contracts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer_store.go -->
## sources/cloud-native/moby/daemon/internal/layer/layer_store.go

Purpose: Implements the concrete graphdriver-backed layer store for immutable layers and mutable mounts.

Important APIs/types: `maxLayerDepth`, `layerStore`, `StoreOptions`, `NewStoreFromOptions`, `newStoreFromGraphDriver`, `Driver`, `loadLayer`, `loadMount`, `applyTar`, `Register`, `registerWithDescriptor`, `Get`, `Map`, `Release`, `CreateRWLayer`, `GetRWLayer`, `GetMountID`, `ReleaseRWLayer`, `saveMount`, `initMount`, `getTarStream`, `assembleTarTo`, `Cleanup`, `DriverStatus`, `DriverName`, and the `naiveDiffPathDriver` fallback.

Control flow: Initialization creates graphdriver and layerdb store, lists layer/mount metadata, recursively loads read-only layers, increments parent reference counts, and restores mounts. Registering a layer retains the parent, creates a graphdriver cache ID, starts metadata transaction, applies tar through tar-split metadata capture, computes diff/chain IDs, stores metadata, deduplicates against existing chain IDs, commits transaction, and returns a retained reference. Release removes a reference, decrements reference counts recursively, renames metadata to `-removing`, removes graphdriver data, then deletes metadata. RW layer creation locks by name, retains parent, optionally creates an init layer, creates graphdriver read-write layer, persists mount metadata, and returns a reference. RW release removes graphdriver layers and mount metadata, then releases parent. Tar stream reconstruction reads tar-split metadata and graphdriver diff files, then verifies through `ro_layer.go`.

State and persistence: In-memory maps `layerMap` and `mounts` plus reference maps/counts are protected by locks. Durable state is graphdriver data and layerdb metadata. Cleanup removes orphaned `-removing` layerdb entries and delegates driver cleanup.

Dependencies and integration: Central integration with graphdriver, layer metadata store, tar-split asm/storage, digest identity chain IDs, string IDs, user ID mapping, and daemon logging.

Risks: Reference-count invariants are strict and can panic on impossible states. Deduplication sets a cleanup error to remove the just-created duplicate graphdriver layer while returning the existing reference. Register writes/driver operations span several systems and must clean up on every failure. `Map` exposes underlying `*roLayer` values, not new references, so callers must not release them as retained references.

Test signals: `layer_test.go`, `mount_test.go`, `layer_unix_test.go`, and `migration_test.go` cover registration, restore, release, tar stability, duplicate registration, tar verification, mount behavior, and migration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer_store_windows.go -->
## sources/cloud-native/moby/daemon/internal/layer/layer_store_windows.go

Purpose: Exposes descriptor-aware registration on Windows builds.

Important API: `(*layerStore).RegisterWithDescriptor(ts, parent, descriptor)` delegates to `registerWithDescriptor`.

Control flow and state: No additional logic; build tags/platform filename select this implementation.

Dependencies and integration: Allows Windows layer store to satisfy `DescribableStore`, so tar load can preserve foreign source descriptors when registering layers.

Risks: Behavior is entirely inherited from `registerWithDescriptor`; platform-specific differences are in graphdriver behavior. No direct tests in this subset.

Persistence: Same as `layer_store.go` through metadata transactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer_store_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer_test.go -->
## sources/cloud-native/moby/daemon/internal/layer/layer_test.go

Purpose: Provides broad integration-style tests for the concrete layer store using the vfs graphdriver.

Important helpers: `newVFSGraphDriver`, `newTestStore`, `createLayer`, `FileApplier`, `testFile`, `initWithFiles`, `getCachedLayer`, metadata assertions, `tarFromFiles`, `assertLayerDiff`, and `assertReferences`.

Important tests: `TestMountAndRegister` verifies creating a layer and mounting a child RW layer. `TestLayerRelease` checks recursive deletion only after all children/references release. `TestStoreRestore` verifies restoring layers and mounts from layerdb, duplicate mount name conflict, repeated mount/unmount, RW release, and final parent cleanup. `TestTarStreamStability` confirms registered layer tar streams remain stable even if graphdriver content is later modified. `TestRegisterExistingLayer` confirms duplicate registration returns references to the same underlying layer. `TestTarStreamVerification` corrupts tar-split metadata and expects verification failure.

Control flow and state: Tests create real temp graphdriver data, write files, register tar streams, manipulate driver state, and inspect internal maps/reference sets.

Dependencies and integration: Exercises graphdriver/vfs, archive packing, tar-split reconstruction, digest verification, and reference counting.

Risks covered: Restore, deduplication, recursive release, tar reproducibility, and metadata corruption. Several tests skip Windows due to known graphdriver differences.

Persistence: Strongly exercises layerdb plus graphdriver temp filesystem state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer_unix.go -->
## sources/cloud-native/moby/daemon/internal/layer/layer_unix.go

Purpose: Provides Unix-like mount ID generation for writable layers.

Important API: `(*layerStore).mountID(name string) string` returns `stringid.GenerateRandomID()`.

Control flow and state: Build-tagged for Linux, FreeBSD, Darwin, and OpenBSD. It ignores the caller-visible mount name and generates a random graphdriver ID.

Dependencies and integration: Used by `CreateRWLayer` in `layer_store.go`. Separates user-visible mount names from graphdriver cache IDs on Unix-like platforms.

Risks: Random ID generation must avoid collisions; collision handling is delegated to graphdriver create errors. Windows differs by using the name directly.

Tests: Indirectly covered by layer and mount tests on Unix-like platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer_unix_test.go -->
## sources/cloud-native/moby/daemon/internal/layer/layer_unix_test.go

Purpose: Tests layer size accounting on non-Windows builds.

Important helper/test: `graphDiffSize` extracts the underlying `roLayer` and calls graphdriver `DiffSize`. `TestLayerSize` creates two layers with known file contents and verifies both graphdriver diff sizes and layer cumulative sizes.

Control flow and state: Uses `newTestStore` and `createLayer` from `layer_test.go`, then compares expected byte lengths for base and child layers.

Dependencies and integration: Exercises graphdriver `DiffSize` and `Layer.Size` on Unix-like platforms. The build tag excludes Windows because its graphdriver does not support the same Changes/DiffSize path.

Risks covered: Cumulative size calculation and per-layer diff size. Gaps include sparse files, whiteouts, metadata-only changes, and compression effects.

Persistence: Temporary graphdriver/layerdb state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer_windows.go -->
## sources/cloud-native/moby/daemon/internal/layer/layer_windows.go

Purpose: Adds Windows-specific layer path lookup and mount ID behavior.

Important APIs: `Getter` is a graphdriver extension for direct layer paths. `GetLayerPath(s Store, layer ChainID)` returns the host path for a layer. `(*layerStore).mountID(name)` returns the mount name itself.

Control flow: `GetLayerPath` asserts the store is a `*layerStore`, locks layer map, finds the read-only layer, then either calls driver `Getter.GetLayerPath(cacheID)` or mounts the driver layer with `Get` and immediately `Put`s it after capturing the path. `mountID` preserves the container/mount name due to Windows constraints.

State and persistence: Reads in-memory layer map and graphdriver state. No new persistence.

Dependencies and integration: Used by Windows daemon paths needing host layer paths. Integrates with graphdriver-specific Windows APIs.

Risks: The returned path from fallback `Get` may become invalid after `Put` depending on driver semantics. Holding `layerL` while calling driver methods may block other layer operations. Unsupported store types fail.

Tests: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/layer_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/migration.go -->
## sources/cloud-native/moby/daemon/internal/layer/migration.go

Purpose: Supports migration of existing graphdriver layers into layerdb/tar-split metadata without reapplying tar data.

Important APIs/types: `ChecksumForGraphID`, `RegisterByGraphID`, `unpackSizeCounter`, and `packSizeCounter`.

Control flow: `ChecksumForGraphID` reads a graphdriver diff for graph ID and parent, creates a tar-split metadata file at `newTarDataPath`, wraps the diff with `asm.NewInputTarStreamWithDone`, hashes the archive via `digest.FromReader`, waits for tar-split completion, and returns diff ID plus unpacked size. `RegisterByGraphID` retains the parent, computes chain ID from parent and diff ID, deduplicates if already present, starts metadata transaction, copies the previously generated tar-split data into transaction storage without gzip recompression, writes layer metadata, commits, inserts the layer into `layerMap`, and returns a retained reference. Counters accumulate entry sizes while packing/unpacking tar-split metadata.

State and persistence: Reads graphdriver data, writes tar-split metadata and layerdb sidecars, updates in-memory layer map and reference counts.

Dependencies and integration: Used by daemon migration paths from older graph/layer layouts. Depends on graphdriver diffs, tar-split asm/storage, gzip, digest identity, and metadata transactions.

Risks: Parent release cleanup on error must remain balanced. The function trusts `size` and `diffID` provided to `RegisterByGraphID` from prior checksum work. Tar data file lifecycle is external to these functions.

Test signals: `migration_test.go` validates migration registration deduplicates with normal registration and reference release semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/migration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/migration_test.go -->
## sources/cloud-native/moby/daemon/internal/layer/migration_test.go

Purpose: Tests migration from existing graphdriver layers into the layer store.

Important helpers/tests: `tarFromFilesInGraph` creates graphdriver layers and reads their diffs. `TestLayerMigrationNoTarsplit` creates two graph layers, computes checksum/tar-split metadata for the first, registers it by graph ID, registers the same tar normally and asserts shared references, registers a child normally, computes and registers child by graph ID, asserts shared references, then releases both child references and checks metadata deletion only after the second release.

Control flow and state: Uses vfs graphdriver temp roots and a `.migration-tardata` file to simulate migration metadata generation.

Dependencies and integration: Exercises `ChecksumForGraphID`, `RegisterByGraphID`, regular `Register`, reference counting, and metadata deletion. Skips Windows due to graphdriver differences.

Risks covered: Migration/normal registration deduplication, tar-split metadata import, and release semantics. Gaps include corrupt migration tar data, parent missing errors, and cleanup on commit failure.

Persistence: Uses temporary graphdriver and layerdb data.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/migration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/mount_test.go -->
## sources/cloud-native/moby/daemon/internal/layer/mount_test.go

Purpose: Tests writable layer mount behavior.

Important tests: `TestMountInit` verifies an init layer can alter file content and permissions visible in the mounted RW layer. `TestMountSize` verifies init-layer changes are excluded from mutable layer size while newly written RW data is counted. `TestMountChanges` verifies modify/delete/add changes relative to base/init parent are reported. `TestMountApply` applies a diff tar to a RW layer and verifies the new file appears. Helpers `assertChange`, `sortChanges`, and `changeSorter` normalize change ordering.

Control flow and state: Tests create base layers, optional init functions, RW layers, mount paths, direct filesystem mutations, graphdriver diff/change calls through `RWLayer` methods, and unmount/release paths inherited from helpers.

Dependencies and integration: Exercises `CreateRWLayer`, `Mount`, `Size`, `Changes`, `ApplyDiff`, graphdriver vfs, archive change types, and local chmod support. Skips Windows.

Risks covered: Init-layer parent selection, size accounting excluding init content, change detection, and applying tar diffs. Gaps include mount labels, storage options, repeated mount reference counting, and cleanup after failed init/apply.

Persistence: Temporary graphdriver/layerdb state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/mounted_layer.go -->
## sources/cloud-native/moby/daemon/internal/layer/mounted_layer.go

Purpose: Implements `RWLayer` references for mutable container layers.

Important APIs/types: `mountedLayer` stores name, graphdriver mount ID, optional init ID, parent `roLayer`, store pointer, and active RW references. Methods implement `cacheParent`, `TarStream`, `Name`, `Parent`, `Size`, `Changes`, `Metadata`, `getReference`, `hasReferences`, `deleteReference`, `retakeReference`. `referencedRWLayer` embeds `mountedLayer` and implements `Mount`, `Unmount`, and `ApplyDiff`.

Control flow: RW operations delegate to the graphdriver using `mountID` and `cacheParent`, where `cacheParent` prefers init layer over parent layer. `getReference` creates a wrapper and records it under a mutex. `deleteReference` ensures release is balanced and returns `ErrLayerNotRetained` for unknown references. `retakeReference` restores a reference after failed deletion. `Metadata` ensures an `ID` key defaults to the user-visible mount name.

State and persistence: Reference map is in-memory. Durable mount metadata is handled by `layer_store.go`/`filestore.go`; graphdriver stores filesystem data.

Dependencies and integration: Used by layer store RW lifecycle and container mount operations. Depends on graphdriver Diff/Get/Put/ApplyDiff/Changes/DiffSize.

Risks: Mount/unmount balance is caller-managed. `referencedRWLayer` references share the same underlying mutable layer, so concurrent filesystem modifications are graphdriver/caller responsibility. Error recovery in release depends on `retakeReference`.

Test signals: `mount_test.go` and `layer_test.go` cover mount content, size, changes, apply diff, restore, repeated mount/unmount, and release.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/mounted_layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/ro_layer.go -->
## sources/cloud-native/moby/daemon/internal/layer/ro_layer.go

Purpose: Implements immutable layer objects, retained references, tar stream verification, and metadata serialization helpers.

Important APIs/types: `roLayer` stores chain ID, diff ID, parent, graphdriver cache ID, size, store, optional distribution descriptor, reference count, and retained reference set. Methods implement `Layer`: `TarStream`, `TarStreamFrom`, `ChainID`, `DiffID`, `Parent`, `Size`, `DiffSize`, `Metadata`, plus `CacheID`, reference helpers, `depth`, `storeLayer`, `newVerifiedReadCloser`, and `verifiedReadCloser`.

Control flow: `TarStream` reconstructs the original tar from tar-split metadata and graphdriver files, then wraps it in a digest verifier that checks against `diffID` at EOF. `TarStreamFrom` returns a graphdriver diff from an ancestor cache ID but explicitly does not guarantee exact original tar bytes. `Size` recursively adds parent sizes. `getReference` creates a `referencedCacheLayer` and records it. `storeLayer` writes diff, size, cache ID, non-empty descriptor, and parent into a metadata transaction. `verifiedReadCloser.Read` hashes bytes as they pass and errors at EOF if digest verification fails.

State and persistence: Reference state is in memory; serialized metadata is persisted by `storeLayer`. Tar verification protects against layerdb/driver tampering.

Dependencies and integration: Used by image store layer retention, tar export, distribution upload, and layer store registration/release.

Risks: Reference helpers assume external locking by `layerStore`. `TarStreamFrom` can produce non-verifiable streams and must not be used for content identity. Verification errors only appear when the stream is fully read to EOF.

Test signals: Layer tests cover tar stability, duplicate references, release behavior, and verification failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/ro_layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/ro_layer_windows.go -->
## sources/cloud-native/moby/daemon/internal/layer/ro_layer_windows.go

Purpose: Adds Windows-only descriptor exposure for read-only layers.

Important API: The file asserts `*roLayer` implements `distribution.Describable` and defines `Descriptor() distribution.Descriptor`.

Control flow and state: Returns the descriptor stored on the layer. No extra persistence; descriptor data is loaded/stored through file metadata.

Dependencies and integration: Lets Windows layer store layers expose distribution metadata to tar export/save paths and other distribution-aware code.

Risks: Empty descriptors are valid and mean no descriptor was stored. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/layer/ro_layer_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/lazyregexp/lazyregexp.go -->
## sources/cloud-native/moby/daemon/internal/lazyregexp/lazyregexp.go

Purpose: Provides a lazy wrapper around `regexp.Regexp` for global regex variables without init-time compilation cost.

Important APIs/types: `Regexp` stores the pattern string, `sync.Once`, and compiled regexp pointer. `New` constructs a lazy regexp and eagerly compiles in test binaries. Wrapper methods expose common regexp operations: submatches, all string submatches, string match/index, replace, find, match, replace func, and subexpression names.

Control flow: First method call invokes `re`, which runs `build` once. `build` calls `regexp.MustCompile`, stores the compiled regexp, and clears the original string. `inTest` detects test binaries by executable name ending `.test` (after trimming `.exe`) so invalid regexps panic during tests rather than later at runtime.

State and persistence: In-memory cached compiled regex only. No persistence.

Dependencies and integration: Based on Go module lazyregexp pattern, used by packages with package-level regexps.

Risks: Invalid patterns panic on first use in production. After compilation, the original pattern string is cleared, so debugging relies on `regexp.Regexp` string output. Only wrapped regexp methods are available.

Test signals: `lazyregexp_test.go` confirms eager test panic for invalid regex and basic valid matching.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/lazyregexp/lazyregexp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/lazyregexp/lazyregexp_test.go -->
## sources/cloud-native/moby/daemon/internal/lazyregexp/lazyregexp_test.go

Purpose: Tests lazy regexp construction in test mode.

Important test: `TestCompileOnce` has an invalid regexp subtest expecting `New("[")` to panic, and a valid regexp subtest expecting `[a-z]` to match `"hello"`.

Control flow and state: Panic recovery validates eager compilation under test binary detection.

Dependencies and integration: Uses the package's `New` and `MatchString`.

Risks covered: Invalid patterns are caught during tests and valid patterns work after construction. It does not assert `sync.Once` directly or every wrapper method.

Persistence: None.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/lazyregexp/lazyregexp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/libcontainerd_linux.go -->
## sources/cloud-native/moby/daemon/internal/libcontainerd/libcontainerd_linux.go

Purpose: Linux constructor shim for the daemon's libcontainerd client abstraction.

Important API: `NewClient(ctx, cli, stateDir, ns, b)` returns `remote.NewClient(ctx, cli, stateDir, ns, b)`.

Control flow and state: No branching; Linux always uses the remote containerd client wrapper with the supplied `*containerd.Client`.

Dependencies and integration: Depends on containerd v2 client, daemon internal `remote` libcontainerd implementation, and libcontainerd types. Used by daemon startup code that wants platform-neutral client construction.

Risks: Passing a nil `cli` on Linux is not handled here and is delegated to `remote.NewClient`, unlike Windows which supports a local fallback. No direct tests in this subset.

Persistence: State is owned by remote client implementation, not this shim.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/libcontainerd_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/libcontainerd_windows.go -->
## sources/cloud-native/moby/daemon/internal/libcontainerd/libcontainerd_windows.go

Purpose: Windows constructor shim for the daemon's libcontainerd client abstraction.

Important API: `NewClient(ctx, cli, stateDir, ns, b)` returns a local client when `cli == nil`; otherwise it returns `remote.NewClient`.

Control flow and state: One branch selects `local.NewClient(ctx, b)` for nil containerd clients and remote wrapper for real containerd clients.

Dependencies and integration: Depends on containerd v2 client, internal local and remote libcontainerd implementations, and shared libcontainerd types. Supports Windows daemon modes where no external containerd client is provided.

Risks: Behavior differs from Linux nil-client handling. Callers relying on the local fallback must be Windows-specific. No direct tests in this subset.

Persistence: Client state is managed by local/remote implementations, not this shim.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/libcontainerd_windows.go -->
