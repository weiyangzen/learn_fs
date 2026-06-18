# Group Research: subset-b-000211

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/client.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/client.go

This file defines the `NydusdClient` interface and its Unix-domain-socket HTTP implementation for controlling a running `nydusd`. It centralizes daemon API paths for daemon info, mount/umount, blob binding, metrics, failover takeover/sendfd/start/exit, runtime config updates, and v2 blob cache operations.

Important APIs include `NewNydusClient`, `GetDaemonInfo`, `Mount`, `Umount`, `BindBlob`, `UnbindBlob`, `GetFsMetrics`, `GetInflightMetrics`, `GetCacheMetrics`, `UpdateConfig`, `TakeOver`, `SendFd`, `Start`, and `Exit`. `buildTransport` rewires HTTP dialing to a Unix socket, while `request` builds requests, attaches JSON content type for bodies, treats 200/204 as success, and decodes nydusd error bodies through `types.ErrorMessage`.

State is mostly external: the client stores an `http.Client`, while daemon lifecycle state remains in `nydusd`. `WaitUntilSocketExisted` polls for a socket file and validates socket mode before client creation. Integration points include `pkg/daemon/daemon.go`, manager recovery/upgrade, metrics collection, fscache blob lifecycle, and auth hot reload. Risks include strict assumptions about JSON error bodies, the `decode` helper passing `&v`, socket residuals from dead daemons, and retry behavior around zombie detection. Unit tests cover daemon info, Unix socket transport, and `UpdateConfig`; mount, metrics, blob, and failover endpoints are integration-level.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/client_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/client_test.go

This test file validates the daemon HTTP client against an in-process HTTP server bound to a Unix socket. `prepareNydusServer` creates a temporary socket, attaches it to `httptest.NewUnstartedServer`, and returns a JSON `types.DaemonInfo` payload with a known build-time version and `RUNNING` state.

`TestNydusClient_CheckStatus` verifies that `NewNydusClient` can talk over the Unix socket, decode daemon info, map the state through `DaemonState()`, and preserve build metadata. `TestUpdateConfig` exercises `PUT /api/v1/config?id=...` for shared and dedicated daemon IDs, decodes the JSON request body, and checks that server-side error payloads are surfaced in the returned error.

The tests provide useful signals for transport construction, query parameter propagation, request body marshaling, success status handling, and error parsing. They do not cover socket wait logic, request timeout behavior, mount/umount/blob endpoints, metrics decoding, or failover APIs. The mocked server replies generically to all paths in the first helper, so path-specific behavior is mainly asserted in the config update test. Persistence is limited to temporary sockets and directories; no daemon process is spawned.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/command/command.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/command/command.go

This file implements a reflection-based command-line builder for launching `nydusd`. `DaemonCommand` declares supported subcommand, parameter, and flag fields using struct tags. `BuildCommand` applies option functions, scans the tagged fields in struct order, appends non-zero parameters as `--name value`, appends boolean flags when true, and prepends the subcommand.

Important option helpers include `WithMode`, `WithFscacheDriver`, `WithFscacheThreads`, `WithThreadNum`, `WithConfig`, `WithBootstrap`, `WithMountpoint`, `WithAPISock`, `WithLogFile`, `WithLogLevel`, `WithLogRotationSize`, `WithSupervisor`, `WithID`, `WithUpgrade`, `WithBackendSource`, `WithPrefetchFiles`, and `WithFailoverPolicy`. The builder is consumed by `pkg/manager/daemon_adaptor.go` to translate daemon state and configuration into an `exec.Cmd`.

The main dependency is Go reflection plus `strconv` for numeric string conversion. There is no persistence; state lives only in the temporary `DaemonCommand`. Risks are tag-sensitive: field order defines argument order, zero values silently omit parameters, non-bool `flag` tags fail at runtime, and invalid tag types are runtime errors. The unit test checks expected ordering for singleton fscache command construction with and without `--upgrade`, but not every option or error path.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/command/command.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/command/command_builder_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/command/command_builder_test.go

This test file verifies the command builder's observable argument ordering for a representative fscache singleton daemon command. `TestBuildCommand` constructs option slices using `WithMode`, `WithFscacheDriver`, `WithFscacheThreads`, `WithAPISock`, and optionally `WithUpgrade`, then joins the returned args to compare exact output strings.

The benchmark repeatedly calls `BuildCommand` with the same option set and asserts no error. Its comments record historical timings for the reflection implementation versus a baseline, making performance awareness explicit even though the benchmark is not a correctness gate.

The tests are useful because command-line ordering is field-order dependent in `DaemonCommand`; a refactor that reorders fields can change process launch behavior and fail this test. Coverage is narrow: it does not exercise fuse mode, config/bootstrap/mountpoint arguments, log options, supervisor/id coupling, backend source, prefetch files, failover policy, zero-value omission for numeric fields, or invalid tag handling. There is no filesystem or process state, only in-memory option application.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/command/command_builder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/config.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/config.go

This file provides `NewDaemonOpt` option constructors that populate the persistent and runtime fields of a `Daemon`. The options set socket directory, initial reference count, log directory, stdout logging, log level, log rotation size, config directory, mountpoint, nydusd thread count, filesystem driver, failover policy, and daemon mode.

State effects are direct mutations of `Daemon.States` or `Daemon.ref`. `WithSocketDir` and `WithConfigDir` create per-daemon directories named by `d.ID()`. `WithSocketDir` sets `APISocket` to `<dir>/<daemon-id>/api.sock`, while `WithConfigDir` sets `ConfigDir` to `<dir>/<daemon-id>`. `WithLogDir` creates the root log directory and stores a per-daemon log subpath, but does not create that subdirectory itself. `WithLogLevel` falls back to `constant.DefaultLogLevel` for an empty input.

These options are used by filesystem daemon creation and manager recovery paths. Dependencies include global `config` daemon mode types, the default log-level constant, and OS directory creation. Risks include partial directory creation if a later option fails, assumptions that `d.ID()` is already set, and path package mixing (`path` and `filepath`). There are no direct tests for these options; behavior is indirectly covered by daemon creation and manager command-building tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/daemon.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/daemon.go

This is the core runtime model for a `nydusd` process. `ConfigState` captures persisted daemon identity and launch state: ID, PID, API socket, mode, filesystem driver, logs, mountpoint, supervisor path, thread count, failover policy, and config directory. `Daemon` adds synchronization, RAFS instance cache, cached API client, supervisor handle, daemon config, startup CPU measurement, version, reference count, and cached daemon state.

Important control flow covers reference management, config file paths, state polling, shared RAFS mount/umount, fscache blob bind/unbind plus kernel EROFS mount, failover state transfer through `SendFd`/`TakeOver`/`Start`, auth config hot reload, client reset, process termination/wait, vestige cleanup, RAFS cloning/recovery, and daemon construction. Shared mode paths call nydusd APIs after reloading per-instance config; fscache additionally creates work dirs, records fscache annotations, mounts EROFS, and removes bootstrap cache blobs on unmount.

Persistence is split between `ConfigState` in the manager store, per-daemon/per-instance config files, RAFS cache membership, and supervisor state files. Integration points include daemon client, `daemonconfig`, auth keychains, metrics collectors, RAFS cache, EROFS utilities, mount utilities, and manager recovery. Risks include complex reference-count semantics, concurrent RAFS cache updates, stale sockets, partial cleanup failures, fscache annotation dependence, and broad integration behavior not unit covered. Tests focus mainly on `UpdateAuthConfig`; most lifecycle paths require real nydusd or mocked managers.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/daemon_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/daemon_test.go

This test file targets `Daemon.UpdateAuthConfig`. `TestMain` initializes global snapshotter configuration so daemon config serialization can run safely. `minimalFuseConfig` creates a small valid `daemonconfig.FuseDaemonConfig` using a registry backend.

`TestUpdateAuthConfig` covers three cases: shared daemon basic auth updates a per-snapshot config and calls `PUT /api/v1/config?id=/snap-1`; dedicated daemon basic auth updates root config and calls `id=/`; bearer-token style credentials update disk only and skip the API because runtime token reload is not supported. The test pre-creates config files, starts a Unix-socket mock API server, injects a `NydusdClient` into the daemon to avoid socket wait, then validates both API body and on-disk config content.

The test is valuable because auth update spans file persistence and live daemon state. It confirms API ID selection based on daemon mode and validates basic-auth base64 storage. It does not cover load failures, dump failures, API error propagation, fscache config shape, nil clients, or concurrent updates. Temporary directories and sockets are the only external state.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/daemon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/idgen.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/idgen.go

