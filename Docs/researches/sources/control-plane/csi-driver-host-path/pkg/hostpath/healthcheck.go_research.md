# sources/control-plane/csi-driver-host-path/pkg/hostpath/healthcheck.go

## Purpose
This file implements volume health and stats helpers for controller and node CSI responses. It checks source path existence, filesystem capacity/availability, and whether a volume appears mounted under kubelet pod mount information.

## Important APIs, Types, And Functions
Types `MountPointInfo`, `ContainerFileSystem`, and `FileSystems` model `findmnt --json` output. Helpers include `checkPathExist`, `parseMountInfo`, `checkMountPointExist`, `checkPVCapacityValid`, `getPVStats`, `checkPVUsage`, `doHealthCheckInControllerSide`, and `doHealthCheckInNodeSide`. Constants identify `/var/lib/kubelet/pods` and the CSI pod volume path fragment.

## Control Flow
Controller-side health checks verify the driver source path exists, the filesystem capacity reported by Kubernetes `fs.Info` is at least the requested volume size, and available bytes are positive. Node-side health executes `findmnt --json`, parses the first filesystem tree, finds the `/var/lib/kubelet/pods` subtree, and checks whether any child mount source contains the hostpath volume path and still has a target path on disk.

## State, Persistence, And Dependencies
The functions read live host filesystem and mount state. They depend on `findmnt`, JSON output shape, `os.Stat`, `os/exec`, klog, and Kubernetes `pkg/volume/util/fs.Info`.

## Integration Points
`ListVolumes`, `ControllerGetVolume`, and `NodeGetVolumeStats` include `VolumeCondition` based on these helpers. The deployment manifests mount kubelet pod directories so node-side checks can see pod CSI mounts.

## Risks
Node-side mount detection is heuristic: it looks only under the first top-level filesystem's children and uses substring matching on mount source. Different `findmnt` JSON shapes or kubelet paths can cause false unhealthy results. Controller capacity checks compare the whole filesystem capacity to requested volume size, not real quota. The typo `Filsystem` is only a struct field name but can confuse readers.

## Test Signals
Existing tests parse a representative `findmnt` JSON document and helper extraction functions. Additional tests should cover empty/malformed JSON, missing `/var/lib/kubelet/pods`, mount source substring collisions, `findmnt` absence, and controller-side missing path/capacity/usage failures.
