<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/validate_cluster.sh -->
# sources/control-plane/rook/tests/scripts/validate_cluster.sh

Purpose: cluster readiness validator for Rook/Ceph demo and integration environments. It checks CSI pods and selected Ceph daemons through toolbox and Kubernetes status.

Important APIs and control flow: first argument chooses daemons or defaults to `all`; second is OSD count or object-store name for RGW. `wait_for_daemon` retries command predicates. Dedicated tests check mon quorum, mgr presence, OSD up/in count, RGW pod readiness, MDS pools/up status, rbd-mirror, fs-mirror, pool count, CSI pod minimum, and NFS pod count. Main always checks CSI, mon, and mgr, then expands daemon list and runs selected checks, finally printing Ceph status, pods, operator logs, and cluster YAML.

State, persistence, and integration: reads cluster state and logs but does not create resources. Dependencies include a `rook-ceph-tools` deployment, `kubectl`, Ceph CLI, and expected labels/resource names. Risks include grep-string fragility, `log` function references in the error path without definition, and assumptions about namespace `rook-ceph`. Test signals are successful predicates and diagnostic output on failure.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/validate_cluster.sh -->
