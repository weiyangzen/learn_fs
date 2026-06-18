# subset-b-000169 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/tarsum_test.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/tarsum_test.go

## Purpose
Exercises the legacy internal TarSum implementation against fixture layers, synthetic tar streams, gzip passthrough, alternate hash algorithms, duplicate-path ordering, xattr-sensitive versions, iteration behavior, and performance benchmarks. It is a regression suite for deterministic build-context/layer checksums rather than production logic.

## Important APIs, Types, And Functions
Defines `testLayer`, `sizedOptions`, `testLayers`, helper `sizedTar`, `emptyTarSum`, and `renderSumForHeader`. Tests cover `NewTarSum`, `NewTarSumHash`, `NewTarSumForLabel`, `TarSum.Read`, `TarSum.Sum`, `TarSum.Hash`, and `TarSum.Version`. Benchmarks use `benchmarkTar` over real and in-memory tar streams.

## Control Flow
Fixture entries are opened or generated, wrapped in TarSum readers, partially read with small and larger buffers, drained, and compared to known digests. Empty tar tests run pipe-backed tar writers and compare raw/gzip output. Header iteration constructs one-entry tars and drains them through `tar.NewReader` to force checksum recording.

## State And Persistence
Tests read `testdata` fixtures and create temp files only for benchmark streams. TarSum state is accumulated during reads and finalized by `Sum`; duplicate path tests intentionally depend on archive order and per-entry position.

## Dependencies And Integration Points
Depends on `archive/tar`, `compress/gzip`, crypto hash constructors, fixture layers/json, and `gotest.tools` assertions. It validates behavior consumed by remote build context hashing and archive context cache keys.

## Risks And Test Signals
The suite locks in legacy hashes, so harmless selector changes can break compatibility. Random benchmark data is not used for assertions. Failures signal digest drift, gzip corruption, read-size sensitivity, xattr ordering regressions, or broken support for non-default hash algorithms.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/tarsum_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/versioning.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/versioning.go

## Purpose
Defines TarSum algorithm versions and the ordered tar-header field selection used to produce stable per-entry hashes. It preserves the original `tarsum` behavior while adding a v1/dev selector that ignores mtime and includes sorted xattrs.

## Important APIs, Types, And Functions
Exports `Version`, constants `Version0`, `Version1`, `VersionDev`, `WriteV1Header`, `VersionLabelForChecksum`, `GetVersions`, `Version.String`, and `GetVersionFromTarsum`. Internal selectors are `v0TarHeaderSelect`, `v1TarHeaderSelect`, `tarHeaderSelector`, `tarHeaderSelectFunc`, `registeredHeaderSelectors`, and `getTarHeaderSelector`.

## Control Flow
`GetVersionFromTarsum` cuts at `+` and looks up the version label. `v0TarHeaderSelect` emits fixed metadata fields including mtime. `v1TarHeaderSelect` gathers `SCHILY.xattr.` PAX records, overlays deprecated `Header.Xattrs` values when both exist, appends xattr-only entries, sorts by key, copies v0 fields except mtime, then appends xattrs.

## State And Persistence
State is static maps from version enum to label and selector. No persistent storage is touched, but selector output defines persistent checksum compatibility for stored layer/build-cache metadata.

## Dependencies And Integration Points
Used by `NewTarSum`, file hashing helpers, and tests. Depends on Go `archive/tar` header semantics, including deprecated `Xattrs`, and mirrors archive/tar precedence between PAX and xattr maps.

## Risks And Test Signals
Map iteration makes `GetVersions` unordered. Changing field order or xattr precedence changes every digest for affected archives. Tests in `versioning_test.go` and `tarsum_test.go` catch labels, version lookups, and xattr selector order.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/versioning.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/versioning_test.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/versioning_test.go

## Purpose
Tests version label parsing, enum stringification, version lookup, advertised known versions, and v1 xattr selection rules for TarSum.

## Important APIs, Types, And Functions
Targets `VersionLabelForChecksum`, `Version.String`, `GetVersionFromTarsum`, `GetVersions`, helper `containsVersion`, and internal `v1TarHeaderSelect`. Uses `slices.Contains`, `errors.Is`, and `gotest.tools` deep equality.

## Control Flow
The tests feed valid labels with and without hash suffixes and one invalid label. `GetVersions` is checked by membership rather than order. The xattr test builds a tar header containing both `PAXRecords` and `Xattrs`, renders selected headers into test logs, and asserts the last three fields are sorted xattrs with `Xattrs` taking precedence over PAX for the duplicate key.

## State And Persistence
No file or persistent state. The test reflects static version maps and selector behavior.

## Dependencies And Integration Points
This is the direct unit coverage for `versioning.go`; broader checksum consequences are covered by `tarsum_test.go`.

## Risks And Test Signals
The tests intentionally accept unordered `GetVersions` output. Failure indicates label compatibility breakage, missing version registration, or xattr ordering/precedence drift that would alter v1/dev TarSum output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/versioning_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/writercloser.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/writercloser.go

## Purpose
Provides a tiny adapter for code paths that require a writer that can also be closed and flushed. It allows a plain `io.Writer` to satisfy an internal `writeCloseFlusher` contract without owning real resources.

## Important APIs, Types, And Functions
Defines unexported interface `writeCloseFlusher` embedding `io.WriteCloser` and adding `Flush() error`. Defines `nopCloseFlusher` with embedded `io.Writer`, plus no-op `Close` and `Flush` methods.

## Control Flow
Calls to `Write` dispatch to the embedded writer. `Close` and `Flush` immediately return nil, so callers can uniformly defer or flush without checking whether the underlying writer needs it.

## State And Persistence
No state beyond the wrapped writer reference. It does not persist data, close underlying resources, or force buffered output.

## Dependencies And Integration Points
Used by TarSum/gzip/tar writer plumbing where callers need a common interface for real closers/flushers and plain writers.

## Risks And Test Signals
The main risk is assuming `Close` or `Flush` affects the wrapped writer; it deliberately does not. It has no direct tests, but failures would surface in TarSum read/write tests if stream wrappers lost data.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/writercloser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/lazycontext.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/lazycontext.go

## Purpose
Implements a `builder.Source` backed by a filesystem directory that computes file hashes lazily and caches them by relative path. It is used for build contexts where hashing every file upfront is unnecessary.

## Important APIs, Types, And Functions
Exports `NewLazySource(root string) (builder.Source, error)`. Internal `lazySource` implements `Root`, `Close`, `Hash`, and `prepareHash`. It relies on `normalize`, `NewFileHash`, `pools.Copy`, and path error conversion.

## Control Flow
`Hash` normalizes the requested path under the root, computes the relative path, `Lstat`s the file, and returns the relative path for missing targets to preserve broken-symlink compatibility. Cache misses call `prepareHash`, which creates a tar-compatible file hash and copies file data only for non-empty regular files.

