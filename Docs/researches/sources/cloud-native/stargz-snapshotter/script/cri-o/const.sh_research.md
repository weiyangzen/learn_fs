# sources/cloud-native/stargz-snapshotter/script/cri-o/const.sh

Purpose: Defines shared Docker image names for CRI-O tests.
Important APIs/types/functions: variables `NODE_BASE_IMAGE_NAME`, `NODE_TEST_IMAGE_NAME`, and `PREPARE_NODE_IMAGE`.
Control flow: sourced by CRI-O mirror and test scripts.
State and persistence: no persistent state.
Dependencies and integration points: coordinates Docker image naming across the CRI-O test workflow.
Risks: name changes must be synchronized with all CRI-O scripts.
Test signals: covered by `script/cri-o/test.sh`.
