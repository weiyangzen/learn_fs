<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/build.sh -->
# sources/cloud-native/containerd/test/build.sh

- Purpose: Builds a CRI+CNI containerd release tarball for Kubernetes test infrastructure and uploads it to GCS.
- Important behavior: Runs `make clean`, `make BUILDTAGS="seccomp no_btrfs no_devmapper no_zfs" cri-cni-release`, rewrites tarball naming, computes version with `git describe`, then delegates upload to `test/push.sh`.
- Control flow and state: Use a temp build directory, copy release tarball/checksum, set deployment directory, and clean temp files on exit.
- Dependencies and integration: Requires make, git, release make targets, GCS tooling from `push.sh`, and build utilities.
- Risks: Assumes `releases/cri-cni-containerd.tar.gz` symlink exists; uploads are externally visible and versioned.
- Test signals: Release tarball/checksum existence and GCS upload success.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/build.sh -->
