# sources/control-plane/juicefs-csi-driver/.github/workflows/version.yaml

## Purpose
This release workflow builds and publishes versioned CSI driver and dashboard images, bundling selected CE and EE JuiceFS mount image versions.

## Important Jobs and Steps
The `publish-version` job checks out full history, builds dashboard dist, logs into Docker Hub, resolves CE, EE, and CSI versions from inputs or upstream sources, configures QEMU/Buildx, runs `make -C docker image-version` and `make -C docker dashboard-buildx`, then syncs the CSI image through `.github/scripts/sync.sh`.

## Control Flow
It runs on manual dispatch and GitHub release creation. Input versions override auto-detected latest versions. CE version detection queries GitHub releases, EE version detection downloads and inspects a static package, and CSI version detection uses `git describe --tags --match 'v*'`.

## State and Persistence Behavior
The workflow publishes versioned container images and syncs them externally. It does not create commits or tag changes; it consumes release/tag state.

## Dependencies and Integration Points
It depends on pnpm/dashboard build, Docker Hub credentials, Docker Buildx, Docker Makefile release targets, GitHub release/tag metadata, JuiceFS static package endpoints, and ACR sync credentials.

## Risks
Version parsing is shell/grep based and can fail on unexpected upstream formats. If release creation happens before assets or upstream mount images are ready, build may fail. The workflow does not run E2E tests; it assumes release checks already validated combinations.

## Test Signals
Success indicates versioned images were built and the CSI image was synced. Functional validation must come from CI/release-check workflows.