This file contains a single helper, `newID`, which returns `xid.New().String()`. It is used by `NewDaemon` to assign each daemon a unique stable identifier before daemon options derive socket, config, and log paths from the ID.

The dependency is `github.com/rs/xid`, which produces compact globally unique identifiers without needing an external sequence store. There is no local persistence in this file, but the generated ID becomes part of persisted `daemon.ConfigState`, per-daemon config directories, API socket directories, log paths, supervisor names, manager cache keys, and daemon-image metrics labels.

The main risk is not algorithmic uniqueness but lifecycle coupling: options such as `WithSocketDir` and `WithConfigDir` assume the ID already exists, and manager recovery overwrites `Daemon.States` from stored state after constructing a placeholder daemon. There are no direct tests for ID generation. Indirect coverage comes from daemon creation paths and manager cache tests that use explicit IDs.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/idgen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/types/types.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/types/types.go

This file defines JSON-facing data contracts shared by the daemon HTTP client, daemon state logic, and metrics collectors. `BuildTimeInfo` captures version metadata. `DaemonState` enumerates `UNKNOWN`, `INIT`, `READY`, `RUNNING`, `DIED`, and `DESTROYED`. `DaemonInfo` exposes helper methods for state and version. `ErrorMessage` models nydusd API errors.

`MountRequest` and `NewMountRequest` define the request body for mounting RAFS instances, always using `fs_type: "rafs"`. `FsMetrics`, `InflightMetrics`, and `CacheMetrics` mirror nydusd metrics JSON and are consumed by metrics collectors and readiness logic. Cache metrics include hit counts, prefetch state, backend buffering, and underlying cache files.

The file has no active control flow beyond trivial helpers, but it is an important integration boundary: field tags must match nydusd's API schema, and slices such as `FopHits`, `FopErrors`, `BlockCountRead`, and `ReadLatencyDist` are indexed by metrics code. Risks include schema drift, missing bounds checks before metrics indexing, and typo propagation in serialized fields. Tests indirectly validate daemon info decoding and some metrics consumers, but the full schema is not round-trip tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/daemon/types/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/encryption/encryption.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/encryption/encryption.go

This file wraps containerd/imgcrypt and ocicrypt behavior to encrypt and decrypt Nydus bootstrap layers stored in a containerd content store. Internal helpers `encryptLayer`, `decryptLayer`, and `ingestReader` adapt `content.ReaderAt` data to ocicrypt readers, translate media types between Docker/OCI and encrypted media types, write transformed blobs, and return updated OCI descriptors.

Public APIs are `EncryptNydusBootstrap` and `DeryptNydusBootstrap` (note the spelling). Encryption creates a crypto config from recipient strings, filters encryption annotations out of the old descriptor, writes changed content either with `content.WriteBlob` when digest is known or through `ingestReader` when digest is computed, then merges finalizer annotations into the descriptor. Decryption creates a decrypt config from key paths, supports `unwrapOnly`, maps encrypted media types back to plain media types, and persists decrypted content when needed.

State is the content store and OCI descriptor graph; no local files are written directly. Dependencies include `ocicrypt`, containerd content APIs, image media types, digests, and OCI descriptors. Risks include unsupported media type failures, random refs when digest is initially unknown, annotation handling, the `unwrapOnly` path returning a wrapped error with nil underlying error, and lack of direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/encryption/encryption.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/errdefs/errors.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/errdefs/errors.go

This file centralizes project-level error sentinels and classifiers. It aliases containerd's `ErrAlreadyExists` and `ErrNotFound`, defines local sentinels for invalid argument, unavailable, not implemented, and device busy, then exposes helpers such as `IsAlreadyExists`, `IsNotFound`, `IsConnectionClosed`, and `IsErofsMounted`.

Integration points are broad: daemon creation checks `ErrAlreadyExists`, client socket failures wrap `ErrNotFound`, filesystem and manager cleanup check EROFS busy via `IsErofsMounted`, and metrics tooling returns `ErrInvalidArgument` for invalid CPU samples. The file depends on `github.com/pkg/errors` for compatibility with wrapped errors, standard `errors` for syscall matching, `net.OpError`, and `syscall.EBUSY`.

State and persistence are absent; this is a semantic layer over error values. Risks include `IsConnectionClosed` comparing an inner error string exactly to `"use of closed network connection"`, local sentinel values not matching containerd `errdefs` classifiers, and comments for `ErrDeviceBusy` copied from not-implemented text. There are no direct tests in this subset, so behavior is only indirectly validated by callers.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/errdefs/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/fanotify/conn/conn.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/fanotify/conn/conn.go

This file defines the small line-oriented client used by the fanotify server wrapper. `Client` owns a `bufio.Reader`, and `EventInfo` models newline-delimited JSON events with `path`, `size`, and `elapsed` fields. `GetEventInfo` reads until `\n`, unmarshals one event, and returns it.

There is no persistence here; the stream is owned by the fanotify process stdout pipe created in `pkg/fanotify/fanotify.go`. This package is intentionally minimal so the higher-level receiver can convert events to plain text and CSV. Dependencies are limited to `bufio` and `encoding/json`.

Risks include assuming each event is newline-delimited JSON, returning read errors directly, and allocating one full line in memory. Partial or malformed JSON terminates the receiver. The `Size` field is `uint32`, so very large values would truncate if the producer emits larger numbers. There are no direct tests for stream parsing or malformed input in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/fanotify/conn/conn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/fanotify/fanotify.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/fanotify/fanotify.go

This file wraps an external fanotify binary and records accessed paths. `Server` stores the binary path, target container PID, image name, persistence path, formatting flags, timeout, stdout client, `exec.Cmd`, and syslog writer. `NewServer` constructs the state object.

`RunServer` skips work if an existing persist file should be preserved, starts the binary in a new mount namespace with `_MNTNS_PID` and `_TARGET=/` environment variables, pipes stdout into `conn.Client`, and launches goroutines for process wait, event receiving, and optional timeout shutdown. `RunReceiver` creates a plain path file plus a `.csv` file, writes a CSV header, reads events until EOF, and writes raw or human-readable size/latency values. `StopServer` sends SIGTERM to the process group and waits.

State is persisted in the configured text and CSV files. Integration points include syslog, mount namespace behavior, external fanotify server contract, display formatting utilities, and logrus. Risks include blocking process waits, unguarded `LogWriter` assignment to stderr, duplicated wait paths between the wait goroutine and `StopServer`, overwrite semantics, and no tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/fanotify/fanotify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/bootstrap.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/bootstrap.go

This file implements bootstrap readiness validation before a snapshot is mounted. It prevents `nydusd` from reading partially written `image.boot` and related `.blob.meta` files. `waitForReadyBootstrapWithRetry` repeatedly calls `validateBootstrapAndBlobMeta` and requires two consecutive equal `bootstrapState` observations before returning success.

`validateBootstrap` opens the bootstrap, requires a regular file, reads up to `layout.MaxSuperBlockSize`, detects RAFS v5/v6 via `layout.DetectFsVersion`, and for v6 validates size alignment based on block bits at `layout.RafsV6SuperBlockOffset + 12`. `validateBlobMetaFiles` finds sibling `*.blob.meta` files, sorts them, and validates each is a regular non-empty readable file. `detectV6BlockSize` currently accepts 512 and 4096 byte block sizes.

State is derived from file size and blob-meta filenames/sizes; persistence belongs to snapshot preparation. Integration points include `Filesystem.Mount`, RAFS layout constants, and the retry utility. Risks include accepting stable but semantically incomplete files, limited v6 block-bit support, and relying on consecutive polling instead of writer-side atomic rename. Tests cover stable changes, misalignment, v5 acceptance, too-small headers, blob-meta sorting, and block-bit errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/bootstrap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/bootstrap_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/bootstrap_test.go

This test file provides detailed coverage for bootstrap readiness and validation. Helpers `writeFakeV5Bootstrap` and `writeFakeV6Bootstrap` create synthetic RAFS headers using layout constants. The tests simulate changing file size, delayed blob-meta creation, stable invalid v6 alignment, valid v5 bootstraps, too-small files, unknown v6 block bits, sorted blob-meta state, empty blob-meta rejection, combined state generation, and `bootstrapState.Equal`.

The test signals are strong for local file validation because they exercise both the retry-stability behavior and individual validation helpers. They verify that readiness waits through a first valid-but-changing observation and that `.blob.meta` state is included in stability decisions. The tests use short retry intervals and temporary files only; no real nydusd, daemon manager, or snapshotter state is required.

Coverage gaps are around real RAFS headers beyond the minimal magic/block-bit fields, concurrent file replacement/rename behavior, non-regular file cases for bootstrap, and permission errors. Still, this file materially reduces risk in the mount path because `Filesystem.Mount` calls `waitForReadyBootstrap` before daemon configuration and start.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/bootstrap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/config.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/config.go

