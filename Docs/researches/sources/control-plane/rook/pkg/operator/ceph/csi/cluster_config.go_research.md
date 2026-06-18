# sources/control-plane/rook/pkg/operator/ceph/csi/cluster_config.go

## Purpose
`cluster_config.go` manages legacy ceph-csi cluster JSON config and the `rook-ceph-csi-config` ConfigMap. It also formats monitor endpoints and normalizes network namespace fields during the ceph-csi-operator transition.

## Important APIs, Types, and Functions
`CSIClusterConfigEntry` embeds `cephcsi.ClusterInfo` and adds `Namespace`. `FormatCsiClusterConfig`, `parseCsiClusterConfig`, and `formatCsiClusterConfig` marshal/unmarshal JSON. `MonEndpoints` optionally converts msgr1 monitor ports to msgr2. `updateCsiClusterConfig` adds, updates, or removes cluster entries while preserving subvolume groups, RBD namespaces, mount options, NFS/RBD/CephFS network fields, and read-affinity values. `CreateCsiConfigMap` and `updateCsiConfigMapOwnerRefs` create or fix the CSI ConfigMap owner reference.

## Control Flow, State, and Persistence
The key state is JSON stored under `csi-cluster-config-json` in `rook-ceph-csi-config`. Updates parse existing JSON, patch entries by cluster ID and namespace, clear `NetNamespaceFilePath` for entries owned by the namespace, and marshal back to JSON. ConfigMap owner references are corrected to the operator deployment owner.

## Dependencies and Integration Points
The file integrates with ceph-csi JSON schema, Rook cluster info, Kubernetes ConfigMaps, `k8sutil.OwnerInfo`, and CSI read-affinity logic.

## Risks
JSON entry update behavior is intricate and order-sensitive. `MonEndpoints` iterates maps, so output order is nondeterministic. `updateCsiClusterConfig` only updates some nested fields when non-empty, which preserves state but can make clearing fields difficult. Owner-ref correction overwrites multiple owners to a single expected owner.

## Test Signals
Tests cover JSON add/update/remove scenarios, mon port conversion including IPv6, namespace correction, net namespace clearing, and owner-ref repair. A test helper bug compares expected JSON to itself, weakening some string-equality assertions.
