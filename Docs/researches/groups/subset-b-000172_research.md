# subset-b-000172 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/view.go -->
# sources/cloud-native/moby/daemon/container/view.go

## Purpose
Implements the daemon's in-memory, transactional read model for containers. `ViewDB` stores immutable deep-copied `Container` objects and name reservations in a HashiCorp `go-memdb` database, then exposes read-only `View` snapshots used by container listing, lookup, and name-resolution paths.

## Important APIs, Types, And Functions
- `Snapshot` embeds API `container.Summary` and adds query/filter fields such as `CreatedAt`, `StartedAt`, `Pid`, `Running`, `Paused`, `Managed`, port sets, health, and isolation.
- `NewViewDB`, `Save`, `Delete`, `ReserveName`, and `ReleaseName` are the mutating store API.
- `Snapshot`, `All`, `Get`, `GetID`, and `GetAllNames` are read APIs backed by read transactions.
- `GetByPrefix` resolves unique ID prefixes and reports empty, missing, or ambiguous prefixes with typed `errdefs` errors.
- Custom memdb indexers add null-terminated exact keys and prefix keys for container IDs and name associations.

## Control Flow
Writers call `withTxn`, mutate the containers or names tables, and commit or abort atomically. Readers acquire a memdb read transaction through `Snapshot()` and resolve objects through indexed queries. `transform` converts a `Container` into an API-facing `Snapshot`, copying selected network endpoint fields, port mappings, mount summaries, labels, host config details, command strings, health state, and image manifest descriptor data.

## State And Persistence
This file is memory-only. Persistence comes from containers checkpointing deep copies into this replica elsewhere. The key invariant is that stored containers must be immutable copies because `transform` does not take the container lock.

## Dependencies And Integration Points
Depends on `go-memdb`, daemon `container.Container`, API container/network types, and Moby `errdefs`. It integrates with container checkpointing (`CheckpointTo`), name reservation flows, container list/filter APIs, and ID-prefix lookup paths.

## Risks And Edge Cases
Mutating a stored container copy would race readers because snapshots are intentionally lock-free. `Delete` removes associated names even when the container record is absent, which is useful for cleanup but depends on correct container IDs. `transform` logs and skips invalid host port ranges rather than failing a list request. Network and label maps are partially cloned; future fields need the same immutability discipline.

## Test Signals
Covered by `view_test.go`: save/delete, listing, exact lookup, name reservation conflicts and snapshot isolation, health propagation, prefix ambiguity, and prefix lookup benchmarks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/view.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/view_test.go -->
# sources/cloud-native/moby/daemon/container/view_test.go

## Purpose
Tests the in-memory container view database, name index, health projection, ID-prefix lookup behavior, and benchmark characteristics of prefix lookups at small container counts.

## Important APIs, Types, And Functions
- `newContainer` creates a temporary base container with a UUID ID and root directory.
- `TestViewSaveDelete`, `TestViewAll`, and `TestViewGet` validate basic store/read behavior through `CheckpointTo`.
- `TestNames` verifies name reservation, conflict typing, release/reuse, `GetID`, `GetAllNames`, and cleanup through `Delete`.
- `TestViewWithHealthCheck` checks `Health.Status()` is projected into `Snapshot.Health`.
- `TestTruncIndex` and `assertIndexGet` exercise exact, prefix, ambiguous, missing, and deleted prefix cases.
- `BenchmarkDBAdd100` and `BenchmarkDBGetByPrefix*` measure insert and prefix lookup costs.

## Control Flow
Each test creates a fresh `ViewDB`, writes containers or names, then uses a read `View` to assert snapshot state. The name test deliberately keeps an old read transaction while changing live reservations to prove snapshot isolation. Prefix tests insert overlapping IDs, assert ambiguity for short prefixes, delete one ID, and assert the remaining prefix is unambiguous.

## State And Persistence
State is local to each test's temporary directory and memdb instance. The tests indirectly validate that `CheckpointTo` writes immutable copies into the replica, but no daemon disk checkpoint files are the target of these assertions.

## Dependencies And Integration Points
Uses `gotest.tools`, containerd errdefs predicates, UUIDs, daemon `stringid` helpers for benchmarks, and container checkpoint integration. It is the direct regression suite for `view.go`.

## Risks And Edge Cases
The tests rely on map/slice ordering in expected `GetAllNames` results after deterministic insert order. Benchmarks use random IDs and random prefix lengths, so they are performance signals rather than behavioral gates. The health test only checks status, not failing streak or full health summary projection.

## Test Signals
Failures identify broken transactional isolation, name conflict classification, reservation cleanup, health mapping, or prefix-index semantics. Benchmarks detect gross regressions in add and prefix-resolution cost.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/view_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_linux.go -->
# sources/cloud-native/moby/daemon/container_linux.go

## Purpose
Provides the non-Windows implementation of AppArmor profile derivation for container creation/start configuration.

## Important APIs, Types, And Functions
- `saveAppArmorConfig(container *container.Container) error` resets `AppArmorProfile`, reads daemon system info, parses security options, and assigns default or unconfined AppArmor profiles.
- Uses `daemon.RawSysInfo`, `parseSecurityOpt`, `unconfinedAppArmorProfile`, and `defaultAppArmorProfile`.

## Control Flow
The function first clears the existing profile so it can be derived from current `HostConfig.SecurityOpt`. If AppArmor is disabled according to daemon system info, it exits without setting a profile. Otherwise it parses security options as invalid-parameter errors, then defaults privileged containers to unconfined and non-privileged containers to the default profile when no explicit profile was set.

## State And Persistence
It mutates the in-memory `container.Container` security fields before those settings are persisted with the rest of the container metadata. It does not write profile files.

## Dependencies And Integration Points
Integrated by daemon container setup and validation paths that prepare Linux/FreeBSD security configuration. It depends on daemon system capability detection and the shared security option parser.

## Risks And Edge Cases
Resetting the profile is intentional, but callers must invoke it before checkpointing final container state. `RawSysInfo` failures are treated as system errors. If security option parsing changes, this file controls whether errors surface as invalid parameters.

## Test Signals
No direct test in this subset. Indirect coverage should come from container-create security option tests and platform integration tests that assert AppArmor defaults.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_operations.go -->
# sources/cloud-native/moby/daemon/container_operations.go

