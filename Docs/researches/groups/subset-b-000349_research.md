# subset-b-000349 Research

Grouped source research for Ceph-CSI RBD snapshot/type contracts and utility packages covering Ceph commands, cluster config, RADOS connections, credentials, encryption, Kubernetes helpers, locking, logging, PID limits, and read affinity. Each section preserves the source path in its title and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snapshot_test.go -->
## sources/control-plane/ceph-csi/internal/rbd/snapshot_test.go

**Purpose:** Unit-tests RBD snapshot conversion and type narrowing used by the RBD snapshot implementation. It verifies that an internal `rbdSnapshot` can be converted into a CSI snapshot only when its CSI snapshot ID, source volume ID, and creation time are present, and that `rbdSnapFromSnapshot` accepts only the concrete RBD snapshot type behind the `types.Snapshot` interface.

**Important APIs and functions:** `TestToCSISnapshot` builds table cases for valid and missing `VolID`, `SourceVolumeID`, and `CreatedAt` fields and calls `(*rbdSnapshot).ToCSI`. `Test_rbdSnapFromSnapshot` passes a valid `*rbdSnapshot`, nil `types.Snapshot`, and an embedded mock `types.Snapshot` to `rbdSnapFromSnapshot`.

**Control flow, state, and persistence:** The tests are pure in-memory checks. They use `t.Parallel()` for the outer tests and each subtest, create static `rbdImage`/`rbdSnapshot` values, and compare errors or returned pointers. There is no Ceph, filesystem, journal, or Kubernetes state.

**Dependencies and integration points:** The file depends on Go `testing`, `reflect`, `time`, internal RBD concrete types, and `internal/rbd/types`. It protects the boundary where generic snapshot interfaces are converted back to RBD-specific snapshots for implementation paths that need RBD internals.

**Risks and test signals:** Coverage is narrow but directly targets API contract failures that would produce invalid CSI responses or panics from wrong snapshot implementations. It does not validate actual CSI field contents beyond error/no-error behavior and pointer equality, so regressions in exact `csi.Snapshot` fields need tests elsewhere.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snapshot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/group.go -->
## sources/control-plane/ceph-csi/internal/rbd/types/group.go

**Purpose:** Defines the interface contract for journal-backed RBD volume groups. It is a type boundary that lets the RBD manager, CSI-Addons volume-group services, and concrete RBD group objects interact without importing implementation structs.

**Important APIs and types:** `journalledObject` requires `GetID`, `GetName`, `GetPool`, `GetClusterID`, and `Destroy`, modeling the common journal handle, backend name, pool, cluster, and lifecycle surface. `VolumeGroup` embeds that contract and adds `GetIOContext`, `ToCSI`, `Create`, `Delete`, `AddVolume`, `RemoveVolume`, `ListVolumes`, and crash-consistent `CreateSnapshots`.

**Control flow, state, and persistence:** This file has no executable logic. The interface comments define expected persistence behavior: group identity is stored in the CSI/journal handle and backend group name, while implementations create/delete backend RBD groups, mutate group membership, and allocate resources that must be released through `Destroy`.

**Dependencies and integration points:** It depends on `context`, go-ceph `rados.IOContext`, CSI-Addons `volumegroup.VolumeGroup`, and `util.Credentials`. Consumers are expected to use the returned IO context for librbd group operations and credentials for snapshot creation.

**Risks and test signals:** Changes here are high blast-radius because implementers across the RBD package must satisfy the interface. There are no direct tests in this file; compile-time conformance and volume-group operation tests elsewhere are the main signals. The key risk is mismatched lifecycle ownership for IO contexts and `Destroy`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/group.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/manager.go -->
## sources/control-plane/ceph-csi/internal/rbd/types/manager.go

**Purpose:** Defines the high-level RBD manager contract for resolving volumes, snapshots, volume groups, and volume group snapshots from CSI handles/names while maintaining backend and journal consistency.

**Important APIs and types:** `VolumeResolver.GetVolumeByID`, `SnapshotResolver.GetSnapshotByID`, and `VolumeGroupResolver` methods provide handle-to-object resolution, volume-group ID construction, and group membership checks. `Manager` embeds all resolvers and adds `Destroy`, `CreateVolumeGroup`, `GetVolumeGroupSnapshotByID`, `GetVolumeGroupSnapshotByName`, `CreateVolumeGroupSnapshot`, and `RegenerateVolumeGroupJournal`.

**Control flow, state, and persistence:** The file is declarative. Comments specify that concrete managers allocate backend objects, update journal entries, resolve CSI IDs to backend identities, and can regenerate OMAP journal data for an existing group. Manager lifecycle is explicit through `Destroy`.

**Dependencies and integration points:** It depends only on `context` and sibling RBD interfaces. It is the service boundary used by CSI controllers and CSI-Addons handlers to keep object resolution and journal repair centralized.

**Risks and test signals:** Interface changes affect many controller and manager implementations. The most important behavioral risks are inconsistent journal/backend updates, incorrect mapping of pool ID/name into group handles, and accepting volume sets that are not actually in the same group. No direct tests exist here; compile-time conformance and manager integration tests carry the signal.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/mirror.go -->
## sources/control-plane/ceph-csi/internal/rbd/types/mirror.go

**Purpose:** Defines the abstraction for RBD mirroring operations and status reporting across images or groups. It models promotion/demotion, resync, global/local/remote site state, sync details, and snapshot scheduling.

**Important APIs and types:** `FlattenMode` has `FlattenModeNever` and `FlattenModeForce`, used by volume parent handling. `Mirror` exposes `EnableMirroring`, `DisableMirroring`, `Promote`, `Demote`, `Resync`, `GetMirroringInfo`, `GetGlobalMirroringStatus`, and `AddSnapshotScheduling`. `MirrorInfo`, `GlobalStatus`, `SiteStatus`, and `SyncInfo` model primary state, site health, timestamps, descriptions, last sync duration/bytes/time, and active sync state.

**Control flow, state, and persistence:** This is a contract file; implementations perform librbd/admin mutations and status queries. State is remote in Ceph mirroring metadata and snapshot scheduling configuration, with status reflecting local and peer site observations.

**Dependencies and integration points:** It depends on go-ceph `rbd` mirror mode, `rbd/admin` scheduling types, `context`, and `time`. It integrates with RBD volume/group mirroring controllers and CSI-Addons failover/recovery workflows.

**Risks and test signals:** Mirroring is operationally sensitive: incorrect primary state, forced promotion/demotion, or stale remote-site status can cause split-brain or failed failover. The duplicated comment on `GetGlobalMirroringStatus` is cosmetic but could obscure docs. No direct tests exist in this file; status parsers and mirror workflow integration tests must validate behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/mirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/snapshot.go -->
## sources/control-plane/ceph-csi/internal/rbd/types/snapshot.go

**Purpose:** Defines the public RBD snapshot interface consumed by manager, controller, and metadata services. It extends journal identity with deletion, CSI conversion, creation time, volume-group linkage, size, and block metadata processing.

**Important APIs and types:** `MetadataCallback` sends slices of CSI `BlockMetadata`. `Snapshot` embeds `journalledObject` and requires `Delete`, `ToCSI`, `GetCreationTime`, `SetVolumeGroup`, `GetSize`, and `ProcessMetadata`, including optional delta processing against a base snapshot.

**Control flow, state, and persistence:** The interface implies backend snapshot deletion, metadata mutation for group association, journal identity lookup, and iterative block metadata scans with pagination parameters `startingOffset` and `maxResults`. Persistent state belongs to RBD snapshots, OMAP metadata, and potentially volume-group identifiers.

**Dependencies and integration points:** It depends on CSI protobuf types, `context`, `time`, and `util.Credentials`. Integration points include CSI snapshot responses, Snapshot Metadata Service callbacks, and group snapshot metadata.

**Risks and test signals:** `ProcessMetadata` has high risk around pagination, base snapshot deltas, and callback error propagation. `SetVolumeGroup` must safely update snapshot metadata with proper credentials. There are no tests here, but `snapshot_test.go` covers part of `ToCSI` behavior in the concrete RBD implementation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/volume.go -->
## sources/control-plane/ceph-csi/internal/rbd/types/volume.go

**Purpose:** Defines the RBD volume contract, split into snapshot-specific operations, CSI-Addons operations, and base volume lifecycle/metadata methods.

**Important APIs and types:** `snapshottableVolume` requires `NewSnapshotByID` and `PrepareVolumeForSnapshot`. `csiAddonsVolume` includes group membership, key rotation, sparsify, parent image validation/flattening, mirror resync ID repair, and `ToMirror`. `Volume` embeds `journalledObject`, both subinterfaces, and adds `Delete`, `ToCSI`, `GetCreationTime`, `GetMetadata`, and `SetMetadata`.

