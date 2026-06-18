# sources/control-plane/csi-driver-nfs/deploy/csi-nfs-controller.yaml

Purpose: deploys the NFS CSI controller in `kube-system`. The controller handles control-plane CSI calls such as dynamic provisioning, deletion, expansion in newer versions, and snapshot orchestration when the matching sidecars are present.

Important APIs/types/functions: the manifest is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica, `hostNetwork: true`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and service account `csi-nfs-controller-sa`. It runs csi-provisioner v6.2.0, csi-resizer v2.1.0, csi-snapshotter v8.5.0, livenessprobe v2.18.0, and the canary NFS plugin image from `gcr.io/k8s-staging-sig-storage/nfsplugin:canary`. The driver container is privileged, adds `SYS_ADMIN`, exposes the CSI socket at `/csi/csi.sock`, and mounts `/var/lib/kubelet/pods` bidirectionally so controller-side NFS directory operations can use host mount semantics.

Control flow: Kubernetes schedules the deployment, the NFS container serves the CSI endpoint on an `emptyDir` socket, and sidecars connect to that endpoint. leader election uses `$(POD_NAMESPACE)`, provisioner disables `VolumeAttributesClass`, resizer disables in-use resize errors and `VolumeAttributesClass`, and long 1200s CSI timeouts are configured for create/snapshot operations. Liveness probes use the local health endpoint and cause pod restarts when the driver endpoint stops responding.

State and persistence: controller state is mostly Kubernetes API state in PVs, PVCs, VolumeSnapshots, VolumeSnapshotContents, Leases, and Events. The pod itself uses an ephemeral CSI socket directory; persistent NFS data is stored on the configured server/share and subdirectories rather than in the controller pod.

Dependencies and integration points: depends on `rbac-csi-nfs.yaml` or the versioned RBAC file, `csi-nfs-driverinfo.yaml`, the node DaemonSet, kubelet pod mount paths, and a reachable NFS server. Snapshot behavior also depends on snapshot CRDs, snapshot controller RBAC, and snapshot class manifests.

Risks: privileged `SYS_ADMIN`, host networking, and bidirectional `/var/lib/kubelet/pods` mount propagation are high-trust settings. Controller placement on control-plane nodes relies on tolerations and may fail under custom taints. The canary plugin image is intentionally unstable relative to tagged release manifests. Sidecar and CRD version skew is the main compatibility risk.

Test signals: validate with `kubectl apply --dry-run=server`, rollout status for `deployment/csi-nfs-controller`, a dynamically provisioned PVC from `storageclass.yaml`, expansion of an existing PVC for resize-capable versions, and snapshot/restore flows when snapshot sidecars are included.
