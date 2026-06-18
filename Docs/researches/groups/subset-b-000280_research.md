# subset-b-000280 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/util/utils.sh -->
# sources/cloud-native/stargz-snapshotter/script/util/utils.sh

## Purpose
Provides shared shell helpers for stargz-snapshotter integration and release scripts. It prepares throwaway registry credentials, checks JSON logs for remote snapshot preparation, and extracts version values from Dockerfiles.

## Important APIs, Types, And Functions
- `prepare_creds OUTPUT REGISTRY_HOST USER PASS` creates `auth` and `certs` directories, generates a self-signed certificate with a SAN for the registry host, and writes an htpasswd file.
- `check_remote_snapshots LOG_FILE` counts log records where `remote-snapshot-prepared` is `true` or `false` using `jq`.
- `get_version_from_arg DOCKERFILE ARGNAME` parses an `ARG` directive and strips an optional leading `v`.
- `go_base_version DOCKERFILE` extracts the tag from the first `FROM golang:` line.

## Control Flow
The helpers are meant to be sourced by other scripts. Credential preparation is linear: create directories, run `openssl req`, then run `htpasswd`. Log checking branches on local-fallback count, then remote-success count, then missing debug log. Version helpers pipeline `cat`, `grep`, `head`, `sed`, and `tr`.

## State And Persistence
Writes registry auth material under the caller-provided output directory. It does not clean generated certs or htpasswd files. Log and Dockerfile helpers are read-only.

## Dependencies And Integration Points
Depends on `openssl`, `htpasswd`, `jq`, and standard Unix text tools. The log key is coupled to `snapshot/snapshot.go` and `store/manager.go`, where remote preparation status is emitted.

## Risks And Edge Cases
`mkdir` lacks `-p`, so existing directories fail. The parsing helpers are simple text pipelines and can misread unusual Dockerfile formatting or repeated args. `check_remote_snapshots` requires JSON logs at debug level; otherwise valid behavior can be reported as failure because no marker exists.

## Test Signals
Useful signals are generated cert/key/auth files, `jq` counts showing at least one remote-prepared log and zero local-fallback logs, and expected extracted version strings from representative Dockerfiles.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/util/utils.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/util/verify-no-patent.sh -->
# sources/cloud-native/stargz-snapshotter/script/util/verify-no-patent.sh

## Purpose
Verifies release binaries do not include HashiCorp `golang-lru`'s patented `NewARC` symbol. It is a licensing/supply-chain guard copied and adapted from nerdctl.

## Important APIs, Types, And Functions
- Computes `CONTEXT` and `REPO` relative to the script location.
- Runs `make` with `GO_BUILD_LDFLAGS=""` so symbols remain visible.
- Iterates over `containerd-stargz-grpc`, `ctr-remote`, and `stargz-store`.
- Uses `go tool nm`, `grep -w -F main.main`, and `grep -w NewARC`.

## Control Flow
The script enables `set -eux -o pipefail`, builds the repository, emits one `.sym` file per binary, validates the symbol dump by requiring `main.main`, and fails if `NewARC` is present.

## State And Persistence
Writes symbol dump files under `out/*.sym` and rebuilds binaries under `out/` via the project `Makefile`. It does not remove these artifacts.

## Dependencies And Integration Points
Depends on Go tooling, `make`, shell utilities, and the project binary names. It is intended for CI or release verification after dependency changes.

## Risks And Edge Cases
The guard only checks linked symbols in the selected binaries. Build failures, stripped symbols, renamed outputs, or non-main artifacts can make the check fail or miss an affected path. Emptying `GO_BUILD_LDFLAGS` intentionally changes build flags for observability.

## Test Signals
Passing output includes `main.main` in each symbol file, no `NewARC` match, and a final `OK`. Failure signals include corrupt symbol dumps or any matching `NewARC` symbol.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/util/verify-no-patent.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/config.go -->
# sources/cloud-native/stargz-snapshotter/service/config.go

## Purpose
Defines the top-level service configuration shape for stargz snapshotter, embedding filesystem settings and adding keychain, resolver, and snapshotter-specific options.

## Important APIs, Types, And Functions
- `Config` embeds `fs/config.Config`, `KubeconfigKeychainConfig`, `CRIKeychainConfig`, `ResolverConfig`, and `SnapshotterConfig`.
- `KubeconfigKeychainConfig` controls Kubernetes secret-backed credentials and kubeconfig path.
- `CRIKeychainConfig` controls CRI PullImage auth capture and CRI image service/listen sockets.
- `ResolverConfig` aliases `service/resolver.Config`.
- `SnapshotterConfig.AllowInvalidMountsOnRestart` lets startup continue when remote snapshot remounting fails.

## Control Flow
This file has no executable flow; it provides TOML/JSON-tagged structs consumed by plugin and service constructors.

## State And Persistence
Configuration fields determine persistent roots, registry behavior, credential sources, and snapshotter recovery policy. The file itself stores no state.

## Dependencies And Integration Points
Couples the service package to `fs/config` and resolver configuration. `plugincore.RegisterPlugin` and `service.NewStargzSnapshotterService` consume these fields during containerd plugin initialization.

## Risks And Edge Cases
Embedded structs flatten configuration fields, so TOML layout and backward compatibility need care. `AllowInvalidMountsOnRestart` can leave unusable remote snapshots in containerd metadata that users must remove manually.

## Test Signals
Signals are mostly integration-level: config TOML should unmarshal into these structs, keychain/resolver toggles should alter plugin setup, and restart behavior should match `AllowInvalidMountsOnRestart`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/cri.go -->
# sources/cloud-native/stargz-snapshotter/service/cri.go

## Purpose
Builds a `source.GetSources` provider from CRI snapshot labels. It lets the filesystem resolve a specific target layer and optionally pre-resolve neighboring image layers for parallel lazy pulling.

## Important APIs, Types, And Functions
- Label constants cover image ref, target layer digest, full image layer list, descriptor URL maps, and target URLs.
- `sourceFromCRILabels(hosts)` returns a closure that parses labels into one `source.Source`.
- Uses `reference.Parse`, `digest.Parse`, and OCI descriptors/manifests.

## Control Flow
The closure requires `containerd.io/snapshot/cri.image-ref` and `containerd.io/snapshot/cri.layer-digest`. It parses optional comma-separated image layer labels, skips the target digest when building neighbors, attaches URLs from indexed labels, adds target URLs, and returns a manifest whose first layer is the target followed by neighbors.

## State And Persistence
No persistent state is written. State is derived from snapshot labels supplied during `Prepare`.

## Dependencies And Integration Points
Integrated by `service.NewFileSystem` ahead of default label parsing. It depends on containerd CRI label conventions and stargz filesystem `source.Source` semantics.

## Risks And Edge Cases
Missing or malformed labels fail source resolution. Neighbor layer metadata affects performance rather than correctness. URL labels are comma-split without escaping, so unusual URL values can misparse.

## Test Signals
Expected signals are successful source construction from CRI labels, digest parse failures for invalid labels, descriptor URL propagation, and fallback to other source providers when CRI labels are absent.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/cri.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/cri/cri.go -->
# sources/cloud-native/stargz-snapshotter/service/keychain/cri/cri.go

## Purpose
Implements a CRI image service proxy that records `PullImage` auth configs and exposes them as resolver credentials for lazy snapshot pulls.

## Important APIs, Types, And Functions
- `NewCRIKeychain(ctx, connectCRI)` returns a `resolver.Credential` and a `runtime.ImageServiceServer` proxy.
- `instrumentedService.credentials` looks up auth by normalized image reference and handles Docker Hub host aliases.
- `PullImage` stores request auth before forwarding to the backend CRI service.
- `RemoveImage` deletes stored auth for the image and forwards the request.
- `parseReference` normalizes Docker references through distribution and containerd parsers.

## Control Flow
A background goroutine retries backend CRI connection up to 100 times with 10 second sleeps. Proxy methods fail until a backend client exists. Image operations parse the image reference, mutate the auth map under a mutex when needed, and delegate to the real CRI client.

## State And Persistence
Auth configs are stored only in memory in `map[string]*runtime.AuthConfig`. They persist for the process lifetime until `RemoveImage` or restart.