**Control flow, state, and persistence:** No logic is implemented here. Concrete volumes manipulate RBD images, snapshots, group membership, image metadata, encryption metadata, mirroring state, and journal entries. The parent-image handling comment defines a control policy for missing, trashed, non-mirrored, and force-flatten parent states.

**Dependencies and integration points:** It depends on CSI volume protobufs, `context`, `time`, and `util.Credentials`. It is consumed by CSI controller paths, CSI-Addons volume-group/encryption/sparsify/mirroring paths, and snapshot code.

**Risks and test signals:** This interface is broad and operationally dense; changes can break many flows. Risks include failing to flatten when required, rotating keys without metadata consistency, and returning group IDs that do not match backend membership. Tests are indirect via concrete RBD volume implementations and compile-time interface use.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/volume_group_snapshot.go -->
## sources/control-plane/ceph-csi/internal/rbd/types/volume_group_snapshot.go

**Purpose:** Defines the interface for inspecting and managing RBD volume group snapshots, preserving journal identity while exposing CSI conversion and member snapshot listing.

**Important APIs and types:** `VolumeGroupSnapshot` embeds `journalledObject` and requires `Delete`, `ToCSI`, `GetCreationTime`, and `ListSnapshots`. `ToCSI` returns CSI `VolumeGroupSnapshot`, while `ListSnapshots` exposes the member `Snapshot` interfaces.

**Control flow, state, and persistence:** This file has no executable logic. Implementations are expected to delete backend group snapshot state, read journal identity, produce CSI response objects, and enumerate member snapshots created under a crash-consistent group snapshot.

**Dependencies and integration points:** It depends on CSI protobuf types, `context`, and `time`. The interface is used by RBD manager and CSI group snapshot controller paths.

**Risks and test signals:** The key risks are incomplete member snapshot lists, stale journal data after deletion, and incorrect creation timestamps in CSI responses. Direct tests are absent; coverage must come from concrete group snapshot manager tests and compile-time conformance.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/volume_group_snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cephcmds.go -->
## sources/control-plane/ceph-csi/internal/util/cephcmds.go

**Purpose:** Provides shared Ceph command and RADOS helper operations: external command execution, pool ID/name lookup, object creation/deletion, and OSD blocklist management.

**Important APIs and functions:** `ExecuteCommandWithNSEnter`, `ExecCommand`, and `ExecCommandWithTimeout` run external commands with separated stdout/stderr and sanitized logging. `GetPoolID`, `GetPoolName`, and `GetPoolIDs` resolve pools through the global connection pool. `CreateObject` and `RemoveObject` create/delete RADOS objects with namespace support and map RADOS errors to `ErrObjectExists`/`ErrObjectNotFound`. `AddCephBlocklist` and `RemoveCephBlocklist` use go-ceph OSD admin APIs and constants `AutoBlocklistTime`/`MaxBlocklistTime`.

**Control flow, state, and persistence:** Command helpers capture buffers, run subprocesses, and log success or wrapped errors unless context is `context.TODO()`. Timeout execution uses a new background timeout context and wraps deadline exceeded. Pool and object helpers acquire pooled RADOS connections or `ClusterConnection`, open IO contexts, optionally set namespaces, and mutate Ceph pools. Blocklisting connects to the cluster, builds `osdAdmin.AddressEntry`, formats IPv4/IPv6 nonce addresses when needed, and adds/removes blocklist entries.

**Dependencies and integration points:** Depends on `os/exec`, net parsing, go-ceph `rados` and OSD admin packages, internal logging, credentials, connection pool, and secret stripping. It integrates with provisioning, fencing/unfencing, OMAP/object lifecycle, and any code needing command-line fallback.

**Risks and test signals:** Subprocess calls are sensitive to secret leakage, timeout semantics, and stderr handling. `ExecCommandWithTimeout` ignores the caller context for cancellation and always bases timeout on `context.Background`. RADOS helpers require balanced pooled connection use. Blocklist formatting must handle IPv6 brackets and nonce/range modes correctly. `cephcmds_test.go` covers timeout and stdout behavior only; cluster operations need integration coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cephcmds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cephcmds_test.go -->
## sources/control-plane/ceph-csi/internal/util/cephcmds_test.go

**Purpose:** Unit-tests the timeout command runner for successful command output and process termination on timeout.

**Important APIs and functions:** `TestExecCommandWithTimeout` runs `echo hello` with a one-second timeout and `sleep 3` with a one-second timeout, then checks stdout, error presence, and `errors.Is(err, context.DeadlineExceeded)`.

**Control flow, state, and persistence:** The test is table-driven and parallelized. It executes real local programs but does not touch Ceph state or persistent files.

**Dependencies and integration points:** Depends on standard `context`, `errors`, `testing`, and `time`. It protects callers that rely on timeout errors being wrap-detectable and stdout being returned.

**Risks and test signals:** The test assumes POSIX `echo` and `sleep` are available. It does not cover stderr inclusion, command-not-found, logging suppression for `context.TODO`, caller context cancellation, or secret stripping.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cephcmds_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cephconf.go -->
## sources/control-plane/ceph-csi/internal/util/cephconf.go

**Purpose:** Creates a minimal `/etc/ceph/ceph.conf` and `/etc/ceph/keyring` so Ceph libraries and CLI tools have baseline configuration files.

**Important APIs and functions:** `WriteCephConfig` creates `/etc/ceph`, writes default cephx-required config if `CephConfigPath` does not exist, and calls `createKeyRingFile`. `createCephConfigRoot` and `createKeyRingFile` are small filesystem helpers. Constants define `CephConfigPath`, `cephConfigRoot`, and `keyRing`.

**Control flow, state, and persistence:** This file writes persistent host/container files under `/etc/ceph`. It preserves existing `ceph.conf` and keyring files by only creating missing paths. Permissions are `0755` for the directory and `0600` for the config; the keyring uses `os.Create` defaults.

**Dependencies and integration points:** Depends on `os`. It supports `ConnPool.Get`, which reads `CephConfigPath`, and any Ceph CLI command that expects config/keyring paths.

**Risks and test signals:** Writing under `/etc/ceph` requires permissions and can fail in restricted containers. Existing malformed files are not corrected. There are no direct tests in this subset; behavior is validated indirectly by components that need Ceph config.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cephconf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cluster_mapping.go -->
## sources/control-plane/ceph-csi/internal/util/cluster_mapping.go

**Purpose:** Reads failover/failback cluster mapping configuration and resolves alternate cluster IDs and monitor lists when a CSI object created in one cluster is handled in another.

**Important APIs and types:** `ClusterMappingInfo` holds cluster ID mappings plus RBD pool ID and CephFS filesystem ID mappings. `readClusterMappingInfo` loads JSON. `getClusterMappingInfo` filters mapping entries that mention the requested ID as key or value. `GetMappedID` returns the opposite side of a mapping pair. `fetchMappedClusterIDAndMons` and exported `FetchMappedClusterIDAndMons` combine mapping lookup with CSI config monitor lookup.

**Control flow, state, and persistence:** Mapping is read from `/etc/ceph-csi-config/cluster-mapping.json` or a supplied test path on every call. Missing mapping files are treated as non-errors to preserve non-failover behavior. When mappings exist, the resolver tries mapped IDs first and skips ones whose monitors are not in CSI config, then falls back to the original cluster ID.

**Dependencies and integration points:** Depends on JSON, filesystem reads, internal logging, and `Mons` from CSI config. It integrates with restore/failover paths that parse cluster IDs from CSI handles and need local monitor endpoints.

**Risks and test signals:** Ambiguous mappings are possible because map iteration order is randomized and multiple entries can map a cluster to different targets. Raw invalid JSON content is included in errors, which helps debugging but can be noisy. Tests cover missing files, no mapping, bidirectional mapping counts, mapped ID helper, mapped monitor resolution, and fallback/error behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cluster_mapping.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cluster_mapping_test.go -->
## sources/control-plane/ceph-csi/internal/util/cluster_mapping_test.go

**Purpose:** Validates cluster mapping JSON parsing, bidirectional cluster/pool/filesystem mapping lookup, simple ID mapping, and monitor resolution through mapped cluster IDs.

**Important APIs and functions:** `TestGetClusterMappingInfo` builds two mapping entries and checks file-missing, empty-data, unmatched, and site1/site2/site3 matching behavior. `validateMapping` checks cluster, RBD pool, and CephFS ID mappings. `TestGetMappedID` covers key, value, and no-match cases. `TestFetchMappedClusterIDAndMons` writes CSI and mapping configs and checks mapped/fallback monitor results.