## Purpose
Implements common daemon container networking operations: sandbox option construction, network setting normalization, endpoint validation, network attach/detach, sandbox initialization and release, service-binding activation, and connect/disconnect API behavior.

## Important APIs, Types, And Functions
- `buildSandboxOptions` builds libnetwork sandbox options from host config, daemon DNS settings, extra hosts, exposed ports, port bindings, publish-all settings, and platform options.
- `updateNetworkSettings`, `updateContainerNetworkSettings`, `updateNetworkConfig`, and `buildEndpointDNSNames` maintain container endpoint maps and DNS names.
- `findAndAttachNetwork`, `connectToNetwork`, `disconnectFromNetwork`, and `tryDetachContainerFromClusterNetwork` integrate local libnetwork state with swarm attachable networks.
- `initializeNetworking`, `allocateNetwork`, `updateNetwork`, and `releaseNetwork` manage sandbox lifecycle.
- `validateEndpointSettings`, `normalizeEndpointIPAMConfig`, and `validateIPAMConfigIsInRange` enforce IPAM rules.
- Public methods include `ConnectToNetwork`, `DisconnectFromNetwork`, `ForceEndpointDelete`, and service-binding activation/deactivation wrappers.

## Control Flow
Creation/start calls initialize networking, destroy stale sandboxes, handle `--network container:` path sharing, set hostnames for host networking, create a sandbox, and later connect endpoint configs. Runtime connect resolves or attaches dynamic networks, normalizes host network restrictions, validates static IP/MAC/sysctl settings, creates an endpoint, joins it to the sandbox, updates operational endpoint data, activates DNS/service binding for unmanaged containers, writes port info, logs events, and checkpoints container state. Disconnect reverses endpoint membership, updates port info, removes endpoint settings, detaches cluster networks, logs events, and checkpoints.

## State And Persistence
Mutates `ctr.NetworkSettings`, including sandbox ID/key, endpoint maps, operational IP/MAC/gateway fields, swarm endpoint flags, port maps, and desired MAC addresses. `ConnectToNetwork` and `DisconnectFromNetwork` persist changes through `CheckpointTo(daemon.containersReplica)`. Operational endpoint data is cleaned before reallocation and on release.

## Dependencies And Integration Points
Depends on libnetwork, daemon network lookup, swarm `clusterProvider`, daemon config, Moby network API types, metrics, events, OpenTelemetry spans, and platform helpers from `container_operations_unix.go`/`_windows.go`. It is central to `docker run`, `start`, `network connect`, `network disconnect`, live restore cleanup, and service discovery.

## Risks And Edge Cases
Rollback paths must keep libnetwork endpoints, swarm attachments, and container maps consistent after partial failures. Extra-host `host-gateway` requires daemon-level gateway IPs. Default/predefined network IP and alias support differs by platform. Dynamic network attach races are retried only for a bounded set of no-such-network cases. Platform deletion with force and namespace-sharing modes require careful restriction to avoid connecting host/container namespace users to extra networks.

## Test Signals
`container_operations_test.go` covers DNS name ordering and IPAM validation. Wider coverage is expected from integration tests for network connect/disconnect, swarm attachable networks, links, port mappings, and host/container namespace modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_operations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_operations_test.go -->
# sources/cloud-native/moby/daemon/container_operations_test.go

## Purpose
Tests focused pure functions in container networking: DNS name ordering for endpoints, static IP range validation, and endpoint IPAM normalization/validation.

## Important APIs, Types, And Functions
- `TestDNSNamesOrder` drives `updateNetworkConfig` and expects container name, alias, truncated ID, and hostname order.
- `buildNetwork` constructs a libnetwork `Network` from JSON test config.
- `TestEndpointIPAMInfoWithOutOfRangeAddrs` validates static addresses against libnetwork IPAM pools.
- `TestEndpointIPAMConfigWithInvalidConfig` validates malformed IPv4/IPv6/link-local addresses and unmapped normalization.

## Control Flow
Tests build small network and endpoint objects in memory, call the production validation/config functions, then compare returned error strings and mutated `EndpointSettings` fields. Error cases join multiple validation errors and assert each expected substring is present.

## State And Persistence
No persistent daemon state is used. The IPAM normalization test mutates the supplied endpoint config in place, mirroring production behavior.

## Dependencies And Integration Points
Uses API container/network types, libnetwork network JSON unmarshalling, driver IPAM data, and `gotest.tools`. It directly guards helper behavior used by `connectToNetwork` and `updateNetworkConfig`.

## Risks And Edge Cases
The tests do not instantiate real sandboxes, so they do not cover endpoint create/join rollback or checkpointing. Error-string assertions can be brittle if wording changes while semantics remain correct.

## Test Signals
Failures indicate DNS records may be generated in an order that breaks PTR assumptions, static IPs may be accepted outside subnets, or invalid IP forms may leak into endpoint settings.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_operations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_operations_unix.go -->
# sources/cloud-native/moby/daemon/container_operations_unix.go

## Purpose
Provides Linux/FreeBSD implementations for container operation helpers: legacy links, IPC namespace setup, tmpfs/secrets/config mounts, direct process killing, sandbox path setup, and platform feature flags for default networking.

## Important APIs, Types, And Functions
- `setupLinkedContainers` and `addLegacyLinks` manage deprecated bridge link environment variables and `/etc/hosts` entries.
- `getIPCContainer`, `getPIDContainer`, `setupContainerDirs`, `setupIPCDirs`, `setupSecretDir`, `createSecretsDir`, `remountSecretDir`, and `cleanupSecretDir` prepare IPC, tmpfs, secrets, and configs.
- `killProcessDirectly` sends SIGKILL and detects missing/zombie processes.
- `enableIPOnPredefinedNetwork` and `serviceDiscoveryOnDefaultNetwork` return Linux/FreeBSD defaults.
- `buildSandboxPlatformOptions` selects origin hosts/resolv.conf paths and sets container `HostsPath`/`ResolvConfPath`.
- `initializeNetworkingPaths` shares network namespace file paths for `--network container:`.

## Control Flow
Container setup creates mount roots, configures IPC based on host/container/private/shareable modes, writes secrets/config data into a tmpfs, fixes ownership under user namespace remapping, remounts secrets read-only with EBUSY retries, and returns mounts for the OCI spec. Networking setup chooses host/user-defined/default DNS behavior, then writes libnetwork sandbox path options. Legacy link setup updates hosts files before default-network endpoint joins and propagates parent/child link labels.

