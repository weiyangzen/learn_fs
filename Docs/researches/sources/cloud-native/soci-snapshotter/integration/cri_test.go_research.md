# sources/cloud-native/soci-snapshotter/integration/cri_test.go

Purpose: verifies SOCI lazy pulling through containerd's CRI image service rather than only `ctr` or `nerdctl`.

Important APIs and flow: `TestCRIImagePull` mirrors an Alpine image, builds and pushes a SOCI index, restarts containerd with CRI-enabled config and snapshotter config using the CRI keychain, then runs `crictl pull --creds` and checks that all layers were mounted as remote snapshots.

State and persistence: writes local registry image/index artifacts and restarts containerd with a CRI-specific configuration.

Dependencies and integration: integrates CRI plugin config, `crictl`, registry credentials, snapshotter resolver credentials, and remote snapshot log monitoring.

Risks and test signals: compact but important coverage for Kubernetes-facing pull paths. It assumes CRI config generation and credential propagation match registry setup; it does not run a pod/container through CRI after pull.