**Control flow, state, and persistence:** Tests write temporary JSON files and also mutate the package-level `clusterMappingConfigFile` for exported `GetClusterMappingInfo`. Many subtests are parallel, while shared package variable mutation happens after the first table loop.

**Dependencies and integration points:** Uses JSON, temp files, string joining, reflection, and `api/deploy/kubernetes.ClusterInfo`. It exercises integration between mapping and `csiconfig.Mons`.

**Risks and test signals:** The tests give good signal for bidirectional mappings and fallback behavior. A residual risk is package-level `clusterMappingConfigFile` mutation in a parallel test process, which can interfere with other tests in the same package if they run concurrently. Random Go map iteration can also make first-success mapped target behavior difficult to assert for ambiguous config.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cluster_mapping_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/conn_pool.go -->
## sources/control-plane/ceph-csi/internal/util/conn_pool.go

**Purpose:** Implements a reference-counted pool of go-ceph `rados.Conn` objects keyed by monitor list, user, and key contents, with periodic garbage collection of idle connections.

**Important APIs and types:** `ConnPool` stores interval, expiry, timer, lock, and `map[string]*connEntry`. `NewConnPool`, `Destroy`, `Get`, `Copy`, `Put`, `gc`, `generateUniqueKey`, `getConn`, and `connEntry` methods manage lifecycle and reference counts.

**Control flow, state, and persistence:** `Get` reads the key file to build a stable key, checks existing entries under an RW lock, creates and connects a new `rados.Conn` if absent, then inserts it under a write lock with race handling. `Copy` increments reference count for an existing pointer. `Put` decrements but does not destroy immediately. `gc` destroys entries with zero users and age greater than expiry, then resets the timer. `Destroy` stops GC, panics if entries still have users, and shuts down all connections.

**Dependencies and integration points:** Depends on `sync`, `time`, `os`, and go-ceph `rados`. `ClusterConnection` and pool/object helpers use the global pool for Ceph access.

**Risks and test signals:** Reference leaks prevent GC and make `Destroy` panic. Double `Put` can decrement below zero because no guard prevents it. Creating a connection outside the write lock avoids blocking but can race, so the loser destroys the extra connection. The unique key includes keyfile contents, not path, which is correct for rotated temp key files but reads secret material into memory. Tests use a fake getter and validate reuse, refcounting, and GC without needing a real Ceph cluster.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/conn_pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/conn_pool_test.go -->
## sources/control-plane/ceph-csi/internal/util/conn_pool_test.go

**Purpose:** Tests connection pool reference counting, key-based reuse, and garbage collection using a fake getter that avoids connecting to Ceph.

**Important APIs and functions:** `fakeGet` mirrors `ConnPool.Get` up to the real `Connect` call and inserts a new `rados.Conn`. `TestConnPool` covers first get, second get reusing the same map entry and increasing users, `Put` decreasing users, forced expiry, and `gc` removing the idle entry.

**Control flow, state, and persistence:** The test creates a temp keyfile, a pool with long durations, and subtests that share `conn`/`unique` state, so it intentionally does not run subtests in parallel. It mutates `lastUsed` to force expiration.

**Dependencies and integration points:** Uses go-ceph `rados.NewConn` but does not connect to a cluster. It exercises internal pool data structures directly.

**Risks and test signals:** Good unit signal for reuse and GC. It does not cover real `ParseCmdLineArgs`, `ReadConfigFile`, connect failures, `Copy`, `Destroy` panic, or double `Put` underflow. Because it reaches into internals, refactors need coordinated test updates.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/conn_pool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/connection.go -->
## sources/control-plane/ceph-csi/internal/util/connection.go

**Purpose:** Wraps pooled RADOS connections with helper methods for CephFS, RBD, OSD, task, NFS, IO context, FSID, and address access.

**Important APIs and types:** `ClusterConnection` stores `*rados.Conn`, credentials, and a discard setting. Package globals create `connPool` with long interval/expiry. Methods include `Connect`, `Destroy`, `Copy`, `GetIoctx`, `GetFSAdmin`, `GetOSDAdmin`, `GetFSID`, `GetRBDAdmin`, `GetTaskAdmin`, `GetNFSAdmin`, and `GetAddrs`.

**Control flow, state, and persistence:** `Connect` lazily obtains a pooled connection and stores credentials. `Destroy` returns the connection to the pool but does not nil the field. `Copy` creates another `ClusterConnection` around the same pooled connection with an incremented refcount. Admin and IO context getters validate that a connection exists and then instantiate go-ceph admin wrappers or open a pool IO context.

**Dependencies and integration points:** Depends on go-ceph RADOS, CephFS admin, RBD admin, OSD admin, and NFS admin packages. It is the central utility boundary used by RBD, CephFS, NFS, and blocklist helpers.

**Risks and test signals:** Callers must balance each `Connect`/`Copy` with `Destroy`. Because `Destroy` does not nil `cc.conn`, calling it twice can double-decrement the pool refcount. Pool-not-found errors are normalized to `ErrPoolNotFound`. No direct tests in this subset cover this wrapper; connection behavior is mainly integration-tested with Ceph.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/connection.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/credentials.go -->
## sources/control-plane/ceph-csi/internal/util/credentials.go

**Purpose:** Converts Kubernetes/CSI secret maps into temporary Ceph key files and user IDs for go-ceph/CLI authentication, including legacy admin fields and migration secret formats.

**Important APIs and types:** `Credentials` holds `ID` and `KeyFile`. Constructors are `NewUserCredentials`, `NewAdminCredentials`, and `NewUserCredentialsWithMigration`. `DeleteCredentials`, `storeKey`, `newCredentialsFromSecret`, `GetMonValFromSecret`, `ParseAndSetSecretMapFromMigSecret`, and `isMigrationSecret` provide lifecycle and parsing helpers.

**Control flow, state, and persistence:** Constructors validate required map fields, write key contents to a temp file under `/tmp/csi/keys`, and return the temp path. Admin credentials prefer `userID/userKey` and fall back to deprecated `adminID/adminKey`. Migration secrets with key `key` are converted to `userKey` and `userID`, defaulting the user to `admin` unless `adminId` is set. `DeleteCredentials` removes the temp key file.

**Dependencies and integration points:** Depends on `os`, internal logging, and constants consumed by RADOS connection code. It integrates with CSI request secrets, migration volume flows, and `connPool.Get`.

**Risks and test signals:** `/tmp/csi/keys` must exist and be writable. Temp key files must be removed by callers to avoid credential residue. `newCredentialsFromSecret` indexes `secrets[keyField]` without checking presence separately, so missing and empty values share the same error. Tests cover migration secret detection and conversion only, not temp file creation, admin fallback, monitor extraction, or cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/credentials.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/credentials_test.go -->
## sources/control-plane/ceph-csi/internal/util/credentials_test.go

**Purpose:** Tests migration-secret detection and conversion into normal Ceph-CSI user credential fields.

**Important APIs and functions:** `TestIsMigrationSecret` checks that a non-empty `key` marks a migration secret. `TestParseAndSetSecretMapFromMigSecret` checks default admin ID, invalid empty/missing key cases, and explicit `adminId` mapping.

**Control flow, state, and persistence:** Pure in-memory table tests with parallel subtests; no temp key files are created.

**Dependencies and integration points:** Uses `reflect.DeepEqual` and Go testing. It protects migration volume request credential compatibility.

**Risks and test signals:** Coverage does not exercise actual `NewUserCredentialsWithMigration`, key file storage, cleanup, or monitor lookup. It also does not validate behavior when unrelated fields are present in the migration secret.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/credentials_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crushlocation.go -->
## sources/control-plane/ceph-csi/internal/util/crushlocation.go

**Purpose:** Converts configured Kubernetes node label names and actual node labels into a Ceph CRUSH location map used for localized read-affinity options.

**Important APIs and functions:** `GetCrushLocationMap` handles the empty-config fast path and calls `getCrushLocationMap`. The helper splits comma-separated label names, finds matching non-empty node label values, derives the CRUSH type from the suffix after `/`, maps `hostname` to `host`, trims whitespace, and replaces dots in values with hyphens.

**Control flow, state, and persistence:** The function is stateless and returns nil when there are no configured labels or no matching non-empty node labels. Output is a map from CRUSH bucket type to sanitized value.

**Dependencies and integration points:** Depends on `strings` and internal logging. It integrates with CSI config read-affinity settings, Kubernetes node label lookup, and `ConstructReadAffinityMapOption`.

**Risks and test signals:** If a configured label lacks `/`, `strings.IndexRune` returns -1 and the full key is used due to slicing at zero, which may be surprising but avoids panic. Map output order is nondeterministic. Tests cover empty inputs, matches, multiple labels, no match, dot replacement, hostname mapping, and empty values.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crushlocation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crushlocation_test.go -->
## sources/control-plane/ceph-csi/internal/util/crushlocation_test.go

