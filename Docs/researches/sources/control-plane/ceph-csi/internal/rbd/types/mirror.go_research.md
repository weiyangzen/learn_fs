<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/mirror.go -->
## sources/control-plane/ceph-csi/internal/rbd/types/mirror.go

**Purpose:** Defines the abstraction for RBD mirroring operations and status reporting across images or groups. It models promotion/demotion, resync, global/local/remote site state, sync details, and snapshot scheduling.

**Important APIs and types:** `FlattenMode` has `FlattenModeNever` and `FlattenModeForce`, used by volume parent handling. `Mirror` exposes `EnableMirroring`, `DisableMirroring`, `Promote`, `Demote`, `Resync`, `GetMirroringInfo`, `GetGlobalMirroringStatus`, and `AddSnapshotScheduling`. `MirrorInfo`, `GlobalStatus`, `SiteStatus`, and `SyncInfo` model primary state, site health, timestamps, descriptions, last sync duration/bytes/time, and active sync state.

**Control flow, state, and persistence:** This is a contract file; implementations perform librbd/admin mutations and status queries. State is remote in Ceph mirroring metadata and snapshot scheduling configuration, with status reflecting local and peer site observations.

**Dependencies and integration points:** It depends on go-ceph `rbd` mirror mode, `rbd/admin` scheduling types, `context`, and `time`. It integrates with RBD volume/group mirroring controllers and CSI-Addons failover/recovery workflows.

**Risks and test signals:** Mirroring is operationally sensitive: incorrect primary state, forced promotion/demotion, or stale remote-site status can cause split-brain or failed failover. The duplicated comment on `GetGlobalMirroringStatus` is cosmetic but could obscure docs. No direct tests exist in this file; status parsers and mirror workflow integration tests must validate behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/mirror.go -->
