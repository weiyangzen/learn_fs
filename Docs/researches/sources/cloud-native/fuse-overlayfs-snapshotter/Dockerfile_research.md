<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/Dockerfile -->
# sources/cloud-native/fuse-overlayfs-snapshotter/Dockerfile

Purpose: multi-stage test image for running snapshotter tests under rootlesskit with a built fuse-overlayfs binary.

Important flow: builds Go test binary with CGO disabled; clones and statically builds `containers/fuse-overlayfs` at configurable commit; clones and builds rootlesskit at configurable commit; final Alpine image installs FUSE/user namespace dependencies, grants `newuidmap` and `newgidmap` capabilities, creates a test user and subuid/subgid ranges, and runs the compiled Go test under rootlesskit.

State and integration: used by `make test` and CI. It downloads external source repositories and packages, builds binaries, and requires runtime flags for `/dev/fuse` plus relaxed seccomp/AppArmor. Risks include unpinned default `main` for fuse-overlayfs, privileged build/run assumptions, and package version drift. Test signal is the containerized snapshotter suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/Dockerfile -->