This file defines `NewFSOpt` option functions used by `NewFileSystem`. Options set the nydusd binary path, enabled managers by filesystem driver, cache manager, referrer manager, index manager, tarfs manager, signature verifier, root mountpoint, and optional stargz resolver.

The important behavior is dependency injection. `WithManagers` builds `enabledManagers` keyed by `Manager.FsDriver`, letting the filesystem route fscache, fusedev, blockdev, proxy, and nodev paths. `WithCacheManager`, `WithReferrerManager`, `WithIndexManager`, and `WithTarfsManager` reject nil inputs to fail early. `WithEnableStargz` constructs a `stargz.Resolver` only when enabled. `WithVerifier` allows nil and simply stores the pointer, so callers must ensure mount-time verification can be invoked safely.

There is no persistent state beyond the configured `Filesystem` fields. Integration points are all downstream filesystem operations: daemon startup needs managers and cache, metadata detection needs referrer/index managers, tarfs paths need `tarfs.Manager`, stargz conversion needs a resolver, and signature verification runs during mount. Risks include missing nil checks for verifier and root mountpoint, overwriting duplicate managers by driver, and no direct unit tests for option validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/fs.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/fs.go

This file is the main filesystem orchestration layer. `Filesystem` owns shared fscache/fusedev daemons, managers, cache/referrer/index/stargz/tarfs/verifier dependencies, the nydusd binary path, root mountpoint, and per-snapshot mutexes. `NewFileSystem` recovers daemon and RAFS records, initializes missing shared daemons, restarts recovering daemons, remounts RAFS instances, and hot-upgrades live daemons when binary git commit differs.

`Mount` is the central workflow. It serializes per snapshot, creates a RAFS instance, chooses driver overrides for tarfs, waits for bootstrap readiness, copies `.blob.meta` files to cache, chooses shared or dedicated daemon, supplements and persists daemon config, adds RAFS to the daemon, verifies signatures, dispatches to fscache/fusedev/tarfs/nodev/proxy mount logic, waits for daemon `RUNNING`, then persists RAFS state through the manager. `Umount` reverses state by driver, removing RAFS records and destroying daemons when refs drop to zero.

State spans global RAFS cache, manager store, daemon configs, cache files, fscache annotations, and mounted filesystems. Integration points include daemon, manager, daemonconfig, cache, tarfs, EROFS, labels, signature, referrer/index adaptors, and metrics. Risks include many partial-failure cleanup paths, shared-daemon reference accounting, global config dependence, concurrent recovery, and nil dependency assumptions. Unit coverage is mostly in bootstrap validation; most orchestration requires integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/index_adaptor.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/index_adaptor.go

This adaptor connects `Filesystem` to the OCI index-alternative detector. `IndexDetectEnabled` reports whether an `index.Manager` is configured. `CheckIndexAlternative` validates required snapshot labels, detects an explicit `containerd.io/snapshot/nydus-index-alternative=true` fast path, then calls `indexMgr.CheckIndexAlternative` with the image ref and target manifest digest. `TryFetchMetadataFromIndex` validates labels, skips work if the metadata file already exists, and delegates to `indexMgr.TryFetchMetadata`.

State is mostly external: labels describe the image, `metadataPath` is written by the index manager, and the manager caches descriptors by manifest digest. This adaptor decides whether filesystem preparation should use an alternative Nydus manifest from an OCI index rather than a referrer or normal layer.

Dependencies include containerd snapshotter labels, Nydus label constants, OpenContainers digests, filesystem existence checks, logging, and `pkg/index`. Risks include silently returning false for missing/invalid labels, trusting the explicit label without rechecking the registry, and not checking `indexMgr` nil in `TryFetchMetadataFromIndex`. Tests for descriptor selection live in `pkg/index`, not this adaptor.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/index_adaptor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/referer_adaptor.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/referer_adaptor.go

This adaptor connects `Filesystem` to the OCI referrers-based metadata detector. `ReferrerDetectEnabled` checks whether a referrer manager is configured. `CheckReferrer` extracts the image reference and manifest digest from containerd labels, validates the digest, and delegates to `referrerMgr.CheckReferrer`. `TryFetchMetadata` validates the same labels and calls `referrerMgr.TryFetchMetadata` to fetch and unpack metadata to a path.

No local persistence is managed here except passing `metadataPath` to lower layers. The lower referrer manager maintains an LRU descriptor cache and writes metadata via `remote.Unpack`. This file is part of the metadata discovery decision path used when a Nydus metadata layer is published as an OCI referrer instead of directly in the pulled manifest.

Risks include returning false for all label or registry errors in `CheckReferrer`, dereferencing `fs.referrerMgr` in `TryFetchMetadata` without a local nil guard, and relying on label-provided manifest digest correctness. The code uses the package name `referer` in the filename but `referrer` in types and package paths. There are no direct tests for this adaptor in the subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/referer_adaptor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/stargz_adaptor.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/stargz_adaptor.go

This file adds estargz compatibility paths to `Filesystem`. `UpperPath` maps snapshot IDs to the upper filesystem directory. `StargzEnabled` checks resolver configuration. `IsStargzDataLayer` parses registry labels, builds auth, fetches a stargz blob, and detects TOC offset to decide whether the layer is estargz.

`PrepareStargzMetaLayer` downloads the stargz TOC, writes it to storage, chooses a blob-meta path based on fscache mode, and runs the configured nydusd binary as `nydus-image create --source-type stargz_index` to generate a Nydus bootstrap and `.blob.meta`. `MergeStargzMetaLayer` locates per-parent bootstraps, copies non-base blob-meta files into the first parent, and either reflinks a single bootstrap or invokes `nydus-image merge` to build `image.boot`. `StargzLayer` checks the stargz label marker.

State is file-heavy: TOC files, converted bootstraps, blob-meta files, temp files, chmodded outputs, and copied metadata. Dependencies include auth, registry label parsing, stargz resolver, reflink, nydusd/nydus-image CLI behavior, digest validation, and global fs-driver config. Risks include external command failures, assumptions about parent order, temp cleanup, file-name digest detection, and no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/stargz_adaptor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/tarfs_adaptor.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/tarfs_adaptor.go

This adaptor exposes tarfs/blockdev operations through `Filesystem`. `TarfsEnabled` checks whether a `tarfs.Manager` is installed. `PrepareTarfsLayer` validates image ref, layer digest, and manifest digest labels, asks the tarfs manager whether the image has a tarfs hint annotation, optionally acquires a per-ref concurrency limiter, prepares the layer, releases the limiter, and annotates labels with the layer blob ID under `NydusTarfsLayer`.

Other methods are thin delegations: `MergeTarfsLayers`, `DetachTarfsLayer`, `ExportBlockData`, `GetTarfsImageDiskFilePath`, and `GetTarfsLayerDiskFilePath`. The filesystem mount path uses the `NydusTarfsLayer` label to switch to `FsDriverBlockdev` and call `MountTarErofs`.

State lives in tarfs manager storage and the mutable labels map. Integration points include containerd snapshot metadata, Nydus label constants, tarfs manager concurrency limiting, and block-data export. Risks include label mutation as control flow, misspelled error text, limiter release not deferred around all error paths, logging and continuing after `PrepareLayer` error before still labeling the layer, and no direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/filesystem/tarfs_adaptor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/index/detector.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/index/detector.go

This file implements OCI index-based Nydus alternative detection. A `detector` owns a `remote.Remote`. `checkIndexAlternative` fetches the resolved index manifest, limits reads to 8 MiB, unmarshals an OCI index, finds a same-platform Nydus manifest alternative, fetches that manifest, validates it has layers, and returns the last layer if it is marked as a Nydus metadata layer.

`findNydusManifestInIndex` first locates the original manifest descriptor by digest, then uses `platforms.NewMatcher` against its platform and returns the first same-platform descriptor with either the Nydus OS feature or Nydus artifact type. `fetchMetadata` fetches a selected descriptor and unpacks `converter.BootstrapFileNameInLayer` to the requested metadata path, removing partial output on unpack error.

State is remote registry content plus local metadata output. Dependencies include auth-backed remote resolvers, OCI descriptors/index/manifest, Nydus converter constants, Nydus labels, and digest/platform packages. Risks include nil platform dereference in `platforms.NewMatcher(*originalDesc.Platform)` or `pMatcher.Match(*manifest.Platform)`, selecting the first matching alternative, and silent plain-HTTP retry only when remote allows it. Tests cover platform feature/artifact matching and descriptor selection, not network or unpack paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/index/detector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/index/detector_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/index/detector_test.go

