# sources/control-plane/rook/pkg/operator/ceph/csi/ceph_connection.go

## Purpose
This file creates or updates ceph-csi-operator `CephConnection` custom resources that describe how CSI drivers connect to a Rook-managed Ceph cluster.

## Important APIs, Types, and Functions
`CreateUpdateCephConnection` upserts a `csiopv1.CephConnection` named after the Ceph cluster namespace and placed in the operator pod namespace. `generateCephConnSpec` builds `CephConnectionSpec` with monitors, read-affinity settings, and the first `CephRBDMirror` daemon count. `ReadAffinityEnabled` gates read affinity and disables it specifically for Ceph `20.2.0`.

## Control Flow, State, and Persistence
The reconciler reads `POD_NAMESPACE`, lists `CephRBDMirror` resources in the cluster namespace, computes monitor endpoints using `MonEndpoints`, and persists the result as a controller-runtime custom resource create or update. Read affinity defaults to CRUSH topology labels when enabled without explicit labels.

## Dependencies and Integration Points
It depends on Rook Ceph cluster info, Ceph version parsing, `cephv1.ClusterSpec`, OSD topology defaults, and the ceph-csi-operator API. It reuses `cluster_config.go` for monitor endpoint formatting.

## Risks
Only the first `CephRBDMirror` item is used, so multiple mirror CRs are not represented. Upserts use the cluster context and operator namespace env var, making missing env setup a deployment/test risk. Read affinity has a hard-coded version exclusion that must track Ceph bugs.

## Test Signals
Tests cover create/update with and without RBD mirror resources, default topology labels, and read-affinity behavior for versions below, at, and above `20.2.0`.
