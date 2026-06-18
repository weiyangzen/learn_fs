## sources/control-plane/longhorn-engine/scripts/package

### Purpose
`scripts/package` builds the Longhorn engine container image using Docker Buildx, optionally pushing and producing SBOM/provenance attestations.

### Important APIs, Types, And Functions
It sources `scripts/version`, then reads environment parameters including `REPO`, `IMAGE_NAME`, `TAG`, `PUSH`, `IS_SECURE`, `MACHINE`, `TARGET_PLATFORMS`, `IID_FILE`, `IID_FILE_FLAG`, `SRC_BRANCH`, and `SRC_TAG`. It selects `buildx` or `docker buildx`, detects architecture from `TARGET_PLATFORMS` or `uname -m`, builds Docker args, ensures binaries exist, pulls base images, runs buildx, and writes `bin/latest_image`.

### Control Flow
The script chooses `--push` or `--load`, optionally adds `--sbom` and provenance, computes `ARCH`, and runs a no-cache build of `package/Dockerfile`. It exits on unsupported architecture or command failure.

### State, Persistence, And Dependencies
It creates/updates `bin/latest_image`, may run `make build`, pulls base images, and builds local or remote images. Dependencies are Docker Buildx, Docker daemon, `grep`, `awk`, make, and the package Dockerfile.

### Integration Points
CI release flows and local packaging use this script. `scripts/ci` includes it after tests.

### Risks
The variable `IAMGE` is misspelled but consistently used; changing it carelessly can break tagging. Base images are always pulled, so builds depend on network availability. `TARGET_PLATFORMS` parsing assumes one `os/arch` pair, not comma-separated multi-platform lists.

### Test Signals
Signals include successful local `--load` image builds, pushed images for release, correct `bin/latest_image`, and expected provenance/SBOM output when `IS_SECURE=true`.
