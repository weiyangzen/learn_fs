# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/crd-csi-snapshot.yaml

## Purpose
This v4.7.0 manifest installs the CSI snapshot CRDs for the NFS CSI bundle. The file is byte-identical to the v4.4.0 through v4.6.0 CRD files in this subset.

## Important APIs, Types, and Functions
It creates `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs under `snapshot.storage.k8s.io`, serving both `v1` and `v1beta1` and storing `v1`. Schemas define snapshot source references, CSI driver and class fields, deletion policies, snapshot handles, content references, readiness, restore size, error status, printer columns, and status subresources.

## Control Flow, State, and Persistence
The manifest has declarative API-install behavior only. Once present, it gives the snapshot controller and CSI snapshotter persistent custom resources for snapshot request, binding, and status state.

## Dependencies and Integration Points
It integrates with the v4.7.0 `snapshot-controller:v8.0.1` and `csi-snapshotter:v8.0.1` images, plus the NFS CSI driver name used in snapshot classes. Kubernetes must support apiextensions v1 and structural schemas.

## Risks and Test Signals
Risks include a large controller-sidecar version jump while the CRD schema stays unchanged, cluster-wide CRD update impact, and legacy `v1beta1` served-version expectations. Test signals are API discovery, no snapshot-controller CRD readiness failures, successful `VolumeSnapshot` creation and binding, and status updates on both snapshot and content resources.