## State And Persistence
Mutates container paths such as `ShmPath`, `HostsPath`, `ResolvConfPath`, and secret/config directories under the container root. It creates and unmounts tmpfs mounts, writes secret/config payload files, relabels them for SELinux, and can update hosts entries inside existing sandboxes.

## Dependencies And Integration Points
Depends on Unix syscalls, `moby/sys/mount`, idmapping/user helpers, SELinux labels, libnetwork bridge/link support, daemon link index, process utilities, and daemon config. It integrates with container start, legacy link behavior, secret/config injection, and runtime kill fallback paths.

## Risks And Edge Cases
Secret tmpfs remount races are handled with retries, but failures can leave start failures and require cleanup. IPC donor validation must reject non-running/restarting/non-shareable containers. Direct SIGKILL cannot kill zombies and returns a system error with guidance. Environment-controlled legacy link variables retain deprecated behavior and can affect container environments.

## Test Signals
No direct tests in this subset for most helpers. `container_unix_test.go` covers host-network port warning behavior in nearby validation. Broader daemon integration tests should cover IPC modes, secrets/configs, links, DNS file generation, and process kill behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_operations_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_operations_windows.go -->
# sources/cloud-native/moby/daemon/container_operations_windows.go

## Purpose
Provides Windows-specific container operation helpers for secrets/configs, network namespace sharing metadata, and feature flags that differ from Unix implementations.

## Important APIs, Types, And Functions
- `setupLinkedContainers`, `addLegacyLinks`, `setupIpcDirs`, `mountVolumes`, and `killProcessDirectly` are Windows no-op or placeholder implementations.
- `setupConfigDir` and `setupSecretDir` create ACL-protected local directories and write config/secret file payloads.
- `enableIPOnPredefinedNetwork` and `serviceDiscoveryOnDefaultNetwork` return `true` for Windows default network behavior.
- `buildSandboxPlatformOptions` returns no extra sandbox options.
- `initializeNetworkingPaths` rejects Hyper-V donor sharing and records shared HNS endpoint IDs.

## Control Flow
Secrets/config setup checks for references, creates local directories with administrators/local-system ACLs, validates dependency store availability, skips non-file runtime configs, then writes file contents with configured modes. Network namespace sharing records the donor container ID and walks donor networks/endpoints, extracting HNS IDs from endpoint driver data into `SharedEndpointList`.

## State And Persistence
Writes config and secret payloads into container-specific local filesystem directories and removes them if setup fails. It mutates `NetworkSharedContainerID` and `SharedEndpointList` for Windows network namespace sharing.

## Dependencies And Integration Points
Depends on Windows ACL helpers, daemon dependency stores, libnetwork endpoint driver metadata, and Windows isolation mode checks. It is used by Windows container start/configuration flows and by `--network container:` sharing support.

## Risks And Edge Cases
Several Unix behaviors are no-ops on Windows, so shared code must not assume IPC setup, direct kill, or sandbox path options did work. Hyper-V network sharing is explicitly unsupported. Type assertions on endpoint driver data assume HNS metadata shapes and could panic if driver info changes unexpectedly.

## Test Signals
No direct tests in this subset. Expected coverage comes from Windows CI for config/secret injection, network sharing, default network service discovery, and HNS endpoint metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_operations_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_unix_test.go -->
# sources/cloud-native/moby/daemon/container_unix_test.go

## Purpose
Verifies that Unix daemon container settings validation warns when published ports are configured together with host network mode.

## Important APIs, Types, And Functions
- `TestContainerWarningHostAndPublishPorts` drives `verifyContainerSettings`.
- Test cases vary `HostConfig.NetworkMode` and `PortBindings`.

## Control Flow
Each subtest constructs a host config and empty container config, calls daemon validation, and compares returned warnings. Only the case with `NetworkMode: "host"` and non-empty port bindings should produce `Published ports are discarded when using host network mode`.

## State And Persistence
No daemon state is persisted. The daemon instance is empty and the config store is a test stub.

## Dependencies And Integration Points
Uses API container/network types and daemon validation helpers. The build tag restricts this test to Linux/FreeBSD where host network mode is supported.

## Risks And Edge Cases
This only validates warning emission, not the runtime discard behavior. It intentionally excludes Windows because host networking is unsupported there.

## Test Signals
Failures indicate user-facing warnings for ignored port publishing may be missing or emitted in the wrong cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_windows.go -->
# sources/cloud-native/moby/daemon/container_windows.go

## Purpose
Provides the Windows stub for AppArmor configuration.

## Important APIs, Types, And Functions
- `saveAppArmorConfig(container *container.Container) error` always returns nil.

## Control Flow
No logic is performed because AppArmor does not apply to Windows containers.

## State And Persistence
Does not mutate container state.

## Dependencies And Integration Points
Keeps the daemon build portable by satisfying the same method used by non-Windows container setup paths.

## Risks And Edge Cases
Shared code must not infer AppArmor state on Windows. This stub should remain intentionally empty unless Windows gains an equivalent security-profile abstraction with a different name.

## Test Signals
No direct tests are needed beyond Windows build coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/cache.go -->
# sources/cloud-native/moby/daemon/containerd/cache.go

## Purpose
Adapts the containerd-backed image service to Docker's classic builder image cache interface. It resolves images, parent/child metadata, locally built markers, and creates cached images using containerd content and image labels.

## Important APIs, Types, And Functions
- `ImageService.MakeImageCache` constructs a `cache.New` instance with `cacheAdaptor`.
- `cacheAdaptor.Get`, `GetByRef`, `SetParent`, `GetParent`, `Create`, `IsBuiltLocally`, and `Children` implement builder cache storage.
- `findContentByUncompressedDigest` locates a compressed content blob by the `containerd.io/uncompressed` label.

## Control Flow
`Get` loads the Docker image view, then walks image manifests looking for a config blob label that references stored classic `ContainerConfig` content. Parent labels are written to all references sharing a target digest. `Create` marshals target image config, resolves an optional extra layer's compressed digest, calls `CreateImage`, and returns the resulting image ID. Children are found through parent labels or from-scratch labels.

## State And Persistence
Persists classic builder metadata as containerd image labels (`org.mobyproject.image.parent`, `fromscratch`, and `containerconfig`) and content labels referencing stored container configs. It does not manage cache eviction itself.

