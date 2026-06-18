# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/values.yaml

Purpose: default values and operator-facing schema for the RBD Helm chart.

Important APIs/types/functions: key groups are `rbac`, `serviceAccounts`, `csiConfig`, `csiMapping`, `encryptionKMSConfig`, logging, `CSIDriver`, `nodeplugin`, `provisioner`, `topology`, `storageClass`, snapshot/group snapshot classes, `secret`, `cephconf`, `extraDeploy`, and internal socket/configmap names.

Control flow: templates consume values to render config maps, RBAC, service accounts, node DaemonSet, controller Deployment, metric Services, StorageClass, SnapshotClass, GroupSnapshotClass, and optional Secret.

State and persistence behavior: values materialize as Kubernetes objects and then drive persistent Ceph RBD images/snapshots/metadata. Runtime sockets and key directories are ephemeral; Secrets and ConfigMaps persist in Kubernetes.

Dependencies and integration points: integrates with Helm, Kubernetes CSI sidecars, Ceph RBD, KMS providers, Prometheus, CSI-Addons, kubelet paths, and external snapshot/group-snapshot APIs.

Risks: defaults are development-oriented (`canary`, placeholder cluster/secrets, verbose logging, storage class disabled). Many parameters are strings expected by CSI, so boolean-looking values such as `encrypted` must remain strings. Broad RBAC and privileged host access are inherent.

Test signals: Helm render/lint, chart install tests, and RBD e2e coverage for provisioning, expansion, snapshots, clones, encryption, topology, read affinity, and metrics.
