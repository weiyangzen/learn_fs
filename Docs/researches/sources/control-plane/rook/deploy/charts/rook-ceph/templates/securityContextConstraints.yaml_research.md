
# sources/control-plane/rook/deploy/charts/rook-ceph/templates/securityContextConstraints.yaml

Purpose: conditionally renders OpenShift `SecurityContextConstraints` for Rook Ceph daemons and CSI pods when the cluster supports `security.openshift.io/v1`.

Important APIs/types/functions: OpenShift `security.openshift.io/v1` `SecurityContextConstraints`, Helm `.Capabilities.APIVersions.Has`, `.Values.useOperatorHostNetwork`, `.Release.Namespace`, and `include "library.rook-ceph.labels"`. The file emits `rook-ceph` for Rook/Ceph service accounts and `rook-ceph-csi` for ceph-csi-operator-managed CSI service accounts.

Control flow: non-OpenShift clusters render nothing. On OpenShift, `rook-ceph` allows privileged containers, hostPath, host IPC, selected capabilities, and optionally host networking/ports. `rook-ceph-csi` always allows host network, host ports, host PID, host IPC, hostPath, privileged containers, and `SYS_ADMIN`.

State and persistence: SCCs are cluster-level security policy state. They do not persist Ceph data, but they authorize pods that mount host devices, host paths, and privileged contexts needed by OSDs and CSI node plugins.

Dependencies/integration: integrates with service accounts `rook-ceph-system`, `rook-ceph-default`, `rook-ceph-mgr`, `rook-ceph-osd`, `rook-ceph-rgw`, `rook-ceph-nvmeof`, and ceph-csi controller/node plugin accounts. It depends on OpenShift SCC admission behavior.

Risks: the SCCs intentionally grant high privilege. The CSI SCC permits host PID and host networking by design. Missing a service account in `users` causes pod admission failures. Enabling host networking expands network exposure.

Test signals: render on OpenShift and non-OpenShift capability sets; verify SCC users match all service accounts created by chart and ceph-csi-operator; run pod admission smoke tests for OSD, RGW, mgr, and CSI node plugin pods.