## Dependencies And Integration Points
Depends on containerd image/content stores, daemon internal image/cache interfaces, layer DiffIDs, Moby multierror, and OCI descriptors. It integrates legacy Dockerfile builder cache behavior with the containerd image store.

## Risks And Edge Cases
Missing or malformed config labels are logged and skipped, so cache reads may silently lose `ContainerConfig`. `SetParent` updates every image sharing a target and can partially fail; errors are joined. `findContentByUncompressedDigest` walks labels and returns not found if differ output lacks expected metadata.

## Test Signals
No direct tests in this subset. Related builder and image tests should verify cache hits, parent links, from-scratch children, and locally-built image detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/fake_service_test.go -->
# sources/cloud-native/moby/daemon/containerd/fake_service_test.go

## Purpose
Provides reusable test fixtures for the containerd-backed image service: a fake `ImageService`, a read-only blob-directory content store, a no-op leases manager, and a delay wrapper for content-store benchmarks.

## Important APIs, Types, And Functions
- `fakeImageService` wires metadata image store, content store, snapshotter service, event service, memory container store, and a containerd client with injected services.
- `noopLeasesManager` satisfies containerd leases APIs without retaining resources.
- `blobsDirContentStore` implements content store reads, info, walk, and delete against files in a `blobs/sha256` directory.
- `delayedStore` wraps content operations with a constant sleep.

## Control Flow
Tests call `fakeImageService` with a content store, then exercise image service methods without an external containerd daemon. Blob reads map descriptor digest encodings to filenames. Walk enumerates files and constructs content info from stat data. Delay wrapper forwards all calls after sleeping.

## State And Persistence
State lives in temporary metadata databases, in-memory snapshotter fixtures, and test blob directories. `blobsDirContentStore.Delete` removes files, while writes/status updates are intentionally unsupported or read-only.

## Dependencies And Integration Points
Depends on containerd client service injection, metadata DB, snapshotter service test doubles, daemon events, and Moby container memory store. It underpins tests for image identity, deletion, import/export, and manifest walking.

## Risks And Edge Cases
The blob content store is intentionally incomplete; tests using it must not expect writes, status tracking, label updates, or real lease semantics. Digest construction in `Walk` uses file names as digest inputs and is only suitable for controlled fixtures.

## Test Signals
This file is test infrastructure. Failures in dependent tests can indicate fake service drift from containerd service interfaces or fixture behavior insufficient for new image-service code paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/fake_service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/handlers.go -->
# sources/cloud-native/moby/daemon/containerd/handlers.go

## Purpose
Defines descriptor-walk helpers that traverse only content present in the local content store. This is used when operations need to inspect or delete reachable descriptors without failing on missing children.

## Important APIs, Types, And Functions
- `ImageService.walkPresentChildren` wraps containerd `images.Walk`.
- `presentChildrenHandler` checks descriptor presence with `content.Store.Info`, invokes a caller handler, and appends containerd-discovered child descriptors.

## Control Flow
For each descriptor, the wrapper first verifies the digest exists. Missing descriptors return `images.ErrSkipDesc`, which prunes that branch. Present descriptors are passed to the caller handler, then `images.Children` is called to discover and append children, again skipping missing child metadata.

## State And Persistence
Read-only. It observes the content store but does not mutate descriptors or labels.

## Dependencies And Integration Points
Depends on containerd content and image traversal APIs. It is used by platform-specific image deletion to gather content descendants that are actually present before deletion.

## Risks And Edge Cases
The helper deliberately tolerates missing content, which is correct for partial image stores but can hide integrity issues if used where complete content is required. Non-not-found errors still abort traversal.

## Test Signals
Indirectly covered by image deletion and platform-specific content tests. Expected signals are skipped missing descriptors and correct traversal of present manifests/config/layers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/identitycache/backend.go -->
# sources/cloud-native/moby/daemon/containerd/identitycache/backend.go

## Purpose
Defines the persistent backend contract for image signature identity cache entries and supplies a no-op implementation for configurations without durable caching.

## Important APIs, Types, And Functions
- `Entry` stores `CachedAt`, `ExpiresAt`, and an optional `SignatureIdentity`.
- `Backend` defines `Load`, `Store`, `Walk`, `PruneExpired`, and `Close`.
- `NewNopBackend` returns `nopBackend`, whose methods are successful no-ops and always miss.

## Control Flow
Callers depend on the backend interface for cache reads, writes, iteration, pruning, and lifecycle closure. The no-op backend short-circuits all persistence paths while preserving the same call contract.

## State And Persistence
The interface represents durable storage, but `nopBackend` persists nothing. Entry expiry semantics are implemented by concrete backends and callers.

## Dependencies And Integration Points
Uses API image signature identity types. It is consumed by `image_identity.go` and implemented by `bbolt.go`.

## Risks And Edge Cases
Backends must make clear whether `Walk` includes expired entries; the bbolt implementation does until prune. Callers must handle nil signatures as cacheable values.

## Test Signals
The contract is indirectly tested by bbolt backend and image identity cache tests for persistence, nil signatures, expiry, walking, and pruning.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/identitycache/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/identitycache/bbolt.go -->
# sources/cloud-native/moby/daemon/containerd/identitycache/bbolt.go

## Purpose
Implements a bbolt-backed persistent image identity cache with corruption recovery and explicit pruning of expired or invalid records.

## Important APIs, Types, And Functions
- `NewBoltDBBackend(root)` creates `<root>/image/identity-cache.db`, initializes bucket `image-identity-cache-v1`, or returns a no-op backend for empty root.
- `Load`, `Store`, `Walk`, `PruneExpired`, and `Close` implement `Backend`.
- `safeOpen`, `fallbackOpen`, and `fileHasContent` recover from corrupt non-empty database files by renaming them to timestamped `.bak` files.

## Control Flow
Loads copy raw bbolt values out of a read transaction, unmarshal JSON, delete corrupt entries, and treat expired entries as misses without deleting them. Stores marshal entries and put them in the bucket. Walk iterates all decodable entries and honors context cancellation. Pruning deletes entries that are expired or no longer JSON-decodable.

## State And Persistence
Persists cache entries as JSON values keyed by cache key in a bbolt bucket under daemon root. `Close` is idempotent through `sync.Once`. Corruption recovery preserves the old file as a backup and starts with a new empty DB.

## Dependencies And Integration Points
Depends on bbolt, filesystem permissions, containerd logging, and the identitycache backend interface. It is used by the image service identity cache to survive daemon restarts.

