<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/Dockerfile -->
# sources/control-plane/beegfs-csi-driver/Dockerfile

## Purpose
The Dockerfile packages the BeeGFS CSI driver into a minimal distroless static image with prebuilt driver and `chwrap` helper artifacts.

## Important Instructions
It starts from `gcr.io/distroless/static:latest` for the target platform, sets OCI labels, defines `TARGETARCH` and fallback `ARCH`, copies `bin/beegfs-csi-driver$ARCH` to `/beegfs-csi-driver`, adds `bin/chwrap$ARCH.tar` into `/`, prepends `/osutils` to `PATH`, and sets `/beegfs-csi-driver` as the entrypoint.

## Control Flow
There is no build-stage compilation. The Docker build assumes `make all` already created architecture-specific binaries and tarballs under `bin/`. Buildx or release-tools provides the target architecture; the Dockerfile selects the matching prebuilt artifact by suffix.

## State and Persistence
The resulting image contains the driver binary and `/osutils` symlink tree from the tarball. At runtime, `/osutils` commands invoke `chwrap`, which finds and executes host binaries under `/host`.

## Dependencies and Integration Points
This file integrates with the Makefile's `build` and `bin/chwrap.tar` targets, GitHub Actions multi-arch buildx configuration, CSI deployment manifests that mount `/host`, and the `cmd/chwrap` program.

## Risks
Using `distroless/static:latest` makes base-image content time-dependent. A missing or mis-suffixed binary/tarball fails the build. Runtime command behavior depends on `/host` being mounted and `/osutils` being first in `PATH`. The image itself does not include BeeGFS utilities or common system binaries beyond the wrapper symlinks.

## Test Signals
Signals include local and buildx image builds for amd64/arm64, verifying `/beegfs-csi-driver --version`, inspecting `/osutils`, and running deployment smoke tests that require mount, umount, modprobe, lsmod, touch, and BeeGFS utilities through `chwrap`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/Dockerfile -->