## State And Persistence
Maintains an in-memory `map[string]string` of relative-path hashes. `Close` is a no-op and the root directory is not owned. The type is explicitly not concurrency-safe.

## Dependencies And Integration Points
Integrates with builder cache keys and remotecontext file hashing. It depends on filesystem metadata and file content, but delegates canonical hash format to `NewFileHash`.

## Risks And Test Signals
Stale cache entries are possible if files mutate after first hash. Broken symlinks returning paths is compatibility-sensitive. No direct file in this subset tests it; archive-context hashing tests provide adjacent coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/lazycontext.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/mimetype.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/mimetype.go

## Purpose
Centralizes MIME type detection for remote build-context preambles, normalizing Go's sniffed content type to the bare media type without parameters.

## Important APIs, Types, And Functions
Defines constants `mimeTypeTextPlain` and `mimeTypeOctetStream`, and unexported `detectContentType(c []byte) (string, error)`.

## Control Flow
`detectContentType` passes bytes to `http.DetectContentType`, then uses `mime.ParseMediaType` to strip parameters such as charset and return only the MIME token.

## State And Persistence
No mutable or persistent state.

## Dependencies And Integration Points
Called by `inspectResponse` in `remote.go` when the server omits `Content-Type` or reports `application/octet-stream`. It relies on Go's built-in sniffing behavior.

## Risks And Test Signals
Sniffing only sees the supplied preamble, so short or ambiguous content can be classified as octet-stream. `mimetype_test.go` verifies plain text normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/mimetype.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/mimetype_test.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/mimetype_test.go

## Purpose
Provides a minimal unit test that `detectContentType` recognizes a plain text byte slice and returns the normalized `text/plain` constant.

## Important APIs, Types, And Functions
Tests `detectContentType` and `mimeTypeTextPlain` using `gotest.tools` assertions.

## Control Flow
The test sends a simple ASCII sentence to `detectContentType`, asserts no error, and checks the exact returned media type.

## State And Persistence
No state or filesystem access.

## Dependencies And Integration Points
Directly guards the helper used by remote context response inspection.

## Risks And Test Signals
Coverage is narrow: it does not test charset stripping, binary data, or parse errors. A failure indicates drift in MIME sniffing assumptions or constant values.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/mimetype_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/remote.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/remote.go

## Purpose
Downloads remote Docker build contexts and validates response content type before exposing a readable body. It also classifies HTTP errors into Docker `errdefs`.

## Important APIs, Types, And Functions
Defines `maxPreambleLength`, `acceptableRemoteMIME`, lazy `mimeRe`, `downloadRemote`, `GetWithStatusError`, `inspectResponse`, and `selectAcceptableMIME`.

## Control Flow
`downloadRemote` calls `GetWithStatusError`, then `inspectResponse`, and wraps the reconstructed body with a closer that closes the original response. `GetWithStatusError` maps DNS misses and HTTP 400/401/403/404/default failures to specific `errdefs`. `inspectResponse` reads up to 100 bytes, rejects empty bodies, replays the preamble with `io.MultiReader`, sniffs missing/octet-stream content, and accepts only tar/compressed/text/plain/octet-stream MIME matches.

## State And Persistence
No persistent state. It consumes bytes from network responses but reconstructs the reader so callers see the full body.

## Dependencies And Integration Points
Uses `http.Get`, `lazyregexp`, `ioutils.NewReadCloserWrapper`, `detectContentType`, and Docker error classification. It feeds higher-level build-context selection between Dockerfile text and archive streams.

## Risks And Test Signals
Accepting regex substrings can tolerate parameters but also depends on MIME spelling. DNS error classification is specific to non-timeout `net.DNSError`. Tests cover MIME acceptance, body preservation, empty responses, downloads via `httptest`, and status error bodies.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/remote_test.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/remote_test.go

## Purpose
Tests remote-context response inspection, MIME selection, HTTP download behavior, and status-code error handling.

## Important APIs, Types, And Functions
Defines `binaryContext`, tests `selectAcceptableMIME`, `inspectResponse`, `downloadRemote`, and `GetWithStatusError`, plus helper `readBody`.

## Control Flow
Tests validate accepted tar/compression/text/octet MIME values and rejected JSON/empty/incomplete strings. `inspectResponse` cases cover empty response errors, binary octet-stream preservation, unsupported content type returning a replayable body, text/plain, missing content type sniffed as text, and unknown content length. `TestDownloadRemote` serves a temp Dockerfile through `httptest`. Status tests assert 200 body reads and 400 body-in-error text.

## State And Persistence
Uses temp directories and in-memory test servers. All state is test-scoped.

## Dependencies And Integration Points
Depends on `httptest`, `builder.DefaultDockerfileName`, and `createTestTempFile` from `utils_test.go`. It confirms `remote.go` preserves response bodies for later build processing.

## Risks And Test Signals
The suite does not cover every HTTP error mapping or DNS classification. Failures usually indicate preamble replay corruption, MIME regression, or error wrapping changes visible to API callers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/remote_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/tarsum_test.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/tarsum_test.go

## Purpose
Tests the archive-backed remotecontext source created by `FromArchive`, including root cleanup, path hashing, subdirectory hashing, and removal of files/directories from the unpacked context.

## Important APIs, Types, And Functions
Defines constants `filename` and `contents`, `TestMain` for `reexec.Init`, tests `TestCloseRootDirectory`, `TestHashFile`, `TestHashSubdir`, `TestRemoveDirectory`, and helper `makeTestArchiveContext`.

## Control Flow
Tests build temporary filesystem content, tar it with `archive.Tar`, pass the stream to `FromArchive`, and then call `Close`, `Hash`, or `Remove`. Hash tests compare fixed SHA256 strings. Removal tests cast to `modifiableContext` and assert the path disappears from the extracted root.

## State And Persistence
`FromArchive` extracts into a temporary root owned by the source; `Close` removes it. Tests require root and skip otherwise, reflecting archive ownership/permission semantics.

## Dependencies And Integration Points
Depends on `github.com/moby/go-archive`, `compression.None`, builder source interfaces, and `reexec`. It validates code in adjacent `archive.go` and file-hash behavior.

## Risks And Test Signals
Root-only requirement limits coverage in unprivileged CI. Fixed hashes make metadata changes visible. Failures indicate extraction lifecycle leaks, path normalization issues, or hash compatibility drift.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/tarsum_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/urlutil/urlutil.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/urlutil/urlutil.go

## Purpose
Classifies docker build context strings as HTTP(S) URLs or remote Git repository references using Docker-specific compatibility rules.

## Important APIs, Types, And Functions
Exports `IsURL` and `IsGitURL`. Uses lazy regexp `urlPathWithFragmentSuffix` for `.git` suffixes with optional fragments.

