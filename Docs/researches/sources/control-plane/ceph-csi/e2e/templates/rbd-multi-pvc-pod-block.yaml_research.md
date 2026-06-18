# sources/control-plane/ceph-csi/e2e/templates/rbd-multi-pvc-pod-block.yaml

Purpose: Pod template for testing a single workload with three raw block RBD PVCs.

Important fields and flow: Pod `pod-multi-pvc-block` runs a sleeping CentOS container with `volumeDevices` `vol-0`, `vol-1`, and `vol-2` mapped to `/dev/xvda`, `/dev/xvdb`, and `/dev/xvdc`. Volumes reference PVCs `rbd-pvc-0` through `rbd-pvc-2`.

State, dependencies, and integration: creates one Pod that attaches multiple existing block-mode PVCs. It complements helper-created multi-PVC pods and exercises code paths that must update per-device cgroup or staging state without overwriting sibling volumes.

Risks and test signals: device path collisions or missing block PVCs will fail pod startup. It uses a long-running sleep command, so validation depends on external exec checks. Passing tests indicate all three devices attach and publish to the same pod.