## Risks And Edge Cases
Expired loads do not delete entries, so prune maintenance must run to bound disk usage. Corrupt JSON entries are silently dropped on load and deleted on prune. `safeOpen` recovers only when the DB file has content; empty-file open failures are returned.

## Test Signals
`bbolt_test.go` checks expired entries remain visible to walk until prune and that expired loads miss without deleting. Image identity tests verify persistence across restart and refresh of expired persisted entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/identitycache/bbolt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/identitycache/bbolt_test.go -->
# sources/cloud-native/moby/daemon/containerd/identitycache/bbolt_test.go

## Purpose
Tests bbolt identity cache expiry semantics, specifically the distinction between load-time misses and explicit prune-time deletion.

## Important APIs, Types, And Functions
- `TestBoltBackendWalkIncludesExpiredEntriesUntilPrune` stores fresh and expired entries, walks before/after prune, and compares keys.
- `TestBoltBackendLoadExpiredReturnsMissWithoutDelete` verifies `Load` misses expired entries while `Walk` can still see them before pruning.

## Control Flow
Each test creates a temp bbolt backend, stores entries with controlled timestamps, then calls backend APIs with a fixed `now`. The first test sorts walked keys for deterministic comparison.

## State And Persistence
Uses temporary on-disk bbolt databases and closes them with `defer`. The tests validate durable backend behavior, not in-memory image service cache behavior.

## Dependencies And Integration Points
Uses `gotest.tools` assertions and the bbolt backend constructor. It guards assumptions made by image identity maintenance, where refresh can inspect expired persisted entries before pruning.

## Risks And Edge Cases
These tests do not exercise corruption recovery or JSON decode failures. They intentionally assert that expired records can remain on disk, so any future eager-delete design would require coordinated test and maintenance changes.

## Test Signals
Failures indicate changed backend expiry semantics that could break cache refresh, pruning, or disk-bounding behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/identitycache/bbolt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image.go -->
# sources/cloud-native/moby/daemon/containerd/image.go

## Purpose
Provides core image resolution and inspection helpers for the containerd-backed image service, including name/digest/short-ID lookup, platform-specific manifest selection, parent label retrieval, reference grouping, and truncated ID validation.

## Important APIs, Types, And Functions
- `GetImage`, `ResolveImage`, `resolveImage`, `resolveDescriptor`, and `resolveAllReferences`.
- `getBestPresentImageManifest` selects the best local platform manifest using a platform matcher.
- `getAllImagesWithRepository`, `imageFamiliarName`, and `getImageLabelByDigest`.
- `checkTruncatedID` validates 4-64 hex chars with optional `sha256:` prefix.
- `errPlatformNotFound` reports platform-specific missing-manifest errors as not found.

## Control Flow
`GetImage` resolves a containerd image, chooses a present manifest matching requested/default platform, reads OCI config into Docker image metadata, attaches parent label and manifest descriptor details, then returns the internal image object. Resolution handles digested references first, name:tag references next, and valid short IDs by regex filtering target digests. `resolveAllReferences` returns the matched reference plus all images with the same target digest and retries if image data changes mid-lookup.

## State And Persistence
Read-only against image/content stores. It interprets containerd image names, target digests, and labels but does not mutate them.

## Dependencies And Integration Points
Depends on containerd image store, distribution reference parsing, OCI descriptors, platform matchers, Moby image error types, and Docker image-spec conversion helpers. It underlies nearly every image API: inspect, history, delete, export, builder cache, and commit.

## Risks And Edge Cases
Ambiguous short IDs return not-found conflict-style errors, and named digested references must match repository names, not just digest. `resolveAllReferences` detects inconsistent data and retries only three times. Parent label conflicts across references are surfaced as conflicts. Platform selection considers only locally present manifests.

## Test Signals
No direct test in this subset, but deletion/export/history/identity tests exercise resolution paths. Dedicated coverage should assert short-ID ambiguity, named digest repository filtering, label conflicts, and platform-not-found messaging.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_attestations.go -->
# sources/cloud-native/moby/daemon/containerd/image_attestations.go

## Purpose
Exposes BuildKit in-toto attestation statements attached to a local OCI index image for a requested platform.

## Important APIs, Types, And Functions
- `ImageService.ImageAttestations` implements the daemon image attestation API.
- `localReferrersProvider` adapts local content to `policyimage.ReferrersProvider` with no remote referrer fetching.
- `inTotoPredicateTypeAnnotation` identifies statement layers.

## Control Flow
The method resolves the image, exits early for non-index targets, asks `policyimage.ResolveSignatureChain` to locate the platform image manifest and sibling attestation manifest, reads the attestation manifest, filters layers by `in-toto.io/predicate-type` and requested predicates, and optionally reads statement blobs into `json.RawMessage`.

## State And Persistence
Read-only against local content. It does not cache attestations or fetch remote referrers.

## Dependencies And Integration Points
Depends on containerd content, Moby policy helpers, OCI descriptors, and image backend attestation options. It integrates with `GET /images/{name}/attestations` and BuildKit's sibling-manifest attestation storage model.

## Risks And Edge Cases
Docker Hardened Image and Sigstore referrer discovery are unsupported because `FetchReferrers` is a no-op. Statement bodies are read eagerly when requested, so large attestations can consume memory. Missing platform maps to `errdefs.NotFound`, while absent attestation manifests return nil without error.

## Test Signals
No direct tests in this subset. Expected coverage should include non-index images, missing platform, missing attestation manifest, predicate filtering, and include-statement read errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_attestations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_builder.go -->
# sources/cloud-native/moby/daemon/containerd/image_builder.go

## Purpose
Bridges Docker's classic builder layer/cache API to containerd images, content, snapshots, leases, and OCI manifests.

## Important APIs, Types, And Functions
- `GetImageAndReleasableLayer`, `pullForBuilder`, and `newROLayerForImage` resolve or pull builder base images and create read-only layer handles.
- `createLease`, `rolayer`, `rwlayer`, `NewRWLayer`, `Commit`, and `Release` manage temporary snapshots and leases.
- `CreateImage`, `createImageOCI`, `writeContentsForImage`, and `saveContainerConfig` create containerd images and content from Docker image configs and layer descriptors.
- Constants define classic builder image/content labels.

