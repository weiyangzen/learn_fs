
# sources/control-plane/rook/deploy/examples/cluster.yaml

Purpose: is the primary production-oriented CephCluster example for raw-device Rook deployments, documenting many supported cluster settings in one manifest.

Important APIs/types/functions: Rook `CephCluster` with `cephVersion`, `dataDirHostPath`, upgrade gates, mon/mgr counts, dashboard, monitoring/exporter settings, network encryption/compression/msgr2/Multus/host options, crash and log collectors, cleanup policy, placement/annotations/labels/resources, storage selection and config, disruption management, CSI read affinity, and health/liveness/startup probes.

Control flow: once CRDs/common/operator are installed, the operator reconciles the CR by creating mons, mgrs, OSD discovery/prepare/daemon resources, services, secrets, configmaps, collectors, PDBs, and optional monitoring/network behavior according to the spec.

State and persistence: Ceph state persists on selected raw devices and `dataDirHostPath`; Kubernetes stores CR status, secrets, services, and managed workloads. Cleanup policy can intentionally destroy host data only when confirmation is set.

Dependencies/integration: depends on Rook operator, common RBAC/service accounts, Ceph image availability, Kubernetes node/device topology, optional Prometheus, optional Multus, CSI drivers, and any configured placement labels/taints.

Risks: `useAllDevices` can claim unexpected disks. Cleanup confirmation is destructive. Generic network/security settings require kernel and CNI support. Production should pin exact image tags and validate upgrade gates.

Test signals: dry-run and apply in a representative cluster, verify mon quorum, mgr active/standby, OSD inventory, dashboard TLS, health checks, log collection, PDBs, and safe upgrade behavior.
