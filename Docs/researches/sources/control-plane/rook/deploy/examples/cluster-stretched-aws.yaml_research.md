
# sources/control-plane/rook/deploy/examples/cluster-stretched-aws.yaml

Purpose: defines an AWS-like stretched Ceph cluster using PVC-backed OSDs across zones with an arbiter zone.

Important APIs/types/functions: Rook `CephCluster`, `mon.count: 5`, `mon.stretchCluster` with `failureDomainLabel: topology.kubernetes.io/zone`, arbiter zone `us-east-2a`, OSD zones `us-east-2b` and `us-east-2c`, mon PVC template using `gp2-csi`, two storageClassDeviceSets, placement/preparePlacement node affinity, and `CephBlockPool` `.mgr` with `failureDomain: zone`, `size: 4`, and `replicasPerFailureDomain: 2`.

Control flow: Rook creates five monitors, assigns stretch roles by zone labels, schedules OSD PVC sets only in the two data zones, and configures the manager pool for zone-aware replicated placement.

State and persistence: Ceph state persists in AWS-style PVCs and Rook host path metadata. Stretch topology becomes part of Ceph CRUSH and pool placement behavior.

Dependencies/integration: requires zone labels, `gp2-csi`, sufficient nodes/PVC capacity in data zones, Rook stretch-cluster support, and an arbiter-capable topology.

Risks: wrong zone labels break stretch placement. `allowUnsupported: true` is not production-safe. Insufficient OSDs per failure domain prevents healthy replicated placement.

Test signals: validate node labels before apply, confirm mon zone assignments, inspect CRUSH map and `.mgr` pool properties, and run failure tests for one data zone and the arbiter zone.
