<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/snapshotter-kubeconf.yaml -->
## sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/snapshotter-kubeconf.yaml

Purpose: Kubernetes manifest deploying nydus snapshotter for e2e tests using kubeconfig-backed secret watching.

Important resources: same namespace/service account/pod/config structure as CRI manifest, but RBAC also grants `get/list/watch` on secrets. ConfigMap sets `enable_index_detect=true`, kubeconfig keychain enabled, CRI keychain disabled, and systemd service disabled.

Control flow and state: deployed by `kind.sh` when `AUTH_TYPE=kubeconf`. It relies on the snapshotter reading Kubernetes dockerconfigjson secrets through kubeconfig rather than kubelet image-service credential forwarding. The same privileged hostPath mounts expose containerd config, binaries, snapshotter data, `/run/containerd-nydus`, `/dev/fuse`, and systemd paths.

Dependencies/integration: integrates with e2e secret creation in `kind.sh`, index-detect validation, and snapshotter config parsing from mounted ConfigMap.

Risks and test signals: broader RBAC to secrets is required and should be scoped carefully outside tests. Index-detect is enabled here, making it the manifest used to test alternative nydus image detection through logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/snapshotter-kubeconf.yaml -->