## Control Flow
`IsURL` checks literal `https://` or `http://` prefixes without URL parsing. `IsGitURL` returns true for HTTP(S) strings ending in `.git` plus optional fragment, and for legacy prefixes `git://`, `github.com/`, and `git@`.

## State And Persistence
No persistent state beyond the compiled lazy regexp.

## Dependencies And Integration Points
Used by Docker build context resolution before deciding whether to clone, download, or treat input as a local path. It intentionally is not a general URL validator.

## Risks And Test Signals
Rudimentary prefix checks can classify malformed strings as git or ignore valid but unsupported forms. The `github.com/` legacy path requires callers to check local existence first. `urlutil_test.go` guards known accepted and rejected patterns.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/urlutil/urlutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/urlutil/urlutil_test.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/urlutil/urlutil_test.go

## Purpose
Tests Docker build-context Git URL detection for explicit git transports, HTTP(S) `.git` URLs with fragments, legacy GitHub shorthand, and known invalid suffixes.

## Important APIs, Types, And Functions
Defines `gitUrls`, `incompleteGitUrls`, `invalidGitUrls`, and `TestIsGIT`, which exercises `IsGitURL`.

## Control Flow
The test loops accepted full Git URLs and legacy shorthand expecting true, then loops invalid HTTP(S) cases expecting false.

## State And Persistence
No state or filesystem access.

## Dependencies And Integration Points
Direct unit coverage for `urlutil.go`, indirectly protecting build context dispatch behavior.

## Risks And Test Signals
The test name uses `GIT` but only tests git classification, not `IsURL`. Coverage reflects compatibility examples rather than exhaustive URL syntax. Failures signal user-visible context-type detection changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/urlutil/urlutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/utils_test.go -->
# sources/cloud-native/moby/daemon/builder/remotecontext/utils_test.go

## Purpose
Provides a shared test helper for creating files with specific contents and permissions inside temporary build-context directories.

## Important APIs, Types, And Functions
Defines `createTestTempFile(t, dir, filename, contents string, perm os.FileMode) string`.

## Control Flow
The helper joins `dir` and `filename`, writes bytes with `os.WriteFile`, fails the test on error, and returns the created path.

## State And Persistence
Creates test-scoped filesystem files. Cleanup is owned by the temp directory from callers.

## Dependencies And Integration Points
Used by remotecontext tests such as archive hash and remote download tests.

## Risks And Test Signals
It does not create parent directories, so callers must prepare subdirectories. Because it calls `t.Fatalf`, failures stop the active test immediately.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cdi.go -->
# sources/cloud-native/moby/daemon/cdi.go

## Purpose
Registers and implements Docker's CDI device driver, allowing container device requests to inject Container Device Interface devices into OCI specs and list discovered CDI devices.

## Important APIs, Types, And Functions
Defines `cdiHandler`, `RegisterCDIDriver`, `newCDIDeviceDriver`, `createCDICache`, `injectCDIDevices`, `getErrors`, and `listDevices`.

## Control Flow
Registration resolves configured spec directory symlinks, builds a CDI cache, and registers a driver named `cdi`. Cache creation errors do not fail daemon startup; instead the registered driver returns injection errors and list warnings. Injection rejects nonzero `Count` and nonempty `Options`, then passes requested device IDs to `registry.InjectDevices`. Listing emits cache warnings and `system.DeviceInfo` IDs.

## State And Persistence
State lives in the CDI cache, which watches/parses spec directories outside this file. No specs are written. Directory symlink resolution mutates the argument slice before cache creation.

## Dependencies And Integration Points
Integrates with daemon device driver registration, runtime-spec mutation, Docker config, errdefs, system device listing, and `tags.cncf.io/container-device-interface/pkg/cdi`.

## Risks And Test Signals
Startup tolerance means CDI misconfiguration appears later at request time. Directory errors except missing paths become warnings. No direct tests in this subset; integration tests should cover invalid requests, cache errors, and device injection effects.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cdi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/changes.go -->
# sources/cloud-native/moby/daemon/changes.go

## Purpose
Implements the daemon API for returning filesystem changes for a container.

## Important APIs, Types, And Functions
Defines `(*Daemon) ContainerChanges(ctx, name) ([]archive.Change, error)`.

## Control Flow
The method records start time, resolves the container, rejects running containers on Windows, delegates diff computation to `daemon.imageService.Changes`, records the `changes` metric, and returns the change list.

## State And Persistence
No direct persistence. It reads container/image layer state through `imageService` and updates metrics.

## Dependencies And Integration Points
Integrates daemon container lookup, image service diffing, platform flag `isWindows`, archive change types, and container action metrics.

## Risks And Test Signals
Windows running-container rejection is a platform-specific behavior. Errors from container lookup or image diff pass through. Tests are outside this subset; expected signals are API diff responses and metric updates.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/changes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/checkpoint.go -->
# sources/cloud-native/moby/daemon/checkpoint.go

## Purpose
Implements create, delete, and list operations for container checkpoints backed by CRIU/runtime task support.

## Important APIs, Types, And Functions
Defines checkpoint name validation variables, helper `getCheckpointDir`, and daemon methods `CheckpointCreate`, `CheckpointDelete`, and `CheckpointList`.

## Control Flow
`getCheckpointDir` selects user-provided or container checkpoint root, checks existence, creates directories on create, and rejects missing/non-directory paths as appropriate. Create resolves the container, obtains a running task under lock, validates the checkpoint ID, creates the directory, calls `CreateCheckpoint`, cleans up on failure, and logs an event. Delete resolves and removes the checkpoint directory. List ensures the root exists and returns directory names.

## State And Persistence
Checkpoint state is persisted as directories under the container checkpoint root or requested external directory. Create uses `0700`; list creates root with `0755`; delete removes recursively.

## Dependencies And Integration Points
Uses daemon container/task APIs, CRIU/runtime checkpoint implementation, backend checkpoint option types, Docker events, and restricted name validation.

## Risks And Test Signals
`filepath.Join(checkpointDir, "")` is used for list root checks. Directory cleanup after failed checkpoint can remove partial runtime output. No direct tests here; integration should cover validation, duplicate names, external dirs, and runtime failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/checkpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster.go -->
# sources/cloud-native/moby/daemon/cluster.go

## Purpose
Defines narrow daemon-facing interfaces for swarm cluster status, events, and network management without importing the concrete cluster implementation everywhere.

## Important APIs, Types, And Functions
Defines interfaces `Cluster`, `ClusterStatus`, and `NetworkManager`. `Cluster` embeds status and network manager capabilities and adds `SendClusterEvent`.

## Control Flow
No executable control flow; this is a contract file.

## State And Persistence
No state. Implementations provide live swarm status and network mutations.

## Dependencies And Integration Points
References API network inspection types, libnetwork cluster event types, and daemon network filters. The concrete implementation is `daemon/cluster.Cluster`.

