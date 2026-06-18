# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-clusterrole.yaml

Purpose: renders cluster-wide RBAC for the RBD nodeplugin service account.

Important APIs/types/functions: gated by `.Values.rbac.create`; grants reads on nodes, secrets, configmaps, serviceaccounts, persistentvolumes, volumeattachments, and creation of `serviceaccounts/token`.

Control flow: the nodeplugin needs these permissions for node identity/topology, KMS/Vault token or connection secret access, config loading, PV lookup, volume attachment inspection, and projected service-account token creation.

State and persistence behavior: Kubernetes RBAC object only.

Dependencies and integration points: bound by the nodeplugin ClusterRoleBinding and consumed by the DaemonSet service account.

Risks: secret `get/list/watch` is broad cluster-wide access. Operators seeking least privilege may need namespace scoping or externally managed RBAC.

Test signals: mount/encryption/fencing/read-affinity e2e tests and Kubernetes authorization failures validate the permission set.
