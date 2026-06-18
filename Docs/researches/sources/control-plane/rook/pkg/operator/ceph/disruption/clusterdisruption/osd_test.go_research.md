# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/osd_test.go

## Purpose
This test file validates OSD disruption state-machine behavior, including failure-domain discovery, node-drain detection, PDB creation/deletion, and ConfigMap state updates.

## Important APIs, Types, and Functions
Helpers define fake Ceph status JSON, fake OSD deployments, fake nodes, fake PDB ConfigMaps, fake reconcilers, and fake cluster info. `TestGetOSDFailureDomains`, `TestGetOSDFailureDomainsError`, `TestReconcilePDBForOSD`, `TestHasNodeDrained`, and `TestSetPDBConfig` cover the main behavior.

## Control Flow, State, and Persistence
Tests use controller-runtime fake clients containing Deployments, Nodes, ConfigMaps, and CephCluster objects. Mock executors return Ceph `status`, `osd dump`, and `osd metadata` output. Reconcile tests inspect created PDBs and updated ConfigMaps.

## Dependencies and Integration Points
The file depends on Rook schemes, fake exec, Kubernetes fake client objects, OSD topology labels, and PDB v1 APIs.

## Risks
Many assertions rely on deterministic ordering of failure-domain slices returned from sets; this can be fragile if set ordering changes. `updateNoout` is only lightly exercised through mock OSD dump output, not detailed CRUSH flag behavior. Timing behavior around the 60-second node-drain delay is not directly tested.

## Test Signals
Strong signals include schedulable vs unschedulable node detection, missing node treated as drained, missing topology label errors, active drain blocking PDBs, default PDB restoration, excluded down OSDs, and `set-no-out` state selection.
