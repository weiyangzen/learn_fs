## sources/control-plane/ceph-csi/internal/cephfs/core/quiesce.go

Purpose: Wraps CephFS filesystem quiesce operations used to take crash-consistent group snapshots across subvolumes.

Important types/functions: `QuiesceState` constants `Released`, `Quiescing`, `Quiesced`; `GetQuiesceState`; `FSQuiesceClient` interface; `FSQuiesceClientMap`; `Volume`; `fsQuiesce`; `NewFSQuiesce`; `FSQuiesce`, `FSQuiesceWithExpireTimeout`, `ResetFSQuiesce`, `ReleaseFSQuiesce`, and `getMembers`.

Control flow: `NewFSQuiesce` binds FSAdmin and a map from subvolume groups to subvolume names. Quiesce calls build `admin.FSQuiesceOptions` with timeout/expiration/reset/release flags and call `FSQuiesce` on go-ceph with a reservation name. `getMembers` formats members as `group/subvolume`.

State and persistence: Quiesce state is maintained by the CephFS manager under the reservation name. The client holds a cluster connection and must destroy it after use.

Dependencies and risks: Depends on go-ceph admin quiesce APIs and Ceph versions that support them. Hard-coded 180-second timeouts/expirations may be too short for large sets. Map iteration order is nondeterministic but should not matter to Ceph. Tests are indirect through group snapshot request validation only; integration should cover quiesce in-progress, reset, release, and multi-filesystem grouping.
