<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/build.yml -->
## sources/control-plane/longhorn-engine/.github/workflows/build.yml

### Purpose
`build.yml` is the main Longhorn Engine CI and image publication workflow. It builds and tests AMD64/ARM64 binaries, uploads artifacts, builds architecture-specific images, pushes them, and creates a multi-arch manifest.

### Important APIs, Types, And Functions
Jobs are `build_info`, `build-amd64-binaries`, `build-arm64-binaries`, `build-push-amd64-images`, `build-push-arm64-images`, and `manifest-image`. It uses pinned checkout, codecov, upload/download artifact, QEMU, Buildx, and Docker login actions. `build_info` computes version and image tag from branch/tag refs.

### Control Flow
Pushes to `master`, `v*`, tags `v*`, pull requests, and manual dispatch trigger the workflow. Binary jobs run `make ci`, `make sync-grpc-py`, and `make integration-test`, then upload `./bin/*`; AMD64 also uploads coverage. Push/tag/branch events then download artifacts, copy them into `package/bin`, log into Docker Hub, and run `make workflow-image-build-push` with arch-specific tags. The final job pulls both arch tags and creates a combined manifest tag.

### State, Persistence, And Dependencies
Persistent outputs include GitHub artifacts, Codecov uploads, Docker Hub images, and manifest lists. Dependencies include Docker Buildx, Docker Hub secrets, Codecov token, arm64 hosted runners, and Makefile/script targets.

### Integration Points
Mergify depends on the build job names. Docker image publishing depends on `Makefile` workflow targets and `scripts/package`. The Dockerfile supplies build/test/ci targets for `make ci` and integration test container images.

### Risks
The `build_info` tag parsing uses shell regex inside a GitHub expression context and should be monitored for tag variants. Docker login steps are enabled for branch and tag refs, so secret availability controls publish success. Artifact action versions are pinned but comments may drift. Integration tests run privileged containers and can be sensitive to runner kernel/device setup. PRs do not publish images, which is correct, but image jobs are skipped and Mergify only checks binary jobs.

### Test Signals
Signals include successful AMD64 and ARM64 `make ci`, generated Python gRPC stubs in sync, integration tests passing, coverage upload, artifact download/executable bits, architecture image push, and manifest creation from both arch images.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/build.yml -->
