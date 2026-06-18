# sources/cloud-native/stargz-snapshotter/script/k3s/run-k3s.sh

Purpose: Builds a custom k3s node image with current stargz snapshotter and creates a k3d cluster configured for stargz.
Important APIs/types/functions: clone/build workflow, generated registry config YAML, namespace/secret creation.
Control flow: clones k3s, vendors current repo from `HEAD`, patches go.mod replacements, builds local k3s image, writes registry mirror/TLS config, creates k3d cluster with `--snapshotter=stargz`, connects node to private registry network, exports kubeconfig, and installs imagePullSecret.
State and persistence: creates temp repos/context/configs, local k3s image, k3d cluster, and Kubernetes namespace/secret.
Dependencies and integration points: depends on git archive, Go toolchain, k3s build scripts, k3d, kubectl, Docker network, and private registry CA.
Risks: uses `git archive HEAD`, so uncommitted code changes are not tested; tracking k3s `main` can introduce moving failures.
Test signals: used by `k3s/test.sh` before pod remote-snapshot validation.