## Dependencies And Integration Points
Depends on Kubernetes CRI API, containerd reference parsing, and `service/resolver.ParseAuth`. It is registered either by `plugincore` on a Unix socket or by `keychainconfig` on an existing gRPC server.

## Risks And Edge Cases
Credentials are process-memory only and keyed by normalized refs, so alternate tags/digests may not match. Backend connection retry can silently leave the proxy uninitialized. Auth entries can remain if images are never removed.

## Test Signals
Useful tests cover PullImage storing auth, credential lookup for Docker Hub aliases, RemoveImage cleanup, proxy errors before initialization, and parse failures for invalid image refs.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/cri/cri.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/dockerconfig/dockerconfig.go -->
# sources/cloud-native/stargz-snapshotter/service/keychain/dockerconfig/dockerconfig.go

## Purpose
Provides resolver credentials from the local Docker CLI config file.

## Important APIs, Types, And Functions
- `NewDockerconfigKeychain(ctx)` returns a `resolver.Credential` closure.
- Loads Docker config with `config.Load("")` on every credential request.
- Maps `docker.io` and `registry-1.docker.io` to Docker config's legacy index URL.
- Returns identity token preferentially, otherwise username/password.

## Control Flow
For each host/ref request, the closure loads config, normalizes Docker Hub host if needed, calls `GetAuthConfig`, and returns token or basic credentials.

## State And Persistence
No in-process cache is kept. Persistent state lives in the user's Docker config and credential helpers.

## Dependencies And Integration Points
Used as the default first credential provider in plugin and keychain config paths. Depends on Docker CLI config loading and resolver credential chaining.

## Risks And Edge Cases
Loading on every request can be expensive or blocked by credential helpers. Config load failures are logged and treated as anonymous credentials. Credential helper errors propagate from `GetAuthConfig`.

## Test Signals
Signals are Docker Hub key normalization, identity-token precedence, username/password fallback, anonymous behavior on missing config, and propagated helper errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/dockerconfig/dockerconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/keychainconfig/keychainconfig.go -->
# sources/cloud-native/stargz-snapshotter/service/keychain/keychainconfig/keychainconfig.go

## Purpose
Assembles resolver credential providers from Docker config, Kubernetes secrets, and CRI PullImage auth for consumers that already own a gRPC server.

## Important APIs, Types, And Functions
- `Config` contains booleans for kube/CRI keychains plus kubeconfig and CRI image service addresses.
- `ConfigKeychain(ctx, rpc, config)` returns ordered credential functions and registers a CRI image service proxy when enabled.
- `newCRIConn` creates a gRPC client with containerd dialer, insecure transport, bounded backoff, and default max message sizes.

## Control Flow
The function always starts with Docker config credentials. It conditionally appends kubeconfig credentials, then conditionally creates a backend CRI client factory, registers the proxy server on `rpc`, and appends CRI credentials.

## State And Persistence
This file stores no state itself. It wires in-memory CRI auth state and kubeconfig secret cache from the keychain implementations.

## Dependencies And Integration Points
Integrates `dockerconfig`, `kubeconfig`, `cri`, containerd defaults/dialer, gRPC, and CRI API registration. It is a reusable alternative to the full containerd plugin core.

## Risks And Edge Cases
`ConfigKeychain` assumes `config` and `rpc` are non-nil. Enabling CRI without a usable address registers a proxy that may never initialize. Credential order means Docker config wins over kube/CRI when it returns non-empty credentials.

## Test Signals
Tests should validate provider ordering, conditional registration, backend address override, gRPC dial options, and CRI credential availability after a proxied PullImage.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/keychainconfig/keychainconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/kubeconfig/kubeconfig.go -->
# sources/cloud-native/stargz-snapshotter/service/keychain/kubeconfig/kubeconfig.go

## Purpose
Implements a Kubernetes-secret-backed resolver credential provider by watching all `kubernetes.io/dockerconfigjson` secrets visible through a kubeconfig.

## Important APIs, Types, And Functions
- `WithKubeconfigPath` sets an explicit kubeconfig path.
- `NewKubeconfigKeychain` returns a `resolver.Credential` closure.
- `newKeychain` initializes immediately or waits asynchronously for a missing kubeconfig file.
- `initialize` loads client config, creates a Kubernetes client, and starts secret sync.
- `startSyncSecrets`, `runWorker`, and `processItem` maintain a map of parsed Docker config files.
- `credentials` scans cached configs for a host, with Docker Hub alias handling.

## Control Flow
Startup either initializes immediately or polls every 10 seconds for the configured kubeconfig. The informer lists/watches Docker config JSON secrets in all namespaces, queues add/update/delete keys, synchronizes existing items, and runs a worker that updates or removes cached config entries.

## State And Persistence
The keychain keeps an in-memory `map[namespace/name]*ConfigFile`. Persistent source state is Kubernetes Secret data. Cache lifetime follows the process and context cancellation.

## Dependencies And Integration Points
Depends on client-go informers, workqueues, Kubernetes CoreV1 secrets, Docker config parsing, and resolver credential chaining. It integrates with cluster image pull secrets independently of CRI PullImage.

## Risks And Edge Cases
Requires broad secret list/watch permissions. Missing kubeconfig is tolerated, but invalid kubeconfig disables syncing. Only dockerconfigjson secrets are supported; legacy dockercfg is a TODO. Credential selection scans map iteration order, so overlapping host credentials are nondeterministic.

## Test Signals
Signals include delayed initialization after kubeconfig appears, add/update/delete secret cache changes, Docker Hub alias matching, identity-token precedence, and anonymous behavior when no matching secret exists.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/kubeconfig/kubeconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/plugin/plugin.go -->
# sources/cloud-native/stargz-snapshotter/service/plugin/plugin.go

## Purpose
Registers the stargz snapshotter plugin through a package `init`, making it available when this package is imported by a containerd build.

## Important APIs, Types, And Functions
- Imports `service/plugincore`.
- `init()` calls `plugincore.RegisterPlugin()`.

## Control Flow
Registration happens automatically at package initialization time. There is no runtime branching in this file.

## State And Persistence
No file-local state. It mutates containerd's global plugin registry through `RegisterPlugin`.

## Dependencies And Integration Points
This is the thin public plugin entrypoint. Actual config, keychain, and snapshotter setup live in `service/plugincore/plugin.go`.

## Risks And Edge Cases
Import side effects are required. If the package is omitted from a build, the plugin is not registered.

## Test Signals
Containerd plugin registry should include snapshot plugin `stargz` after importing this package.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/plugincore/plugin.go -->
# sources/cloud-native/stargz-snapshotter/service/plugincore/plugin.go

## Purpose
Contains the containerd plugin registration and initialization logic for the `stargz` snapshotter.

## Important APIs, Types, And Functions
- `Config` embeds `service.Config` and adds `RootPath`, CRI keychain proxy socket path, and CRI-compatible registry config.
- `RegisterPlugin` registers a `SnapshotPlugin` with ID `stargz`.
- Init function sets platforms, resolves root, configures Docker/kube/CRI credentials, optionally serves a CRI image-service proxy socket, and constructs the snapshotter service.
- `newCRIConn` dials a containerd/CRI Unix socket with default message sizes and bounded gRPC backoff.

## Control Flow
During plugin init, the config is type-checked, root is selected from containerd properties or override, credentials are assembled, the optional CRI proxy is started on a Unix socket after removing any stale path, and `service.NewStargzSnapshotterService` is called with CRI-style registry hosts.

## State And Persistence
Exports the selected root through plugin metadata. If CRI keychain proxy is enabled, it creates/removes a Unix socket path and runs a gRPC server goroutine. Snapshotter and filesystem state live under the selected root.

## Dependencies And Integration Points
Integrates containerd plugin registry, CRI API, gRPC, Docker config, kubeconfig keychain, CRI keychain, resolver CRI config, and the service constructor.

## Risks And Edge Cases
CRI keychain requires both enable flag and proxy socket path. Stale socket removal is destructive to that path. If backend CRI address is absent, init fails. Plugin init starts goroutines whose lifecycle follows containerd.

## Test Signals
Signals include successful plugin registration, root export, optional keychain setup, Unix socket creation, backend CRI dial options, and snapshotter construction with configured registry hosts.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/plugincore/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/resolver/cri.go -->
# sources/cloud-native/stargz-snapshotter/service/resolver/cri.go