## Control Flow
Builder base resolution handles `FROM scratch`, local images unless force-pull is requested, and fallback pulls with auth/platform options. RO layer creation reads image config/rootfs diff IDs and leases the snapshot chain. RW layer creation prepares a snapshot, mounts it in a temp dir, commits it through containerd differ output, extracts diff ID labels, and returns a new RO layer. Image creation writes manifest/config/container-config blobs with GC labels, creates or replaces a dangling containerd image, logs create events, and unpacks it.

## State And Persistence
Creates leases, snapshots, content blobs, image records, dangling image names, parent labels, from-scratch labels, and container-config content labels. Temp mount directories and leases are released on `Release` or error cleanup.

## Dependencies And Integration Points
Depends on containerd client/snapshotter/differ/content/leases, OCI image-spec identity, Docker image-spec conversion, registry pull support, builder interfaces, archive empty-diff checks, events, and stream progress output. It is the core compatibility path for legacy Dockerfile build with containerd image store.

## Risks And Edge Cases
Every `GetImageAndReleasableLayer` caller must release returned layers to avoid lease leaks. Snapshot commit handles `AlreadyExists`, but mount/unmount failures can leave temp dirs or snapshots if cleanup fails. Empty diff handling avoids adding layers, so history and rootfs diff ID logic must stay aligned. Windows rejects `FROM scratch` in this path.

## Test Signals
No direct tests in this subset. Builder integration tests should cover local base reuse, forced pulls, platform mismatch warnings, RW layer commit/release, empty layer creation, parent labels, and unpack failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_changes.go -->
# sources/cloud-native/moby/daemon/containerd/image_changes.go

## Purpose
Computes filesystem changes between a container's writable layer and its parent image snapshot using containerd snapshot mounts.

## Important APIs, Types, And Functions
- `ImageService.Changes(ctx, ctr)` returns `[]archive.Change`.
- Uses container RW layer mount/unmount, snapshotter `Stat` and `View`, `mount.WithReadonlyTempMount`, and `archive.ChangesDirs`.

## Control Flow
The method validates `ctr.RWLayer`, stats the container snapshot to find its parent, creates a temporary read-only parent view snapshot, mounts the container RW layer, mounts the parent view through a temporary read-only mount, diffs the two directories, then removes the parent view and unmounts the RW layer in defers.

## State And Persistence
Creates a temporary snapshot view named from container ID plus random ID and removes it afterward. It temporarily mounts the RW layer and parent view. No image metadata is changed.

## Dependencies And Integration Points
Depends on containerd snapshotter/mount APIs, Moby archive diff utilities, and container layer abstractions. It powers image/container diff APIs for containerd-backed storage.

## Risks And Edge Cases
The code ignores the error returned by `snapshotter.View` before using `imageMounts`, which relies on later mount behavior to fail. Cleanup failures are logged only. A nil RWLayer is considered unexpected and returned as an error.

## Test Signals
No direct tests in this subset. Integration tests should assert added/modified/deleted paths and cleanup after parent-view creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_changes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_children.go -->
# sources/cloud-native/moby/daemon/containerd/image_children.go

## Purpose
Finds image child and parent relationships encoded by classic builder labels in the containerd image store.

## Important APIs, Types, And Functions
- `getImagesWithLabel` lists image IDs with a matching label key/value.
- `Children(ctx, id)` returns images whose parent label equals `id`.
- `parents(ctx, id)` follows parent labels upward from a child image and returns parent image records.

## Control Flow
Children lookup is a direct image-store label filter. Parent traversal resolves the starting image by digest string, repeatedly reads the parent label, parses it as a digest, resolves that digest to an image, appends it, and continues until no parent label is present.

## State And Persistence
Read-only against containerd image labels. Parent relationships are only as accurate as labels written by builder/commit paths.

## Dependencies And Integration Points
Depends on containerd image store filters, Moby image IDs, and digest parsing. `parents` is used by image deletion to prune dangling parent images.

## Risks And Edge Cases
Malformed parent labels abort parent traversal. Multiple image references for the same digest are collapsed by `resolveImage` behavior, which may pick one reference. BuildKit images generally do not carry these legacy labels, so lineage is limited to classic builder images.

## Test Signals
No direct tests in this subset. Image deletion prune tests and builder cache tests should verify child/parent label behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_children.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_commit.go -->
# sources/cloud-native/moby/daemon/containerd/image_commit.go

## Purpose
Creates a new image from a container's current filesystem and commit configuration using containerd diff, content, snapshots, and OCI image config generation.

## Important APIs, Types, And Functions
- `CommitImage` is the main commit API.
- `generateCommitImageConfig` builds the new Docker OCI image config and history entry.
- `createDiff` exports a diff layer and handles idmapped rootfs unremapping.
- `applyDiffLayer` applies the produced diff to a snapshot chain for the new image.
- `uniquePart`, `cleanup`, and `CommitBuildStep` support temporary keys and builder shim behavior.

## Control Flow
Commit loads the container and parent manifest/config if present, creates a lease, exports a diff between container snapshot and parent, generates updated rootfs/history/config, applies non-empty diffs into a new chain snapshot, appends the layer descriptor, and delegates image/content creation to `createImageOCI`. Empty diffs create a history entry marked `EmptyLayer` without adding a layer.

## State And Persistence
Reads container state from the container store, creates temporary view/prepare snapshots, writes diff content, commits new snapshots, writes image manifests/configs through `createImageOCI`, and persists parent labels/content labels. Cleanup defers remove temporary snapshots with timeout contexts where possible.

## Dependencies And Integration Points
Depends on containerd differ/applier/snapshotter/content, OCI identity chain IDs, archive empty-diff detection, daemon idmapping copy/unremap helpers, backend commit configs, and classic builder shim APIs.

## Risks And Edge Cases
Idmapped rootfs handling creates whole-snapshot copies in some cases and can be expensive. Empty diffs must still update history correctly. Cleanup is best effort, relying on leases and GC if snapshot removal fails. Missing parent manifests are valid for `FROM scratch`, so callers must tolerate nil parent state.

## Test Signals
No direct tests in this subset. Integration tests should cover commits from scratch and parent images, empty/non-empty diffs, idmapped containers, history generation, and builder `CommitBuildStep`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_commit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_delete.go -->
# sources/cloud-native/moby/daemon/containerd/image_delete.go

## Purpose
Implements image deletion, untagging, platform-specific content removal, conflict detection, and optional dangling-parent pruning for the containerd-backed image service.

