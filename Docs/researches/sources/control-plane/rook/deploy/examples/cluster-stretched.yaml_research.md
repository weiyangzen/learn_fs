
# sources/control-plane/rook/deploy/examples/cluster-stretched.yaml

Purpose: defines a raw-device stretched Ceph cluster with three zones, one arbiter zone, and all OSDs constrained to the two non-arbiter zones.

Important APIs/types/functions: Rook `CephCluster`, `mon.stretchCluster` with `failureDomainLabel: topology.kubernetes.io/zone`, `subFailureDomain: host`, zones `a`, `b`, and `c`, `storage.useAllNodes/useAllDevices`, `placement.arbiter` toleration, `placement.osd` node affinity to zones `b` and `c`, and `.mgr` `CephBlockPool` with zone failure domain and host sub-failure domain.

Control flow: the operator creates five mons, places arbiter monitor behavior according to stretch config, consumes raw devices only on nodes matching OSD placement, and applies a replicated manager pool suitable for two data zones plus arbiter.

State and persistence: Ceph data persists on all selected raw devices and `/var/lib/rook`; stretch placement persists in Ceph topology and pool settings.

Dependencies/integration: depends on correct node zone labels, available raw devices, control-plane tolerations for the arbiter if used, and Rook common/operator manifests.

Risks: `useAllDevices` can consume unintended disks. Incorrect labels or not enough hosts per zone break redundancy. `allowUnsupported: true` and stretch mode require careful version validation.

Test signals: verify node labels and devices, check OSD pods only in zones `b`/`c`, inspect mon quorum and CRUSH topology, and simulate zone/node loss to validate health behavior.