## Purpose
Builds registry host configuration from containerd CRI-compatible registry settings, including mirrors, host config directories, TLS files, and auth parsing.

## Important APIs, Types, And Functions
- `Registry`, `Mirror`, `RegistryConfig`, `AuthConfig`, and `TLSConfig` mirror CRI registry config shapes.
- `RegistryHostsFromCRIConfig` returns `source.RegistryHosts` either from `config_path` hosts files or deprecated mirrors/configs.
- `hostDirFromRoots`, `toRuntimeAuthConfig`, `getTLSConfig`, `defaultScheme`, `addDefaultScheme`, `registryEndpoints`, and `ParseAuth` implement CRI-compatible helpers.

## Control Flow
If `ConfigPath` has entries, host files drive configuration and inline auth is added as a credential fallback. Otherwise endpoints are built from host-specific or wildcard mirrors plus the default registry endpoint, retryable HTTP clients are configured with optional TLS, authorizers are attached, and pull/resolve hosts are returned.

## State And Persistence
No state is persisted. TLS and hosts directory files are read when registry hosts are configured or used.

## Dependencies And Integration Points
Depends on containerd Docker resolver/config helpers, CRI runtime auth types, retryable HTTP, TLS/x509, and stargz `source.RegistryHosts`. Used by `plugincore` for CRI-compatible plugin registry configuration.

## Risks And Edge Cases
`ConfigPath` causes mirror/TLS fields to be ignored except inline auth fallback. TLS cert/key must be provided as a pair. Base64 auth parsing trims NULs from passwords. Endpoint defaulting must handle localhost and Docker Hub default hosts correctly.

## Test Signals
Signals include correct endpoint ordering, wildcard mirror fallback, default endpoint insertion, HTTP scheme for localhost, TLS file load errors, host directory lookup across roots, and auth parsing for username/password, identity token, and base64 auth.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/resolver/cri.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/resolver/registry.go -->
# sources/cloud-native/stargz-snapshotter/service/resolver/registry.go

## Purpose
Defines stargz snapshotter's native registry resolver configuration and converts it into containerd Docker registry hosts.

## Important APIs, Types, And Functions
- `Config` maps registry hostnames to `HostConfig` and a global request timeout.
- `MirrorConfig` describes mirror host, insecure mode, per-host timeout, and extra headers.
- `Credential` is a `(host, ref) -> username, secret` callback.
- `RegistryHostsFromConfig` returns a `source.RegistryHosts` closure.
- `multiCredsFuncs` chains credential providers by first non-empty result.
- `makeStringSlice` validates and converts header array values.

## Control Flow
For a requested reference, the closure appends configured mirrors and the original host, builds a retryable client with timeout semantics, converts headers, attaches a Docker authorizer, switches scheme to HTTP for localhost/insecure mirrors, rewrites `docker.io` to `registry-1.docker.io`, and returns pull/resolve hosts.

## State And Persistence
No persistent state. HTTP clients and headers are created per registry-host resolution.

## Dependencies And Integration Points
Used by `service.NewFileSystem` unless custom registry hosts are supplied. It connects keychain credentials to containerd's Docker resolver.

## Risks And Edge Cases
Negative timeout disables HTTP timeout. Header values must be strings or arrays of strings. Credential provider order matters. Mirror host strings are not URL parsed here, so they must be compatible with containerd `docker.RegistryHost` expectations.

## Test Signals
Expected tests cover timeout defaults/overrides/no-timeout, HTTP selection for insecure/local mirrors, Docker Hub rewrite, header conversion failures, and credential chaining precedence.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/resolver/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/service.go -->
# sources/cloud-native/stargz-snapshotter/service/service.go

## Purpose
Wires registry resolution, source-label parsing, filesystem construction, and snapshotter construction into reusable service constructors.

## Important APIs, Types, And Functions
- Options: `WithCredsFuncs`, `WithCustomRegistryHosts`, and `WithFilesystemOptions`.
- `NewStargzSnapshotterService` builds the filesystem and `snapshot.NewSnapshotter` with async removal and optional invalid-mount tolerance.
- `NewFileSystem` selects registry hosts, detects overlay opaque mode, and creates `stargzfs.NewFilesystem`.
- `snapshotterRoot`, `fsRoot`, `sources`, and `Supported` are helper APIs.

## Control Flow
Options are applied, registry hosts come from explicit override or resolver config plus credentials, `NeedsUserXAttr` selects trusted vs user overlay opaque semantics, source providers are chained CRI-first then default-label, external TOC decompressor support is added, and filesystem/snapshotter roots are derived under the service root.

## State And Persistence
Filesystem state is under `<root>/stargz`; snapshot metadata and overlay dirs are under `<root>/snapshotter`. Async removal defers directory cleanup to snapshotter cleanup.

## Dependencies And Integration Points
Integrates containerd snapshot interfaces, overlay utilities, stargz filesystem, layer metadata, resolver credentials, source labels, and external TOC decompression.

## Risks And Edge Cases
Failure to detect `userxattr` only logs a warning and assumes the zero value. Source provider ordering can hide default-label errors behind CRI-label errors only after CRI fails. Async removal changes when disk space is reclaimed.

## Test Signals
Signals include successful filesystem creation with configured registry hosts, correct root paths, overlay support checks, source fallback behavior, and snapshotter startup with remote snapshot restore.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/snapshot/snapshot.go -->
# sources/cloud-native/stargz-snapshotter/snapshot/snapshot.go

## Purpose
Implements a containerd snapshotter that behaves like overlayfs for normal snapshots and can internally commit remotely mounted lazy layers as snapshots.

