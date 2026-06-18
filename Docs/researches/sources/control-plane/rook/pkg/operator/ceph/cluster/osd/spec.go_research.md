# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/spec.go

## Purpose
`spec.go` constructs OSD runtime Kubernetes resources, especially the `apps.Deployment` for each OSD and optional exported Service. It encodes raw vs LVM activation, PVC vs node-backed behavior, encrypted block-device handling, CephX key refresh, probes, placement, topology affinity, service ports, and operational shell scripts used by init containers.

## Important APIs, Types, and Functions
Primary APIs are `deploymentName()`, `Cluster.updateCephConfigVolume()`, `Cluster.makeDeployment()`, `Cluster.createOSDService()`, `Cluster.applyAllPlacementIfNeeded()`, `Cluster.applyTopologyAffinity()`, `Cluster.getCopyBinariesContainer()`, `Cluster.getActivateOSDInitContainer()`, PVC mapper/encryption init-container builders, `Cluster.getCephxKeyUpdateInitContainer()`, `Cluster.getOSDContainerPorts()`, `Cluster.getOSDServicePorts()`, `getOSDCmd()`, and `volumeExistsWithName()`. Constants name init containers, mounts, OSD ports, dmcrypt block types, and shell script templates.

## Control Flow, State, and Persistence
`makeDeployment()` requires `OSDInfo.CVMode`, derives desired device class when updates are allowed, assigns per-class resources, builds volumes from data-path maps, and chooses command mode. Node OSDs run `ceph-osd` directly after activation init containers. PVC LVM OSDs copy the Rook binary and run through `rook ceph osd start`; PVC raw OSDs use block mapper init containers, `ceph-bluestore-tool prime-osd-dir`, BlueFS expansion, and direct `ceph-osd`. Encrypted PVC raw OSDs first copy block devices to temporary paths, open dmcrypt devices, copy mapped blocks into the OSD data dir, print status, and resize encrypted blocks. Every deployment gets CephX status annotation persistence and a post-activation keyring update init container to avoid repeated key rotations across reconciles.

## Dependencies and Integration Points
The deployment builder integrates CephCluster spec fields for network, resources, annotations, labels, log collector, health checks, storage tuning, KMS, and priority classes. It uses controller helpers for Ceph volumes, probes, Multus, network binding, log collectors, chown init containers, and service creation/export. It consumes `OSDInfo` produced by prepare status parsing and `osdProperties` resolved from node or PVC device-set configuration. Labels created here are read by status and health-monitor code, `getOSDInfo()`, and CephCluster storage-status updates.

## Risks
This file has high blast radius because Kubernetes pod specs, device paths, shell scripts, encryption ordering, and Ceph command flags must line up. Init-container order is critical for raw PVC and encrypted PVC startup. The block mapper script handles major/minor changes by force-copying device nodes; a regression can point OSDs at stale or wrong block devices. Privileged contexts are still required for device, log, crash, cryptsetup, and hostPath use. Deployment labels intentionally diverge from pod labels for Rook/Ceph versions to avoid unnecessary OSD restarts; copying those labels to pod templates would change upgrade behavior.

## Test Signals
`spec_test.go` verifies command construction, init-container names/order/counts, volume and mount counts, encrypted metadata/WAL/KMS paths, host networking, placement merging, probe overrides, log collector `ShareProcessNamespace`, service ports for msgr2, prepare resources, per-device and node device-class updates, and `AllowDeviceClassUpdate` semantics.