This file tests local index-selection logic without registry IO. `TestHasNydusFeatures` verifies nil platform, no OS features, one Nydus feature, multiple features, and unrelated features. `TestFindNydusManifestInIndex` builds synthetic OCI indexes and checks original-manifest absence, no alternative, successful same-platform Nydus alternative, multiple alternatives returning the first match, different architecture ignored, artifact-type match, and wrong artifact type ignored.

These tests give confidence that index alternatives are selected by matching the original descriptor's platform and either `nydus.remoteimage.v1` OS feature or Nydus artifact type. They also lock in first-match behavior when multiple alternatives exist.

Coverage gaps include nil platform fields on descriptors, variant/OSVersion matching details, malformed JSON, max-size truncation, remote fetch errors, metadata-layer validation in the fetched manifest, and `fetchMetadata` unpack cleanup. No persistent files are written; all state is in memory. The tests are valuable because filesystem index detection depends on this function to avoid mounting an ordinary OCI layer when a Nydus alternative is advertised.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/index/detector_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/index/manager.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/index/manager.go

This file provides a cached, singleflight-backed manager for OCI index alternative detection. `NewManager` stores the insecure-registry flag, creates a 500-entry LRU, and initializes a `singleflight.Group`. `CheckIndexAlternative` coalesces concurrent checks by manifest digest, returns cached descriptors, treats cached nil as `ErrNoNydusAlternative`, builds auth from the ref, runs a detector on cache miss, caches nil on failure to avoid repeated checks, and logs failures.

`TryFetchMetadata` calls `CheckIndexAlternative`, rebuilds auth, creates a detector, and fetches/unpacks metadata to the requested path. State is the LRU cache keyed by manifest digest and the singleflight in-flight map; metadata output is handled by the detector.

Integration points include `pkg/filesystem/index_adaptor.go`, auth keychain lookup, remote registry fetches, and OCI descriptors. Risks include caching negative results indefinitely even if registry referrers/index content changes under the same digest assumption, type assertions from LRU values, singleflight keyed only by digest rather than ref plus digest, and no local nil cache invalidation. Tests cover cache-hit success and cached nil failure; live registry behavior is untested.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/index/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/index/manager_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/index/manager_test.go

This test file exercises `Manager.CheckIndexAlternative` cache-hit behavior. It constructs a manager, inserts an OCI descriptor under a manifest digest, and verifies the call returns that descriptor without error. A second subtest inserts nil under the digest and verifies the manager returns an error containing `no alternative nydus descriptor found in index`.

The tests are small but important because the manager intentionally caches both positive and negative detection results. They protect the type assertion path for positive descriptors and the sentinel-style error path for cached misses. There is no registry, auth, singleflight contention, or metadata fetch in these tests.

Coverage gaps include detector invocation on cache miss, failure wrapping, cache eviction behavior, concurrent calls, and `TryFetchMetadata`. Persistent state is absent; the LRU is in-memory. The tests support filesystem behavior indirectly because `Filesystem.CheckIndexAlternative` relies on this cache to avoid repeated remote index scans.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/index/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/label/label.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/label/label.go

This file centralizes label keys used to coordinate containerd snapshot metadata, Nydus image metadata, proxy mode, tarfs, stargz, signatures, and index alternatives. It aliases containerd snapshotter label names for compatibility and preserves the old exported `AppendLabelsHandlerWrapper` name.

Important constants include `TargetSnapshotRef`, `NydusDataLayer`, `NydusMetaLayer`, `NydusRefLayer`, `NydusTarfsLayer`, block verity labels, pull secret/user labels, `NydusProxyMode`, `NydusSignature`, `StargzLayer`, `OverlayfsVolatileOpt`, `TarfsHint`, and `NydusIndexAlternative`. Helper functions check map-key presence for Nydus data/meta layers, tarfs data layers, proxy mode, and tarfs hints.

There is no persistence here, but labels are persisted in containerd snapshot/image metadata and are used throughout filesystem preparation, metadata detection, tarfs/stargz adaptors, and proxy mode. Risks include key-presence checks treating empty values as true, mutable label maps being used as state transfer, and semantic drift between containerd labels and project constants. There are no direct tests in this subset; behavior is indirectly exercised by higher-level mount and detector tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/label/label.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/layout/layout.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/layout/layout.go

This file defines RAFS layout constants and filesystem-version detection. Constants describe maximum superblock read size, RAFS v5/v6 names, v5 magic/version, v6 magic, v6 superblock offsets, bootstrap file paths, and a dummy mountpoint. `ImageMode` distinguishes on-demand and preload modes.

At init time, the file detects native byte order using `unsafe`. `DetectFsVersion` first checks the first eight bytes for RAFS v5 magic and version using little endian. If not v5, it checks that the buffer is large enough for v6 and that the v6 magic appears at `RafsV6SuperBlockOffset` using native endian. Unknown or too-small headers return errors.

State is limited to package-level `nativeEndian`. Integration points include bootstrap readiness validation, fake bootstrap tests, image conversion code, and mount preparation paths that locate bootstraps. Risks include native-endian v6 detection on non-little-endian systems, limited magic checks noted by the FIXME, and no direct tests for `DetectFsVersion` in this subset beyond bootstrap tests. The constants are contract-level and changing them affects filesystem validation and generated metadata paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/layout/layout.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_adaptor.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_adaptor.go

This file bridges manager state to actual `nydusd` processes. `StartDaemon` builds an exec command, starts it, records the PID under daemon lock, optionally samples startup CPU utilization, updates daemon state in the store/cache, and launches a goroutine that waits for the API socket, subscribes liveness events, waits for `RUNNING`, records metrics, adds the process to a cgroup, stores version metrics, and sends failover states.

`BuildDaemonCommand` translates daemon mode and driver into command options. Fscache uses `singleton --fscache`; fusedev uses `fuse --mountpoint`. Dedicated fusedev requires a RAFS instance, adds config/bootstrap, and may add backend-source controller URL. Supervisor, prefetch files, log level/socket/log rotation/log file, upgrade flag, and failover policy are appended as appropriate.

State spans process PID, manager store, daemon cache, cgroup membership, metrics, prefetch map deletion, and supervisor state. Integration points include daemon command builder, config globals, RAFS cache, prefetch manager, metrics tooling, and liveness monitor. Risks include committing daemon records before successful readiness, asynchronous subscription failures, cgroup errors after process start, config dependence, and broad behavior requiring integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_adaptor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_cache.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_cache.go

This file implements the manager's in-memory daemon index. `DaemonCache` holds a mutex and a map from daemon ID to `*daemon.Daemon`. `Add` inserts or replaces and returns the previous pointer, `Remove` and `RemoveByDaemonID` delete entries, `Update` logs recovery and replaces the entry, `GetByDaemonID` optionally runs a callback while holding the lock, `List` returns a slice snapshot, and `Size` returns map length.

State is entirely in memory but mirrors the persistent store managed by `Manager`. The manager's comments require store updates before cache modifications, making this cache a performance and coordination layer rather than source of truth. It is used by daemon lookup, recovery, teardown, metrics server manager walks, and filesystem daemon selection.

Risks include callbacks running under the cache lock, `List` returning daemon pointers whose internals may still need their own locks, replacement behavior masking accidental duplicate daemon IDs if used outside `Manager.AddDaemon`, and no ordering guarantee from map iteration. Tests cover add/get/list/size/remove/update basics but not concurrent access or callback mutation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_cache_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_cache_test.go

This test file validates the basic semantics of `DaemonCache`. It creates two daemon objects with explicit IDs, adds them, retrieves them by ID, verifies list membership and size, removes by pointer, removes by ID, updates a daemon back into the cache, and removes it again.

The test signals confirm that the cache stores pointers, returns expected daemon objects, tracks size, and supports both removal styles. It also verifies `Update` can repopulate the cache, which matters during manager recovery from persisted daemon records.

Coverage is intentionally narrow. It does not test replacing an existing daemon via `Add`, callback behavior in `GetByDaemonID`, concurrent access, list nil behavior for empty caches, or interactions with the persistent store. There is no filesystem or process state. Because the cache is a shared lookup path for manager, filesystem, and metrics code, concurrency behavior remains a residual risk despite mutex use.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_event.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_event.go

This file handles daemon liveness events, restart/failover recovery, and hot upgrade. `SubscribeDaemonEvent` and `UnsubscribeDaemonEvent` wrap the liveness monitor. `handleDaemonDeathEvent` consumes death notifications, records daemon count decrement, resets cached state, and dispatches according to recover policy.