## Important APIs, Types, And Functions
- `FileSystem` abstracts remote `Mount`, `Check`, and `Unmount` operations.
- Options: `AsynchronousRemove`, `NoRestore`, and `AllowInvalidMountsOnRestart`.
- `NewSnapshotter` initializes root, d_type support, metadata store, snapshot directory, userxattr detection, and remote restore.
- Snapshotter methods implement `Stat`, `Update`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Walk`, `Cleanup`, and `Close`.
- Helpers include `createSnapshot`, `mounts`, `prepareRemoteSnapshot`, `checkAvailability`, and `restoreRemoteSnapshot`.

## Control Flow
`Prepare` first creates an active snapshot. If labels include `containerd.io/snapshot.ref`, it asks the remote filesystem to mount into the snapshot `fs` directory, labels it remote, commits it to the target name, logs preparation status, and returns `AlreadyExists` to containerd. Non-remote flows return bind or overlay mounts. `Mounts` and new child snapshots verify remote parent availability through `FileSystem.Check`.

## State And Persistence
Metadata lives in `metadata.db`; snapshot directories live under `root/snapshots/<id>/{fs,work}`. Remote snapshots are marked with labels and remounted on startup unless disabled. Cleanup unmounts through `FileSystem.Unmount` before removing directories.

## Dependencies And Integration Points
Built on containerd snapshot storage, overlay mount conventions, continuity disk usage, mountinfo, overlayutils, errdefs, and the stargz filesystem implementation. Log keys are consumed by scripts/tests.

## Risks And Edge Cases
Remote prepare failures fall back to local only before the remote filesystem has done work; commit failures after mount are returned without reusing the key. Startup force-unmounts mounts under the root before restoration. `AllowInvalidMountsOnRestart` can leave metadata for unusable layers. Parent availability checks run concurrently and any remote check failure makes the layer unavailable.

## Test Signals
Tests validate remote prepare/commit labels, overlay mounts over remote parents, failure detection through `Check`, overlayfs compatibility via containerd testsuite, bind/overlay mount options, view behavior, and root-required bind mount scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/snapshot/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/snapshot/snapshot_test.go -->
# sources/cloud-native/stargz-snapshotter/snapshot/snapshot_test.go

## Purpose
Tests remote snapshot behavior and overlayfs compatibility for the custom snapshotter.

## Important APIs, Types, And Functions
- `prepareWithTarget` asserts remote prepare returns `ErrAlreadyExists` and returns the committed target name.
- `TestRemotePrepare`, `TestRemoteOverlay`, `TestRemoteCommit`, and `TestFailureDetection` cover remote-specific flows.
- `bindFs` simulates a remote filesystem using bind mounts and configurable check failures.
- `dummyFs` supports overlay compatibility tests without remote mounting.
- Overlay tests cover containerd `SnapshotterSuite`, mounts, commits, reads, and views.

## Control Flow
Remote tests create temp roots, instantiate snapshotters, prepare remote layers with labels, optionally build overlay children, mount/read/write data, and remove snapshots. Failure detection builds stacks of remote and overlay layers, toggles `bindFs.checkFailure`, and expects unavailable errors. Overlay tests exercise normal snapshot lifecycle.

## State And Persistence
Tests create temp directories, bind mounts, snapshot metadata, and overlay dirs, then remove/unmount via defers. Some tests require root privileges.

## Dependencies And Integration Points
Depends on containerd snapshot testsuite, mount helpers, storage metadata access, `errdefs`, and root-capable Linux mount behavior.

## Risks And Edge Cases
Root and kernel overlay support are required for several tests. Bind mount cleanup relies on defers and snapshot removal. Failure cases depend on labels marking broken mountpoints.

## Test Signals
Strong signals include committed remote snapshots with target labels, expected bind/overlay mount options, persisted file contents through commit/readback, `ErrUnavailable` for broken remote parents, and containerd snapshotter suite compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/snapshot/snapshot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/fs.go -->
# sources/cloud-native/stargz-snapshotter/store/fs.go

## Purpose
Implements the FUSE filesystem for stargz-store, exposing image references and layers as a virtual tree that can resolve lazy layers, expose layer contents, raw blobs, and metadata.

## Important APIs, Types, And Functions
- `Mount(ctx, mountpoint, layerManager, debug)` creates and mounts a go-fuse server.
- `rootnode.Lookup` exposes `pool` and base64-encoded image reference directories.
- `refnode.Lookup` exposes digest-named layer directories; `Rmdir` releases layer references.
- `layernode.Create` treats creating hidden `use` as a reference increment.
- `layernode.Lookup` serves `info`, `diff`, `blob`, and hidden `use` names.
- `blobfile.Read` reads raw layer bytes with direct cache and context cancellation.
- Attribute and inode helpers maintain stable permissions and unique IDs.

## Control Flow
Mount setup chooses `fusermount` with `suid` when available, otherwise direct mount. Lookups decode a ref, parse a digest, resolve layer info or data through `LayerManager`, verify target digest, and then either materialize memory files, raw blob file handles, or the layer root node. Reference accounting is driven by synthetic file creation and directory removal.

## State And Persistence
The FUSE tree is virtual, but it references persistent pool metadata under `refPool.root()` and layer caches managed by `LayerManager`. Inode IDs are in-memory and released on `OnForget`.

## Dependencies And Integration Points
Depends on go-fuse, containerd references, opencontainers digests, stargz layer interfaces, remote/cache options, and `LayerManager` for resolution/lifetime.

## Risks And Edge Cases
Clients must know to base64-encode image refs. `Rmdir` intentionally returns `ENOENT` after release signaling. Resolve failures are logged with remote preparation status. Inode ID allocation is linear and can become expensive at extreme counts.

## Test Signals
Useful tests would mount the store, resolve `pool`, base64 ref directories, `info` JSON, `diff` contents, `blob` reads, hidden `use` reference increments, and release cleanup through `Rmdir`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/manager.go -->
# sources/cloud-native/stargz-snapshotter/store/manager.go

## Purpose
Manages lazy layer resolution, caching, prefetch/background fetch, metrics, and reference lifetimes for stargz-store.

## Important APIs, Types, And Functions
- `NewLayerManager` creates a ref pool, background task manager, layer resolver, metrics controller, locks, and maps.
- `getLayerInfo` returns containers/storage-compatible layer metadata.
- `getLayer` resolves all layers in a reference concurrently until the requested TOC digest is cached.
- `resolveLayer` serializes duplicate layer resolution, handles zstd chunked TOC offset annotations, resolves the layer, starts prefetch/background fetch, and caches the layer.
- `use` and `release` maintain refcounts and call `layer.Done` when unused.
- `genLayerInfo` maps layer digest to image config DiffID and TOC digest.

## Control Flow
A layer request loads manifest/config, starts goroutines to resolve each manifest layer with a background context, waits for the desired TOC digest, and returns timeout or all-done errors if missing. Resolution is cached per ref/layer digest to avoid repeated failed work until the ref is fully released.

## State And Persistence
In-memory maps hold layer objects, refcounts, and resolution errors. The ref pool persists manifest/config metadata briefly under `pool`. Metrics are registered unless disabled. Background fetch/prefetch state is owned by layer objects.

## Dependencies And Integration Points
Integrates metadata store, stargz layer resolver, external TOC remote decompressor, zstd chunked annotations, task manager, named mutex, metrics, and registry hosts.

## Risks And Edge Cases
`errChan` is allocated but never written, so resolution failures are observed through timeout or all-done rather than immediate error propagation. Concurrent goroutines use `context.Background`, so client cancellation does not stop resolution. Refcount map deletion includes a suspicious `delete(r.refcounter, tocDigest.String())` against the top-level map.

## Test Signals
Signals should cover cache hits, duplicate resolution locking, prefetch/background fetch toggles, refcount release calling `Done`, manifest/config mismatch errors, missing target TOC timeout/all-done paths, and generated layer info flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/pb/control.pb.go -->
# sources/cloud-native/stargz-snapshotter/store/pb/control.pb.go

## Purpose
Generated Go protobuf bindings for the stargz store control API.

## Important APIs, Types, And Functions
- Defines the `InfoRequest` message type for `github.com/containerd/stargz-snapshotter/store/pb`.
- Provides standard proto reflection, reset/string/proto message methods, raw descriptor data, exporter setup, and `File_store_pb_control_proto`.
- Generated metadata comes from `store/pb/control.proto`.

## Control Flow
Generated init functions build and register the protobuf file descriptor. Message methods delegate to `protoimpl` runtime helpers.

## State And Persistence
No application state is persisted. Package globals cache descriptor and message info metadata.

## Dependencies And Integration Points
Depends on `google.golang.org/protobuf` runtime. Consumers should import the generated package rather than manually parsing control proto payloads.

## Risks And Edge Cases
Manual edits will be overwritten by regeneration. Generated code must stay in sync with `control.proto` and the protoc/protoc-gen-go versions used by `generate.go`.

## Test Signals
Compilation and proto reflection for `InfoRequest` are the main signals; regeneration should produce a stable diff when the proto is unchanged.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/pb/control.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/pb/control.proto -->
# sources/cloud-native/stargz-snapshotter/store/pb/control.proto

## Purpose
Defines the protobuf schema for stargz store control messages.

## Important APIs, Types, And Functions
- Uses `syntax = "proto3"`.
- Package is `containerd_stargz_grpc`.
- `go_package` points to `github.com/containerd/stargz-snapshotter/store/pb`.
- Declares an empty `InfoRequest` message.

## Control Flow
No control flow; this is schema data consumed by protoc.

## State And Persistence
No state. Wire compatibility is determined by message and field definitions.

## Dependencies And Integration Points
Drives `control.pb.go` generation and any gRPC/control-plane code that imports the store pb package.

## Risks And Edge Cases
`InfoRequest` is empty, so future fields must use compatible proto3 numbering. Package/name changes would break generated Go imports and wire compatibility.

## Test Signals
Regenerating `control.pb.go` and compiling downstream users validates the schema.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/pb/control.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/pb/generate.go -->
# sources/cloud-native/stargz-snapshotter/store/pb/generate.go

## Purpose
Documents protobuf generation for the store pb package through a Go generate directive.

## Important APIs, Types, And Functions
- `//go:generate protoc -I=. --go_out=. --go_opt=paths=source_relative control.proto`.
- Package is `pb`.

## Control Flow
`go generate` invokes `protoc` from this directory to regenerate `control.pb.go` with source-relative paths.

## State And Persistence
Regeneration rewrites generated protobuf Go output. This file itself has no runtime state.

## Dependencies And Integration Points
Requires `protoc` and `protoc-gen-go` in the developer environment. Keeps generated bindings coupled to `control.proto`.

