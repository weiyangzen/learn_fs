# sources/cloud-native/stargz-snapshotter/Dockerfile

## Purpose
The Dockerfile defines a multi-stage build and test image matrix for stargz-snapshotter, including release binaries, containerd variants, podman/CRI-O/stargz-store environments, demo images, and KinD node images.

## Important APIs, Types, and Functions
Top-level build args pin versions for containerd, runc, CNI plugins, nerdctl, Podman, CRI-O, conmon, containers/common, pause images, rootless helpers, and cri-tools. Stages build containerd, builtin containerd with stargz plugin, runc, snapshotter binaries, stargz-store, Podman, CRI-O, conmon, seccomp config, release binaries, containerd bases, podman rootless environment, demo, kind builtin snapshotter, CRI-O stargz-store, and the final KinD image.

## Control Flow, State, and Persistence
Build stages clone upstream repos at pinned versions, compile binaries, copy outputs into later runtime/test stages, install packages and downloaded tools, configure services, and set entrypoints. `release-binaries` is a scratch target containing built binaries for release packaging.

## Dependencies and Integration Points
The Dockerfile is consumed by Makefile targets, CI workflows, release workflow, and runtime integration scripts. It depends heavily on network access to GitHub, package mirrors, container images, and versioned upstream repositories.

## Risks and Test Signals
Many stages build from live upstream source tags and downloaded scripts, so build reproducibility depends on network and tag integrity. Some stages use `apt-get install -y` without cleanup. Architecture args must be correctly supplied for multi-arch builds. The Dockerfile is central to CI signals for containerd, CRI-O, Podman, k3s, KinD, and release artifacts.