## Risks And Test Signals
Interface changes ripple into daemon wiring and mocks. No tests directly target this file; compile-time conformance across daemon packages is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/cluster.go -->
# sources/cloud-native/moby/daemon/cluster/cluster.go

## Purpose
Defines the core swarm `Cluster` object, its configuration, startup from persistent state, state-query helpers, manager action locking, shutdown behavior, and cluster event delivery.

## Important APIs, Types, And Functions
Defines constants for swarm directories, sockets, timeouts, and defaults; interfaces `NetworkSubnetsProvider`; structs `Config`, `Cluster`, and `attacher`; functions `New`, `Start`, `newNodeRunner`, status/address getters, `GetWatchStream`, `ListenClusterEvents`, `errNoManager`, `Cleanup`, `managerStats`, `detectLockedError`, `lockedManagerAction`, and `SendClusterEvent`.

## Control Flow
`New` normalizes runtime root and raft ticks, initializes channels and maps. `Start` creates state dirs, loads `docker-state.json`, starts a node runner when state exists, and waits up to 20 seconds for readiness. `newNodeRunner` validates backend compatibility, derives a local address if omitted, starts swarmkit, and notifies the backend. Manager actions take a read lock, verify active manager state, attach a timeout, and invoke a closure.

## State And Persistence
Persistent swarm state is under `<Root>/swarm`; runtime sockets live under `RuntimeRoot`. In-memory state includes `nr`, attachers, config event channel, and watch stream. Locking is explicit: `controlMutex` for lifecycle operations and `mu` for state visibility.

## Dependencies And Integration Points
Bridges daemon backends, swarmkit node/control clients, plugin controller, executor backends, libnetwork cluster events, and stack dump logging.

## Risks And Test Signals
`currentNodeState` assumes `nr` is usable while locked; callers must respect locking. Startup readiness failures are logged but may not always fail daemon startup. Quorum warnings in cleanup depend on manager stats. Tests elsewhere should cover init/join/leave, locked swarm, address derivation, and shutdown.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/cluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/configs.go -->
# sources/cloud-native/moby/daemon/cluster/configs.go

## Purpose
Implements swarm config object CRUD and listing for manager nodes.

## Important APIs, Types, And Functions
Defines methods `GetConfig`, `GetConfigs`, `CreateConfig`, `RemoveConfig`, and `UpdateConfig` on `Cluster`.

## Control Flow
Each operation runs inside `lockedManagerAction`, obtains a swarmkit control client, converts API types with `convert.ConfigFromGRPC` or `ConfigSpecToGRPC`, and calls the corresponding swarmkit RPC. List builds filters with `newListConfigsFilters` and uses the large receive limit.

## State And Persistence
Config data is persisted in swarmkit's raft store, not locally in this file. The methods read or mutate cluster state through RPCs.

## Dependencies And Integration Points
Depends on swarm backend option types, swarmkit API requests, conversion helpers, and manager availability checks from `cluster.go`.

## Risks And Test Signals
Update relies on caller-provided version index for optimistic concurrency. Remove first resolves name/ID with `getConfig`. No tests in this subset; API/integration tests should verify manager-only errors, filters, conversion, and version conflicts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/configs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/controllers/plugin/controller.go -->
# sources/cloud-native/moby/daemon/cluster/controllers/plugin/controller.go

## Purpose
Implements a swarmkit task controller for Docker plugins, treating a plugin as a singleton with desired enabled/disabled state instead of a container-like process lifecycle.

## Important APIs, Types, And Functions
Defines `Controller`, `Backend`, `NewController`, `readSpec`, lifecycle methods `Update`, `Prepare`, `Start`, `Wait`, `Shutdown`, `Terminate`, `Remove`, `Close`, helper `isNotFound`, and `convertPrivileges`.

## Control Flow
`Prepare` parses the remote reference, defaults name, checks existing plugin ownership by swarm service ID, disables before upgrade when needed, pulls new plugins with service/env options, stores `pluginID`, and acquires a plugin ref on success. `Start` reconciles enabled state. `Wait` subscribes to enable/disable/remove events and returns errors when actual state diverges or plugin is removed. `Remove` releases the ref and removes only when refcount reaches zero.

## State And Persistence
Controller state holds desired spec, service ID, plugin ID, and logger. Persistent plugin state is managed by the plugin backend; refcounting protects singleton removal across multiple tasks.

## Dependencies And Integration Points
Connects swarmkit generic runtime plugin specs, daemon plugin manager backend, registry references, plugin events, and Docker plugin API privilege structures.

## Risks And Test Signals
Registry auth is intentionally unsupported. Existing plugin name conflicts across services fail prepare. Event races are mitigated in tests with `signalWaitReady`. Tests cover prepare pull/upgrade/conflict, start state, wait cancellation/state drift/removal, and refcounted remove.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/controllers/plugin/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/controllers/plugin/controller_test.go -->
# sources/cloud-native/moby/daemon/cluster/controllers/plugin/controller_test.go

## Purpose
Validates the plugin swarm controller lifecycle using an in-memory mock backend and pubsub event stream.

## Important APIs, Types, And Functions
Defines constants for test plugin names/remotes, tests `TestPrepare`, `TestStart`, `TestWaitCancel`, `TestWaitDisabled`, `TestWaitEnabled`, and `TestRemove`, plus `newTestController`, `newMockBackend`, and `mockBackend` methods implementing `Backend`.

## Control Flow
Prepare tests assert initial pull, subsequent upgrade, and service ID conflict. Start tests toggle desired disabled/enabled state. Wait tests run `Wait` in goroutines, publish enable/disable/remove events, and use readiness hooks to avoid racing the subscription. Remove tests create two controllers sharing one plugin and assert first release does not remove while second does.

## State And Persistence
All state is in `mockBackend.p` and a pubsub publisher. Plugin refcounts are exercised through real `v2.Plugin` methods.

## Dependencies And Integration Points
Depends on daemon plugin event types, backend config structs, logrus discard logging, and pubsub.

## Risks And Test Signals
The mock `Get` ignores its name argument and returns generic errors, so not-found classification is not deeply tested. Timeouts guard goroutine/event regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/controllers/plugin/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/config.go -->
# sources/cloud-native/moby/daemon/cluster/convert/config.go

## Purpose
Converts swarmkit config objects and references between gRPC/raft-store representation and Docker API types.

## Important APIs, Types, And Functions
Exports `ConfigFromGRPC`, `ConfigSpecToGRPC`, and `ConfigReferencesFromGRPC`.

## Control Flow
`ConfigFromGRPC` copies ID, annotations, data, templating driver, version, and timestamps. `ConfigSpecToGRPC` builds swarmkit annotations, data, and optional templating driver. `ConfigReferencesFromGRPC` converts IDs/names and file targets when present.

## State And Persistence
No state. It translates objects persisted by swarmkit.

