<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/tmate-pod.yaml -->
# sources/control-plane/rook/tests/scripts/tmate-pod.yaml

Purpose: CI debugging manifest that deploys a tmate session into a cluster for interactive troubleshooting.

Important structure: creates namespace `tmate`, service account, all-powerful ClusterRole and binding, and a Deployment running Fedora 39. The container installs tmate, kubernetes-client, bash, and vim, then runs `tmate -F` with a socket readiness probe.

State, persistence, and integration: creates privileged-by-RBAC debugging access to the whole cluster and exposes tmate connection details in logs. Dependencies include package install from Fedora repos and cluster network egress. Risks are intentionally severe security exposure through cluster-admin-like RBAC and remote shell access; it should only be applied to disposable CI clusters. Test signals are pod readiness and tmate log output containing SSH/web links.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/tmate-pod.yaml -->
