
# sources/control-plane/rook/deploy/examples/cluster-external.yaml

Purpose: defines an external-mode `CephCluster` for connecting Rook to an existing Ceph cluster without creating local Ceph daemons.

Important APIs/types/functions: Rook `ceph.rook.io/v1` `CephCluster`, `spec.external.enable: true`, disabled crash collector, mon daemon health check interval, and commented external manager Prometheus endpoint configuration.

Control flow: after CRDs, common resources, operator, and external connection setup are applied, the operator reconciles the CR as an external cluster. It expects imported monitor endpoints and credentials instead of provisioning storage.

State and persistence: the CR stores desired external-cluster integration state in Kubernetes. Ceph data and core daemon state remain in the external Ceph cluster.

Dependencies/integration: depends on external cluster import scripts/secrets, `common-external.yaml` when a separate namespace is used, the Rook operator watch scope, and optional Prometheus endpoints for external manager metrics.

Risks: applying without required external secrets produces a nonfunctional cluster CR. Crash collection is disabled, reducing local diagnostics. Monitoring requires accurate manager IP/port configuration.

Test signals: verify CephCluster reaches ready/connected status, check operator logs for imported mon endpoints, create a simple storage/object CR against the external cluster, and test optional metrics scraping if enabled.
