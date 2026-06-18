## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/securityContextConstraints.yaml

Purpose: renders an OpenShift `SecurityContextConstraints` resource for Rook and Ceph daemons when the cluster supports `security.openshift.io/v1`.

Important template behavior: gated by `.Capabilities.APIVersions.Has "security.openshift.io/v1"`. It creates SCC `rook-cluster-<namespace>` with privileged containers and hostPath allowed, host network/ports allowed only when `cephClusterSpec.network.provider` is `host`, capabilities `MKNOD` and `SYS_ADMIN`, host IPC, runAsAny user, SELinux/fsGroup constraints, allowed volume types, and service account users for default, mgr, osd, rgw, and nvmeof.

Control flow: Kubernetes capability detection plus network-provider conditional.

State and persistence: creates cluster-level OpenShift security policy granting elevated permissions to Rook service accounts.

Dependencies and integration points: OpenShift SCC API and Rook service account naming. Risks: SCC is broad by necessity for host storage; host network toggling must match cluster spec; missing service accounts for new daemon types can block pods. Tests should render under OpenShift capabilities and verify non-OpenShift omission.
