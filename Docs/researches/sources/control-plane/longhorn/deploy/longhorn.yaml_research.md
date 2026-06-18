<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/longhorn.yaml -->
# sources/control-plane/longhorn/deploy/longhorn.yaml

Purpose: rendered install manifest for a development Longhorn control plane in `longhorn-system`. It creates the namespace, priority class, service accounts, default setting/resource/storage-class config maps, Longhorn CRDs, broad RBAC, backend/UI/webhook/recovery services, the manager DaemonSet, CSI driver deployer, and UI deployment.

Important APIs/types/functions: Kubernetes APIs include `Namespace`, `PriorityClass`, `ServiceAccount`, `ConfigMap`, `CustomResourceDefinition`, RBAC resources, `Service`, `DaemonSet`, and `Deployment`. Longhorn API types under `longhorn.io/v1beta2` include backing images/data sources/managers, backups, backup targets/volumes/backing images, engine frontends/images/engines, instance managers, nodes, orphans, recurring jobs, replicas, settings, share managers, snapshots, support bundles, system backups/restores, volume attachments, and volumes.

Control flow: installation registers CRDs before controllers, grants the manager cluster and namespace permissions, exposes manager ports 9500/9502/9503, runs `longhorn-manager -d daemon` on every node, waits for the backend before `longhorn-manager -d deploy-driver`, and runs two UI replicas pointed at `http://longhorn-backend:9500`. The manager then reconciles CRDs and deploys runtime CSI/engine/replica/share-manager components from the configured images.

State and persistence: Kubernetes stores desired and observed state in CRDs with `/status` subresources. Volume data persists on host path `/var/lib/longhorn/`; manager pods mount `/boot`, `/dev`, `/proc`, `/etc`, and optional `longhorn-grpc-tls`. ConfigMaps seed default settings and a default `driver.longhorn.io` StorageClass with replica, timeout, filesystem, data locality, unmap, data engine, and backup target parameters.

Dependencies/integration points: depends on Kubernetes CRD/status, RBAC, storage, snapshot, admission registration, metrics, discovery, CSI sidecars, host block devices, iSCSI/NFS support, and Longhorn container images. It integrates with webhook admission on 9502, recovery backend on 9503, CSI provisioning through the driver deployer, and support bundle collection with a separate cluster-admin binding.

Risks/test signals: the manager is privileged and host-mounted, RBAC includes `*` on CRDs/storage/snapshot/Longhorn resources, and support bundle service account binds `cluster-admin`. Image tags are `master-head`, making reproducibility weaker than pinned releases. Test signals are `kubectl apply --dry-run=server`, CRD schema validation, rollout/readiness of manager/driver/UI, default StorageClass creation, webhook health, PVC provisioning, volume attach/detach, snapshot/backup flows, and host-path mount behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/longhorn.yaml -->
