# sources/control-plane/rook/pkg/operator/ceph/controller/cluster_info.go

## Purpose
`cluster_info.go` creates, loads, migrates, and updates the cluster identity and monitor connection state used by the Ceph operator. It is the persistence layer for FSID, mon/admin credentials, monitor endpoint maps, out-of-quorum status, external monitor classification, and CSI defaults derived from the CephCluster spec.

## Important APIs, Types, and Functions
Core constants name the `rook-ceph-mon` Secret, the `rook-ceph-mon-endpoints` ConfigMap, Secret keys, endpoint keys, and disaster-protection finalizer. `LoadClusterInfo()` and `CreateOrLoadClusterInfo()` are the primary entry points. `createNamedClusterInfo()` generates FSID and cephx keys with `ceph-authtool`; `genSecret()` and `ExtractKey()` parse generated keyrings. `createClusterAccessSecret()` persists new cluster credentials. `UpdateClusterAccessSecret()` updates admin and mon keys. `loadMonConfig()` parses monitor endpoint ConfigMap data, out-of-quorum marks, max mon ID, mon scheduling mapping JSON, and external monitor IDs. `ParseMonEndpoints()` parses `a=ip:port,b=ip:port` strings. `PopulateExternalClusterInfo()` waits for externally supplied connection info.

## Control Flow, State, and Persistence
`CreateOrLoadClusterInfo()` first tries to read `rook-ceph-mon`. If missing and owner info is present, it creates a new FSID and cephx secrets, then writes a Secret with the disaster-protection finalizer. If the Secret exists, it loads FSID, monitor secret, and either new-style username/secret keys or migrates old `admin-secret` data into `ceph-username` and `ceph-secret`. It then loads monitor config from `rook-ceph-mon-endpoints`. CSI settings are copied from the CR and defaulted for topology labels and CephFS kernel mount options, including `ms_mode=secure` when network encryption is enabled. External clusters may use legacy `rook-ceph-operator-creds` if the Secret stores an admin placeholder.

## Dependencies and Integration Points
The file depends on `clusterd.Context` for clientset, executor, and config dir; `cephclient.ClusterInfo` for runtime cluster state; `cephv1.ClusterSpec` for network/CSI defaults; Kubernetes Secrets and ConfigMaps; OSD topology defaults; `k8sutil.OwnerInfo`; and Ceph CLI tooling via `ceph-authtool`. Many controllers call this before running Ceph commands or constructing daemon specs.

## Risks
Key generation writes temporary keyring files under `ConfigDir/namespace`; path sanitization only replaces the first `..`. `ExtractKey()` greps for `"key"` and assumes the third field is the secret, which is format-sensitive. `loadMonConfig()` logs invalid mapping JSON but returns success with an empty mapping, which may hide corrupted scheduling state. External cluster population loops every 60 seconds until context cancellation. Backward-compatibility branches around `AdminSecretNameKey` are subtle and can fail if Secrets contain mixed old/new keys. Updating the old Secret during migration can conflict under concurrent reconciles.

## Test Signals
`cluster_info_test.go` covers new Secret creation, owner info reconstruction, old admin-secret migration, legacy external credentials, and CSI kernel mount defaults. Endpoint parsing, max mon ID repair, out-of-quorum flags, mapping JSON, and external monitor filtering lack direct tests in this subset.
