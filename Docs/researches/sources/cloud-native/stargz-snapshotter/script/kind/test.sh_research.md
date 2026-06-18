# sources/cloud-native/stargz-snapshotter/script/kind/test.sh

Purpose: End-to-end kind private registry lazy-pull and keychain test.
Important APIs/types/functions: uses `prepare_creds`, compose registry/prepare node, `run-kind.sh`, and `create-pod.sh`.
Control flow: builds prepare image, creates auth/TLS registry on a dedicated network, mirrors optimized Ubuntu image, creates configured kind cluster, waits for secret sync, creates pod and validates remote snapshots, then tears down compose, cluster, and network.
State and persistence: creates temp auth/dockerconfig/compose/kubeconfig dirs, Docker network, registry content, and kind cluster.
Dependencies and integration points: depends on Docker Compose, kind, kubectl, registry:2, keychain-enabled node image, and mirror script.
Risks: heavy integration test with many external tools; early failures can leave artifacts if cleanup commands fail.
Test signals: success proves kind/Kubernetes secret credentials work with stargz lazy pulls.
