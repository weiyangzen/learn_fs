## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/Chart.yaml

Purpose: declares the Helm chart that manages a single Ceph cluster namespace for Rook.

Important metadata: apiVersion v2, name `rook-ceph-cluster`, version/appVersion `0.0.1`, icon and source URL, and a dependency on the local `library` chart.

Control flow: this chart renders CephCluster-scoped resources such as CephCluster, pools, filesystems, object stores, dashboard exposure, toolbox deployment, monitoring rules, RBAC, SCC, and snapshot classes according to `values.yaml`.

State and persistence: chart install/upgrade manages namespace-scoped and some cluster-scoped Kubernetes resources for a Ceph cluster. Persistent effects include Ceph CRs that cause operator reconciliation and storage resources.

Dependencies and integration points: expects the Rook operator chart to be installed, and uses library chart helpers. Risks: version/appVersion placeholders require release automation to stamp real values; dependency path assumes repository chart layout. Test signals should include Helm lint/template rendering and operator e2e installs for representative values.