`doDaemonRestart` waits for the old process, unsubscribes, clears vestiges, restarts the daemon, and remounts shared RAFS instances. `doDaemonFailover` waits, unsubscribes, asks supervisor to send states, restarts the daemon, waits for `INIT`, calls `TakeOver`, then starts service. `DoDaemonUpgrade` clones daemon state and RAFS instances, chooses the next API socket name, starts a new daemon with `--upgrade`, transfers states, waits through `INIT` and `READY`, unsubscribes the old daemon, asks it to exit, starts the new daemon, subscribes it, waits for `RUNNING`, recovers mounts, and persists the new daemon. `buildNextAPISocket` increments `apiN.sock`.

State spans supervisor sockets, daemon process IDs, API sockets, RAFS cache, monitor subscriptions, and manager store. Risks include asynchronous recovery races, upgrade rollback gaps, socket-name assumptions, supervisor nil assumptions in failover, and limited unit tests for helper behavior in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_event.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/manager.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/manager.go

This file defines `Manager`, the owner of daemon and RAFS persistence for one filesystem driver. It holds a store, daemon cache, daemon config template, optional cgroup manager, liveness monitor, death event channel, binary path, recovery policy, and optional supervisor set. `NewManager` creates the store and monitor, creates supervisors for failover policy, starts the monitor, and launches death-event handling.

Recovery is split between `recoverDaemons` and `recoverRafsInstances`. Daemons are loaded from store, cached, optionally assigned supervisors/configs, queried for current state, classified as recovering or live, added to cgroups/metrics, and subscribed asynchronously. RAFS instances are loaded, attached to matching recovering/live daemons, and added to the global RAFS cache. CRUD methods keep daemon and RAFS store/cache in sync. `DestroyDaemon` deletes DB state first, removes RAFS refs, unmounts, unsubscribes, destroys supervisor, terminates/waits process, records metrics, and cleans config/log/socket resources.

State is both persistent DB data and in-memory cache. Integration points include store, daemon, RAFS, config, supervisor, cgroup, metrics, and monitor. Risks include cleanup after DB deletion failures, recovery silently skipping non-running daemons, asynchronous subscription errors, global RAFS cache coupling, and sparse unit coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/monitor.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/monitor.go

This file implements Unix-socket based daemon liveness monitoring with epoll. `LivenessMonitor` defines subscribe, unsubscribe, run, and destroy. `livenessMonitor` tracks subscribers by daemon ID and by file descriptor, using `EpollCreate1` with `EPOLL_CLOEXEC`.

`Subscribe` retries dialing the daemon Unix socket, converts to `*net.UnixConn`, obtains the raw fd, sets it nonblocking, registers `EPOLLHUP|EPOLLERR|EPOLLET`, and records the target. `Run` starts a goroutine that blocks in `EpollWait`, looks up targets, and on HUP/ERR increments daemon-died metrics and sends `deathEvent` to the subscriber channel. `Unsubscribe` removes the fd from epoll, deletes maps, and closes the connection. `Destroy` unsubscribes all and closes the epoll fd, though comments note closing does not wake `EpollWait`.

State is in-memory fd maps and a long-running goroutine. Integration points include manager death handling, daemon API sockets, metrics collectors, retry utilities, and Linux `x/sys/unix`. Risks include Linux-only behavior, event races around unsubscribe, blocked goroutine shutdown, duplicate subscription semantics, and file descriptor lifecycle. Tests exercise death notification and unsubscribe behavior with local Unix servers.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/monitor_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/monitor_test.go

This test file validates the liveness monitor using temporary Unix sockets. `startUnixServer` accepts one connection and keeps it open until its context is canceled. `TestLivenessMonitor` starts two such servers, subscribes daemon IDs, verifies duplicate subscription for the same ID/path errors, runs the monitor, cancels the first server and receives a death event, unsubscribes the second daemon, cancels it, and verifies no extra event is queued. Finally it destroys the monitor and asserts internal maps are empty.

The test gives meaningful coverage of subscription, duplicate detection, epoll HUP delivery, unsubscribe suppression, and cleanup. It uses real Unix sockets and epoll behavior, so it is closer to integration than pure unit testing.

Residual risks include timing sensitivity from sleeps, single-connection server behavior, lack of coverage for failed dial retries, fd control failures, monitor goroutine shutdown after epoll fd close, and manager recovery reactions to delivered death events. Temporary socket files are the only persisted state.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/monitor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/store.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/store.go

This file defines the `Store` interface for daemon and RAFS persistence. It includes daemon CRUD and walking, RAFS instance CRUD and walking, cleanup, and sequence allocation through `NextInstanceSeq`. The compile-time assertion ensures `store.DaemonRafsStore` implements the interface.

The interface is used by `Manager` to persist `daemon.ConfigState` and whole `rafs.Rafs` records. It is central to restart recovery because `Manager.Recover` walks daemon and RAFS records to reconstruct in-memory cache and mount state. `AddRafsInstance` obtains a sequence number from this store so RAFS recovery can later preserve mount order.

This file contains no concrete control flow, but it defines a contract boundary between manager orchestration and the database layer. Risks include interface changes affecting store implementations, no explicit transaction grouping between daemon and RAFS updates, and reliance on callers to update store before cache. There are no direct tests here; store behavior is tested wherever `store.DaemonRafsStore` is covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/manager/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/cache.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/cache.go

This file maps `types.CacheMetrics` returned by nydusd into Prometheus gauges. `CacheMetricsCollector` carries one metrics payload, image ref, and daemon ID. `CacheMetricsVecCollector` iterates a slice of collectors.

`Collect` guards nil metrics, computes a prefetch duration value, and sets TTL-backed gauges for partial/whole hits, total cache requests, entry count, prefetched bytes, prefetch request count, workers, unmerged chunks, cumulative prefetch time, total duration, and buffered backend size. Labels are keyed by image ref. It depends on metric definitions in `pkg/metrics/data` and daemon metrics schemas from `pkg/daemon/types`.

There is no persistence; state is held in Prometheus collectors, with TTL cleanup managed by the metric type. Integration points include `metrics.Server.CollectCacheMetrics`, daemon `GetCacheMetrics`, and the registry. Risks include the duration formula subtracting begin and end timestamps while adding `PrefetchCumulativeTimeMillis` to both sides, which cancels cumulative time and may indicate a bug; also no delete path for stale image labels beyond TTL. There are no direct tests for this collector.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/collector.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/collector.go

This file provides factory functions and a shared `Collector` interface for Prometheus metric collectors. It constructs daemon event/info/image collectors, filesystem metrics collectors, inflight metrics collectors, snapshotter resource collectors, snapshot operation timers, and cache metrics collectors.

`NewSnapshotterMetricsCollector` is the only factory with substantive work: it samples the current process stat for the supplied PID and stores it as the baseline for later CPU/resource calculations. Other constructors mostly package values into structs. `NewSnapshotMetricsTimer` returns a Prometheus timer that observes elapsed time in milliseconds through `CollectSnapshotMetricsTimer`.

State is limited to constructed collector objects and the initial process stat baseline. Integration points include daemon event handling, daemon lifecycle metrics, filesystem/cache/inflight polling, snapshotter operation instrumentation, and Prometheus histograms. Risks include factory calls failing when `/proc` stats are unavailable, process stat baseline staleness, and no direct tests for constructor wiring. Most behavior is validated through downstream collector tests or runtime metric scraping rather than this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/collector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/daemon.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/daemon.go

This file defines collectors for daemon lifecycle and identity metrics. `DaemonEventCollector` increments event counters by daemon state string. `DaemonInfoCollector` adjusts the daemon count gauge by version and a signed value. `DaemonResourceCollector` sets daemon RSS by daemon ID. `DaemonImageCollector` maintains a daemon-to-image gauge and can delete its label values.

State is stored in Prometheus metrics. Integration points include manager process start, recovery, destruction, liveness monitor death events, daemon RAFS add/remove, and metrics server daemon RSS polling. The `Version` pointer is protected by daemon locks in callers when necessary, not internally.

Risks include daemon count gauges requiring balanced positive and negative calls, nil version silently skipping count updates, RSS values being whatever the caller computed, and image-info labels needing explicit deletion on RAFS removal. There are no direct unit tests for these collectors in the subset, but the functions are simple wrappers around metric vectors.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/fs.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/fs.go

This file collects filesystem and inflight IO metrics from nydusd API payloads. `FsMetricsCollector` maps total read bytes, read hits, read errors, and custom histograms into Prometheus metrics. `FsMetricsVecCollector` clears histogram state before collecting a vector. `InflightMetricsVecCollector` counts hung IOs whose elapsed time exceeds a configured interval.

Important dependencies are `types.FsMetrics`, `types.InflightMetrics`, metric definitions in `data`, histogram utilities in `metrics/types`, and log output for invalid histogram shapes. `OPCodeMap` currently names only opcode 15 as `OP_READ`.

