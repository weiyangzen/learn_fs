# sources/cloud-native/stargz-snapshotter/script/k3s/test.sh

Purpose: End-to-end k3s private registry lazy-pull test.
Important APIs/types/functions: uses `prepare_creds`, compose registry/prepare services, `run-k3s.sh`, and `create-pod.sh`.
Control flow: builds prepare image, starts authenticated TLS registry and prepare node on a dedicated network, mirrors optimized test image, creates custom k3s cluster, waits for secret sync, creates a pod, validates remote snapshots, and cleans up compose, cluster, and network.
State and persistence: creates temp auth/dockerconfig/compose/kubeconfig dirs, registry data, Docker network, and k3d cluster.
Dependencies and integration points: depends on Docker Compose, k3d, kubectl, k3s build, registry auth/TLS, and stargz mirror script.
Risks: heavyweight and network-dependent; cleanup occurs after test block and may leave artifacts on abrupt termination.
Test signals: success proves k3s can pull private optimized images lazily via stargz.
