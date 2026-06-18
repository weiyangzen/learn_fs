
# sources/control-plane/rook/deploy/examples/cluster-test.yaml

Purpose: provides a minimal non-production Ceph cluster for quick tests on one or more nodes with raw devices.

Important APIs/types/functions: Rook `CephCluster`, `mon.count: 1`, `allowMultiplePerNode: true`, `skipUpgradeChecks: true`, one mgr with rook module, dashboard, disabled crash collector, `storage.useAllNodes/useAllDevices`, health checks, priority classes, disruption management, Ceph config for pool size 1, and `.mgr` `CephBlockPool` size 1.

Control flow: after common/operator manifests, Rook creates a one-mon/one-mgr cluster, consumes all raw devices, suppresses no-redundancy warnings, and creates a single-replica manager pool.

State and persistence: data persists on selected devices and `/var/lib/rook`, but redundancy is intentionally disabled. Upgrade safety gates are skipped.

Dependencies/integration: depends on available raw devices, Rook CRDs/operator/RBAC, Ceph image `quay.io/ceph/ceph:v20`, and a test environment where data loss is acceptable.

Risks: not production safe: one mon, pool size 1, all-device consumption, unsupported generic image tag, and skipped upgrade checks. Reinstall requires cleaning dataDirHostPath and devices.

Test signals: verify CephCluster readiness, `.mgr` pool size, dashboard availability, and expected HEALTH warnings suppressed by config. Confirm no production automation applies this file.