## Dependencies And Integration Points
Used by cluster config CRUD and service/container conversion. Depends on gogo timestamp conversion and shared `annotationsFromGRPC`.

## Risks And Test Signals
`ConfigReferencesFromGRPC` ignores non-file targets in this exported helper, while `container.go` has fuller runtime target handling. Tests in service conversion cover config references indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/container.go -->
# sources/cloud-native/moby/daemon/cluster/convert/container.go

## Purpose
Converts Docker swarm container specs between Docker API types and swarmkit gRPC types, including DNS, privileges, mounts, secrets/configs, healthchecks, resources-adjacent fields, and platform isolation.

## Important APIs, Types, And Functions
Key functions include `containerSpecFromGRPC`, `containerToGRPC`, `initFromGRPC`, `initToGRPC`, secret/config reference converters, credential spec converters, healthcheck converters, `IsolationFromGRPC`, `isolationToGRPC`, ulimit converters, and tmpfs option JSON shims.

## Control Flow
Inbound conversion copies scalar fields, best-effort parses DNS IPs, expands privileges, converts mount option substructures, durations, and healthcheck. Outbound conversion validates config reference oneofs, credential spec exclusivity, enum values for mount type/propagation, and serializes tmpfs options into swarmkit's string field.

## State And Persistence
No local state. It preserves API-visible configuration crossing the Docker API/swarmkit raft boundary. Tmpfs options are persisted as JSON strings in swarmkit.

## Dependencies And Integration Points
Used by service/task conversion and executor container creation. Depends on Docker container/mount/swarm types, swarmkit API enums, netip, gogo wrappers, and logging for unsupported inbound targets.

## Risks And Test Signals
Invalid inbound IP strings become zero values because parsing errors are ignored after storage. Outbound validation prevents ambiguous config and credential specs. Tests cover tmpfs JSON conversion; service tests cover credential specs, config targets, isolation, and volume subpath.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/container_test.go -->
# sources/cloud-native/moby/daemon/cluster/convert/container_test.go

## Purpose
Tests the tmpfs options compatibility shim between Docker API's structured `[][]string` representation and swarmkit's string field.

## Important APIs, Types, And Functions
Tests unexported `tmpfsOptionsToGRPC` and `tmpfsOptionsFromGRPC`.

## Control Flow
One test marshals options such as `noexec` and `uid=12345` to a compact JSON string. The other unmarshals that string and deep-compares the original structure.

## State And Persistence
No state. The tested representation is what may be stored in swarmkit service specs.

## Dependencies And Integration Points
Directly covers helper behavior used by container mount conversion.

## Risks And Test Signals
Does not cover malformed JSON; production intentionally returns an empty value on unmarshal errors. Failures indicate backward-compatibility changes in stored tmpfs option encoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/container_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/netextra/extra.pb.go -->
# sources/cloud-native/moby/daemon/cluster/convert/netextra/extra.pb.go

## Purpose
Generated gogo/protobuf implementation for network inspection extension messages carrying options and IPAM status data between Docker and swarmkit.

## Important APIs, Types, And Functions
Defines generated message types `GetNetworkExtraOptions`, `Extra`, and `IPAMStatus`, getters, `Reset/String/ProtoMessage/Descriptor`, marshal/unmarshal/size helpers, `skipExtra`, and generated error variables.

## Control Flow
Marshal methods write fields in reverse into sized buffers. Unmarshal methods parse protobuf wire types, append repeated `IPAMStatus` entries, copy subnet bytes, skip unknown fields for forward compatibility, and detect overflow/negative length/unexpected EOF.

## State And Persistence
No process state, but this file defines the wire format persisted or transported inside protobuf `Any` values. `IPAMStatus.Subnet` stores `netip.Prefix` binary bytes as defined by `network_extra.go`.

## Dependencies And Integration Points
Generated from `extra.proto`; used by `netextra.OptionsFrom`, `StatusFrom`, and `MarshalStatus`. Registered type names are under `docker.engine.netextra`.

## Risks And Test Signals
Manual edits would be overwritten by protoc. Compatibility depends on stable field numbers. There are no direct tests in this subset; conversion tests should exercise `Any` marshaling and unknown-type behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/netextra/extra.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/netextra/extra.proto -->
# sources/cloud-native/moby/daemon/cluster/convert/netextra/extra.proto

## Purpose
Declares the protobuf schema for Docker network extra request options and status payloads.

## Important APIs, Types, And Functions
Defines package `docker.engine.netextra`, Go package `netextra`, messages `GetNetworkExtraOptions`, `Extra`, and `IPAMStatus`, and a `go:generate` path in the companion Go file.

## Control Flow
No executable control flow. Field numbers assign `WithIPAMStatus = 1`, repeated `IPAMStatus = 1`, and IPAM status fields `Subnet = 1`, `IPsInUse = 2`, `DynamicIPsAvailable = 3`.

## State And Persistence
This schema is the persistent/wire contract for network extra `Any` payloads. `Subnet` is documented as a binary-marshaled `netip.Prefix`.

## Dependencies And Integration Points
Source for `extra.pb.go` and consumed by `network_extra.go`.

## Risks And Test Signals
Changing field numbers or package/type names breaks compatibility with stored or transported `Any` values. Regeneration consistency is the main validation signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/netextra/extra.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/netextra/network_extra.go -->
# sources/cloud-native/moby/daemon/cluster/convert/netextra/network_extra.go

## Purpose
Converts Docker network extra options and status between API structs and protobuf `Any` messages, with forward-compatible unknown-type handling.

## Important APIs, Types, And Functions
Exports `OptionsFrom`, `StatusFrom`, and `MarshalStatus`.

## Control Flow
`OptionsFrom` returns zero options for empty or unknown type URLs, otherwise unmarshals `GetNetworkExtraOptions`. `StatusFrom` ignores nil or unknown `Any`, unmarshals `Extra`, converts binary subnet prefixes to `netip.Prefix`, and fills `network.Status.IPAM.Subnets`. `MarshalStatus` converts each subnet prefix to binary and marshals an `Extra` message into `Any`.

## State And Persistence
No local state. It serializes IPAM status maps into protobuf payloads; map iteration means marshaled order is not deterministic unless the protobuf layer enforces it.

## Dependencies And Integration Points
Used by network inspection conversion in `network.go`. Depends on gogo `types.Any`, generated netextra messages, `netip`, and Docker network status types.

## Risks And Test Signals
Invalid subnet binary data returns errors on inspect conversion. Unknown message types are silently ignored for compatibility. No direct tests here; network inspect tests should include status payloads.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/netextra/network_extra.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/network.go -->
# sources/cloud-native/moby/daemon/cluster/convert/network.go

## Purpose
Converts swarmkit network, endpoint, IPAM, port, and filter representations to Docker API/network types and back for swarm-scoped networks.

