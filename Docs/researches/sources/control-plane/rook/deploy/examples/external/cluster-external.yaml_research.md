<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/cluster-external.yaml -->
# sources/control-plane/rook/deploy/examples/external/cluster-external.yaml

Purpose: minimal `CephCluster` CR for a Kubernetes consumer cluster that connects to an external Ceph cluster.
Important APIs/types/functions: `CephCluster` `rook-ceph-external`, `spec.external.enable: true`, disabled crash collector, daemon health check for mons, and optional external mgr monitoring endpoints.
Control flow: Rook reconciles this CR without provisioning local Ceph daemons, instead using imported external cluster secrets/configmaps to represent and monitor the external cluster. State is the CephCluster CR status plus imported credentials/endpoints. Dependencies are `common-external.yaml`, external-cluster import resources, Rook operator, and external Ceph availability. Risks: missing imported secrets prevents readiness, monitoring endpoints are optional/commented, and crash collection is disabled. Test signals: CephCluster becomes Connected/Ready, operator logs external mode, and storage classes using imported credentials provision volumes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/cluster-external.yaml -->
