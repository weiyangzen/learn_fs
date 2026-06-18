# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/deviceSet.go

## Purpose
This file converts `StorageClassDeviceSet` entries from the CephCluster spec into concrete PVCs and internal `deviceSet` records used by OSD preparation and Deployment generation. It is responsible for idempotent PVC creation, backward-compatible PVC identity, PVC expansion waiting, and carrying storage-class-derived properties into OSD provisioning.

## Important APIs, Types, and Functions
`deviceSet` is the processed representation of one OSD's PVC sources and settings: data/metadata/wal PVC sources, crush device class, initial weight, primary affinity, resource requests, placement, portability, scheduler, tuning flags, and encryption. `PrepareStorageClassDeviceSets()` exposes the internal preparation path for tests. `prepareStorageClassDeviceSets()` lists existing PVCs, validates prepare OSD memory and volume templates, preserves existing PVC indexes, creates missing PVC groups, and waits for pending PVC expansions.

`createDeviceSetPVCsForIndex()` creates or reuses data, metadata, and wal PVCs for one set index. It handles blank template names as backward-compatible data volumes, rejects duplicate template names, extracts crush annotations, and returns a populated `deviceSet`. `createDeviceSetPVC()` resolves old and new PVC IDs, sets owner references, expands existing PVCs if size changed, records resize state, or creates new PVCs. `makeDeviceSetPVC()` builds generated-name PVCs with Rook labels plus user-provided labels. `GetExistingPVCs()` returns PVCs keyed by device-set PVC ID and a per-device-set set of existing indexes. `deviceSetPVCID()` normalizes spaces in template names and dots in device-set names. `createValidImageVersionLabel()` sanitizes image strings for Kubernetes label values. `waitForPvcToExpandWithTimeout()` and `checkAllPvcResize()` poll PVC spec/status capacity convergence.

## Control Flow
For each device set, existing PVC indexes are processed first so missing companion PVCs can be recreated. New indexes begin after the highest existing ID to avoid reusing old OSD identities. The desired count controls how many new PVC groups are created, but extra existing PVCs are not deleted here.

## State and Persistence
Persistent state is Kubernetes PVCs. Labels `ceph.rook.io/DeviceSet`, `ceph.rook.io/setIndex`, and `ceph.rook.io/DeviceSetPVCId` form the reconciliation identity. Image-at-creation labels persist Ceph and Rook image versions. Owner references connect PVCs to the CephCluster owner. PVC resize state is transient in `pvcResizeMap`, with actual progress observed from the Kubernetes API.

## Dependencies and Integration Points
The file integrates with CephCluster storage spec types, controller memory validation, Kubernetes client-go and controller-runtime clients, Rook label helpers in `labels.go`, and OSD provisioning in `create.go`/`osd.go`. It uses Kubernetes resource quantities for resize comparisons.

## Risks and Edge Cases
PVC identity must remain backward compatible with legacy IDs while supporting template-name-specific IDs. Generated names reduce OSD ID reuse risk but mean tests and controllers must rely on labels, not exact names. Resize waiting can delay reconciliation until timeout. Duplicate template names and invalid existing indexes are accumulated as provision errors. The resize equality check compares desired spec size and status capacity, so delayed CSI status updates can leave OSDs needing manual restart.

## Test Signals
`deviceset_test.go` covers blank and explicit template names, scheduler propagation, image labels, holes in PVC sets, scale-down/scale-up index behavior, crush annotation extraction, PVC ID normalization, valid image label sanitization, and PVC resize confirmation logic.