## Important APIs, Types, And Functions
- `ImageDelete` is the public delete API.
- `deleteImagePlatforms` and `deleteImagePlatformByImageID` remove selected platform descriptor content.
- `deleteAll`, `imageDeleteHelper`, `untagReferences`, and `getSameReferences` manage image reference deletion.
- `checkImageDeleteConflict` classifies running-container, stopped-container, and active-reference conflicts.
- `imageDeleteConflict`, `conflictType`, and `isImageIDPrefix` support delete semantics and errors.

## Control Flow
Deletion resolves the requested ref/ID to a matching image and all references sharing the target. Named references may only untag matching references, while explicit image IDs or dangling refs can delete all references. Conflicts are hard for running containers and soft for stopped containers or multiple active refs unless force is used. Platform-specific deletion walks present descendants of the selected manifest and deletes content digests directly. Full deletion removes image records, logs untag/delete events, records API delete responses, and optionally prunes dangling parents quietly.

## State And Persistence
Mutates the containerd image store by deleting image names and can mutate the content store for platform-specific deletion. It may create a dangling image name to preserve parent/child relationships before deleting an active tag. It logs daemon image events and updates metrics on successful full API calls.

## Dependencies And Integration Points
Depends on image resolution helpers, container store usage checks, containerd image/content APIs, events, metrics, platform matchers, daemon image errors, and parent/child label helpers. It backs `docker image rm` and platform variant removal.

## Risks And Edge Cases
Reference grouping is subtle: tags, digest refs, dangling refs, and other repositories sharing the same target are treated differently. Platform deletion warns that shared manifests across indexes are not fully protected. Mounted image volumes are checked by source digest, but parentage conflicts are still a TODO. Force can untag images used by containers but must not remove running-container images through hard conflicts.

## Test Signals
`image_delete_test.go` covers many reference-resolution and untag/delete combinations. Additional integration coverage is needed for containers, forced deletes, platform deletion, events, and parent pruning.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_delete_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_delete_test.go

## Purpose
Tests image delete semantics for references, digest references, same-target tags, missing images, and remaining image-store records.

## Important APIs, Types, And Functions
- `TestImageDelete` is a table-driven parallel test over reference scenarios.
- `emptyTestContainerStore` and `testContainerStore` provide a no-container store implementation.
- Test helpers such as `nameTag`, `nameDigest`, `desc`, and `digestFor` are assumed from nearby test files.

## Control Flow
Each subtest creates a fresh metadata image store and event service, inserts starting image records, calls `ImageDelete` with default options, compares any expected error string, lists remaining images, and compares their names and target digests in order.

## State And Persistence
State is a temporary containerd metadata database. No content store or real containers are used, so tests focus on image-name records rather than blob deletion or container conflicts.

## Dependencies And Integration Points
Uses containerd metadata image store, namespaces, log test context, daemon image errors, and the image backend remove options. It directly guards `image_delete.go` reference grouping behavior.

## Risks And Edge Cases
The table does not test force, prune, running/stopped containers, platform-specific deletion, events, response records, or labels. The custom container store always reports no containers, so conflict logic is only partially covered.

## Test Signals
Failures indicate regressions in missing-image handling, digest/name matching, untag-only behavior, or full target deletion when references are equivalent.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_events.go -->
# sources/cloud-native/moby/daemon/containerd/image_events.go

## Purpose
Centralizes image event logging for the containerd-backed image service and safely copies image labels into event attributes when available.

## Important APIs, Types, And Functions
- `LogImageEvent(ctx, imageID, refName, action)` logs events with labels from `GetImage` when possible.
- `logImageEvent(img, refName, action)` logs name-only events from a known containerd image.
- `copyAttributes` copies labels into a destination map without aliasing.

## Control Flow
Public logging uses `context.WithoutCancel`, attempts to load image metadata to copy config labels, adds a `name` attribute when a reference name is provided, and logs through daemon events service. The private helper bypasses image lookup and logs digest plus optional name.

## State And Persistence
Writes daemon event records through `eventsService`; does not mutate images. Attribute maps are newly allocated per event.

## Dependencies And Integration Points
Depends on daemon event service, API event types, containerd image records, and image backend get options. Used by create, delete, save, load, untag, and related image operations.

## Risks And Edge Cases
Delete events often occur after image metadata is gone, so label copy is best effort. Event consumers may see different attributes depending on whether metadata was still readable. Labels are copied to avoid mutation by event triggers.

## Test Signals
No direct tests in this subset. Event integration tests should verify action type, actor ID, `name` attribute, and label immutability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_exporter.go -->
# sources/cloud-native/moby/daemon/containerd/image_exporter.go

## Purpose
Implements image save/load for the containerd image store, including multi-platform selection, Docker archive compatibility, content leases, referrer import/export, unpacking, and platform verification.

## Important APIs, Types, And Functions
- `ExportImage` saves named images, repositories, or explicit digests to a tar stream.
- `leaseContent` leases all reachable content descriptors while exporting.
- `LoadImage` imports a tar stream, handles requested platforms, creates dangling refs for unnamed/invalid images, warms identity cache, unpacks selected platforms, and logs load events.
- `verifyImagesProvidePlatform` checks imported images contain requested platform content.
- `referrersForImport`/`referrersForExport` expose OCI referrers from local content labels.

## Control Flow
Export builds archive options with platform filtering, skip-missing, non-distributable skip, and referrers. Repository names without tags export every tag in the repository; explicit digests are exported without a tag. Single-platform exports replace the target with the selected manifest descriptor. Load decompresses input, imports through containerd with platform/referrer options, optionally verifies requested platforms, unpacks host or requested platform manifests, emits progress lines, warms identity cache for named images, and logs events.

## State And Persistence
Export is read-only except for temporary leases. Load writes image records, dangling digest refs, content blobs, referrer labels, snapshots from unpack, identity cache warmup entries, progress output, and events.

## Dependencies And Integration Points
Depends on containerd archive import/export, content leases, compression, platform matchers, reference parsing, image resolution, push descriptor selection, referrer helpers, events, and identity cache warmup. It backs `docker save` and `docker load`.

## Risks And Edge Cases
Platform filtering is nuanced: no requested platforms tolerates missing variants, but explicit platforms turn missing content into not-found errors. Exporting by repository can include many tags. Import can succeed but unpack fail; errors are printed but the image remains imported. Referrer discovery parses labels and manifests best-effort, skipping malformed data.

