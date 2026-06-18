# sources/cloud-native/stargz-snapshotter/script/criauth/run-kind.sh

Purpose: Builds a kind node image with CRI keychain support and creates a single-node kind cluster wired to a private registry.
Important APIs/types/functions: kind node image variables, generated containerd config snippets, builtin snapshotter hack config, namespace/secret creation.
Control flow: optionally builds base image, writes TLS and CRI keychain containerd config, builds node image, creates kind cluster, connects node to registry network, prints versions, and installs namespace plus imagePullSecret.
State and persistence: creates Docker images, a kind cluster, temporary configs, kubeconfig, and Kubernetes secret state.
Dependencies and integration points: integrates kind, containerd CRI registry TLS, standalone or builtin stargz snapshotter, Docker network, and Kubernetes secret auth.
Risks: cluster creation is heavyweight; builtin and standalone config paths differ and can drift; typo in log text is harmless.
Test signals: used by `criauth/test.sh` before `create-pod.sh`.