## Risks And Edge Cases
Different generator versions can churn generated files. Missing protoc tooling causes `go generate` failure.

## Test Signals
Running `go generate ./store/pb` followed by `go test` or `go test ./store/pb` should leave generated code compiling.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/pb/generate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/refs.go -->
# sources/cloud-native/stargz-snapshotter/store/refs.go

## Purpose
Caches image manifest/config metadata by reference for stargz-store and manages reference lifetimes around that metadata.

## Important APIs, Types, And Functions
- `newRefPool` creates `<root>/pool` and an LRU cache with eviction cleanup.
- `loadRef` reads manifest/config from disk or fetches and writes them.
- `use` and `release` pin references in the LRU cache while layers are in use.
- `readManifestAndConfig`, `writeManifestAndConfig`, and `fetchManifestAndConfig` handle metadata I/O and remote resolution.
- Path helpers derive digest-based metadata dirs.

## Control Flow
`loadRef` first attempts disk reuse; on failure it resolves the image using registry hosts restricted to the reference host, fetches the platform manifest and config, writes both JSON files, adds an LRU reference, and schedules release after 120 seconds unless pinned.

## State And Persistence
Manifest/config JSON are stored under `pool/metadata--<digest(ref)>`. LRU eviction removes metadata directories only after reference counts drop to zero.

## Dependencies And Integration Points
Uses containerd Docker resolver, platform selection, `containerdutil.FetchManifestPlatform`, `cacheutil.LRUCache`, and `source.RegistryHosts`. Consumed by `LayerManager`.

## Risks And Edge Cases
Platform is hardcoded to default. Disk cache read failures always trigger fetch. Timed goroutine release relies on clients calling returned done functions and reference counters staying balanced. Eviction removes entire metadata dirs.

## Test Signals
Signals include disk reuse after first fetch, metadata JSON correctness, LRU eviction cleanup after done, pin/unpin behavior through use/release, and host mismatch rejection in the temporary resolver.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/refs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/task/task.go -->
# sources/cloud-native/stargz-snapshotter/task/task.go

## Purpose
Coordinates lower-priority background work so it yields to prioritized operations such as mounts/checks.

## Important APIs, Types, And Functions
- `NewBackgroundTaskManager(concurrency, period)` constructs semaphores and condition variables.
- `DoPrioritizedTask` increments the prioritized count and closes a notification channel to cancel active background tasks.
- `DonePrioritizedTask` waits the silence period, decrements the count, and broadcasts.
- `InvokeBackgroundTask(do, timeout)` retries a cancellable background function until it completes without priority interruption.

## Control Flow
Background invocation waits while priority count is positive, acquires a weighted semaphore slot, snapshots the current notification channel, runs the task under a timeout context, cancels/retries if a priority task starts, and exits only after the task completes.

## State And Persistence
All state is in memory: atomic priority count, semaphore occupancy, notification channels, and condition variable waiters.

## Dependencies And Integration Points
Used by layer prefetch/background fetch to avoid competing with foreground lazy reads. Depends on `golang.org/x/sync/semaphore`.

## Risks And Edge Cases
`DonePrioritizedTask` decrements asynchronously after the silence period, so unbalanced calls can permanently block or make counts negative. `Acquire` uses `context.Background` and ignores errors. Background tasks must honor context cancellation.

## Test Signals
Tests cover priority blocking, concurrency limits, cancellation on priority start, resume after priority completion, and sequential task completion.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/task/task.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/task/task_test.go -->
# sources/cloud-native/stargz-snapshotter/task/task_test.go

## Purpose
Verifies `BackgroundTaskManager` scheduling, cancellation, concurrency, and retry behavior.

## Important APIs, Types, And Functions
- `TestBackgroundTasks` table drives scenarios named `privilege_running`, `concurrency`, `cancel`, `resume`, `finish_partial`, and `finish_all`.
- `sampleTask` records started/done/canceled flags and blocks on either finish channel or context cancellation.
- Helpers `doGo` and `wait` coordinate goroutine startup and polling assertions.

## Control Flow
Each test creates a manager and four sample tasks, runs a scenario that invokes background work and priority transitions, then checks final task flags. Timeout polling fails after five seconds.

## State And Persistence
All state is in-memory task flags, channels, and manager counters. No files are written.

## Dependencies And Integration Points
Directly tests `task.go` and indirectly validates assumptions used by layer prefetch/background fetch code.

## Risks And Edge Cases
Timing sleeps make tests sensitive to slow CI, though waits use generous timeouts. The test names use `privilege` where the implementation says prioritized, but behavior is clear.

## Test Signals
Passing means background tasks do not start during priority work, concurrency is capped, running tasks are canceled when priority starts, tasks resume after silence, and semaphore slots are released after completion.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/task/task_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/lrucache.go -->
# sources/cloud-native/stargz-snapshotter/util/cacheutil/lrucache.go

## Purpose
Provides an LRU cache whose eviction callback is delayed until all external references release the value.

## Important APIs, Types, And Functions
- `LRUCache` wraps `groupcache/lru.Cache` and exposes `OnEvicted`.
- `NewLRUCache(maxEntries)` installs internal eviction behavior.
- `Get` increments a refcount and returns a one-shot `done` callback.
- `Add` returns an existing value without replacement or adds a new refcounted value.
- `Remove` evicts from LRU while respecting outstanding references.
- `refCounter` handles initialize/finalize/inc/dec semantics.

## Control Flow
Each cached value has one cache-owned reference plus caller references. LRU eviction/finalize drops the cache reference; caller `done` drops caller refs. `OnEvicted` fires only when the refcount reaches zero.

## State And Persistence
State is in-memory LRU entries, refcounts, and callbacks. No persistence.

## Dependencies And Integration Points
Used by store ref pooling to avoid removing manifest/config directories while still referenced. Depends on `github.com/golang/groupcache/lru`.

## Risks And Edge Cases
Callers must invoke `done` exactly once; leaked callbacks delay cleanup. Refcount can go negative if implementation bugs bypass the once wrapper. Callback runs while locks are held, so slow callbacks can block cache operations.

## Test Signals
Tests validate duplicate add behavior, get behavior, remove-delayed eviction, and eviction after LRU overflow once references are released.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/lrucache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/lrucache_test.go -->
# sources/cloud-native/stargz-snapshotter/util/cacheutil/lrucache_test.go

## Purpose
Tests the delayed-eviction semantics of `LRUCache`.

## Important APIs, Types, And Functions
- `TestLRUAdd` verifies duplicate `Add` returns the original cached value.
- `TestLRUGet` verifies retrieval and value identity.
- `TestLRURemove` verifies `OnEvicted` waits for all `done` callbacks.
- `TestLRUEviction` verifies LRU overflow does not finalize until references are released.

## Control Flow
Tests create small caches, attach an `OnEvicted` recorder, add/get/remove entries, call returned done functions, and assert eviction ordering/counts.

## State And Persistence
State is in-memory cache entries and a test slice of evicted keys.

## Dependencies And Integration Points
Directly covers `lrucache.go`, which is used by store reference metadata caching.

## Risks And Edge Cases
Tests focus on single-threaded behavior and do not stress concurrent callers or slow callbacks.

## Test Signals
Passing demonstrates that cached values are stable, duplicate additions do not replace data, and eviction callbacks are reference-count gated.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/lrucache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/ttlcache.go -->
# sources/cloud-native/stargz-snapshotter/util/cacheutil/ttlcache.go

## Purpose
Implements a TTL cache with reference-counted values so entries expire only after their timer fires and all active users release them.

## Important APIs, Types, And Functions
- `TTLCache` stores refcounted entries and a TTL duration.
- `NewTTLCache(ttl)` constructs the map.
- `Get` returns value plus `done(evict bool)` and increments references.
- `Add` inserts or returns existing value and starts/resets timer semantics.
- `Remove` forces eviction when references drain.
- `evictLocked` and `decreaseOnceFunc` coordinate timer and caller releases.
- `refCounterWithTimer` holds value, key, count, timer, and evicted flag.

## Control Flow
Adding creates a timer that marks the entry evicted after TTL. Active callers hold references through `done`; eviction removes the map entry and final cleanup waits for refs to reach zero. A caller can request eviction through the boolean done argument.