State is metric state plus temporary collector slices. Integration points include `metrics.Server.CollectFsMetrics` and `CollectInflightMetrics`, which poll running fusedev daemons. Risks include indexing `FopHits[mtypes.Read]` and `FopErrors[mtypes.Read]` without length checks, returning early if any histogram fails, clearing all histogram state before vector collection, and wall-clock dependence for hung IO classification. There are no direct unit tests here; histogram behavior is covered in `metrics/types`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/snapshotter.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/snapshotter.go

This file collects resource metrics for the snapshotter process and cache directory. `SnapshotterMetricsCollector` stores context, cache path, PID, and the last process stat sample. Snapshot methods are enumerated for operation latency labels.

`CollectCacheUsage` runs `continuity/fs.DiskUsage` and reports kilobytes. `CollectResourceUsage` samples `/proc` through `metrics/tool`, computes CPU system/user deltas, CPU percent, memory RSS, fd count, runtime, and thread count, then updates gauges. `Collect` runs both cache and resource collection. `CollectSnapshotMetricsTimer` creates a Prometheus timer that writes elapsed milliseconds to the snapshot operation histogram.

State is the rolling `lastStat` baseline and Prometheus metric values. Integration points include `metrics.Server`, manager cache directories, snapshotter operation instrumentation, and `/proc`. Risks include failed stat reads, CPU percent division by zero if uptime delta is zero, resource units depending on global `ClkTck` and page size, and disk usage cost on large cache directories. There are no direct tests for this collector in the subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/auth.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/auth.go

This file declares Prometheus metrics for credential renewal behavior. `CredentialRenewals` is a counter vector labeled by image ref and result, intended to count renewal attempts as success or failure. `CredentialStoreEntries` is a gauge vector labeled by image ref, intended to show how many credentials are currently tracked in the renewal store.

There is no control flow or persistence in this file. The metric objects are registered by `pkg/metrics/registry/registry.go` and updated by auth/credential renewal code elsewhere. The labels reuse shared label-name constants from `metrics/data/labels.go`.

Risks are mostly integration-level: label cardinality can grow with image references, callers must use consistent result values, and gauges must be maintained when credentials expire or are deleted. There are no tests in this subset that assert registration or update behavior for these metrics.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/cache.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/cache.go

This file declares cache-related nydusd metrics as TTL-backed Prometheus gauge vectors labeled by image ref. Metrics cover partial and whole cache hits, total requests, entry count, prefetch data bytes, prefetch request count, worker count, unmerged chunks, cumulative prefetch latency, wall-clock prefetch duration, and buffered backend size.

The definitions have no control flow beyond constructing `ttl.GaugeVec` objects. They are registered by `metrics/registry` and populated by `metrics/collector/cache.go`. TTL behavior means stale image-ref labels are eventually deleted if collectors stop setting them.

State lives inside Prometheus gauge vectors and TTL label maps. Integration points include daemon cache metrics API, metrics server collection, and registry registration. Risks include image-ref label cardinality, metric names becoming part of external monitoring contracts, and the collector's duration calculation needing to match these help strings. There are no direct tests for these definitions; TTL cleanup is tested in `metrics/types/ttl`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/daemon.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/daemon.go

This file declares daemon-level Prometheus metrics. `NydusdEventCount` counts lifetime events by daemon state/event label. `NydusdCount` tracks daemon count by nydusd version. `NydusdRSS` is a TTL-backed gauge for daemon memory RSS by daemon ID. `NydusdImageInfo` maps daemon IDs to served image references.

The metrics are registered by `metrics/registry` and updated by collectors in `metrics/collector/daemon.go`, liveness monitor, manager start/recovery/destroy paths, and daemon RAFS add/remove methods. State is metric state only; there are no files or external resources.

Risks include balancing count increments/decrements across recovery, hot upgrade, and destroy paths; daemon ID and image ref label cardinality; and stale RSS label cleanup depending on TTL. `NydusdImageInfo` is not TTL-backed and relies on explicit deletion when RAFS instances are removed. There are no direct tests for these metric definitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/fs.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/fs.go

This file declares filesystem-related Prometheus metrics and custom histogram descriptors. TTL-backed gauges track total read bytes, read hits, and read errors by image ref. `TotalHungIO` tracks the total number of hung IOs. `MetricHists` defines cumulative read block size and read latency histograms with bucket boundaries and functions that extract counters from `types.FsMetrics`.

State is held in metric objects and histogram collectors. The histogram descriptors are registered directly by the custom registry and are populated by `FsMetricsCollector`, which saves generated const histograms into each `MetricHistogram`.

Integration points include nydusd metrics JSON, `metrics/types.MetricHistogram`, and metrics server collection. Risks include strict expectation that counter slice lengths equal bucket lengths, image-ref label cardinality, and metric help/bucket changes affecting dashboards. `FsMetricsCollector` reads `FopHits` and `FopErrors` by operation index, so mismatched nydusd schemas can cause panics before histogram validation. No direct tests cover these definitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/labels.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/labels.go

This file contains shared label-name constants for metrics declared in `pkg/metrics/data`. Labels include image reference, nydusd event, version, daemon ID, snapshot operation, and credential result.

There is no runtime control flow or persistence. The constants are a small but important compatibility surface because metric vectors across auth, cache, daemon, filesystem, and snapshotter data use them. Renaming any value changes the exported Prometheus label schema.

Integration points are all metric declarations and collectors. Risks include label cardinality, especially `image_ref` and `daemon_id`, and inconsistent result values for credential metrics because only the label name is centralized. There are no direct tests for this file; registration failures would appear through metrics registry initialization if label descriptors became inconsistent.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/labels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/snapshotter.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/snapshotter.go

This file declares snapshotter-level Prometheus metrics. It defines default duration buckets for snapshot operation histograms, then declares gauges for cache usage, CPU usage, memory usage, CPU system/user time, fd count, runtime, thread count, and cache cleanup counters/gauges for deleted blobs, in-use blobs, and deletion errors.

These metrics are registered by `metrics/registry`. Snapshot operation histograms are populated through `collector.NewSnapshotMetricsTimer`, while process and cache resource gauges are populated by `SnapshotterMetricsCollector`. Cache cleanup metrics are updated by cleanup code outside this subset.

State is metric-only. Integration points include snapshotter operation handlers, process `/proc` sampling, disk usage scanning, and cache cleanup. Risks include units encoded in names/help text, bucket choices affecting alerting precision, and cleanup counters needing consistent caller updates. There are no direct tests in this subset; correctness depends on collector behavior and Prometheus registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/listener.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/listener.go

This file starts the HTTP endpoint used by Prometheus scraping. `endpointPromMetrics` is `/v1/metrics`. `trapClosedConnErr` normalizes nil and `net.ErrClosed` to nil. `NewMetricsHTTPListenerServer` validates the address, registers `promhttp.HandlerFor(registry.Registry, ...)` on the default HTTP mux, binds a TCP listener, and serves it in a goroutine.

State includes the global default HTTP mux registration and the listener goroutine. Integration points are the custom registry, Prometheus client library, snapshotter configuration that supplies the address, and process lifecycle. The function returns after listener creation, not after serve completion.

Risks include using the package-global `http.Handle`, which can conflict if multiple metric servers or tests register the same path; no shutdown handle is returned; listener errors after startup are only logged; and address validation only checks empty string. There are no direct tests for listener startup or handler output.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/listener.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/registry/registry.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/registry/registry.go

This file creates the package-level Prometheus registry and registers all snapshotter, daemon, filesystem, cache, auth, and cleanup metrics. `init` calls `Registry.MustRegister` for standard collectors, then registers each custom filesystem histogram in `data.MetricHists`.

State is the global `Registry`, which is later served by `metrics/listener.go`. Integration points include every metric definition in `metrics/data`, custom histogram collectors in `metrics/types`, and Prometheus HTTP serving. Because `MustRegister` panics on duplicate or invalid collectors, initialization failures surface early.

Risks include adding a metric definition but forgetting to register it, duplicate metric names across files, and tests importing the package multiple ways with global state. There are no direct tests for registry contents in this subset. This file is a monitoring contract boundary: removing or renaming metrics affects external dashboards and alerts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/registry/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/serve.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/serve.go

This file implements periodic metrics collection. `Server` holds managers, snapshotter collectors, filesystem/cache/inflight vector collectors, and collection intervals. Options configure managers, metric interval, and hung-IO interval, rejecting negative durations. `NewServer` creates vector collectors and one snapshotter resource collector per manager cache directory.

