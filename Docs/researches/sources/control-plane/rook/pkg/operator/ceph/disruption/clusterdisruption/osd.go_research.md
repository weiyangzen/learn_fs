# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/osd.go

## Purpose
`osd.go` implements dynamic OSD PodDisruptionBudget management during node drains and OSD outages. It protects non-draining failure domains, allows one active drain domain, and manages Ceph `noout` on drained failure domains.

## Important APIs, Types, and Functions
PDB helpers include `createPDB`, `deletePDB`, `createDefaultPDBforOSD`, `deleteDefaultPDBforOSD`, `createBlockingPDBForOSD`, and `deleteBlockingPDBForOSD`. State helpers include `initializePDBState`, `resetPDBConfig`, `setPDBConfig`, and `getLastNodeDrainTimeStamp`. Main orchestration is `reconcilePDBsForOSDs`. Discovery helpers include `getOSDFailureDomains`, `hasOSDNodeDrained`, `getNode`, `getPDBName`, `requeuePDBController`, and `pdbExcludesOSDs`. `updateNoout` applies/unsets Ceph `noout` per CRUSH unit.

## Control Flow, State, and Persistence
The reconciler reads Ceph health, OSD deployments, OSD metadata, Kubernetes Nodes, and a state ConfigMap `rook-ceph-pdbstatemap`. Clean clusters reset state and restore a default PDB. Unhealthy OSD-down states set a draining failure domain, delete the default PDB, and create blocking PDBs for other domains. Clean clusters with down OSDs can exclude those OSD IDs from the default PDB. State is persisted in the ConfigMap and PDB objects; Ceph flags are persisted in OSD map state.

## Dependencies and Integration Points
It integrates with Ceph status/OSD dump/metadata commands, Rook OSD labels, Kubernetes Deployments/Nodes/PDBs/ConfigMaps, topology failure domains, and operator requeue constants.

## Risks
Correctness depends on deployment labels and Ceph metadata hostnames. The state machine is time-sensitive, especially the 60-second wait after node drain detection and maintenance timeout. `sets.List` ordering can influence which failure domain is chosen first. `updateNoout` errors are logged but reconciliation continues to update ConfigMap state.

## Test Signals
Tests cover failure-domain detection, node-drain detection, healthy/unhealthy PDB transitions, OSD exclusion, `setPDBConfig`, and custom PG healthy regex behavior.
