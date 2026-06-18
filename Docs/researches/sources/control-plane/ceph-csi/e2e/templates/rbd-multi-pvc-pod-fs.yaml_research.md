# sources/control-plane/ceph-csi/e2e/templates/rbd-multi-pvc-pod-fs.yaml

Purpose: Pod template for testing a single workload with three filesystem RBD PVC mounts.

Important fields and flow: Pod `pod-multi-pvc-fs` runs a sleeping CentOS container and mounts PVCs `rbd-pvc-0`, `rbd-pvc-1`, and `rbd-pvc-2` at `/mnt/vol-0`, `/mnt/vol-1`, and `/mnt/vol-2`.

State, dependencies, and integration: creates one Pod that requires three existing filesystem-mode PVCs. It is used by QoS and multi-volume attach tests to validate independent mount handling in one cgroup and pod.

Risks and test signals: missing PVCs, access-mode conflicts, or mount path issues prevent pod readiness. Success gives direct signal that multiple filesystem volumes can be published to a single pod without state collision.