## Important APIs, Types, And Functions
Key functions include `networkAttachmentFromGRPC`, `networkFromGRPC`, `ipamFromGRPC`, `endpointSpecFromGRPC`, `endpointFromGRPC`, `swarmPortConfigToAPIPortConfig`, `BasicNetworkFromGRPC`, `NetworkInspectFromGRPC`, `BasicNetworkCreateToGRPC`, `IsIngressNetwork`, and `FilterNetwork` methods.

## Control Flow
Inbound conversion copies metadata, annotations, drivers, endpoint ports/VIPs, IPAM configs, config-from references, and status extras. IP/CIDR parsing is best-effort for values already stored in swarmkit. Outbound network create conversion defaults IPAM driver to `default`, unmapped/masks prefixes, and includes config-from and IPv6 only when provided.

## State And Persistence
No local state. It translates swarmkit raft objects into API responses and create requests into raft specs.

## Dependencies And Integration Points
Used by cluster network APIs, filters, and task/service conversion. Integrates `netextra.StatusFrom`, libnetwork swarm scope, netip utility wrappers, and Docker network filters.

## Risks And Test Signals
Legacy ingress detection accepts label `com.docker.swarm.internal` plus name `ingress`. Invalid stored IPs become zero values. Test coverage here only checks `CreatedAt`; broader network API tests should cover IPAM/status/ingress/filter behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/network_test.go -->
# sources/cloud-native/moby/daemon/cluster/convert/network_test.go

## Purpose
Tests that `BasicNetworkFromGRPC` preserves the swarmkit network creation timestamp in the Docker API network type.

## Important APIs, Types, And Functions
Defines `TestNetworkConvertBasicNetworkFromGRPCCreatedAt`.

## Control Flow
The test parses a fixed timestamp, converts it to protobuf timestamp form, embeds it in a minimal `swarmapi.Network`, converts with `BasicNetworkFromGRPC`, and compares `Created`.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Covers timestamp conversion in `network.go` using gogo protobuf timestamp helpers.

## Risks And Test Signals
Coverage is narrow and does not exercise IPAM, status extras, ports, or create conversion. Failure indicates metadata timestamp drift in network inspect/list output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/network_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/node.go -->
# sources/cloud-native/moby/daemon/cluster/convert/node.go

## Purpose
Converts swarmkit nodes and node specs to Docker API swarm node types.

## Important APIs, Types, And Functions
Exports `NodeFromGRPC` and `NodeSpecToGRPC`.

## Control Flow
`NodeFromGRPC` copies ID, role, availability, status, metadata timestamps, annotations, platform/resources/generic resources, engine labels/plugins, TLS info, CSI info including topology, and manager status. `NodeSpecToGRPC` converts annotations and validates role/availability enum strings before constructing a swarmkit `NodeSpec`.

## State And Persistence
No local state. Converts data persisted in swarmkit raft.

## Dependencies And Integration Points
Used by node API handlers. Depends on shared `GenericResourcesFromGRPC`, annotations conversion, gogo timestamps, and swarmkit enum naming.

## Risks And Test Signals
Outbound invalid role or availability returns errors. Inbound enum strings are lower-cased, so unknown enum names can leak as API strings. `node_test.go` covers CSI info conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/node_test.go -->
# sources/cloud-native/moby/daemon/cluster/convert/node_test.go

## Purpose
Tests conversion of swarmkit `NodeCSIInfo` entries into Docker API `NodeCSIInfo` structures.

## Important APIs, Types, And Functions
Defines `TestNodeCSIInfoFromGRPC`, targeting `NodeFromGRPC`.

## Control Flow
The test builds a swarmkit node with two CSI entries, one with accessible topology, converts it, and deep-compares the resulting Docker API slice.

## State And Persistence
No state.

## Dependencies And Integration Points
Direct coverage for CSI node description conversion used by `docker node inspect`.

## Risks And Test Signals
Does not test nil entries, manager status, resources, or spec conversion. Failure indicates loss of CSI plugin/node/topology fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/node_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/pluginadapter.go -->
# sources/cloud-native/moby/daemon/cluster/convert/pluginadapter.go

## Purpose
Adapts Docker's plugin getter interfaces to swarmkit's plugin getter/plugin interfaces while preserving optional address support.

## Important APIs, Types, And Functions
Exports `SwarmPluginGetter`. Defines `pluginGetter`, `swarmPlugin`, `addrPlugin`, `adaptPluginForSwarm`, and methods `Get` and `GetAllManagedPluginsByCap`.

## Control Flow
`Get` calls the daemon plugin getter with lookup mode and wraps the returned compatible plugin. `GetAllManagedPluginsByCap` wraps every managed plugin. `adaptPluginForSwarm` chooses `addrPlugin` if the plugin also exposes `PluginAddr`; otherwise it uses `swarmPlugin`.

## State And Persistence
No state beyond holding the delegated plugin getter.

## Dependencies And Integration Points
Used when constructing swarmkit components that need plugin access. Bridges `pkg/plugingetter` and `swarmkit/node/plugin`.

## Risks And Test Signals
Compile-time interface assertions verify adapter shape. No direct tests; integration failures would appear in swarm networking/volume plugin discovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/pluginadapter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/secret.go -->
# sources/cloud-native/moby/daemon/cluster/convert/secret.go

## Purpose
Converts swarmkit secret objects, specs, and file references to Docker API swarm secret types.

## Important APIs, Types, And Functions
Exports `SecretFromGRPC`, `SecretSpecToGRPC`, and `SecretReferencesFromGRPC`.

## Control Flow
`SecretFromGRPC` copies ID, annotations, data, driver, templating driver, version, and timestamps. `SecretSpecToGRPC` maps annotations, data, driver, and optional templating. Reference conversion copies ID/name and file target fields.

## State And Persistence
No local state. Secret data is persisted in swarmkit and passed through by these converters.

## Dependencies And Integration Points
Used by swarm secret APIs and service/container conversion. Depends on driver helpers from `service.go` and gogo timestamps.

## Risks And Test Signals
The exported reference converter only handles file targets. No tests in this subset directly target secret conversion; service/executor paths indirectly depend on it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/secret.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/service.go -->
# sources/cloud-native/moby/daemon/cluster/convert/service.go

## Purpose
Converts Docker service specs, services, task specs, resources, update policies, runtimes, modes, and supporting structures between Docker API and swarmkit gRPC representations.

## Important APIs, Types, And Functions
Exports `ErrUnsupportedRuntime`, `ErrMismatchedRuntime`, `ServiceFromGRPC`, `ServiceSpecToGRPC`, `GenericResourcesFromGRPC`, and `GenericResourcesToGRPC`. Internal helpers include `serviceSpecFromGRPC`, `resourcesFromGRPC`, `resourcesToGRPC`, restart/update/placement/driver converters, `networkAttachmentSpecFromGRPC`, and `taskSpecFromGRPC`.

