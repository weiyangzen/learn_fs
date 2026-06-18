# sources/cloud-native/stargz-snapshotter/script/criauth/test.sh

Purpose: End-to-end test for CRI image-pull secret auth with stargz snapshotter in kind.
Important APIs/types/functions: registry/auth constants, `prepare_creds`, compose setup, `run-kind.sh`, `create-pod.sh`.
Control flow: builds prepare image, creates htpasswd/TLS registry and prepare service on a dedicated Docker network, mirrors an optimized test image into the registry, creates a kind cluster with keychain support, waits, creates a private-image pod, then tears down compose, cluster, and network.
State and persistence: creates temp auth data, Docker config JSON, compose file, kind kubeconfig, registry content, Docker network, and cluster.
Dependencies and integration points: depends on Docker Compose, kind, kubectl, registry:2, mounted repo, and utility credential helper.
Risks: cleanup is manual after the main test block; failures during early registry prep perform explicit partial cleanup but abrupt host failures can leave networks/clusters.
Test signals: success proves CRI credentials reach stargz snapshotter for lazy pulls.