**Purpose:** Unit-tests CRUSH location map derivation from requested label names and node labels.

**Important APIs and functions:** `Test_getCrushLocationMap` covers empty configuration, empty node labels, single and multiple matches, no match, Ceph-compatible dot replacement, Kubernetes `hostname` to Ceph `host`, and skipping matching labels with empty values.

**Control flow, state, and persistence:** Pure table-driven tests using `require.Equal`. There is no external state.

**Dependencies and integration points:** Depends on `testify/require` and the unexported helper. It validates the input feeding read-affinity map construction.

**Risks and test signals:** Good signal for common topology labels. It does not cover labels without separators, whitespace-heavy label names, duplicate CRUSH types, or nondeterministic ordering downstream.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crushlocation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crypto.go -->
## sources/control-plane/ceph-csi/internal/util/crypto.go

**Purpose:** Provides volume encryption orchestration for Ceph-CSI, including KMS-backed passphrase storage, passphrase generation, LUKS device mapping helpers, and calls into the cryptsetup wrapper.

**Important APIs and types:** `VolumeEncryption` stores a KMS, optional DEK store, ID, and cipher options. Important functions include `FetchEncryptionKMSID`, `FetchEncryptionType`, `NewVolumeEncryption`, `SetDEKStore`, `RemoveDEK`, `StoreCryptoPassphrase`, `StoreNewCryptoPassphrase`, `GetCryptoPassphrase`, `generateNewEncryptionPassphrase`, `VolumeMapper`, `EncryptVolume`, `OpenEncryptedVolume`, `ResizeEncryptedVolume`, `CloseEncryptedVolume`, `IsDeviceOpen`, and `DeviceEncryptionStatus`.

**Control flow, state, and persistence:** KMS flow chooses a default KMS ID when encryption is true and ID is empty, configures integrated DEK stores automatically, or returns `ErrDEKStoreNeeded` for metadata-style stores. Passphrases are generated from `crypto/rand`, base64 URL encoded, encrypted through KMS, and stored in the DEK store. LUKS flow delegates to a package-level wrapper, logs stderr/errors, blocks resize when integrity mode is detected, and parses `cryptsetup status` output for mapper-to-device resolution.

**Dependencies and integration points:** Depends on internal KMS interfaces, `cryptsetup`, logging, and package crypto enum parsing. It integrates with RBD/CephFS volume staging, encryption key rotation, and KMS provider plugins.

**Risks and test signals:** `StoreCryptoPassphrase` and `GetCryptoPassphrase` assume `dekStore` is set; callers must handle `ErrDEKStoreNeeded`. `DeviceEncryptionStatus` treats cryptsetup status errors as non-LUKS and can hide real command failures. Integrity-protected volumes cannot be resized. Tests cover passphrase length, a default SecretsKMS workflow, and encryption type parsing; LUKS command behavior needs wrapper/integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crypto.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crypto_test.go -->
## sources/control-plane/ceph-csi/internal/util/crypto_test.go

**Purpose:** Tests passphrase generation, the default KMS encryption workflow, and encryption type parsing.

**Important APIs and functions:** `TestGenerateNewEncryptionPassphrase` decodes the base64 output and checks byte length. `TestKMSWorkflow` creates the default KMS from a secret, creates `VolumeEncryption`, stores a new passphrase, and reads it back. `TestFetchEncryptionType` checks fallback, empty invalid value, block/file strings, and invalid strings.

**Control flow, state, and persistence:** Tests are parallel and mostly in-memory. The KMS workflow uses the test/default KMS behavior rather than real external KMS state.

**Dependencies and integration points:** Depends on `testify/require`, internal KMS, and package crypto enum types. It protects controller option parsing and KMS integration at a unit level.

**Risks and test signals:** It does not cover `FetchEncryptionKMSID`, missing DEK store errors, LUKS mapper helpers, cryptsetup status parsing, or command execution paths. The default KMS test relies on provider-specific semantics where the fetched passphrase equals the configured secret.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crypto_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cryptsetup/crypsetup_test.go -->
## sources/control-plane/ceph-csi/internal/util/cryptsetup/crypsetup_test.go

**Purpose:** Unit-tests cryptsetup option recommendation, allowlist validation, LUKS status field modeling, and parsing of `cryptsetup status` output. The filename appears to contain a typo (`crypsetup_test.go`) but the package is `cryptsetup`.

**Important APIs and functions:** `TestGetRecommendation` covers invalid cipher, uncommon key sizes, unknown integrity modes, and recommended AES-XTS-random/HMAC combinations. `TestAllowedEncryptionOptions` exercises `EncryptionOptions.SetCipher`, `SetKeySize`, and `SetIntegrityMode`. `TestLuksStatus` tests status setters, integrity-mode translation, sector size, key-size subtraction, and `EncryptionOptions.Equal`. `TestParseLuksStatus` parses valid compound-mode output and malformed outputs. `setError` is a small assertion helper.

**Control flow, state, and persistence:** Tests are pure and parallel, using synthetic status strings. They do not run `cryptsetup` or touch block devices.

**Dependencies and integration points:** Depends on `testify/assert` and `require`. It protects the validation and parser logic that `crypto.go` uses to judge resize safety and report configuration quality.

**Risks and test signals:** Good signal for current recommendation maps and parser assumptions. It does not test command argument construction, temporary key files, AddKey/RemoveKey/VerifyKey behavior, timeout behavior, or all allowed ciphers and integrity modes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cryptsetup/crypsetup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cryptsetup/cryptsetup.go -->
## sources/control-plane/ceph-csi/internal/util/cryptsetup/cryptsetup.go

**Purpose:** Wraps Linux `cryptsetup` for LUKS2 volume operations and centralizes encryption option validation, recommendation scoring, LUKS status parsing, and key-slot management.

**Important APIs and types:** Constants define timeouts, PBKDF resource limits, LUKS2 header sizing, status field names, and recommendation levels. `LuksStatus` parses cipher, keysize, integrity mode/key size, and sector size. `EncryptionOptions` validates cipher/integrity allowlists and compares desired options to status. `GetRecommendation` scores cipher/key/integrity tuples. `LUKSWrapper` exposes `Format`, `Open`, `Resize`, `Close`, `Status`, `AddKey`, `RemoveKey`, `VerifyKey`, and `IsIntegrityProtected`.

**Control flow, state, and persistence:** `Format` constructs `cryptsetup luksFormat` arguments for LUKS2, optional cipher/integrity/key/sector options, reduced PBKDF resources, and custom LUKS2 metadata/keyslot sizes. `AddKey` writes current and new passphrases to temp files, handles full slots by verifying whether the new key already exists, removes the old slot if necessary, and retries recursively. `RemoveKey` tolerates inactive slots. `VerifyKey` uses read-only `open --test-passphrase`. `ParseLuksStatus` scans colon-separated fields and translates LUKS integrity names. `execCryptsetupCommand` runs the binary with optional stdin, sanitized args, stdout/stderr capture, and context-deadline handling.

**Dependencies and integration points:** Depends on `os/exec`, context, temp file helper, Kubernetes volume size constants, logging, and secret stripping. It integrates with `util/crypto.go`, block device staging, resize, and encryption key rotation.

**Risks and test signals:** `NewLUKSWrapper` accepts a context but does not create the documented `ExecutionTimeout`; callers must supply a deadline if desired. Key-slot replacement depends on stderr string matching from cryptsetup. Temp key files must be removed even on failure. Parser errors have a few typo-prone messages and one branch wraps the wrong variable for key size parse. Tests cover validation and parser logic but not live command execution or key-slot mutation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cryptsetup/cryptsetup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/csiconfig.go -->
## sources/control-plane/ceph-csi/internal/util/csiconfig.go

**Purpose:** Reads `/etc/ceph-csi-config/config.json` and exposes typed helper accessors for monitors, namespaces, read affinity, network namespaces, mirror daemon counts, mount options, cluster IDs, and secret references.

**Important APIs and functions:** `readClusterInfo` loads JSON into `api/deploy/kubernetes.ClusterInfo` and finds a cluster ID. Accessors include `Mons`, `GetRBDRadosNamespace`, `GetCephFSRadosNamespace`, `GetRBDMirrorDaemonCount`, `CephFSSubvolumeGroup`, `GetMonsAndClusterID`, `GetClusterID`, network namespace getters, `GetCrushLocationLabels`, `GetCephFSMountOptions`, `GetRBDControllerPublishSecretRef`, `GetCephFSControllerPublishSecretRef`, and `GetRBDNodePublishSecretRef`.

