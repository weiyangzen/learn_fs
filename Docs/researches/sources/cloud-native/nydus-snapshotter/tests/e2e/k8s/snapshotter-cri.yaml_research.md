<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/snapshotter-cri.yaml -->
## sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/snapshotter-cri.yaml

Purpose: Kubernetes manifest deploying nydus snapshotter for e2e tests using CRI image-service auth.

Important resources: namespace, service account, cluster role allowing node get/patch, role binding, privileged hostNetwork/hostPID pod running `local-dev:e2e`, hostPath mounts for nydus/containerd/systemd/bin/Fuse paths, and ConfigMap containing `config.toml` and `nydusd.json`.

Control flow and state: pod command runs `/opt/nydus-artifacts/opt/nydus/snapshotter.sh deploy`; preStop runs cleanup. Config sets fusedev, multiple daemon mode, system controller socket, metrics on `:9110`, restart recovery, CRI keychain enabled, kubeconfig keychain disabled, and systemd service enabled. HostPath volumes persist snapshotter state and allow bidirectional mount propagation.

Dependencies/integration: consumed by `kind.sh` when `AUTH_TYPE=cri`; later kubelet is configured to use the snapshotter gRPC image service endpoint.

Risks and test signals: privileged pod with broad hostPath write access is appropriate for e2e but unsafe for production defaults. RBAC lacks secrets because CRI auth mode proxies image credentials instead of watching Kubernetes secrets.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/snapshotter-cri.yaml -->
