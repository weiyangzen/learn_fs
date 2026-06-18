# sources/control-plane/rook/tests/framework/installer/general_manifests.go

Purpose: this file generates generic Kubernetes manifests used by block/filesystem/NFS CSI tests: pods, PVCs, restored PVCs, cloned PVCs, and volume snapshots.

Important APIs/types/functions: `GetPodWithVolume`, `GetPVC`, `GetPVCRestore`, `GetPVCClone`, and `GetSnapshot`.

Control flow: each function returns YAML through string concatenation. Pod manifests use `busybox`, sleep forever, mount a PVC at the requested path, and set `restartPolicy: Never`. PVC restore and clone functions set `dataSource` to either `VolumeSnapshot` or another `PersistentVolumeClaim`.

State and persistence behavior: no direct mutation. Applied manifests create persistent Kubernetes pods, PVC/PV state, clone/restore relationships, and VolumeSnapshot resources.

Dependencies and integration points: used by `BlockOperation` and `FilesystemOperation`. Integrates with Kubernetes CSI provisioners and snapshot APIs installed by test helpers.

Risks: direct string interpolation assumes valid names, access modes, sizes, and paths. The busybox image and sleep command need to be available in the test cluster. YAML has no labels, so some helper functions that select by app label do not apply to these resources.

Test signals: applied manifests should result in bound PVCs, running pods with mounted volumes, ready snapshots, and successful restore/clone PVC binding.
