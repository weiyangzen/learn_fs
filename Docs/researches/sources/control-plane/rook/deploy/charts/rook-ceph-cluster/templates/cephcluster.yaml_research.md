## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephcluster.yaml

Purpose: renders the primary `CephCluster` custom resource for the cluster chart.

Important template behavior: sets metadata name from `.Values.clusterName` or the release namespace, places it in the release namespace, and applies optional labels/annotations from `cephClusterMetadata`. The spec optionally renders monitoring settings, optional `cephImage` as `cephVersion`, then appends raw `.Values.cephClusterSpec`.

Control flow: simple single-resource template with `with` blocks. Monitoring values are rendered before the generic cluster spec, so users should avoid duplicating incompatible monitoring keys in `cephClusterSpec`.

State and persistence: creates/updates the CephCluster CR, which drives operator reconciliation of the entire Ceph deployment. Persistent effects include host data directories, daemons, secrets, ConfigMaps, services, and storage lifecycle managed by the operator.

Dependencies and integration points: depends on the CephCluster CRD and Rook operator. `cephImage` provides a chart-level override while `cephClusterSpec` mirrors CRD shape. Risks: raw `toYaml` of cluster spec gives power but little chart-side validation; dangerous fields such as cleanup policy, storage discovery, and unsupported Ceph versions are passed through. Test signals should include Helm rendering and e2e operator reconciliation.