**Control flow, state, and persistence:** The file is read on each call; no cache is kept. `readClusterInfo` returns `ErrConfigNotFound` when a cluster ID is absent. Some accessors provide backward-compatible defaults: CephFS subvolume group `csi`, CephFS RADOS namespace `csi`, and RBD mirror daemon count `1`. `GetMonsAndClusterID` optionally routes through cluster mapping before monitor lookup.

**Dependencies and integration points:** Depends on filesystem JSON, deployment API schema, and cluster mapping. It is a central integration point for controller/node configuration, multi-cluster support, read affinity, CephFS/RBD/NFS net namespaces, and secret reference lookup.

**Risks and test signals:** Re-reading config keeps behavior fresh but repeats IO and parsing. Error messages include raw malformed JSON buffers. Monitor lists must be non-empty. Tests cover malformed configs, monitor extraction, net namespace accessors, read-affinity labels, mount options, mirror daemon defaults/type errors, and controller publish secret references.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/csiconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/csiconfig_test.go -->
## sources/control-plane/ceph-csi/internal/util/csiconfig_test.go

**Purpose:** Exercises CSI config accessors against temporary JSON configs, including malformed input and optional per-cluster fields.

**Important APIs and functions:** Tests cover `Mons`, `GetRBDNetNamespaceFilePath`, `GetCephFSNetNamespaceFilePath`, `GetNFSNetNamespaceFilePath`, `GetCrushLocationLabels`, `GetCephFSMountOptions`, `GetRBDMirrorDaemonCount`, `GetRBDControllerPublishSecretRef`, and `GetCephFSControllerPublishSecretRef`.

**Control flow, state, and persistence:** Each test writes a temp config file and runs parallel subtests for independent cluster IDs. `TestCSIConfig` sequentially rewrites one file to check missing, empty, malformed, missing monitors, wrong monitor type, absent cluster, and valid monitor cases.

**Dependencies and integration points:** Uses deployment `ClusterInfo`, Kubernetes `corev1.SecretReference`, JSON, temp files, and `testify/require`. It validates the config schema consumed by controller/node startup and request handling.

**Risks and test signals:** Good signal for many optional fields and defaults. It does not cover `GetCephFSRadosNamespace`, `CephFSSubvolumeGroup`, `GetClusterID`, `GetMonsAndClusterID` with mapping, or `GetRBDNodePublishSecretRef`. Parallel subtests are safe because each reads immutable temp content.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/csiconfig_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/errors.go -->
## sources/control-plane/ceph-csi/internal/util/errors.go

**Purpose:** Defines shared sentinel errors used across Ceph-CSI utilities and storage backends.

**Important APIs and types:** Package variables include `ErrKeyNotFound`, `ErrObjectExists`, `ErrObjectNotFound`, `ErrSnapNameConflict`, `ErrPoolNotFound`, `ErrClusterIDNotSet`, `ErrMissingConfigForMonitor`, and `ErrConfigNotFound`.

**Control flow, state, and persistence:** This file has no control flow or state. The errors are intended to be wrapped with `%w` so callers can use `errors.Is`.

**Dependencies and integration points:** Depends only on `errors`. These sentinels are used by RADOS object helpers, pool lookup, config lookup, snapshot conflict handling, and option validation.

**Risks and test signals:** Renaming or replacing these values breaks `errors.Is` checks. There are no direct tests here; usage tests in helpers validate wrapping behavior indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/feature_gates.go -->
## sources/control-plane/ceph-csi/internal/util/feature_gates.go

**Purpose:** Implements simple process-wide feature gate parsing and lookup, currently for `SlowGRPCRestart`.

**Important APIs and types:** `FeatureGate` is a string alias. `SlowGRPCRestart` is enabled by default in `defaultFeatureGates`. `InitFeatureGates` parses comma-separated `Key=bool` entries into `activeFeatureGates`. `IsFeatureGateEnabled` returns active values or defaults.

**Control flow, state, and persistence:** `InitFeatureGates` copies defaults on every call, rejects malformed entries, unknown gates, and non-bool values, and mutates the package-level `activeFeatureGates` map. State is in-memory only and affects subsequent lookups.

**Dependencies and integration points:** Uses `maps.Copy`, `strconv.ParseBool`, and string splitting. It integrates with process startup/config parsing and gRPC restart behavior.

**Risks and test signals:** The package-level map is not synchronized, so initialization should happen before concurrent use. `IsFeatureGateEnabled` returns the zero value for unknown gates because it indexes `defaultFeatureGates`. Tests intentionally do not run in parallel and cover defaults, enable/disable, unknown keys, bad format, and lookup before init.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/feature_gates.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/feature_gates_test.go -->
## sources/control-plane/ceph-csi/internal/util/feature_gates_test.go

**Purpose:** Tests process-wide feature gate parsing and default lookup behavior.

**Important APIs and functions:** Tests call `InitFeatureGates` with empty, true, false, unknown key, bad format, and bad bool values. `TestIsFeatureGateEnabledBeforeInit` temporarily nils `activeFeatureGates` and verifies default enablement.

**Control flow, state, and persistence:** Tests are deliberately not parallel because they mutate package-level state. One test saves and restores the original map.

**Dependencies and integration points:** Uses `testify/require`. It protects startup parsing behavior for gate strings.

**Risks and test signals:** Good signal for current one-gate parser. It does not test multiple comma-separated gates or duplicate entries, which will matter when more gates are added.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/feature_gates_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/file/file.go -->
## sources/control-plane/ceph-csi/internal/util/file/file.go

**Purpose:** Provides small filesystem helpers for cryptsetup tests and runtime key handling: synced temp file creation and sparse file sizing.

**Important APIs and functions:** `CreateTempFile(prefix, contents)` creates a temp file in the system temp directory, writes the full string, syncs, closes, and returns the file handle for its name. `CreateSparseFile(file, sizeMB)` seeks to `sizeMB*MiB - 1` and writes one zero byte.

**Control flow, state, and persistence:** Temp files persist until callers remove them. On write/sync error, `CreateTempFile` closes and removes the temp file. Sparse file creation mutates the provided open file and returns errors for invalid seek/write cases such as zero or negative sizes.

**Dependencies and integration points:** Depends on `os` and `fmt`. `cryptsetup.AddKey`, `RemoveKey`, and `VerifyKey` use temp files to pass passphrases to cryptsetup.

**Risks and test signals:** `CreateTempFile` returns a closed `*os.File`; callers should mainly use `Name`. The write-short error wraps `err`, which can be nil if the count mismatches without an error. Temp files may hold secrets and must be removed by callers. Tests cover valid/empty/large contents and sparse file sizing/error cases.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/file/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/file/file_test.go -->
## sources/control-plane/ceph-csi/internal/util/file/file_test.go

**Purpose:** Validates temp file content persistence and sparse file sizing behavior.

**Important APIs and functions:** `TestCreateTempFile_WithValidContent`, `_WithEmptyContent`, and `_WithLargeContent` read back created temp files. `TestCreateSparseFile` checks a 10 MiB sparse file and expects errors for zero and negative sizes.

**Control flow, state, and persistence:** Tests create temporary files and remove temp files explicitly where needed. Parallel subtests are used for independent cases.

**Dependencies and integration points:** Uses standard `os` and `testing`. It protects helper behavior used by cryptsetup passphrase file handling and sparse-device style tests.

**Risks and test signals:** It does not check file permissions, closed-file behavior, sync failures, or whether sparse allocation actually avoids disk blocks. It also leaves `CreateSparseFile` temp files to `t.TempDir` cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/file/file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/fscrypt/fscrypt.go -->
## sources/control-plane/ceph-csi/internal/util/fscrypt/fscrypt.go

**Purpose:** Implements Ceph-CSI file-encryption support using the `google/fscrypt` library, KMS-backed keys, and filesystem/kernel checks.

**Important APIs and functions:** Constants define hashing target, protector prefix, encrypted subdir name, and passphrase size. `AppendEncyptedSubdirectory`, `getPassphrase`, `createKeyFuncFromVolumeEncryption`, `fsyncEncryptedDirectory`, `unlockExisting`, `initializeAndUnlock`, `getInodeEncryptedAttribute`, `IsDirectoryUnlocked`, `getBestPolicyVersion`, `InitializeNode`, and `Unlock` make up the flow.

**Control flow, state, and persistence:** `InitializeNode` writes `/etc/fscrypt.conf` with policy v2 on supported kernels, tolerating existing config. `Unlock` obtains a KMS key function, refreshes mount info, creates an fscrypt context, verifies support, sets up `.fscrypt` metadata, detects whether kernel policy and metadata already exist, chooses custom passphrase or raw key source based on KMS DEK-store mode, stores a new passphrase for integrated stores when initializing, creates/provisions/protects a policy for new encrypted directories, or unlocks existing ones. It fsyncs the encrypted directory after applying a policy and locks policies after use.