Collection methods walk managers and daemons. `CollectDaemonResourceMetrics` samples daemon RSS. `CollectFsMetrics` polls fusedev daemons in `RUNNING` state and collects per-RAFS filesystem metrics. `CollectCacheMetrics` polls cache metrics for each daemon/RAFS. `CollectInflightMetrics` polls fusedev daemons and counts hung IOs. `StartCollectMetrics` runs two tickers: one for fs/cache/daemon/snapshotter metrics and one for inflight metrics, exiting on context cancellation.

State is rolling metric values plus collector baselines. Integration points include manager daemon lists, daemon client metrics APIs, RAFS caches, `/proc`, disk usage, and Prometheus collectors. Risks include ticker creation with zero intervals if not configured, sid handling differing from fscache readiness logic, skipped non-running daemons based on cached state, and no direct tests for server loops.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/serve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/tool/common.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/tool/common.go

This file provides small numeric and system helpers for metrics. `FormatFloat64` rounds through formatted strings to either six or two decimal places. `ParseFloat64` parses strings and ignores errors. `GetClkTck` runs `getconf CLK_TCK`, falling back to 100 when unavailable or failing. `GetPageSize` returns `os.Getpagesize` as float64.

State is exposed through package globals in `stat.go` (`ClkTck` and `PageSize`) initialized from these helpers. Integration points include snapshotter and daemon CPU/memory resource collectors. Dependencies include OS commands, PATH lookup, logging, and strconv formatting.

Risks include ignored parse errors returning zero, shelling out to `getconf` at package initialization time, fallback assumptions for nonstandard platforms, and rounding by string conversion. There are no direct tests for these helpers; process stat tests indirectly rely on initialized globals.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/tool/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/tool/stat.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/tool/stat.go

This file reads Linux `/proc` process data for metrics and daemon startup profiling. `Stat` stores CPU times, thread count, start time, RSS, fd count, and system uptime. `ClkTck` and `PageSize` are package globals initialized from `common.go`.

`CalculateCPUUtilization` computes CPU percent between two stat samples. `GetProcessMemoryRSSKiloBytes` derives RSS in KiB. `GetProcessStat` reads `/proc/uptime`, `/proc/<pid>/stat`, splits after the process name's closing parenthesis, reads `/proc/<pid>/fdinfo`, and maps selected fields. `GetProcessRunningState` reads the process state field. `IsZombieProcess` checks for state `"Z"`.

State is read-only from `/proc`. Integration points include metrics server resource collection, daemon startup CPU profiling, and socket-wait retry behavior. Risks include Linux-only paths, parsing assumptions around `/proc/<pid>/stat`, ignored float parse errors, potential division by zero in CPU utilization, fdinfo permission failures, and state tests differing across init systems. Unit coverage only checks PID 1 running state contains `Ss` or `S`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/tool/stat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/tool/stat_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/tool/stat_test.go

This test file contains `TestFindZombie`, which calls `GetProcessRunningState(1)` and asserts no error and that PID 1's state string contains either `Ss` or `S`. It is a minimal smoke test for reading and parsing `/proc/<pid>/stat`.

The test signal is limited but useful: it verifies the code can access `/proc`, split the stat fields, and extract the process state on the test host. It does not spawn or detect an actual zombie process despite the test name, and it does not exercise `GetProcessStat`, fd counting, CPU utilization, RSS calculation, or parse-error paths.

Risks include portability and environment sensitivity. PID 1 may not have state `Ss` or `S` in all containers or systems, and non-Linux environments lack `/proc`. No persistent state is used. Broader metrics correctness is covered only by runtime behavior, not this test.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/tool/stat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/types/ttl/gauge.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/types/ttl/gauge.go

This file wraps Prometheus `GaugeVec` with label-value TTL tracking. `NewGaugeVecWithTTL` creates an underlying gauge vector, records label names and TTL, initializes a map from label/value pairs to expiration times, and launches `cleanUpExpired` in a goroutine. Cleanup runs every `defaultCleanUpPeriod`, deletes expired label values from the underlying gauge, and removes map entries.

`WithLabelValues` returns a `GaugeWithTTL` wrapper containing the label values and underlying gauge. `Set` updates the expiration deadline under lock and sets the gauge value. Label identity is represented by joined label names and joined label values.

State is in-memory metric data plus the TTL map and cleanup goroutine. Integration points include cache, daemon RSS, and filesystem metrics that should age out stale labels. Risks include one cleanup goroutine per gauge vector, no stop mechanism, joined label values colliding if values contain commas, cleanup assuming one label value in `DeleteLabelValues(k.value)`, and package-level cleanup period mutation in tests. Tests cover basic expiry behavior for one-label gauges.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/types/ttl/gauge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/types/ttl/gauge_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/types/ttl/gauge_test.go

This test file validates TTL gauge cleanup behavior. It shortens `defaultCleanUpPeriod`, creates a one-label gauge with a three-second TTL, sets two label values, collects metrics to confirm both exist, waits, refreshes one label value, verifies both remain in the internal map before cleanup, waits again, and confirms only the refreshed label remains. It then collects metrics and later verifies the map is empty after cleanup.

The test exercises `WithLabelValues`, `Set`, internal expiration tracking, Prometheus collection, and cleanup deletion. It uses sleeps and goroutines, so it is timing-sensitive but covers the intended stale-label lifecycle.

Coverage gaps include multi-label gauge vectors, label values containing commas, cleanup goroutine lifecycle, concurrent `Set` and cleanup under heavier load, and `DeleteLabelValues` correctness with more than one label. The test mutates the package-level cleanup period, which can affect other tests if run in the same process.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/types/ttl/gauge_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/types/types.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/types/types.go

This file defines filesystem operation indexes and a custom Prometheus histogram collector. The `Fop` enum assigns operation positions such as Getattr, Open, Read, Lookup, Readdir, Access, and BatchForget. `GetMaxFops` and `MakeFopBuckets` expose operation count and bucket values.

`MetricHistogram` stores a descriptor, bucket boundaries, a function that extracts counters from `types.FsMetrics`, and the last generated const histograms. `ToConstHistogram` validates counter and bucket lengths, accumulates cumulative bucket counts and weighted sum, then builds a `prometheus.MustNewConstHistogram`. `Clear`, `Save`, `Describe`, and `Collect` implement state management and the Prometheus collector interface.

State is in-memory `constHists`, cleared and repopulated by filesystem metrics collection. Integration points include `metrics/data/fs.go` histogram definitions and `FsMetricsCollector`. Risks include counter/bucket length mismatch, cumulative histogram assumptions, weighted sum interpretation, no locking around `constHists`, and operation indexes needing to match nydusd's metrics arrays. There are no direct tests for this file in the subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/metrics/types/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/pprof/listener.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/pprof/listener.go

This file starts a lightweight pprof HTTP listener. `NewPprofHTTPListener` validates the address, registers selected pprof handlers on the default HTTP mux (`threadcreate`, `goroutine`, `allocs`, `block`, `mutex`, and `heap`), opens a TCP listener, and serves it in a goroutine.

State includes global HTTP mux registrations and a background server goroutine. Integration points are snapshotter diagnostics configuration, Go's standard pprof package, process networking, and logging. The function returns no listener or shutdown function, so lifecycle is tied to process lifetime.

Risks include use of global `http.Handle`, duplicate handler registration if called multiple times, no endpoint for the pprof index/profile/cmdline handlers, no authentication, no graceful shutdown, and address exposure depending on configuration. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/pprof/listener.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/prefetch/prefetch.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/prefetch/prefetch.go

This file implements a global in-memory prefetch map populated by an external NRI plugin or caller. `prefetchInfo` contains a map from image reference to prefetch file list and a mutex. `Pm` is the package-level singleton.

`SetPrefetchFiles` unmarshals a JSON array of maps, initializes the map if needed, stores each `image` to `prefetch` value, and logs the full map. `GetPrefetchInfo` returns the value for an image or an empty string. `DeleteFromPrefetchMap` removes an image. `manager.BuildDaemonCommand` consumes this map for dedicated daemon startup and deletes entries after adding `--prefetch-files`.

State is process-local and not persisted, so restart loses pending prefetch hints. Dependencies are JSON and logging. Risks include accepting arbitrary map keys without schema validation, logging potentially large or sensitive prefetch data, deleting from a nil map being safe but masking missing initialization, and the global singleton making tests/order dependence likely. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/prefetch/prefetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/rafs/rafs.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/rafs/rafs.go

This file defines RAFS instance state and an in-memory cache. `Cache` is a mutex-protected map from snapshot ID to `*Rafs`, with add/remove/get/list/head/locked-list/set methods. `RafsGlobalCache` is initialized at package init. `Rafs` is persisted as the per-snapshot filesystem record, including sequence, image ID, daemon ID, filesystem driver, snapshot ID/dir, underlying cache files, mountpoint, and annotations.

