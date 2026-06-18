# sources/cloud-native/stargz-snapshotter/script/cri-containerd/test-legacy.sh

Purpose: Runs baseline CRI validation against containerd before stargz mirroring.
Important APIs/types/functions: cleanup temp files, readiness loop, and image-list extraction from journald.
Control flow: starts a privileged test node, waits for containerd, runs `critest` against runtime and image endpoints, extracts all pulled image names from containerd logs plus pause images, writes them to the provided list file, then kills the node.
State and persistence: creates a disposable Docker container and temporary log/list files; output is the image list consumed by stargz tests.
Dependencies and integration points: depends on Docker, critest, runc/containerd, optional FUSE manager endpoint, and `utils.sh` version helpers.
Risks: log scraping is format-sensitive; cleanup trap is defined but not installed in the file, so early failures can leak temp files until process exit cleanup by OS.
Test signals: serves as the first phase of `cri-containerd/test.sh`.
