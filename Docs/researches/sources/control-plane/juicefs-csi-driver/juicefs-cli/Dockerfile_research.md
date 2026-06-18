<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/juicefs-cli/Dockerfile -->
# sources/control-plane/juicefs-csi-driver/juicefs-cli/Dockerfile

## Purpose
Minimal Dockerfile that packages the JuiceFS CLI in a Python base image.

## Important APIs, Types, and Resources
Uses `FROM python`, sets `JUICEFS_CLI=/bin/juicefs`, downloads `https://juicefs.com/static/juicefs` with curl, chmods it executable, verifies `juicefs version`, and sets `ENTRYPOINT ["juicefs"]`.

## Control Flow
Docker build pulls the Python base, downloads the CLI binary, validates it during build, and produces an image whose default command runs JuiceFS.

## State and Persistence
Persistent state is the built image layer containing `/bin/juicefs`. The source file stores no runtime state.

## Dependencies and Integration Points
Depends on Docker, the mutable `python` base tag, network access to juicefs.com, and curl availability in the base image. Integrates with CLI/testing workflows needing a containerized JuiceFS binary.

## Risks
Risks include unpinned base image and binary URL, no checksum verification, larger-than-needed Python base, and build breakage if curl is absent from a future base.

## Test Signals
Build the image, run `docker run --rm <image> version`, and consider digest/checksum pinning for release use.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/juicefs-cli/Dockerfile -->