## State And Persistence
All state is in-memory maps, timers, and refcounts. No persistence.

## Dependencies And Integration Points
A general utility for short-lived reference-sensitive caches. It uses `time.Timer` and synchronization primitives.

## Risks And Edge Cases
Timer/refcount interactions are subtle; callers must call done once. Very short TTLs can expire while values are in use, making future gets miss even though cleanup waits. Boolean `done` semantics require careful caller discipline.

## Test Signals
Tests cover add/get/remove, overwritten removal, TTL expiration, and quick done behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/ttlcache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/ttlcache_test.go -->
# sources/cloud-native/stargz-snapshotter/util/cacheutil/ttlcache_test.go

## Purpose
Validates TTL cache insertion, retrieval, removal, expiration, and reference-gated cleanup.

## Important APIs, Types, And Functions
- Tests include `TestTTLAdd`, `TestTTLGet`, `TestTTLRemove`, `TestTTLRemoveOverwritten`, `TestTTLEviction`, and `TestTTLQuickDone`.
- Use small TTLs and explicit done callbacks to assert visibility and eviction timing.

## Control Flow
Each test creates a cache, adds keys, checks cached vs new values, invokes done callbacks with eviction flags, sleeps/polls across TTL boundaries, and validates whether entries remain accessible.

## State And Persistence
State is in-memory cache maps and timers. No files are touched.

## Dependencies And Integration Points
Directly covers `ttlcache.go`; behavior is relevant wherever entries represent resources needing delayed cleanup.

## Risks And Edge Cases
Timing-based tests can be flaky under heavy load. They do not fully cover concurrent access races.

## Test Signals
Passing shows duplicate add preservation, get success, explicit remove/overwrite behavior, TTL expiration after references drain, and safe quick release.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/ttlcache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/containerdutil/manifest.go -->
# sources/cloud-native/stargz-snapshotter/util/containerdutil/manifest.go

## Purpose
Provides containerd/OCI manifest utilities for selecting platform-specific manifests, validating media types, and fetching manifests from remotes.

## Important APIs, Types, And Functions
- `ManifestDesc(ctx, provider, image, platform)` resolves an image/index descriptor to a manifest descriptor for a platform.
- `ValidateMediaType` inspects JSON shape and compares it to expected OCI/Docker media types.
- `FetchManifestPlatform(ctx, fetcher, desc, platform)` fetches and decodes the selected manifest.
- `unknownDocument` helps infer schema fields before strict media-type handling.

## Control Flow
Manifest selection reads descriptor content, handles image index/manifest list by iterating manifests and matching platforms, validates media types, and returns a concrete manifest descriptor. Fetching then opens the descriptor from a remote fetcher and decodes OCI manifest JSON.

## State And Persistence
No persistent state. It streams content from containerd content providers or remote fetchers.

## Dependencies And Integration Points
Used by store ref pool when resolving image manifest/config. Depends on containerd content/remotes/images helpers, platforms matching, and OCI/Docker media type constants.

## Risks And Edge Cases
Platform defaulting is caller-defined. Unknown or mismatched media types fail validation. Multi-platform images without a matching platform return errors even if other manifests exist.

## Test Signals
Expected tests include single manifest pass-through, index platform match/miss, media-type mismatch detection, Docker vs OCI schema handling, and remote fetch decode errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/containerdutil/manifest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/decompressutil/gzip.go -->
# sources/cloud-native/stargz-snapshotter/util/decompressutil/gzip.go

## Purpose
Selects a gzip decompression helper for eStargz, preferring external commands when configured and available with fallback to Go's standard gzip reader.

## Important APIs, Types, And Functions
- Package globals cache discovered paths for `gzip`, `pigz`, and `igzip` behind `sync.Once`.
- `GetGzipHelperFunc(gzipHelper)` validates helper name and returns an `estargz.GzipHelperFunc`.
- `getCmdGzipHelperFunc` runs `<cmd> -d -c` with stdin/stdout pipes.
- `getGoGzipHelperFunc` wraps `gzip.NewReader`.
- `findCmdPath` uses `exec.LookPath`.

## Control Flow
On first use, command paths are discovered. The requested helper name selects a cached path; missing paths print a warning and use Go gzip, invalid names return an error. External helpers start a subprocess and report wait/stderr failures through the pipe.

## State And Persistence
Only in-memory command path cache is retained. No files are written.

## Dependencies And Integration Points
Used by eStargz decompression configuration. Depends on host binaries for parallel/accelerated decompression when available.

## Risks And Edge Cases
Command discovery is one-time unless tests reset `sync.Once`. External helper failures surface while reading, not at helper creation. Warning uses stdout, which can be noisy in libraries.

## Test Signals
Tests cover invalid helper errors, available command decompression, fallback to Go gzip when missing, and exact decompressed bytes.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/decompressutil/gzip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/decompressutil/gzip_test.go -->
# sources/cloud-native/stargz-snapshotter/util/decompressutil/gzip_test.go

## Purpose
Tests gzip helper selection and decompression behavior for external and Go fallback helpers.

## Important APIs, Types, And Functions
- `TestGetGzipHelperFunc` detects available `gzip`, `pigz`, and `igzip` commands.
- Builds compressed test data with Go `gzip.Writer`.
- Resets `findCmdOnce` after the test to avoid leaking discovery state.

## Control Flow
The test skips if no helper command is available, builds cases for invalid helper, available helpers, and unavailable fallback helpers, obtains helper functions, reads decompressed output, and compares bytes.

## State And Persistence
Creates a temp file but primarily uses in-memory buffers. Mutates package globals for command path discovery and resets `sync.Once`.

## Dependencies And Integration Points
Depends on environment-installed gzip-family commands for full coverage and on `gzip.go` helper selection.

## Risks And Edge Cases
Coverage varies by CI environment depending on installed commands. A temp file is created but not central to the assertions.

## Test Signals
Passing means invalid names fail, available helpers decompress correctly, unavailable requested helpers return Go `*gzip.Reader`, and output matches original data.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/decompressutil/gzip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/ioutils/countwriter.go -->
# sources/cloud-native/stargz-snapshotter/util/ioutils/countwriter.go

## Purpose
Provides a simple writer that counts bytes written without storing them.

## Important APIs, Types, And Functions
- `CountWriter` holds an `int64` byte count.
- `Write(p []byte)` increments the count by `len(p)` and reports full success.
- `Size()` returns the accumulated count.

## Control Flow
Each write converts input length to int64, adds it to the counter, and returns `len(p), nil`.

## State And Persistence
State is the in-memory byte count. It is not synchronized for concurrent writes.

## Dependencies And Integration Points
Useful anywhere an `io.Writer` is needed solely to measure serialized size or stream length.

## Risks And Edge Cases
Not thread-safe. Count can overflow int64 on extreme input totals. It never returns write errors, so it should not be used to simulate real sink failures.

## Test Signals
Expected tests write several byte slices and assert returned counts and final `Size`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/ioutils/countwriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/namedmutex/namedmutex.go -->
# sources/cloud-native/stargz-snapshotter/util/namedmutex/namedmutex.go

## Purpose
Implements a keyed mutex that serializes work by string name while allowing unrelated names to proceed concurrently.

## Important APIs, Types, And Functions
- `NamedMutex` holds a map from name to lock entry and a global mutex.
- `Lock(name)` creates or reuses a per-name lock and increments its reference count.
- `Unlock(name)` releases the per-name lock, decrements references, and removes unused entries.

## Control Flow
Lock first protects the map, obtains/creates the named lock entry, increments count, unlocks the map, then locks the named mutex. Unlock checks for an entry, unlocks it, decrements count under the global lock, and deletes the entry at zero.

## State And Persistence
In-memory map of named locks and refcounts only.

## Dependencies And Integration Points
Used by `LayerManager.resolveLayer` to prevent duplicate resolution of the same ref/layer digest.

## Risks And Edge Cases
Unlocking an unknown name is a no-op or error-handled only by code path details, so misuse can hide bugs. Callers must balance lock/unlock exactly. Entries are removed only when refcount reaches zero.

## Test Signals
Expected tests cover same-name serialization, different-name parallelism, refcount cleanup, and balanced unlock behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/namedmutex/namedmutex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/compression.go -->
# sources/cloud-native/stargz-snapshotter/util/testutil/compression.go

