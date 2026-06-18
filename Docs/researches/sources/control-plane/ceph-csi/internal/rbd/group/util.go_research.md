# sources/control-plane/ceph-csi/internal/rbd/group/util.go

## Purpose
Provides shared state and helpers for RBD volume groups and volume group snapshots: CSI ID decomposition, cluster/pool/namespace resolution, journal connection, IO context management, common getters, journal deletion, creation-time lookup, and retry classification for mapped clusters.

## Important APIs, Types, And Functions
`commonVolumeGroup` stores IDs, names, creation time, cluster/pool/namespace details, credentials, cached connection/ioctx, driver instance, and journal. Key methods are `generateVolumeGroup`, `generateVolumeGroupFromMapping`, `initCommonVolumeGroup`, `Destroy`, `getVolumeGroupAttributes`, `String`, `GetID`, `GetName`, `GetRequestName`, `GetPool`, `GetClusterID`, `getConnection`, `getJournal`, `GetIOContext`, `Delete`, `GetCreationTime`, and `ShouldRetryVolumeGroupGeneration`.

## Control Flow
Initialization decomposes the CSI ID, resolves monitors/namespace/pool, reads journal attributes, and if retryable errors occur tries cluster and pool ID mappings. Journal attributes populate request name, backend group name, and creation time. Connections, journals, and IO contexts are created lazily and cached. Destroy releases ioctx, connection, credential reference, and journal. Delete removes the journal reservation for the group.

## State And Persistence
Persistent state is the RADOS volume-group journal reservation and volume map. Runtime state includes cached credentials references, cluster connection, IO context, and journal handle. The helper intentionally does not own credential deletion; callers that allocated credentials must delete them.

## Dependencies And Integration Points
Depends on RADOS, journal volume-group APIs, util cluster mapping and ID helpers, logging, and RBD group errors. It underpins both `volume_group.go` and `group_snapshot.go`.

## Risks And Test Signals
Risks include returning `ErrGroupNotFound` for missing/empty journal attributes, retrying across cluster mappings incorrectly, leaking handles if Destroy is missed, and confusing journal pool versus data pool in cleanup. `util_test.go` verifies retry classification for known errors but not cluster mapping or journal behavior.
