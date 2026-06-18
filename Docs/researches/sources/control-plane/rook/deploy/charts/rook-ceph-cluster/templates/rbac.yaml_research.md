## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/rbac.yaml

Purpose: renders CephCluster-namespace RBAC resources when the cluster chart is installed into a namespace different from the operator namespace.

Important template behavior: checks `ne .Release.Namespace .Values.operatorNamespace`, then includes library templates for cluster service accounts, clusterrolebindings, roles, rolebindings, and monitoring roles/bindings when monitoring is enabled.

Control flow: all detailed RBAC objects are delegated to the library chart. This template exists to avoid duplicating cluster-scoped resource definitions when cluster and operator share the same namespace.

State and persistence: creates service accounts and RBAC bindings required for the operator to manage Ceph resources in a separate cluster namespace.

Dependencies and integration points: depends on `library.cluster.*` templates and `monitoring.enabled`. Risks: namespace comparison is the only gate; incorrect `operatorNamespace` can omit required RBAC or create redundant bindings. Because logic is delegated, tests must render with same-namespace and separate-namespace values and inspect included library outputs.