## Control Flow
Inbound service conversion translates current/previous specs, endpoint, metadata, job status, and update status. Spec conversion handles container, plugin generic runtime, and rejects unknown generic runtime. Outbound conversion defaults unnamed services, validates runtime/spec consistency, forces plugin services to global, serializes plugin specs into protobuf `Any`, validates update/restart/mode combinations, defaults replicated and job values, and rejects unsupported network attachment runtime creation.

## State And Persistence
No local state. It defines how API service specs are persisted in swarmkit's raft store, including plugin runtime payloads and the legacy PidsLimit-in-container workaround.

## Dependencies And Integration Points
Central to service create/update/list/inspect and task conversion. Depends on container conversion, network conversion, runtime plugin proto helpers, names generator, genericresource helpers, and swarmkit enums.

## Risks And Test Signals
Outbound validation is strict for runtime mismatch, memory swap without memory limit, update enum values, endpoint modes, and multiple service modes. Inbound conversion remains compatible with deprecated `ServiceSpec.Networks`. `service_test.go` covers runtime, isolation, credential specs, config targets, network attachment task conversion, and volume subpath.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/service_test.go -->
# sources/cloud-native/moby/daemon/cluster/convert/service_test.go

## Purpose
Exercises service and task conversion edge cases that are user-visible in Docker swarm APIs.

## Important APIs, Types, And Functions
Tests `ServiceFromGRPC`, `ServiceSpecToGRPC`, `taskSpecFromGRPC`, isolation conversion, credential spec conversion, config reference conversion, and volume mount subpath conversion.

## Control Flow
Cases cover container runtime inbound/outbound, plugin generic runtime inbound/outbound, unsupported custom runtime, isolation mapping both directions, credential spec exclusivity and oneof mapping, unsupported network attachment service creation, runtime/spec mismatch, inbound network attachment task specs, config file/runtime targets both directions, invalid config target combinations, and `VolumeOptions.Subpath`.

## State And Persistence
No persistent state; all objects are in-memory API structs.

## Dependencies And Integration Points
This is the main regression suite for `service.go` and parts of `container.go`.

## Risks And Test Signals
The tests intentionally focus on tricky compatibility surfaces rather than all fields. Failures indicate API/raft conversion drift likely to affect service create/update/inspect behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/swarm.go -->
# sources/cloud-native/moby/daemon/cluster/convert/swarm.go

## Purpose
Converts swarmkit cluster specs and cluster state to Docker API swarm objects and merges API swarm spec updates into existing swarmkit specs.

## Important APIs, Types, And Functions
Exports `SwarmFromGRPC`, `SwarmSpecToGRPC`, and `MergeSwarmSpecToGRPC`.

## Control Flow
`SwarmFromGRPC` copies cluster info, orchestration, raft, encryption, CA config minus signing cert/key, TLS trust root/issuer, default address pools, VXLAN port, join tokens, dispatcher heartbeat, external CAs, metadata, and annotations. `MergeSwarmSpecToGRPC` only overwrites fields when API values are nonzero/non-nil except force rotate and autolock, validates external CA protocols, and propagates signing CA material for update requests.

## State And Persistence
No local state. It controls how swarm spec updates preserve existing raft state and which sensitive CA fields are redacted from read responses.

## Dependencies And Integration Points
Used by swarm init/update/inspect flows. Depends on swarmkit CA issuer parsing, gogo durations, netip prefix parsing, and shared annotation conversion.

## Risks And Test Signals
Zero-value merge semantics mean users cannot clear some fields through this path unless represented by pointers. External CA protocol validation can reject updates. Tests are outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/swarm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/task.go -->
# sources/cloud-native/moby/daemon/cluster/convert/task.go

## Purpose
Converts swarmkit tasks to Docker API swarm task objects, including status, networks, volumes, generic resources, job iteration, and port status.

## Important APIs, Types, And Functions
Exports `TaskFromGRPC`.

## Control Flow
`TaskFromGRPC` first converts embedded task spec via `taskSpecFromGRPC`, then copies IDs, annotations, service/slot/node, status strings, desired state, generic resources, metadata timestamps, container status, network attachments, job iteration, volume attachments, and optional published port status.

## State And Persistence
No local state. It reads swarmkit task state that is stored and updated by swarmkit.

## Dependencies And Integration Points
Used by task list/inspect APIs and service logs/selectors. Depends on `networkAttachmentFromGRPC`, `GenericResourcesFromGRPC`, and gogo timestamp conversion.

## Risks And Test Signals
Enum conversion lower-cases swarmkit names; unknown values may produce unexpected API strings. `taskSpecFromGRPC` errors propagate for malformed plugin payloads. Service tests cover network attachment task specs; broader task API tests should cover status and ports.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/task.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/volume.go -->
# sources/cloud-native/moby/daemon/cluster/convert/volume.go

## Purpose
Converts swarmkit cluster volume specs/status into Docker volume API types and Docker volume create requests into swarmkit volume specs.

## Important APIs, Types, And Functions
Exports `VolumeFromGRPC` and `VolumeCreateToGRPC`. Internal helpers include `volumeSpecToGRPC`, `volumeInfoFromGRPC`, `volumePublishStatusFromGRPC`, `accessModeFromGRPC`, `volumeSecretsFromGRPC`, `topologyRequirementFromGRPC`, `topologyFromGRPC`, `capacityRangeFromGRPC`, and `volumeAvailabilityFromGRPC`.

## Control Flow
Inbound conversion maps cluster spec fields, publish status, volume info, metadata, driver, labels, name, options, and global scope. Outbound conversion maps access scope/sharing/type, secrets, topology requirements, capacity range, availability, annotations, and driver/options. Nil cluster specs create a minimal swarmkit spec.

## State And Persistence
No local state. It defines conversion for cluster volume objects persisted by swarmkit and shown through Docker volume APIs.

## Dependencies And Integration Points
Used by swarm volume create/list/inspect flows and executor volume attachments. Depends on Docker API volume types and swarmkit volume enums.

## Risks And Test Signals
Default/unknown inbound availability maps to `drain`, a conservative fallback. `VolumeCreateToGRPC` assumes non-nil request for name/labels/driver after optional cluster spec handling. Tests cover topology, capacity, availability, access modes, and create conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/volume_test.go -->
# sources/cloud-native/moby/daemon/cluster/convert/volume_test.go

## Purpose
Tests cluster volume conversion helpers for topology, capacity, availability, access modes, and create request mapping.

## Important APIs, Types, And Functions
Targets `topologyFromGRPC`, `capacityRangeFromGRPC`, `volumeAvailabilityFromGRPC`, `accessModeFromGRPC`, and `VolumeCreateToGRPC`.

