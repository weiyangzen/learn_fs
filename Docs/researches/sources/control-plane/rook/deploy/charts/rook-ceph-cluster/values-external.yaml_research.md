## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/values-external.yaml

Purpose: alternative values file for deploying the cluster chart against an external Ceph cluster.

Important configuration: `cephClusterSpec.external.enable: true`, crash collector disabled, and monitor daemon health check interval configured. Resource lists for CephBlockPools, CephFileSystems, and CephObjectStores are empty maps, so the chart does not create default local storage resources.

Control flow: values-only file consumed by Helm. In particular, `templates/prometheusrules.yaml` uses `external.enable` to select external Prometheus rules.

State and persistence: creates a CephCluster CR configured as external when combined with the chart, but avoids local pools/filesystems/object stores by default. Persistent state is mostly Kubernetes-side integration resources and external-cluster connection artifacts managed elsewhere.

Dependencies and integration points: depends on external cluster setup, secrets/config expected by Rook external cluster workflows, and the normal cluster chart templates. Risks: empty maps must be compatible with templates that normally range lists; external mode has reduced alert coverage; missing external connection prerequisites will cause operator reconciliation failures. Test signals should include Helm render with this file and external cluster e2e.