## Test Signals
No direct tests in this subset. Save/load tests elsewhere should cover repository expansion, explicit digest exports, platform filtering, missing content, referrers, unpack warnings, and identity cache warmup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_exporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_history.go -->
# sources/cloud-native/moby/daemon/containerd/image_history.go

## Purpose
Builds Docker image history output for a selected platform by reading OCI config history, computing layer sizes from snapshots, and assigning tags/IDs through legacy builder parent labels.

## Important APIs, Types, And Functions
- `ImageHistory(ctx, name, platform)` returns `[]*image.HistoryResponseItem`.
- `getImageTags` converts non-dangling image names into familiar references.
- `getParentsByBuilderLabel` locates parent image records through `org.mobyproject.image.parent`.

## Control Flow
The method resolves the image, selects the best present manifest for requested/default platform, reads config rootfs/history, computes cumulative chain snapshot usage for each diff ID, walks history entries in reverse Docker order, assigns size only to non-empty layers, then walks parent images to fill IDs and tags for each history item.

## State And Persistence
Read-only against image store, content store, and snapshotter usage data. It updates image-action metrics for successful history requests.

## Dependencies And Integration Points
Depends on platform matching, OCI identity chain IDs, containerd snapshot usage, distribution reference parsing, image labels, metrics, and image resolution. It backs `docker image history`.

## Risks And Edge Cases
Missing snapshots are logged and reported as zero-size rather than fatal. History entries with more non-empty layers than sizes cause an error. Parent lookup only works for legacy builder labels, so BuildKit lineage may show less ancestry. Invalid image names are skipped for tags.

## Test Signals
No direct tests in this subset. Expected coverage should include platform-specific history, missing snapshots, empty layers, tag assignment, and parent-label traversal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_history.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_identity.go -->
# sources/cloud-native/moby/daemon/containerd/image_identity.go

## Purpose
Computes and caches image identity metadata: build refs from labels, pull repositories from distribution-source labels, and signature identity from local OCI referrer/signature chains and policy verification.

## Important APIs, Types, And Functions
- `imageIdentity`, `imageIdentityFromCache`, and `imageIdentityWithCachePolicy` combine label-derived identity with cached/computed signature identity.
- `imageIdentityFromLabels`, `imageIdentityBestMatch`, `imageIdentityCacheKey`, and `parseImageIdentityCacheKey`.
- Cache functions: `imageSignatureIdentityFromCache`, `updateImageIdentityCache`, `cacheComputedSignatureIdentity`, pruning/refresh helpers, `startImageIdentityCacheRefresh`, `stopImageIdentityCacheRefresh`, and `warmImageIdentityCache`.
- Verification helpers: `computeSignatureIdentity`, `signatureIdentity`, transient error classifiers, `cloneSignatureIdentity`, and `referrersProvider`.

## Control Flow
Identity lookup reads content labels, derives build/pull identities, computes a cache key from root image digest and best platform manifest, then checks in-memory and persistent caches. On cache miss with compute enabled, singleflight coalesces verification, resolves the signature chain, invokes the configured policy verifier, maps policy identity fields to API types, caches success or deterministic failures for 48 hours, and caches transient verification failures for 15 minutes. Maintenance periodically refreshes near-expiry entries and prunes expired memory/persistent records. Load/import paths can warm the cache asynchronously for available manifests.

## State And Persistence
Uses an in-memory map protected by `cacheMu`, an optional persistent `identitycache.Backend`, a singleflight group, and a background refresh goroutine. Cache entries store cloned signature values, including nil signatures, with `CachedAt` and `ExpiresAt`.

## Dependencies And Integration Points
Depends on containerd content/image stores, labels, distribution references, BuildKit exporter labels, Moby policy helpers, signature verifier providers, OCI referrers, platforms, errgroup, and identitycache backends. It integrates with image inspect/list paths that expose identity and with load warmup.

## Risks And Edge Cases
Transient-error detection currently relies partly on string matching. Cache keys include selected platform digest and platform string, so multi-platform selection changes create separate entries. Nil signatures are cacheable and can suppress repeat work. Background refresh must be stopped cleanly to avoid goroutine leaks. Persistent walk includes expired entries until prune, intentionally enabling refresh before deletion.

## Test Signals
`image_identity_test.go` covers deep-copy isolation, expiry, zero TTL, nil signatures, persistence across restart, refresh keys, persisted refresh, transient classification, label parsing, nil identity output, and cache-only behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_identity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_identity_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_identity_test.go

## Purpose
Tests image identity cache correctness, persistence, refresh semantics, transient signature error classification, label parsing, and cache-only behavior.

## Important APIs, Types, And Functions
- Cache tests cover `updateImageIdentityCache`, `imageSignatureIdentityFromCache`, `cloneSignatureIdentity`, pruning helpers, and cache key construction.
- Persistence tests use `identitycache.NewBoltDBBackend`.
- Refresh tests use `specialimage.MultiLayer`, `fakeImageService`, and `refreshImageIdentityCache`.
- Transient classification tests cover context, net, DNS, URL-wrapped, and string-based errors.
- `newWritableContentStore` and `writeTestBlob` build local metadata/content fixtures.

## Control Flow
Tests create isolated namespaces and temporary content stores, write cache entries or content labels, call identity/cache APIs, then assert returned values, map sizes, persisted reload behavior, sorted refresh keys, and parsed build/pull identities. The refresh test stores an expired persisted entry, confirms load misses, runs refresh, and verifies a fresh persisted entry exists.

## State And Persistence
Uses temporary local content stores, bbolt metadata DBs, bbolt identity cache backends, and in-memory cache maps. It explicitly mutates source and returned signature structs to prove deep-copy isolation.

## Dependencies And Integration Points
Depends on containerd local content and metadata stores, Moby special image fixtures, identitycache backend, BuildKit exporter labels, distribution-source labels, and `gotest.tools`.

## Risks And Edge Cases
Tests do not exercise a real policy verifier success path with a signed image; many signature paths are covered through cache and refresh plumbing. String-based transient detection tests make the current heuristic behavior explicit and could need revision when typed verifier errors become available.

## Test Signals
Failures signal cache aliasing, expired-entry leakage in memory, zero-TTL writes, broken persistence, refresh selection errors, wrong transient TTL classification, bad build/pull label parsing, or unexpected cache population from cache-only lookups.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_identity_test.go -->
