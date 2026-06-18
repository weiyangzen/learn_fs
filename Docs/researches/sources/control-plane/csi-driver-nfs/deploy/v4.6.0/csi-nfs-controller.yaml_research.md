# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-nfs-controller.yaml

## Purpose
This manifest deploys the v4.6.0 NFS CSI controller. Compared with v4.5.0, it upgrades controller sidecars and hardens containers by dropping Linux capabilities on non-privileged sidecars and dropping all non-added capabilities in the privileged NFS container.

## Important APIs, Types, and Functions
The `Deployment` remains a one-replica `csi-nfs-controller` in `kube-system`. Containers are `csi-provisioner:v4.0.0`, `csi-snapshotter:v6.3.3`, `livenessprobe:v2.12.0`, and `nfsplugin:v4.6.0`. The liveness sidecar switches from `--health-port=29652` to `--http-endpoint=localhost:29652`, and the NFS liveness probe targets `host: localhost`, `port: 29652` without declaring a named container port. Security contexts drop `ALL` capabilities for sidecars; the NFS container keeps `privileged: true`, adds `SYS_ADMIN`, drops `ALL`, and allows privilege escalation.

## Control Flow, State, and Persistence
The controller pod still creates a CSI socket in an `emptyDir`, runs sidecar watch loops through leader election, and mounts `/var/lib/kubelet/pods` bidirectionally for NFS directory operations. State persists in Kubernetes PV/PVC/snapshot resources, events, leases, and host pod mount paths. The v4.6.0 flow relies on localhost health endpoints rather than a named exposed port.

## Dependencies and Integration Points
It depends on the v4.6.0-compatible RBAC, `CSIDriver`, snapshot CRDs, snapshot controller, kubelet pod hostPath, host networking, and `registry.k8s.io/sig-storage` images. The provisioner v4.0.0 image may require RBAC verbs that older manifests did not need, making RBAC validation important.

## Risks and Test Signals
Risks include sidecar major-version behavior changes, capability-drop interactions with privileged NFS operations, localhost health endpoint binding differences, and RBAC gaps after upgrading to `csi-provisioner:v4.0.0`. Test signals are healthy 29652 probes, successful rollout, no permission-denied mount errors, no provisioner forbidden errors, successful provisioning/snapshotting, and stable leader-election leases.