`NewRafs` creates the snapshot directory under `config.GetSnapshotsRootDir`, initializes annotations and underlying files, adds the instance to the global cache, and returns it. Methods expose annotations, snapshot dir, fs driver fallback, fscache workdir, mountpoint, shared fusedev relative mountpoint, and bootstrap path lookup. `BootstrapFile` prefers `fs/image/image.boot` and falls back to legacy `fs/image.boot`.

State is both memory and persistent manager-store data. Integration points include filesystem mount/umount, daemon RAFS caches, fscache annotations, manager recovery, metrics, and bootstrap validation. Risks include global mutable cache, deep-copy list behavior, typo `SetIntances`, pointer sharing after `CloneRafsInstances`, directory creation side effects, and no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/rafs/rafs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/referrer/manager.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/referrer/manager.go

This file provides a cached manager for OCI referrers-based Nydus metadata discovery. `NewManager` stores the insecure-registry flag, creates a 500-entry LRU cache, and initializes singleflight. `CheckReferrer` coalesces checks by manifest digest, returns a cached descriptor when present, creates an auth keychain, calls a `referrer` to fetch and parse referrers, caches the returned metadata layer descriptor, and logs failures.

`TryFetchMetadata` checks for a metadata descriptor, rebuilds auth, creates a referrer, and fetches/unpacks metadata to the requested path. State is the LRU descriptor cache and singleflight in-flight state. Unlike the index manager, failed checks are not cached as negative results.

Integration points include filesystem referrer adaptor, auth, remote registry APIs, OCI descriptors, and metadata unpacking. Risks include cache invalidation when referrers change, type assertions on cached values, singleflight keyed only by digest, repeated remote failures because negatives are not cached, and no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/referrer/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/referrer/referrer.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/referrer/referrer.go

This file implements the registry-facing OCI referrers detector. A `referrer` owns a `remote.Remote`. `checkReferrer` fetches the referrers index for a manifest digest through a `ReferrersFetcher`, limits reads to 8 MiB, unmarshals an OCI index, fetches the first returned manifest, validates it has layers, and returns the last layer when it is marked as a Nydus metadata layer. It retries once with plain HTTP when the remote deems that valid.

`fetchMetadata` skips work if the target metadata file already exists, fetches the selected descriptor, and calls `remote.Unpack` to extract the bootstrap file, removing partial metadata on unpack failure. State is remote registry content and the local metadata file path.

Dependencies include auth-backed remote resolvers, custom referrers fetcher interface, OCI image specs, converter bootstrap filename, Nydus labels, and filesystem operations. Risks include choosing only `index.Manifests[0]` despite a TODO about artifact type search, stale existing metadata files, partial-output cleanup, referrers API compatibility, and no tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/referrer/referrer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remote.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/remote/remote.go

This file wraps registry resolver creation and controlled HTTP fallback. `Remote` stores a resolver factory, a `withPlainHTTP` flag, and an `insecure` flag. `New` builds Docker registry resolvers with optional credentials from `auth.PassKeyChain`, TLS skip-verify behavior for insecure registries, an authorizer, a shared HTTP client, and a `WithPlainHTTP` callback driven by the fallback flag.

`RetryWithPlainHTTP` only permits fallback when `insecure` is true and the error string looks like an HTTPS-client-to-HTTP-server mismatch or connection refused. It parses the reference, checks that the error includes the registry host path, logs the downgrade, and sets `withPlainHTTP`. `Resolve` and `Fetcher` create fresh resolver/fetcher instances using the current fallback mode.

State is the mutable fallback flag. Integration points include index/referrer detection, auth, Docker remotes, and registry reference parsing. Risks include mutating `http.DefaultTransport`/`http.DefaultClient`, string-matching unexported Go errors, plain HTTP retry state persisting across later calls on the same `Remote`, and host-string matching assumptions. Tests cover fallback decisions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remote_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/remote/remote_test.go

This test file validates `Remote.RetryWithPlainHTTP`. It constructs an image reference, simulated HTTPS-to-HTTP and connection-refused errors containing the registry host, and an unrelated error. Table tests verify insecure remotes allow fallback for the two expected errors, secure remotes block fallback, unrelated errors do not fallback, and nil error returns false.

The test gives useful coverage for the security-sensitive fallback gate: HTTP downgrade only happens when explicitly insecure and when the error looks like a registry protocol mismatch for the current host. It does not exercise resolver creation, actual registry requests, TLS configuration, host mismatch behavior, malformed references, or persistence of `withPlainHTTP` across calls.

There is no filesystem or network state. The test directly constructs `Remote{insecure: ...}` rather than using `New`, so it isolates fallback logic but does not validate the resolver factory created by `New`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remote_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/fetch.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/fetch.go

This file is copied from containerd auth logic and implements token option generation plus GET/POST token fetching. `GenerateTokenOptions` converts a parsed Bearer challenge into `TokenOptions`, requiring a valid `realm`, copying service, username, secret, and splitting scope by spaces when present.

`FetchTokenWithOAuth` sends an OAuth-style form POST using password or refresh-token grant depending on username, optionally asks for offline access, merges caller headers, sets a default containerd user agent, checks HTTP status, decodes `OAuthTokenResponse`, and requires an access token. `FetchToken` sends a GET token request, adds service/scope query parameters, uses HTTP basic auth when a secret is present, optionally sets `offline_token=true`, decodes `FetchTokenResponse`, canonicalizes `access_token` into `token`, and requires a token.

State is remote auth server response data; no persistence. Integration points include Docker authorizer/resolver code, challenge parsing, registry auth flows, and containerd version. Risks include scope splitting producing `[""]` when an empty scope parameter exists, error handling depending on response bodies, refresh-token grant choice when username is empty, and no direct tests for HTTP fetch functions in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/fetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/fetch_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/fetch_test.go

This test file covers `GenerateTokenOptions`. It builds Bearer challenges for multiple scopes, single scope, and no scope, then checks that realm, service, username, secret, and scope splitting are propagated into `TokenOptions`. It also verifies missing `realm` and syntactically invalid realm return errors.

The tests lock in the current behavior that the `scope` parameter is split by a single space. In the no-scope case, the challenge still includes `"scope": ""` in the test map, so the expected scopes become `strings.Split("", " ")`, a slice containing one empty string; that is a noteworthy behavior for downstream token requests.

Coverage gaps include `FetchToken`, `FetchTokenWithOAuth`, HTTP status errors, user-agent defaults, refresh token options, response decoding, and missing-token errors. The tests are pure in-memory and use no HTTP server or persistent state.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/fetch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/parse.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/parse.go

This file parses `WWW-Authenticate` headers into prioritized auth challenges. It defines bitmask-like authentication schemes for Basic, Digest, and Bearer, `Challenge`, and a sorter that orders higher scheme values first, making Bearer preferred over Digest and Basic.

`init` builds an octet classification table for RFC token and space parsing. `ParseAuthHeader` iterates canonical `WWW-Authenticate` headers, parses the auth scheme and parameters with `parseValueAndParams`, recognizes basic/digest/bearer schemes, appends challenges, and stable-sorts them by scheme priority. Parser helpers skip whitespace, parse tokens, and parse quoted values with backslash escaping.

There is no persistence. Integration points include token option generation and Docker registry authorizer behavior. Risks include a simplified parser that may not handle every legal auth header form, duplicate parameters overwriting earlier values, unclosed quoted strings returning empty values/rest, and unsupported schemes being ignored. Tests cover Bearer headers, empty quoted values, and fuzz arbitrary input for panics.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/parse_test.go -->
# Research: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/parse_test.go

This test file validates auth challenge parsing. `TestParseAuthHeaderBearer` formats Bearer headers with single and multiple scopes and asserts the parsed challenge preserves realm, service, and scope parameters. `TestParseAuthHeader` verifies an empty quoted parameter is retained and service is parsed correctly. `FuzzParseAuthHeader` seeds a Bearer header and fuzzes arbitrary strings to ensure parsing does not panic.

The tests are good signals for common Docker registry Bearer challenges and parser robustness. They cover quoted parameter values, empty quoted values, and space-containing scope strings. The fuzz test intentionally ignores semantic output and focuses on crash resistance.

Coverage gaps include Basic and Digest ordering, multiple `WWW-Authenticate` headers, escaped quotes/backslashes in values, malformed quoted strings, duplicate keys, unknown schemes, and whitespace edge cases. State is in-memory only. These tests support registry auth flows used by remote resolvers, index detection, and referrer detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/parse_test.go -->
