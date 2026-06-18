## sources/control-plane/csi-driver-nfs/deploy/v4.2.0/csi-nfs-controller.yaml

Purpose: Deploys the v4.2.0 NFS CSI controller as a single `apps/v1` Deployment in `kube-system`. It runs the external provisioner, liveness probe, and NFS CSI driver container needed for dynamic NFS volume provisioning.

Important APIs and types: The pod uses `hostNetwork: true`, `dnsPolicy: Default`, ServiceAccount `csi-nfs-controller-sa`, Linux node selection, system-cluster-critical priority, and control-plane tolerations. Containers are `csi-provisioner:v3.3.0`, `livenessprobe:v2.8.0`, and `nfsplugin:v4.2.0`. The sidecars and driver share an `emptyDir` socket at `/csi/csi.sock`. The NFS container is privileged with `SYS_ADMIN`, mounts host `/var/lib/kubelet/pods` with bidirectional propagation, exposes health port 29652, and serves `/healthz`.

Control flow: The provisioner watches PVCs and StorageClasses using RBAC, then calls the NFS driver over the shared Unix socket to create/delete volumes. The controller driver container can mount the configured NFS export and create backing directories because it runs with host networking and privileged mount capabilities. The liveness sidecar probes the CSI socket and the NFS container's HTTP health endpoint.

State and persistence behavior: Kubernetes stores Deployment/ReplicaSet/Pod state. Runtime CSI socket state is ephemeral in `emptyDir`. Actual volume state lives on the external NFS server; the controller temporarily mounts host kubelet pod paths to perform mount-related operations. No persistent local volume is declared.

Dependencies and integration points: Depends on `rbac-csi-nfs.yaml`, `csi-nfs-driverinfo.yaml`, a StorageClass using `nfs.csi.k8s.io`, and network/NFS access from controller nodes. It integrates with kube-system leader-election leases and events through the provisioner.

Risks: `dnsPolicy: Default` with host networking may not resolve cluster service names such as the example `nfs-server.default.svc.cluster.local`, which later versions change to `ClusterFirstWithHostNet`. The privileged NFS container and bidirectional mount propagation are high privilege. This version lacks snapshotter and resizer sidecars, so snapshots and expansion are not supported by this deployment. Health probe args use older `--health-port` syntax.

Test signals: Apply RBAC and Deployment, verify one ready controller pod, check `/healthz` via liveness events, create a PVC using an NFS StorageClass, confirm PV creation and backing directory creation, and test DNS resolution of the configured NFS server from the host-networked pod.
