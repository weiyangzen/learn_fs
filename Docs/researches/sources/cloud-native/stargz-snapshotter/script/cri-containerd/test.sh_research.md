# sources/cloud-native/stargz-snapshotter/script/cri-containerd/test.sh

Purpose: Builds CRI containerd test images and orchestrates legacy plus stargz CRI validation.
Important APIs/types/functions: uses Dockerfile version extraction, env toggles `BUILTIN_SNAPSHOTTER`, `FUSE_MANAGER`, `FUSE_PASSTHROUGH`, `TRANSFER_SERVICE`, `METADATA_STORE`; generates CNI and optional containerd configs.
Control flow: builds base/prepare images, creates a temp Dockerfile installing Go, ginkgo, cri-tools, and CNI plugins, appends snapshotter/fuse configs, builds the node image, runs legacy collection, then stargz validation.
State and persistence: creates temporary build context and image-list file; builds Docker images used by sibling scripts.
Dependencies and integration points: integrates Docker build stages, containerd configs, CRI tools, CNI plugins, and snapshotter runtime variants.
Risks: large network-dependent build; unsupported builtin+FUSE passthrough combination exits early; duplicate `DOCKER_BUILD_ARGS` usage can be noisy but harmless.
Test signals: top-level CRI containerd CI entrypoint.