## Purpose
Defines compression factories used by tests to create gzip, zstd chunked, and external-TOC eStargz compressors/decompressors behind a common interface.

## Important APIs, Types, And Functions
- `Compression` combines estargz compressor/decompressor behavior with `DecompressTOC`.
- `CompressionFactory` returns a fresh `Compression`.
- `ZstdCompressionWithLevel`, `GzipCompressionWithLevel`, and `ExternalTOCGzipCompressionWithLevel` construct configured factories.
- External TOC compression wires a decompressor that reads TOC bytes from the matching compressor.

## Control Flow
Factory calls create compressor/decompressor pairs. External TOC factory captures the compressor in a closure so TOC reads reflect the generated external TOC data.

## State And Persistence
Compression state is per factory invocation. No files are written.

## Dependencies And Integration Points
Used by tests around estargz metadata and blob generation. Depends on estargz, external TOC, zstdchunked, and klauspost zstd.

## Risks And Edge Cases
External TOC decompressor is tied to the compressor instance, so reusing it across unrelated blobs would be invalid. Compression level validity is delegated to underlying libraries.

## Test Signals
Signals include round-trip compression/decompression, TOC decompression success, and expected behavior at chosen compression levels.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/compression.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/ensurehello.go -->
# sources/cloud-native/stargz-snapshotter/util/testutil/ensurehello.go

## Purpose
Downloads a known `hello-world` OCI archive and imports it into a temporary containerd content store for tests.

## Important APIs, Types, And Functions
- `HelloArchiveURL` and `HelloArchiveDigest` define the fixture source and expected archive digest.
- `EnsureHello(ctx)` downloads, verifies, gunzips, imports the OCI index, and returns descriptor plus content store.

## Control Flow
HTTP GET streams through a SHA256 tee into a gzip reader, creates a temp local content store, imports the index with `archive.ImportIndex`, then compares the downloaded gzip digest to the expected digest.

## State And Persistence
Creates a temporary content store directory. The caller receives the store but not an explicit cleanup callback in this function.

## Dependencies And Integration Points
Depends on network access to GitHub releases, Go gzip, containerd local content store, and OCI archive import helpers.

## Risks And Edge Cases
Network availability and remote fixture stability affect tests. Temp directories can leak if callers do not clean them. Digest verifies the compressed archive, not each imported object independently.

## Test Signals
Successful return includes a descriptor, usable content store, and digest match. Failures identify download, gzip, import, or digest mismatch problems.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/ensurehello.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/estargz.go -->
# sources/cloud-native/stargz-snapshotter/util/testutil/estargz.go

## Purpose
Builds in-memory eStargz blobs from synthetic tar entries for tests.

## Important APIs, Types, And Functions
- `buildEStargzOptions` stores estargz and tar builder options.
- `WithEStargzOptions` and `WithBuildTarOptions` configure build behavior.
- `BuildEStargz(ents, opts...)` returns a section reader and TOC digest.

## Control Flow
Options are applied, `BuildTar` creates a tar stream into a buffer, `estargz.Build` converts it, the resulting stream is copied into memory, and a new `io.SectionReader` plus TOC digest are returned.

## State And Persistence
All data is in memory. No files are written.

## Dependencies And Integration Points
Used by tests needing deterministic eStargz blobs. Depends on local tar test utilities and the estargz builder.

## Risks And Edge Cases
Large fixtures are fully buffered twice. Option errors are ignored by the current loop, so failing option functions would not stop the build.

## Test Signals
Tests should verify readable eStargz output, expected TOC digest shape, and preservation of tar entry metadata/content.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/estargz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/tar.go -->
# sources/cloud-native/stargz-snapshotter/util/testutil/tar.go

## Purpose
Provides utilities for constructing synthetic tar archives for tests, including files, directories, symlinks, hardlinks, device metadata, xattrs, and whiteouts.

## Important APIs, Types, And Functions
- `TarEntry` describes path, body, mode, link target, type, xattrs, uid/gid, and times.
- Build options configure tar behavior and entry transforms.
- `BuildTar` writes tar headers and content to a pipe/reader for callers.
- Helpers normalize directory paths, create whiteout entries, and fill tar headers.

## Control Flow
The builder iterates entries, prepares a tar header according to type and options, writes headers, writes file bodies for regular files, and closes the tar writer/pipe with any error.

## State And Persistence
Archives are generated as streams/in-memory data. No persistent files are written unless callers consume the stream into files.

## Dependencies And Integration Points
Used by eStargz and metadata tests to create controlled layer blobs. Depends on Go `archive/tar` and filesystem metadata constants.

## Risks And Edge Cases
Malformed entries can create invalid tar headers. Streaming through pipes means callers must read to observe writer errors. Platform-specific metadata such as devices and xattrs can behave differently across consumers.

## Test Signals
Expected signals include tar readers seeing the requested entries, modes, links, xattrs, uid/gid, times, whiteouts, and file payload bytes.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/tar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/util.go -->
# sources/cloud-native/stargz-snapshotter/util/testutil/util.go

## Purpose
Provides a small random byte helper for tests.

## Important APIs, Types, And Functions
- `RandomBytes(n int)` allocates `n` bytes and fills them with cryptographic randomness.

## Control Flow
The function allocates a slice, calls `rand.Read`, and returns bytes or error.

## State And Persistence
No persistent state. Randomness comes from the OS crypto random source.

## Dependencies And Integration Points
Used by tests that need non-repetitive content payloads.

## Risks And Edge Cases
Can fail if the OS random source fails. Negative sizes panic through slice allocation semantics.

## Test Signals
Expected tests verify length and error-free generation for normal sizes.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/version/version.go -->
# sources/cloud-native/stargz-snapshotter/version/version.go

## Purpose
Defines build-time version metadata variables for stargz snapshotter binaries.

## Important APIs, Types, And Functions
- `Version` defaults to `0.0.0+unknown`.
- `Revision` defaults to empty string.
- `Package` defaults to `github.com/containerd/stargz-snapshotter`.

## Control Flow
No runtime flow; variables are read by binaries and can be overridden with linker flags.

## State And Persistence
Process-global version variables only. Values are typically embedded at build time.

## Dependencies And Integration Points
Used by CLI/server binaries for version output and release identification. Build scripts may set these via `-ldflags`.

## Risks And Edge Cases
Missing linker flags produce unknown version metadata. External consumers should not assume `Revision` is non-empty.

## Test Signals
Version commands or package consumers should report linker-provided values in release builds and defaults in local builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.circleci/config.yml -->
# sources/compression/lz4/.circleci/config.yml

## Purpose
Runs legacy CircleCI coverage for the lz4 project using a Docker executor.

## Important APIs, Types, And Functions
- Workflow/config name: CircleCI config.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
It checks out the repository, initializes submodules, runs make targets/tests in the configured primary image, and preserves CI compatibility outside GitHub Actions. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.circleci/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.circleci/images/primary/Dockerfile -->
# sources/compression/lz4/.circleci/images/primary/Dockerfile

## Purpose
Defines the Docker image used by CircleCI jobs.

## Important APIs, Types, And Functions
- Workflow/config name: CircleCI primary image.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
It installs the compiler/build/test dependencies needed by the CircleCI workflow and pins the execution environment for repeatable legacy CI. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.circleci/images/primary/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.github/dependabot.yaml -->
# sources/compression/lz4/.github/dependabot.yaml

## Purpose
Configures automated dependency update scanning for GitHub Actions.

## Important APIs, Types, And Functions
- Workflow/config name: Dependabot config.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
The file uses dependabot version 2 and schedules updates for the repository workflow ecosystem. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.github/dependabot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.github/workflows/build-systems.yml -->
# sources/compression/lz4/.github/workflows/build-systems.yml

## Purpose
Exercises non-core build integrations for lz4.

## Important APIs, Types, And Functions
- Workflow/config name: Build Systems workflow.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
Jobs cover Visual Studio/MSBuild on Windows and Meson on Linux, using matrices for build system variants and ensuring auxiliary build files remain healthy. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.github/workflows/build-systems.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.github/workflows/cmake-test.yml -->
# sources/compression/lz4/.github/workflows/cmake-test.yml

