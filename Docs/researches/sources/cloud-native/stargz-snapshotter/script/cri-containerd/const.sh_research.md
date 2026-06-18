# sources/cloud-native/stargz-snapshotter/script/cri-containerd/const.sh

Purpose: Defines shared Docker image names for CRI containerd tests.
Important APIs/types/functions: variables `NODE_BASE_IMAGE_NAME`, `NODE_TEST_IMAGE_NAME`, and `PREPARE_NODE_IMAGE`.
Control flow: sourced by sibling scripts before building/running test containers.
State and persistence: no persistence by itself.
Dependencies and integration points: coordinates naming between test, legacy, stargz, and mirror scripts.
Risks: changing names can orphan old Docker images or break compose references.
Test signals: covered by CRI containerd test scripts.