**Dependencies and integration points:** Depends on cgo `linux/fs.h`, fscrypt actions/crypto/filesystem/metadata packages, xattrs, unix ioctl, kernel version helpers, KMS, volume encryption, and logging. It integrates with node staging for file-encrypted volumes and `getsecret_test.go` KMS expectations.

**Risks and test signals:** The function handles sensitive partially initialized states: metadata without kernel policy or vice versa is rejected. Unlock falls back to an older null-padded passphrase length for backward compatibility. `initializeAndUnlock` calls `protector.Revert()` after create failure even if protector may be nil depending on library behavior. The misspelled `AppendEncyptedSubdirectory` is API-visible. There are no direct tests in this file; coverage is mostly KMS secret tests and integration environments with fscrypt-capable filesystems.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/fscrypt/fscrypt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/getsecret_test.go -->
## sources/control-plane/ceph-csi/internal/util/getsecret_test.go

**Purpose:** Validates that KMS test providers used by Ceph-CSI can return secrets needed by fscrypt-style integrations when applicable.

**Important APIs and functions:** `TestGetPassphraseFromKMS` iterates KMS test providers, creates dummy providers, calls `NewVolumeEncryption`, skips unsupported `GetSecret` paths when `ErrDEKStoreNeeded` and `ErrGetSecretUnsupported` apply, skips integrated DEK stores, and verifies metadata-style KMS returns a non-empty secret.

**Control flow, state, and persistence:** Pure test provider workflow with no real external KMS or filesystem state. It uses parallel execution and provider-specific dummy instances.

**Dependencies and integration points:** Depends on internal KMS test provider registry and `VolumeEncryption`. It connects KMS provider behavior to file encryption requirements.

**Risks and test signals:** Good signal for provider contract compatibility. It does not assert exact secret content, real KMS configuration, fscrypt unlock behavior, or `VolumeEncryption` DEK store operations.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/getsecret_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/httpserver.go -->
## sources/control-plane/ceph-csi/internal/util/httpserver.go

**Purpose:** Provides metrics HTTP server startup and pprof handler registration for Ceph-CSI processes.

**Important APIs and functions:** `ValidateURL` parses `Config.MetricsPath`. `StartMetricsServer` registers the Prometheus handler at the configured path and calls `http.ListenAndServe`. `EnableProfiling` registers runtime pprof profiles plus static cmdline/profile/symbol/trace handlers through `addPath`.

**Control flow, state, and persistence:** This mutates the global `http.DefaultServeMux`. `StartMetricsServer` is blocking and calls fatal logging on listen failure. Profiling handlers are registered by profile name, not with an explicit `/debug/pprof/` prefix in the code shown.

**Dependencies and integration points:** Depends on Prometheus `promhttp`, net/http, pprof, runtime/pprof, net/url, and internal logging. It integrates with process metrics and optional profiling configuration.

**Risks and test signals:** Global mux registration can conflict if called multiple times or if paths are not prefixed consistently. `ValidateURL` only parses, it does not ensure sane path semantics. Server lacks read/write timeouts. There are no tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/httpserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/idlocker.go -->
## sources/control-plane/ceph-csi/internal/util/idlocker.go

**Purpose:** Provides in-process locking primitives to prevent conflicting operations on the same volume, snapshot, target path, pod, or host ID.

**Important APIs and types:** `IDLocker` is a simple set protected by a mutex with `TryAcquire` and `Release`. `OperationLock` maintains per-operation maps and exposes typed acquire/release methods for snapshot create, clone, delete, restore, expand, and modify. `conflictMatrix` defines which operations block each other.

**Control flow, state, and persistence:** All state is in-memory and process-local. `tryAcquire` checks conflicting operation maps for the same volume ID, increments counters for create/clone/restore, and sets flag-style locks for delete/expand/modify. `release` decrements counters and removes keys at zero; releasing a missing key is a no-op.

**Dependencies and integration points:** Depends on Kubernetes `sets` and internal logging. It integrates with CSI controller/node operation serialization to return “operation already exists” style errors before starting unsafe work.

**Risks and test signals:** Locks do not coordinate across processes or pods. Conflict coverage is policy-sensitive: `createOp` has no conflicts, while delete does not list clone/create as blockers except through attempted clone/expand/modify conflicts. Counter operations allow multiple same-type operations concurrently by design. Tests cover simple ID locking, clone-vs-expand conflict, multiple clone/restore counters, create, and delete, but not all matrix combinations.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/idlocker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/idlocker_test.go -->
## sources/control-plane/ceph-csi/internal/util/idlocker_test.go

**Purpose:** Tests basic in-process ID locking and selected operation-lock conflict/counter behavior.

**Important APIs and functions:** `TestIDLocker` checks acquire, duplicate-acquire failure, release, and reacquire. `TestOperationLocks` checks clone acquisition blocks expand, clone counters can stack and release, restore counters can stack and release, snapshot create acquire/release, and delete acquire/release.

**Control flow, state, and persistence:** Pure in-memory tests with one lock instance per test and `t.Parallel`.

**Dependencies and integration points:** Uses standard testing. It protects operation serialization used around CSI requests.

**Risks and test signals:** The tests are basic and do not cover concurrent access, delete-vs-restore conflict, modify conflicts, unsupported operations, or counter underflow behavior after extra releases.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/idlocker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/client.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/client.go

**Purpose:** Creates and caches a Kubernetes clientset and provides small environment/error helpers.

**Important APIs and functions:** `NewK8sClient` uses `KUBERNETES_CONFIG_PATH` with `clientcmd.BuildConfigFromFlags` or in-cluster config, sets protobuf content type, creates a clientset, and stores it in package variable `kubeclient`. `RunsOnKubernetes` checks `KUBERNETES_SERVICE_HOST`. `IgnoreNotFound` maps Kubernetes not-found errors to nil.

**Control flow, state, and persistence:** The client cache is process-global and unsynchronized. Once initialized, later environment changes do not affect the client. No persistent state is written.

**Dependencies and integration points:** Depends on client-go, Kubernetes API errors, runtime content type, rest config, and environment variables. All other `internal/util/k8s` helpers call `NewK8sClient`.

**Risks and test signals:** Concurrent first calls could race on `kubeclient`. Protobuf content type can interact with API server/client support. No direct tests in this subset cover client creation or cache behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/configmap.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/configmap.go

**Purpose:** Provides a thin helper to retrieve a Kubernetes ConfigMap by namespace/name.

**Important APIs and functions:** `GetConfigMap` obtains a client with `NewK8sClient`, calls `CoreV1().ConfigMaps(namespace).Get(context.TODO(), name, metav1.GetOptions{})`, and wraps connection or get errors with resource identity.

**Control flow, state, and persistence:** Read-only API call with no local cache. Uses `context.TODO`, so callers cannot cancel the request through this helper.

**Dependencies and integration points:** Depends on Kubernetes corev1 types, metav1, and the shared k8s client helper. It integrates with any code needing dynamic config from Kubernetes.

**Risks and test signals:** Lack of caller context can hang until client-go timeouts. There are no tests or fake-client coverage in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/configmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/node.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/node.go

**Purpose:** Reads Kubernetes node metadata used for topology/read-affinity and detects out-of-service nodes by taint.

**Important APIs and functions:** `GetNodeLabels` fetches a Node and returns its labels. `IsNodeOutOfService` fetches a Node and scans taints for `node.kubernetes.io/out-of-service` with `NoExecute` or `NoSchedule`.

**Control flow, state, and persistence:** Both functions make read-only API calls with `context.TODO`. The out-of-service check returns true on the first matching taint/effect and false otherwise.

**Dependencies and integration points:** Depends on Kubernetes corev1, metav1, and the shared client. It integrates with CRUSH location construction, read affinity, and node fencing/health logic.

**Risks and test signals:** No caller cancellation. Errors wrap node names for diagnostics. No direct tests in this subset; fake-client tests would be useful for taint combinations and missing nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/parameters.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/parameters.go

**Purpose:** Handles CSI external-provisioner metadata parameters, removing driver-internal Kubernetes-prefixed keys and extracting volume/snapshot ownership metadata.

**Important APIs and functions:** Constants define the `csi.storage.k8s.io/` prefix and PVC/PV/snapshot metadata keys. `RemoveCSIPrefixedParameters`, `GetOwner`, `GetVolumeMetadata`, `GetVolumeMetadataKeys`, `PrepareVolumeMetadata`, `GetSnapshotMetadata`, and `GetSnapshotMetadataKeys` are the helper surface.