## Purpose
Validates CMake build configurations across platforms and options.

## Important APIs, Types, And Functions
- Workflow/config name: CMake Build Tests workflow.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
It runs core CMake matrix builds, extended CMake option tests, and Makefile-driven CMake integration tests. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.github/workflows/cmake-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.github/workflows/code-quality.yml -->
# sources/compression/lz4/.github/workflows/code-quality.yml

## Purpose
Runs static and dynamic quality checks.

## Important APIs, Types, And Functions
- Workflow/config name: Code Quality workflow.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
Jobs include cppcheck, clang scan-build, Valgrind, Unicode linting, and example builds to catch correctness and hygiene issues beyond compilation. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.github/workflows/code-quality.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.github/workflows/compilers.yml -->
# sources/compression/lz4/.github/workflows/compilers.yml

## Purpose
Builds lz4 across a compiler/version matrix.

## Important APIs, Types, And Functions
- Workflow/config name: Compiler Tests workflow.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
It validates GCC/Clang and OS combinations with package installation and make invocations that catch compiler-specific warnings or portability breaks. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.github/workflows/compilers.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.github/workflows/core-tests.yml -->
# sources/compression/lz4/.github/workflows/core-tests.yml

## Purpose
Runs core lz4 correctness and regression suites.

## Important APIs, Types, And Functions
- Workflow/config name: Core Tests workflow.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
Jobs cover benchmarks, fuzzers, version checks, ABI checks, frame tests, memory usage, custom distance, Makefile variable propagation, and block-device behavior. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.github/workflows/core-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.github/workflows/cross-platform.yml -->
# sources/compression/lz4/.github/workflows/cross-platform.yml

## Purpose
Validates lz4 on non-default platforms.

## Important APIs, Types, And Functions
- Workflow/config name: Cross Platform workflow.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
It uses QEMU platform matrices and macOS jobs to catch architecture and OS portability problems. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.github/workflows/cross-platform.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.github/workflows/oss-fuzz.yml -->
# sources/compression/lz4/.github/workflows/oss-fuzz.yml

## Purpose
Builds OSS-Fuzz targets for lz4.

## Important APIs, Types, And Functions
- Workflow/config name: OSS-Fuzz workflow.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
It uses the OSS-Fuzz build action/matrix to ensure fuzzing integration continues to compile for sanitizer-driven fuzz infrastructure. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.github/workflows/oss-fuzz.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.github/workflows/release-environment.yml -->
# sources/compression/lz4/.github/workflows/release-environment.yml

## Purpose
Checks release metadata and records environment coverage.

## Important APIs, Types, And Functions
- Workflow/config name: Release & Environment workflow.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
It verifies git tag consistency and runs environment-info jobs across OS matrices for release diagnostics. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.github/workflows/release-environment.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.github/workflows/sanitizers.yml -->
# sources/compression/lz4/.github/workflows/sanitizers.yml

## Purpose
Runs lz4 under compiler sanitizers.

## Important APIs, Types, And Functions
- Workflow/config name: Sanitizers workflow.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
Jobs cover UBSan on x64/x86, ASan, MSan, and TSan with appropriate clang/gcc flags and make test targets. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.github/workflows/sanitizers.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.github/workflows/scorecard.yml -->
# sources/compression/lz4/.github/workflows/scorecard.yml

## Purpose
Runs OpenSSF Scorecard supply-chain checks.

## Important APIs, Types, And Functions
- Workflow/config name: Scorecard workflow.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
It triggers on branch-protection changes, schedule, and pushes, uploads artifacts, and sends SARIF/code-scanning results with security permissions. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.github/workflows/scorecard.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/Makefile -->
# sources/compression/lz4/Makefile

## Purpose
Top-level GNU Make orchestration for building, testing, installing, and validating lz4 libraries, CLI, examples, manuals, and auxiliary build systems.

## Important APIs, Types, And Functions
- Main targets include `default`, `all`, `allmost`, `lib`, `lz4`, `examples`, `manuals`, `build_tests`, `clean`, `install`, `uninstall`, `test`, and `check`.
- Integration targets include `cmakebuild`, `mesonbuild`, and `test-install`.
- Quality/portability targets include `usan`, `ubsan`, `usan32`, `staticAnalyze`, `cppcheck`, `platformTest`, `versionsTest`, `test-freestanding`, C/C++ compatibility, and `c_standards`.
- Propagates standard variables such as `CC`, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, and `LDLIBS` into subdirectories.

## Control Flow
Targets mostly delegate to subdirectory Makefiles in `lib`, `programs`, `examples`, `tests`, and build-system directories. Clean/test targets reset or rebuild relevant subtrees. Sanitizer and standard targets override compiler flags before invoking clean/build/test flows.

## State And Persistence
Produces libraries, binaries, manuals, examples, test artifacts, install trees, and temporary build directories. `clean` removes generated artifacts across subprojects.

## Dependencies And Integration Points
Integrates all major lz4 build surfaces and is the common entry point for CI workflows. Depends on GNU make, C/C++ compilers, shell tools, CMake/Meson for specific targets, and static-analysis tools when requested.

## Risks And Edge Cases
Variable propagation is critical; broken forwarding can make CI misleading. Some targets require optional tools or 32-bit libraries. Install/uninstall targets can affect system paths if `PREFIX`/`DESTDIR` are not controlled.

## Test Signals
Passing `make`, `make test`, sanitizer targets, build-system targets, and `test_stdvars` indicate core build, tests, and variable propagation are healthy.
<!-- END_FILE_RESEARCH: sources/compression/lz4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/appveyor.yml -->
# sources/compression/lz4/appveyor.yml

## Purpose
Defines AppVeyor Windows CI coverage for lz4.

## Important APIs, Types, And Functions
- Uses AppVeyor versioning and an environment matrix for Windows build variants.
- Configures clone/build/test scripts for Visual Studio/MSBuild and command-line builds.
- Captures platform-specific Windows build behavior separate from GitHub Actions.

## Control Flow
AppVeyor provisions the Windows image, applies the matrix environment, checks out source, runs configured build commands, then executes test commands and reports status.

## State And Persistence
State is the CI workspace, Visual Studio build outputs, logs, and any AppVeyor artifacts configured by the platform.

## Dependencies And Integration Points
Integrates with AppVeyor's Windows images, Visual Studio toolchains, and lz4 project build files.

## Risks And Edge Cases
Legacy CI images can drift or disappear. Windows path/toolchain differences can expose issues not seen elsewhere, but duplicated coverage must stay aligned with GitHub Actions.

## Test Signals
Passing AppVeyor jobs demonstrate Windows build/test compatibility for the configured matrix.
<!-- END_FILE_RESEARCH: sources/compression/lz4/appveyor.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/contrib/djgpp/Makefile -->
# sources/compression/lz4/contrib/djgpp/Makefile

## Purpose
Builds and installs lz4 for the DJGPP DOS toolchain contribution.

## Important APIs, Types, And Functions
- Extracts library version from `lib/lz4.h` into `LIBVER` variables.
- Pattern rules build `.o` from `.c` and `.exe` from objects and the static library.
- Targets include `all`, `clean`, `install`, `uninstall`, `showconfig`, `gstat`, and `gpush`.
- Tracks installed files through `.footprint`.

## Control Flow
`all` builds the static library and executables with DJGPP-compatible compiler/linker settings. `install` copies includes, library, binaries, docs, and license files into prefix paths and records footprints. `uninstall` removes files from `.footprint`.

## State And Persistence
Produces DJGPP object files, libraries, executables, install trees, and `.footprint`. Clean removes local build outputs.

## Dependencies And Integration Points
Depends on DJGPP/GCC tooling, sed, install/rm utilities, and relative paths to lz4 `lib` and `programs` sources.

## Risks And Edge Cases
Version parsing relies on exact `#define` patterns. Install/uninstall can remove wrong files if `.footprint` is stale or prefix changes. DOS/DJGPP constraints differ from normal Unix builds.

## Test Signals
Signals include successful DJGPP compilation, correct `showconfig`, installed files matching `.footprint`, and clean uninstall.
<!-- END_FILE_RESEARCH: sources/compression/lz4/contrib/djgpp/Makefile -->
