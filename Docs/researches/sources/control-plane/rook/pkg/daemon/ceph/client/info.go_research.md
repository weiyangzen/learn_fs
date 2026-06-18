# sources/control-plane/rook/pkg/daemon/ceph/client/info.go

Purpose: defines shared cluster identity, monitor, credential, owner, and lifecycle metadata used by all Ceph client command helpers.

Important APIs/types: `ClusterInfo` stores FSID, monitor secret, Ceph credentials, internal/external monitors, Ceph version, namespace, owner info, private cluster name, OSD upgrade timeout, network/CSI specs, reconcile context, and optional keyring override. `AllMonitors()` merges external and internal mons when external mons exist. `MonInfo` stores monitor name, endpoint, and out-of-quorum state. `CephCred` stores username and secret. Constructors/helpers include `NewClusterInfo()`, `SetName()`, `NamespacedName()`, `AdminClusterInfo()`, `AdminTestClusterInfo()`, `IsInitialized()`, `NewMonInfo()`, `NewMinimumOwnerInfo()`, and `NewMinimumOwnerInfoWithOwnerRef()`.

Control flow and state: `NamespacedName()` panics if the private name is unset, enforcing initialization. `AdminClusterInfo()` creates admin credentials and owner info for a namespace/name. `IsInitialized()` validates required fields and propagates context cancellation. `AllMonitors()` returns internal monitors directly when there are no external mons; otherwise it creates a merged map.

Dependencies and integration: this type is passed through nearly every client call. It integrates with ceph API types, version parsing/comparison, Kubernetes owner metadata, and controller-runtime namespaced names. Risks include the panic contract around unset names, map aliasing when only internal mons exist, mutable context state controlling command execution, and misspelled comments around monitors. There is no dedicated test file in this subset, but the constructors and context cancellation are exercised by command/config tests.