**Control flow, state, and persistence:** Functions are pure map transformations. `RemoveCSIPrefixedParameters` returns a new map without CSI-prefixed keys. Metadata getters scan keys and currently use `strings.Contains` against known full key strings. `PrepareVolumeMetadata` only includes non-empty values.

**Dependencies and integration points:** Depends on `strings`. It integrates with CreateVolume/CreateSnapshot request parameter handling and metadata stored on volumes/snapshots.

**Risks and test signals:** `strings.Contains` can match keys that merely contain the known key as a substring rather than exact keys. Map output order is irrelevant but nondeterministic. Tests cover prefix stripping and owner extraction only; metadata getter/preparer behavior is untested here.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/parameters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/parameters_test.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/parameters_test.go

**Purpose:** Tests basic Kubernetes CSI parameter filtering and PVC namespace owner lookup.

**Important APIs and functions:** `TestRemoveCSIPrefixedParameters` checks that non-CSI keys are preserved and CSI-prefixed PVC/PV metadata keys are removed. `TestGetOwner` checks missing and present PVC namespace metadata.

**Control flow, state, and persistence:** Pure parallel table tests with in-memory maps.

**Dependencies and integration points:** Uses `reflect.DeepEqual` and testing. It protects request parameter cleanup before driver-specific option parsing.

**Risks and test signals:** It does not test `GetVolumeMetadata`, `PrepareVolumeMetadata`, snapshot metadata helpers, nil maps, or substring false positives.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/parameters_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/persistentvolumes.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/persistentvolumes.go

**Purpose:** Provides a helper to retrieve a Kubernetes PersistentVolume by name.

**Important APIs and functions:** `GetPersistentVolume` obtains a client and calls `CoreV1().PersistentVolumes().Get(context.TODO(), name, metav1.GetOptions{})`, wrapping errors with the PV name.

**Control flow, state, and persistence:** Read-only API call with no local cache and no caller-provided context.

**Dependencies and integration points:** Depends on Kubernetes corev1, metav1, and the shared client helper. It integrates with code that needs PV specs or annotations from the cluster.

**Risks and test signals:** No direct tests here. Risks are the shared client cache race and inability to cancel/timeout through the helper.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/persistentvolumes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/secrets.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/secrets.go

**Purpose:** Retrieves Kubernetes Secrets and contains an unfinished/disabled secret cache implementation with informer-based invalidation/update.

**Important APIs and types:** `cachedSecret` stores stringified data. `secretCache` has a map, RW mutex, and atomic running flag. Internal methods include `cacheKey`, `startSecretWatcher`, `deleteFromCache`, and `updateCache`. Exported `GetSecret` fetches a secret directly from the API server. An unnamed function `_` contains the cache-aware path but is not callable by normal code.

**Control flow, state, and persistence:** `GetSecret` always creates/uses a Kubernetes client, fetches the named secret with `context.TODO`, converts byte values to strings, and returns a new map. The cache path, if renamed/enabled, would start a shared informer once, hash namespace/name into a 16-byte SHA-256 prefix key, update only already-cached entries on informer updates unless forced, delete on informer deletes, and stop on SIGINT/SIGTERM.

**Dependencies and integration points:** Depends on Kubernetes corev1, informers, cache utilities, OS signals, atomics, SHA-256, and logging. It integrates with CSI secret retrieval for credentials and KMS configuration.

**Risks and test signals:** The active exported path has no cache and no caller context. The disabled cache has an explicit FIXME about memory growth and uses process signal handling internally. Secret values are converted to strings and held in memory. No direct tests in this subset cover direct retrieval or cache behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/secrets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/serviceaccounts.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/serviceaccounts.go

**Purpose:** Provides helpers for ServiceAccount token creation and ServiceAccount retrieval.

**Important APIs and functions:** `CreateServiceAccountToken` calls `CoreV1().ServiceAccounts(namespace).CreateToken` with an empty `TokenRequest`. `GetServiceAccount` fetches a ServiceAccount by namespace/name. Both wrap client creation and API errors.

**Control flow, state, and persistence:** These are direct Kubernetes API calls with `context.TODO`. Token creation persists only as an API-issued token response; no local storage is used.

**Dependencies and integration points:** Depends on Kubernetes authentication/v1 and corev1 APIs, metav1, and the shared k8s client. It integrates with workflows that need short-lived service account tokens.

**Risks and test signals:** Empty `TokenRequest` relies on API defaults for audience/expiration. No caller cancellation is available. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/serviceaccounts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/volumeattachments.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/volumeattachments.go

**Purpose:** Provides helpers to list all Kubernetes VolumeAttachments or fetch one by name.

**Important APIs and functions:** `GetVolumeAttachmentList` calls `StorageV1().VolumeAttachments().List`. `GetVolumeAttachment` calls `StorageV1().VolumeAttachments().Get`. Both wrap client and API errors.

**Control flow, state, and persistence:** Read-only Kubernetes API calls using `context.TODO`; no local caching or persistence.

**Dependencies and integration points:** Depends on Kubernetes storage/v1, metav1, and the shared client. It integrates with attach/detach reconciliation and diagnostics.

**Risks and test signals:** Listing all volume attachments can be expensive in large clusters without selectors/pagination. No caller context is available. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/volumeattachments.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/kmod/modprobe.go -->
## sources/control-plane/ceph-csi/internal/util/kmod/modprobe.go

**Purpose:** Ensures a Linux kernel module is available, loading it with `modprobe` only if it is not already present under `/sys/module`.

**Important APIs and functions:** `Modprobe(ctx, kmod)` checks `/sys/module/<kmod>` with `os.Stat`, returns nil if found, wraps unexpected stat errors, and otherwise runs `util.ExecCommand(ctx, "modprobe", kmod)`.

**Control flow, state, and persistence:** The function mutates kernel module state when `modprobe` succeeds. It logs warnings on stat or load failure and includes stderr in load errors.

**Dependencies and integration points:** Depends on `os`, internal command execution, and logging. It integrates with node setup paths that require kernel modules for storage features.

**Risks and test signals:** Requires host privileges and `modprobe` availability. `ExecCommand` has no timeout, so module loading can hang. Module names are used directly in a command after caller selection. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/kmod/modprobe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/lock/group_lock.go -->
## sources/control-plane/ceph-csi/internal/util/lock/group_lock.go

**Purpose:** Implements two-group mutual exclusion: many operations in the same group may run concurrently, but group A and group B may not overlap.

**Important APIs and types:** `GroupLock` stores a mutex, active counters for each group, and separate condition variables. `NewGroupLock`, `AcquireGroupA`, `ReleaseGroupA`, `AcquireGroupB`, and `ReleaseGroupB` are the full API.

**Control flow, state, and persistence:** Acquire methods lock the mutex, wait while the opposite group count is nonzero, then increment their group count. Release methods decrement their group count and broadcast to the opposite group when the count reaches zero. State is in-memory and per lock instance only.

**Dependencies and integration points:** Depends only on `sync`. It is suitable for node/controller operation classes where same-class concurrency is safe but opposite-class concurrency is not.

**Risks and test signals:** There is no fairness guarantee; a busy group can delay the other. Release without acquire can make counters negative and break exclusion. Broadcast wakes all waiters in the opposite group, creating all-or-nothing group admission. Tests cover same-group concurrency, blocking, deadlock, mutual exclusion, all-or-nothing, stress, and benchmarks.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/lock/group_lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/lock/group_lock_test.go -->
## sources/control-plane/ceph-csi/internal/util/lock/group_lock_test.go

**Purpose:** Tests and benchmarks the two-group mutual exclusion lock under concurrency, blocking, stress, and all-or-nothing wakeup behavior.

**Important APIs and functions:** Tests include `TestGroupLock_MultipleGroupA`, `TestGroupLock_GroupABlocksGroupB`, `TestGroupLock_NoDeadlock`, `TestGroupLock_MutualExclusion`, `TestGroupLock_AllOrNothing`, and `TestGroupLock_StressTest`. Benchmarks are `BenchmarkGroupLock_GroupA` and `BenchmarkGroupLock_Alternating`.

**Control flow, state, and persistence:** Tests spawn goroutines, use wait groups, atomics, timers, and channels to observe concurrency properties. All state is in-memory. Some assertions are timing-based.

**Dependencies and integration points:** Depends on `sync`, `sync/atomic`, `time`, and `math/rand` for benchmarks. It validates a primitive intended for broader operation synchronization.

**Risks and test signals:** Strong concurrency signal for intended properties, but timing-based tests can be flaky under severe scheduler load. Tests do not cover release-without-acquire or starvation over unbounded load, which the implementation explicitly does not prevent.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/lock/group_lock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/lock/lock.go -->
## sources/control-plane/ceph-csi/internal/util/lock/lock.go

