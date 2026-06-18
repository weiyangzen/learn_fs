<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/kind.yaml -->
## sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/kind.yaml

Purpose: defines the Kind cluster configuration for nydus Kubernetes e2e tests.

Important contents: Kind API `kind.x-k8s.io/v1alpha4`, dual-stack IP family, containerd CRI config patches setting `discard_unpacked_layers=false` and `disable_snapshot_annotations=false`, and one control-plane node with `/dev/fuse` mounted from host to container.

Control flow and state: consumed by `tests/helpers/kind.sh` during `kind create cluster`. The containerd patch ensures annotations needed by the snapshotter are preserved and unpacked layers are not discarded in a way that breaks the test flow.

Dependencies/integration: depends on Kind, a host `/dev/fuse`, and containerd inside the Kind node.

Risks and test signals: single-node cluster only. Host Fuse device availability and permissions are required. Dual-stack networking can expose environment-specific issues but may also fail on hosts without IPv6 support.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/kind.yaml -->
