# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: Helm template for the NFS CSI controller Deployment.

Important APIs and types: creates an `apps/v1` Deployment with configurable name, namespace, replicas, strategy, affinity, node selectors, tolerations, priority class, service account, and resources. Containers include `csi-provisioner`, `csi-resizer`, optional `csi-snapshotter`, `liveness-probe`, and privileged `nfs`.

Control flow: sidecars talk to `/csi/csi.sock` in an `emptyDir` shared with the NFS driver container. Provisioner and resizer use leader election in the release namespace and disable `VolumeAttributesClass`. The NFS container runs with host networking, mounts kubelet pods directory bidirectionally, exposes liveness, and receives controller settings for mount permissions, working mount dir, delete policy, tar-based snapshots, and compression.

State and persistence: creates Kubernetes Deployment/Pods; uses hostPath `kubeletDir/pods` for mount propagation and an in-pod socket `emptyDir`.

Dependencies and integration: depends on service account/RBAC templates outside this subset, image values, kubelet directory values, CSI sidecars, and the NFS plugin binary image.

Risks: controller hostNetwork and privileged `SYS_ADMIN` are high privilege but needed for NFS mount operations. Affinity logic uses templated string inspection for `nodeSelectorTerms`, which can be brittle. Long sidecar timeouts may delay failure surfacing.

Test signals: Helm install, Deployment rollout, sidecar leader election, PVC provisioning/resizing/snapshot tests, and liveness probe health.
