## sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-nfs-controller.yaml

Purpose: Deploys the v4.3.0 NFS CSI controller with dynamic provisioning and CSI snapshot sidecar support. It updates sidecar versions, switches host-network DNS to cluster-aware mode, and adds pod-level seccomp defaults.

Important APIs and types: The Deployment has one replica in `kube-system`, ServiceAccount `csi-nfs-controller-sa`, `hostNetwork: true`, `dnsPolicy: ClusterFirstWithHostNet`, `priorityClassName: system-cluster-critical`, and `seccompProfile: RuntimeDefault`. Containers are `csi-provisioner:v3.5.0`, `csi-snapshotter:v6.2.2`, `livenessprobe:v2.10.0`, and `nfsplugin:v4.3.0`. The CSI socket is an `emptyDir`; the driver mounts `/var/lib/kubelet/pods` bidirectionally and exposes health port 29652.

Control flow: Provisioner and snapshotter sidecars connect to `/csi/csi.sock` and use leader election in `kube-system`. The provisioner handles PVC/PV lifecycle; the snapshotter coordinates CSI snapshot calls against `VolumeSnapshotContent`; the NFS driver implements the CSI server and performs NFS mount/directory operations.

State and persistence behavior: Socket state is pod-local and ephemeral. Volume and snapshot records persist in Kubernetes and on the external NFS backend. The Deployment keeps a single controller replica, so sidecar leader election mainly protects against restarts or future scaling.

Dependencies and integration points: Requires `rbac-csi-nfs.yaml` for provisioner/snapshotter permissions, snapshot CRDs plus snapshot-controller/RBAC for full snapshot lifecycle, `csi-nfs-driverinfo.yaml`, and reachable NFS exports. Host-network DNS now supports cluster service resolution.

Risks: The privileged driver and hostPath mount remain sensitive. This version has no resizer sidecar, so `allowVolumeExpansion` requires a later controller. Snapshotter has no resource requests/limits in this manifest, unlike later v4.13.x. Liveness sidecar still uses `--health-port`, and health probes reference a named port. Applying this without CRDs/RBAC will leave snapshot sidecar unable to reconcile.

Test signals: Validate pod readiness, provision a PVC, create/delete a `VolumeSnapshot`, and inspect snapshotter logs for CSI calls. Confirm cluster DNS resolution from the host-network pod, seccomp profile admission, and liveness probe behavior.
