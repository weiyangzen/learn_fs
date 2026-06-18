# sources/cloud-native/stargz-snapshotter/script/kind/run-kind.sh

Purpose: Builds a kind node image with kubeconfig keychain support and creates a single-node kind cluster.
Important APIs/types/functions: generated stargz/containerd configs, builtin snapshotter hack, Kubernetes RBAC/secret setup, `wait_for_data`.
Control flow: optionally builds base image, writes snapshotter kubeconfig-keychain config and registry TLS config, builds node image, creates kind cluster, connects it to registry network, installs namespace/imagePullSecret/RBAC/service-account token secret, waits for CA/token data, builds a kubeconfig for the snapshotter, and copies it into the node.
State and persistence: creates Docker images, cluster, Kubernetes secrets/RBAC, and a kubeconfig copied into the node filesystem.
Dependencies and integration points: integrates kind, Kubernetes service-account credentials, stargz snapshotter kubeconfig keychain, registry TLS, and standalone/builtin modes.
Risks: secret name typo `sercret` is consistent but easy to misread; depends on legacy service-account token secret behavior and API server port parsing from process args.
Test signals: used by `kind/test.sh` before pod validation.
