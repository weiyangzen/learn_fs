
# sources/control-plane/rook/deploy/examples/cluster-multus-test.yaml

Purpose: defines a small one-node test `CephCluster` that uses Multus network attachments for public and cluster networks.

Important APIs/types/functions: Rook `CephCluster`, `spec.network.provider: multus`, `network.selectors.public`, `network.selectors.cluster`, `mon.count: 1`, `mgr.count: 1`, `storage.useAllNodes/useAllDevices`, and Ceph config overrides for single-replica test behavior.

Control flow: the operator creates a single-mon, single-mgr cluster, attaches Ceph pods to Multus networks named `public-net` and `cluster-net`, uses all available raw devices, and applies non-redundant Ceph settings suitable for tests.

State and persistence: Ceph state persists under `/var/lib/rook` and on selected devices. Multus network attachment state is external to this file.

Dependencies/integration: depends on `NetworkAttachmentDefinition` objects matching `public-net` and `cluster-net`, Rook CRDs/common/operator manifests, available raw devices, and Ceph image `quay.io/ceph/ceph:v20`.

Risks: `allowUnsupported: true`, one monitor, and pool size 1 are not production safe. Missing Multus attachments prevent pod networking. `useAllDevices` can consume unexpected disks.

Test signals: create required NADs, apply the cluster, verify pods have Multus interfaces, check mon/mgr readiness, and confirm Ceph health accepts the configured no-redundancy warnings.
