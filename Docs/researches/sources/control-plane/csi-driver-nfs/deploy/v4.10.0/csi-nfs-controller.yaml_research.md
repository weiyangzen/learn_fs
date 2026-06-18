# sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-nfs-controller.yaml

Purpose: deploys the NFS CSI controller in `kube-system`. The controller handles control-plane CSI calls such as dynamic provisioning, deletion, expansion in newer versions, and snapshot orchestration when the matching sidecars are present.

Important APIs/types/functions: the manifest is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica, `hostNetwork: true`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and service account `csi-nfs-controller-sa`. It runs csi-provisioner v5.2.0, csi-resizer v1.13.1, csi-snapshotter v8.2.0, livenessprobe v2.15.0, and nfsplugin v4.10.0. The driver container is privileged, adds `SYS_ADMIN`, exposes the CSI socket at `/csi/csi.sock`, and mounts `/var/lib/kubelet/pods` bidirectionally so controller-side NFS directory operations can use host mount semantics.

Control flow: Kubernetes schedules the deployment, the NFS container serves the CSI endpoint on an `emptyDir` socket, and sidecars connect to that endpoint. leader election is pinned to `kube-system`, the provisioner enables `HonorPVReclaimPolicy`, and long 1200s CSI timeouts plus 30m retry intervals are configured. Liveness probes use the local health endpoint and cause pod restarts when the driver endpoint stops responding.

State and persistence: controller state is mostly Kubernetes API state in PVs, PVCs, VolumeSnapshots, VolumeSnapshotContents, Leases, and Events. The pod itself uses an ephemeral CSI socket directory; persistent NFS data is stored on the configured server/share and subdirectories rather than in the controller pod.

Dependencies and integration points: depends on `rbac-csi-nfs.yaml` or the versioned RBAC file, `csi-nfs-driverinfo.yaml`, the node DaemonSet, kubelet pod mount paths, and a reachable NFS server. Snapshot behavior also depends on snapshot CRDs, snapshot controller RBAC, and snapshot class manifests.

Risks: privileged `SYS_ADMIN`, host networking, and bidirectional `/var/lib/kubelet/pods` mount propagation are high-trust settings. Controller placement on control-plane nodes relies on tolerations and may fail under custom taints. The release-tagged plugin image is stable for this version, but sidecar upgrades still need compatibility checks. Sidecar and CRD version skew is the main compatibility risk.

Test signals: validate with `kubectl apply --dry-run=server`, rollout status for `deployment/csi-nfs-controller`, a dynamically provisioned PVC from `storageclass.yaml`, expansion of an existing PVC for resize-capable versions, and snapshot/restore flows when snapshot sidecars are included.
