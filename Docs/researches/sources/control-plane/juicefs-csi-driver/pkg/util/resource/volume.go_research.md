<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/volume.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/volume.go

### Purpose
`volume.go` detects which PVC-backed volumes in a pod are JuiceFS CSI volumes and provides an in-process lock table for serializing work by volume ID.

### Important APIs, Types, And Functions
`PVPair` groups a `PersistentVolume` and its claiming `PersistentVolumeClaim`. `GetVolumes(ctx, client, pod, reqNs)` returns whether the pod uses JuiceFS and all matching PV/PVC pairs. `getVol` implements the scan. `VolumeLocks`, `SharedVolumeLocks`, `NewVolumeLocks`, `TryAcquire`, and `Release` implement coarse volume-ID locks.

### Control Flow
`GetVolumes` resolves the effective namespace via `GetNamespace`, sets `pod.Namespace`, then delegates to `getVol`. `getVol` iterates pod volumes, fetches each referenced PVC, optionally fetches its StorageClass to detect dynamic JuiceFS provisioning, checks binding state, fetches the PV, and appends the pair if the PV CSI driver matches `config.DriverName`. If a PVC uses a JuiceFS StorageClass but is unbound, it returns an error instead of silently skipping. `TryAcquire` uses a mutex around a `sync.Map` check/store pair to provide atomic lock acquisition.

### State, Persistence, And Dependencies
The helper reads Kubernetes PVC, PV, StorageClass, and pod state through the project k8s client. The only local state is `SharedVolumeLocks`, a process-local lock map with no persistence across controller restarts. Dependencies include Kubernetes core/storage APIs, API error classification, and JuiceFS driver-name config.

### Integration Points
Admission sidecar mutation uses `GetVolumes` to decide whether a pod needs injection and which PV/PVC pairs to mutate. Controllers can use `VolumeLocks` to avoid concurrent operations on the same JuiceFS volume ID.

### Risks
The helper mutates the input pod namespace. StorageClass `NotFound` is tolerated so static PVs can still be detected by PV CSI driver, but other StorageClass errors abort the whole scan. A pod with multiple PVCs returns on the first fetch error. Process-local locks do not protect multi-replica controllers. `GetVolumes` requires helpers such as `GetNamespace` from adjacent files, so namespace resolution behavior is part of its contract.

### Test Signals
Tests should cover dynamic StorageClass detection, static CSI PV detection without an existing StorageClass, non-JuiceFS PV skip, unbound JuiceFS PVC error, multiple matching PVCs, missing PVC/PV errors, namespace override behavior, and lock acquisition/release contention.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/volume.go -->
