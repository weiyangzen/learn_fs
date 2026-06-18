# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-serviceaccount.yaml

Purpose: optionally creates the RBD nodeplugin service account.

Important APIs/types/functions: gated by `.Values.serviceAccounts.nodeplugin.create`; name comes from the service-account helper and labels follow the chart/release/component scheme.

Control flow: the DaemonSet references this service account, and RBAC bindings grant it API permissions.

State and persistence behavior: namespace-scoped Kubernetes identity object.

Dependencies and integration points: tied to ClusterRoleBinding and projected service-account token use for KMS.

Risks: disabling creation requires an existing correctly named service account. Reusing a service account can couple privileges across workloads.

Test signals: pod admission and authorization behavior.
