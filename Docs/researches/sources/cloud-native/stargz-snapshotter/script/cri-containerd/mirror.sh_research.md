# sources/cloud-native/stargz-snapshotter/script/cri-containerd/mirror.sh

Purpose: Mirrors and optimizes CRI test images into a local registry for stargz validation.
Important APIs/types/functions: `retry`; inputs `TOOLS_DIR/list` and `TOOLS_DIR/host`.
Control flow: builds `ctr-remote`, starts containerd, waits for readiness, then for each unique image pulls it, optimizes it with `--oci --period=1`, and pushes to the mirror over plain HTTP.
State and persistence: writes `/bin/ctr-remote` and populates the target registry with optimized image tags.
Dependencies and integration points: runs in the prepare node from `test-stargz.sh`; depends on make, containerd, ctr-remote, and registry connectivity.
Risks: uses simple URL rewriting that strips original host and digest; assumes mirror registry accepts plain HTTP and unique path mapping.
Test signals: stargz CRI tests fail if mirrored images are missing or invalid.
