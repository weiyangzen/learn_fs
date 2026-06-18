# sources/cloud-native/stargz-snapshotter/script/optimize/test.sh

Purpose: Builds and runs optimizer integration tests for zstdchunked and gzip eStargz modes.
Important APIs/types/functions: `test_optimize` writes compose YAML with command parameters; uses version helpers for CNI and nerdctl.
Control flow: builds a race-enabled base image, creates a test image with jq/iptables/zstd/dns/crane/CNI/buildkit tools, prepares TLS registry creds, then runs compose twice with different optimizer/get-TOC/decompress command sets.
State and persistence: creates temp compose/auth/context files, Docker images, registry and buildkit/containerd volumes.
Dependencies and integration points: depends on Docker Compose, registry:2, httpd test server, BuildKit, nerdctl, CNI plugins, and `entrypoint.sh`.
Risks: privileged and network-heavy; test output depends on exact optimizer layer layout.
Test signals: top-level optimizer CI entrypoint.
