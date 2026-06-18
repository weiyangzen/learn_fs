# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/osd.go

## Purpose
This is the central OSD manager for the Rook Ceph operator. It defines cluster-level OSD state, OSD metadata models, validation, the main reconcile entrypoint, migration orchestration, Deployment property extraction, topology/CRUSH location helpers, post-reconcile Ceph updates, storage status reporting, and node-specific configmap discovery.

## Important APIs, Types, and Functions
`Cluster` holds operator context, `ClusterInfo`, Rook/Ceph spec, valid storage, ConfigMap KV store, processed device sets, migration target, deprecated OSDs, and node configmaps. `New()` initializes a reconcile manager. `OSDInfo` serializes OSD identity and runtime attributes including ID, UUID, block paths, device class, topology, encryption, export service, node/PVC names, device type, and Cephx status. `OrchestrationStatus` is the JSON shape used by prepare status ConfigMaps. `osdProperties` carries resolved provisioning inputs for node or PVC OSDs.

`validateOSDSettings()` checks OSD memory and duplicate device set names. `validateTopologyAcrossNodes()` optionally detects topology label conflicts and fails new clusters with no existing OSDs. `Start()` is the main reconcile: validate, initialize node configmaps, set OSD timeout, compute skip-reconcile daemons, start migration, get update info, provision PVCs and nodes, process updates/creates, aggregate errors, clean orphaned prepare artifacts, apply upgrade OSD functionality, reconcile key rotation, update OSD properties, update CephCluster storage status, and delete the bootstrap keyring.

Deployment-related helpers include `deploymentOnNode()`, `deploymentOnPVC()`, `setOSDProperties()`, `resolveNode()`, `getOSDPropsForNode()`, `getOSDPropsForPVC()`, `getPVCHostName()`, `GetOSDID()`, `findOSDContainer()`, and `getOSDInfo()`. Topology helpers include `getLocationFromPod()`, `getTopologyFromNode()`, `GetLocationWithNode()`, `getNode()`, `resolveDeviceClass()`, `updateLocationWithNodeLabels()`, and `getOSDLocationFromArgs()`. Post-reconcile helpers include `applyUpgradeOSDFunctionality()`, `deleteOSDDeployment()`, `waitForHealthyPGs()`, `updateCephOsdStorageStatus()`, `getOSDStoreStatus()`, and `initializeNodeConfigmaps()`.

## Control Flow
The main reconcile deliberately separates update and create planning. Migration can remove candidate OSDs from the update queue and delete one Deployment before provisioning. PVC prepare runs before node prepare; status ConfigMaps from both feed creation. After all OSD create/update work, cleanup and Ceph-side post-processing occur. Many non-critical post-processing errors are logged and reconciliation continues; accumulated provisioning errors fail the reconcile after create/update attempts.

## State and Persistence
Persistent state includes OSD Deployments, prepare Jobs, status ConfigMaps, PVCs, node override ConfigMaps, migration ConfigMaps, CephCluster status, Ceph auth/bootstrap keyrings, Ceph CRUSH/device-class state, and Ceph require-osd-release state. `getOSDInfo()` reconstructs desired/actual OSD state from Deployment labels, env vars, container args, annotations, pod/node state, and legacy activation init scripts. Cephx status is persisted as a JSON annotation on the pod template.

## Dependencies and Integration Points
This file integrates nearly every OSD subsystem: create/update configs, device sets, key rotation, migration, topology, Ceph client commands, Kubernetes clients, reporting status updates, Rook placement/resource helpers, and health/upgrade behavior. It also uses package globals for topology validation and timeouts, which tests override.

## Risks and Edge Cases
Compatibility fallbacks are numerous: legacy block path extraction, missing CV mode defaulting to `lvm`, topology affinity detection after upgrade, CRUSH location fallback from pods/nodes, encryption detection from dmcrypt block path when labels are absent, and hostname lookup by node name or hostname label. These reduce upgrade risk but make behavior dependent on old pod specs and live pod availability. `resolveDeviceClass()` intentionally errors when both CR config and node label specify a device class. `validateTopologyAcrossNodes()` uses a package-global `topologyValidated`, so process lifetime affects repeated validation. `getOSDStoreStatus()` returns nil status if no deployments are found, which callers should handle carefully.

## Test Signals
The listed tests cover major portions indirectly: `integration_test.go` drives `Start()` across many reconcile scenarios; `create_test.go` covers provisioning entrypoints and device-class label conflict; `migrate_test.go` covers migration helpers; `health_test.go` covers release and deletion behavior; `labels_test.go` covers topology labels. Some important helpers, especially `getOSDInfo()` compatibility fallbacks and status update edge cases, are not comprehensively tested in the listed files.
