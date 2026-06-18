# sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: Controller Deployment for v2.0.0 CSI NFS.

Important APIs/types/functions: Kubernetes `apps/v1` `Deployment`; containers `csi-provisioner`, `liveness-probe`, and privileged `nfs`; Helm image/resource values and `include "nfs.labels"`.

Control flow: The deployment runs two replicas by default, selects Linux nodes, starts provisioner against `/csi/csi.sock`, probes the NFS CSI endpoint, and runs the NFS driver with node id and Unix socket endpoint.

State and persistence: Uses hostPath mounts for kubelet plugin and pod directories plus an emptyDir socket directory. Runtime state is CSI socket files, mounts, and provisioned PV/PVC objects.

Dependencies and integration points: Requires controller RBAC/service account, kubelet host paths, NFS CSI image, and external-provisioner.

Risks: Privileged container with `SYS_ADMIN`, hostPath access, hard-coded kubelet path, and Recreate/replica interactions can affect availability. Test signals: render/install smoke, provision a PVC, and inspect liveness endpoint.
