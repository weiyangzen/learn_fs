# sources/cloud-native/stargz-snapshotter/script/cri-o/test.sh

Purpose: Builds CRI-O stargz-store test images and runs legacy plus stargz CRI validation.
Important APIs/types/functions: env `CRI_NO_RECREATE`, `METADATA_STORE`; generated `crio.conf`; Dockerfile installing Go/ginkgo/cri-tools.
Control flow: builds base and prepare images, generates a test node Dockerfile with CRI tools and metadata store config, builds it, then invokes `test-legacy.sh` and `test-stargz.sh` with a shared image-list file.
State and persistence: creates temp build context and image list; produces Docker test images.
Dependencies and integration points: depends on Docker build stages, CRI-O base image, Go toolchain, cri-tools, and utility version parsing.
Risks: network-heavy build; metadata store config is appended rather than replacing prior conflicting entries.
Test signals: top-level CRI-O CI entrypoint.
