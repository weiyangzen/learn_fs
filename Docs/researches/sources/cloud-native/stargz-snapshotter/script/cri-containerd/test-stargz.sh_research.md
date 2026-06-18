# sources/cloud-native/stargz-snapshotter/script/cri-containerd/test-stargz.sh

Purpose: Runs CRI validation against containerd using stargz lazy-pulled mirrored images.
Important APIs/types/functions: `cleanup` trap, registry/mirror setup, config generation, digest replacement, critest, snapshot/log checks.
Control flow: starts a compose stack with test node, prepare node, and registry; mirrors/optimizes images; configures containerd and snapshotter registry mirrors; rewrites digest references in cri-tools to optimized digests; rebuilds critest; restarts services; runs critest; verifies stargz snapshots and remote snapshot log records.
State and persistence: creates compose resources, temp configs, mirrored registry content, modified cri-tools files inside the node, and log extracts.
Dependencies and integration points: depends on Docker Compose, registry:2, ctr-remote, critest, containerd/stargz services, and `check_remote_snapshots`.
Risks: highly environment-sensitive and mutates test tool source in-container; digest extraction with grep/sed can fail if image listing format changes.
Test signals: second phase of `cri-containerd/test.sh`; success proves CRI lazy-pull integration.