## Control Flow
Tests verify nil and populated topology, nil/zero/nonzero capacity, availability enum mapping, block and mount access mode conversion, and a full create request with driver opts, labels, group, access mode, secrets, topology, and capacity.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Directly covers `volume.go`, protecting API-to-swarmkit conversion for cluster volumes.

## Risks And Test Signals
The suite does not cover `VolumeFromGRPC` end-to-end or publish status. Failures point to swarm volume API compatibility regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/convert/volume_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/errors.go -->
# sources/cloud-native/moby/daemon/cluster/errors.go

## Purpose
Defines typed swarm errors that map to Docker API error categories such as forbidden, unavailable, invalid parameter, unauthorized, and conflict.

## Important APIs, Types, And Functions
Defines swarm error constants `errNoSwarm`, `errSwarmExists`, `errSwarmJoinTimeoutReached`, `errSwarmLocked`, `errSwarmCertificatesExpired`, and `errSwarmNotManager`. Defines types `notAllowedError`, `notAvailableError`, `configError`, `invalidUnlockKey`, and `notLockedError` with marker methods.

## Control Flow
No complex control flow. Each error type implements `Error` and a marker method consumed by Docker error classification.

## State And Persistence
No state.

## Dependencies And Integration Points
Used across cluster lifecycle and manager-only APIs, then classified by API error handling through marker interfaces.

## Risks And Test Signals
Changing strings changes user-facing API/CLI messages; changing marker methods changes HTTP status mapping. Compile-time and API tests elsewhere provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/backend.go -->
# sources/cloud-native/moby/daemon/cluster/executor/backend.go

## Purpose
Defines the daemon backend interfaces required by the swarm executor to manage networks, containers, images, volumes, plugins, events, attachments, and cluster membership.

## Important APIs, Types, And Functions
Defines `Backend`, `VolumeBackend`, and `ImageBackend` interfaces. Methods cover managed network lifecycle, ingress setup/release, managed container lifecycle/logs/wait/remove, service binding, dependency/secrets/config refs, system info, event subscriptions, attachment operations, plugin access, compatibility, and image pull/lookup.

## Control Flow
No implementation; this is an interface boundary.

## State And Persistence
No state. Implementations mutate daemon, container, network, image, and volume state.

## Dependencies And Integration Points
Bridges swarmkit agent controllers to the Docker daemon backend. Referenced by container adapters and cluster construction.

## Risks And Test Signals
Interface churn has broad compile impact. Because this is a large boundary, mocks and daemon implementations must stay synchronized. Tests in executor/container exercise selected methods.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/adapter.go -->
# sources/cloud-native/moby/daemon/cluster/executor/container/adapter.go

## Purpose
Implements the swarm executor's container adapter, translating swarmkit task operations into Docker daemon container, image, network, volume, event, and log backend calls.

## Important APIs, Types, And Functions
Defines `containerAdapter`, `newContainerAdapter`, and methods `pullImage`, `waitNodeAttachments`, `createNetworks`, `removeNetworks`, `networkAttach`, `waitForDetach`, `create`, `checkMounts`, `start`, `inspect`, `events`, `wait`, `shutdown`, `terminate`, `remove`, `createVolumes`, `waitClusterVolumes`, `activateServiceBinding`, `deactivateServiceBinding`, and `logs`.

## Control Flow
Image pull skips digest IDs and already-present canonical references, decodes registry auth, streams daemon pull JSON, and rate-limits progress logs. Network setup creates managed networks, ignores already-existing/predefined errors, waits for overlay node attachments by polling the daemon attachment store, and updates/detaches unmanaged attachments. Container creation normalizes default network mode, creates the container, stores dependencies, secrets/config refs, and service config. Runtime methods start, stop, kill, remove, wait, inspect, stream events, create plugin volumes, wait for cluster volume paths, and translate log subscription options.

## State And Persistence
Adapter holds backends, task-derived `containerConfig`, and dependency getter. Persistent effects are delegated to daemon state: images, containers, networks, volumes, service binding, and attachment stores.

## Dependencies And Integration Points
Central executor bridge among swarmkit agent `exec`, daemon backend interfaces, image backend, volume backend, libnetwork, container API, registry auth, and Docker event/log APIs.

## Risks And Test Signals
`waitClusterVolumes` busy-spins until context cancellation or path availability. Bind mount validation differs from normal container API by requiring existing host paths. Pull progress depends on daemon JSON stream format. `adapter_test.go` covers overlay attachment waiting; broader executor tests should cover pull/create/log/shutdown paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/adapter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/adapter_test.go -->
# sources/cloud-native/moby/daemon/cluster/executor/container/adapter_test.go

## Purpose
Tests that `containerAdapter.waitNodeAttachments` blocks until required overlay network node attachments are present while ignoring non-overlay networks.

## Important APIs, Types, And Functions
Defines `TestWaitNodeAttachment`, using a bare `daemon.Daemon`, its attachment store, a hand-built `containerConfig`, and `containerAdapter.waitNodeAttachments`.

## Control Flow
The test seeds one overlay attachment, starts `waitNodeAttachments` in a goroutine for two overlay networks and one bridge network, verifies it does not finish early, then adds the second overlay attachment and verifies the wait completes without error.

## State And Persistence
State is in the daemon attachment store and goroutine-local variables. No persistent filesystem state.

## Dependencies And Integration Points
Directly covers adapter behavior that coordinates swarm overlay network readiness with daemon attachment state.

## Risks And Test Signals
The test relies on sleeps around the 100 ms polling interval, so very slow environments could be flaky. It currently uses `t.Context()` and does not explicitly cancel before normal completion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/adapter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/attachment.go -->
# sources/cloud-native/moby/daemon/cluster/executor/container/attachment.go

## Purpose
Implements a swarmkit controller for network attachment tasks associated with unmanaged containers, delegating concrete network operations to `containerAdapter`.

## Important APIs, Types, And Functions
Defines `networkAttacherController`, `newNetworkAttacherController`, and lifecycle methods `Update`, `Prepare`, `Start`, `Wait`, `Shutdown`, `Terminate`, `Remove`, and `Close`.

## Control Flow
Construction creates a container adapter. `Prepare` ensures task networks exist. `Start` calls backend attachment update through the adapter. `Wait` waits until detachment using a child context. `Remove` attempts network cleanup when the task is gone. Other lifecycle methods are no-ops.

## State And Persistence
Controller holds backend, task, adapter, and an unused `closed` channel. Persistent effects are delegated to managed network creation/removal and attachment state updates.

## Dependencies And Integration Points
Used by swarmkit agent task execution for network attachment runtime tasks. Depends on executor backends, image/volume backends for adapter construction, and swarmkit `exec.DependencyGetter`.

## Risks And Test Signals
The `closed` channel is allocated but not used here. Network cleanup can be skipped when active endpoints remain via adapter logic. Coverage is indirect through executor/network attachment tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/attachment.go -->
