<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/Makefile -->
# sources/cloud-native/fuse-overlayfs-snapshotter/Makefile

Purpose: build, install, test, clean, and release artifact automation for `containerd-fuse-overlayfs-grpc`.

Important targets: builds the gRPC binary with version/revision ldflags and CGO disabled; `install` copies it to `$(BINDIR)`; `test` builds the Docker test image, checks `fuse-overlayfs -V`, runs tests with `/dev/fuse` and relaxed security options, then removes the image; `_test` runs Go tests via rootlesskit; `artifacts` cross-builds Linux archives for amd64, arm64, armv7, ppc64le, s390x, and riscv64.

State and integration: writes `bin/` and `_output/`, uses Docker, Go, tar, git, and rootlesskit. Risks include duplicate `binaries` target declarations, mutable version from dirty git state, Docker cleanup failures, and cross-build assumptions. Test signal is Makefile-driven CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/Makefile -->