**Purpose:** Wraps RADOS object locks as an `IOCtxLock` interface for exclusive volume-level locking with consistent error/log behavior.

**Important APIs and types:** `IOCtxLock` declares `LockExclusive` and `Unlock`. `NewLock` builds a private `lock` with IO context, volume ID, lock name, cookie, description, and timeout. `LockExclusive` calls `ioctx.LockExclusive`; `Unlock` calls `ioctx.Unlock`.

**Control flow, state, and persistence:** Lock state is persisted/managed by RADOS. `LockExclusive` maps negative return codes for `EBUSY` and `EEXIST` into descriptive errors and wraps other failures. `Unlock` logs success, missing-lock `ENOENT`, or other errors but does not return an error to callers.

**Dependencies and integration points:** Depends on go-ceph `rados.IOContext`, syscall errno values, `context`, and logging. It integrates with volume operations that need distributed mutual exclusion across processes.

**Risks and test signals:** Unlock failures are only logged, so callers cannot recover programmatically. Correctness depends on stable lock name/cookie pairs and timeout values. No direct tests in this subset; integration tests with RADOS are needed for errno mapping and distributed behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/lock/lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/log/log.go -->
## sources/control-plane/ceph-csi/internal/util/log/log.go

**Purpose:** Provides Ceph-CSI logging helpers over `k8s.io/klog/v2`, adding request context prefixes and named verbosity levels.

**Important APIs and types:** Verbosity constants are `Default`, `Useful`, `Extended`, `Debug`, and `Trace`. Context keys are `CtxKey` and `ReqID`. Functions include `Log`, `FatalLogMsg`, `ErrorLogMsg`, `ErrorLog`, `WarningLogMsg`, `WarningLog`, `DefaultLog`, `UsefulLog`, `ExtendedLogMsg`, `ExtendedLog`, `DebugLogMsg`, `DebugLog`, `TraceLogMsg`, and `TraceLog`.

**Control flow, state, and persistence:** `Log` prepends `ID` and optional `Req-ID` from context values. Error/warning/fatal functions always format and emit. Verbosity helpers format first, then check `klog.V(level).Enabled()` before logging, so arguments are still evaluated by the caller and formatting cost is still paid.

**Dependencies and integration points:** Depends on `context`, `fmt`, and klog. Used throughout utilities for consistent request-aware logs.

**Risks and test signals:** Context keys are package-level variables of an unexported type, reducing collision risk. Format-before-enabled reduces performance benefits of klog level checks. Fatal exits the process. No direct tests in this subset cover prefix formatting or levels.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/log/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/log/log_utils.go -->
## sources/control-plane/ceph-csi/internal/util/log/log_utils.go

**Purpose:** Provides a helper to gzip-compress a log file and replace the `.log` file with a `.gz` file.

**Important APIs and functions:** `GzipLogFile(pathToFile)` reads the full file, replaces all `.log` substrings in the path with `.gz`, writes gzip content to a created/truncated file, and removes the original on success.

**Control flow, state, and persistence:** The function mutates filesystem state by creating/truncating the compressed file and deleting the original. If gzip writing fails, it removes the new file and leaves the original. Deferred close errors are ignored.

**Dependencies and integration points:** Depends on `compress/gzip`, `os`, and `strings`. It integrates with log rotation or cleanup paths.

**Risks and test signals:** It reads the whole log into memory and uses `strings.ReplaceAll`, so directory names containing `.log` also change. It does not explicitly close the gzip writer before deleting the original except via defer after return path starts, but deferred close happens before function returns. Tests cover existence of the `.gz` output only.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/log/log_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/log/log_utils_test.go -->
## sources/control-plane/ceph-csi/internal/util/log/log_utils_test.go

**Purpose:** Tests that `GzipLogFile` creates a compressed replacement file.

**Important APIs and functions:** `TestGzipLogFile` creates a temp `rbd-*.log`, calls `GzipLogFile`, computes the `.gz` path with the same replacement logic, and checks that it exists.

**Control flow, state, and persistence:** Uses a temp directory and filesystem state cleaned by the test framework. It does not write content into the log before compression.

**Dependencies and integration points:** Uses standard `os`, `strings`, `errors`, and testing. It validates basic log utility output creation.

**Risks and test signals:** Minimal signal: it does not assert original removal, gzip validity, content round-trip, write failure cleanup, or path replacement edge cases.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/log/log_utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/pidlimit.go -->
## sources/control-plane/ceph-csi/internal/util/pidlimit.go

**Purpose:** Reads and writes the current process cgroup PID limit through `pids.max`, supporting cgroup v1 and v2 layouts.

**Important APIs and functions:** `getCgroupPidsFile` parses `/proc/self/cgroup` and builds the matching `pids.max` path using v1 or v2 format strings. `GetPIDLimit` reads `pids.max`, returning `-1` for `max`. `SetPIDLimit` writes a numeric limit or `max` for `-1`.

**Control flow, state, and persistence:** The helper scans cgroup lines for v2 `0::...` first match or v1 `:pids:` subsystem. Reading is non-mutating. Writing opens the cgroup control file with `os.Create`, truncates it, writes the limit string, and closes it.

**Dependencies and integration points:** Depends on `/proc`, `/sys/fs/cgroup`, buffered IO, strconv, and strings. It integrates with process resource tuning for Ceph-CSI containers.

**Risks and test signals:** Path construction assumes standard cgroup mount layout. Writing requires privileges and can fail in restricted containers. `os.Create` truncates the control file before write, though cgroup pseudo-files handle this differently than regular files. Tests are skipped unless `CEPH_CSI_RUN_ALL_TESTS` is set and only lightly exercise get/set.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/pidlimit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/pidlimit_test.go -->
## sources/control-plane/ceph-csi/internal/util/pidlimit_test.go

**Purpose:** Provides an opt-in test for PID limit reading and privileged write behavior.

**Important APIs and functions:** `TestGetPIDLimit` checks `CEPH_CSI_RUN_ALL_TESTS`, calls `GetPIDLimit`, asserts nonzero, attempts `SetPIDLimit(4096)`, and restores the previous value if setting succeeds.

**Control flow, state, and persistence:** The test is skipped by default because it needs root permissions and cgroup support. When enabled, it mutates the process cgroup PID limit and tries to restore it.

**Dependencies and integration points:** Uses `os.Getenv` and standard testing. It validates host/container integration rather than pure unit behavior.

**Risks and test signals:** Useful but intentionally limited. If restoration fails after a successful set, the test only logs. It does not test cgroup path parsing with fixtures or v1/v2 variants deterministically.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/pidlimit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/read_affinity.go -->
## sources/control-plane/ceph-csi/internal/util/read_affinity.go

**Purpose:** Builds Ceph read-affinity mount/map options from CSI config and node CRUSH location labels.

**Important APIs and functions:** `ConstructReadAffinityMapOption` converts a CRUSH location map into `read_from_replica=localize,crush_location=key:value|...`. `GetReadAffinityMapOptions` reads config enablement/labels, returns empty when disabled, falls back to CLI options when config labels are empty, otherwise derives node-label CRUSH locations and constructs the option string.

**Control flow, state, and persistence:** Functions are stateless except for reading CSI config through `GetCrushLocationLabels`. Map iteration order makes the constructed option order nondeterministic for multiple labels. If enabled labels produce no matching node labels, the returned string is empty.

**Dependencies and integration points:** Depends on CSI config helpers and CRUSH location mapping. It integrates with RBD map/mount option generation for localized replica reads.

**Risks and test signals:** Order nondeterminism is acceptable in tests but could complicate string comparisons/logging. Config enablement overrides CLI fallback: disabled returns empty even if CLI options exist. Tests cover option construction for nil, empty, single, and two-entry maps, but not full config integration.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/read_affinity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/read_affinity_test.go -->
## sources/control-plane/ceph-csi/internal/util/read_affinity_test.go

**Purpose:** Tests read-affinity option string construction from CRUSH location maps.

**Important APIs and functions:** `TestReadAffinity_ConstructReadAffinityMapOption` checks nil/empty maps, a single `region:east` entry, and two-entry maps with either possible order accepted.

**Control flow, state, and persistence:** Pure parallel table tests with in-memory maps.

**Dependencies and integration points:** Uses `testify/require`. It protects the final string consumed by Ceph/RBD map options.

**Risks and test signals:** It intentionally accounts for map order nondeterminism. It does not cover `GetReadAffinityMapOptions`, CSI config enablement, CLI fallback, or node label mapping.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/read_affinity_test.go -->
