# sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter-rbac.yaml

Purpose: Kubernetes RBAC for snapshotter DaemonSet.

Structure: creates `nydus-system` namespace, service account, cluster role allowing get/patch on nodes, and cluster role binding.

State/dependencies: cluster-scoped permissions persist after apply until cleanup.

Integration points: service account is referenced by the DaemonSet in base deployment.

Risks/tests: node patch permission is broad enough to affect node metadata/status-related workflows depending on use. No automated policy test in this subset.
