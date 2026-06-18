<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/helpers/kind.sh -->
## sources/cloud-native/nydus-snapshotter/tests/helpers/kind.sh

Purpose: orchestrates the full Kind-based Kubernetes e2e flow for nydus snapshotter.

Important variables/flow: configurable `AUTH_TYPE`, `INDEX_DETECT`, `ROOTFUL`, versions for Kind/Kubernetes/Nydus, test registry credentials, and namespace. The script sources helper libraries, resolves latest Nydus release, builds static snapshotter binaries, builds a local e2e image, starts an authenticated registry, configures Docker, installs dependencies, converts/pushes a busybox nydus image, recreates a Kind cluster, deploys snapshotter manifest, restarts containerd, creates image pull secret, optionally points kubelet at the nydus image service for CRI auth, applies a test pod, validates readiness/logs, optionally checks index-detect log evidence, then deletes the pod.

Dependencies/integration: drives Makefile, Docker, Kind, kubectl, nydusify, GitHub API, local registry, and manifests in `tests/e2e/k8s`.

Risks and test signals: highly stateful and host-mutating: Docker daemon config, Kind cluster deletion, host binary installation, container lifecycle, kubelet/containerd restarts. Provides strong e2e confidence when it passes, especially for auth modes and index detection, but failures may stem from environment rather than code.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/helpers/kind.sh -->
