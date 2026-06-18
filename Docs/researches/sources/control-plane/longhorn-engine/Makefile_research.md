<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/Makefile -->
## sources/control-plane/longhorn-engine/Makefile

### Purpose
The Makefile is the Longhorn Engine developer/CI command surface for Dockerized build, validation, test, packaging, integration tests, gRPC Python sync, and workflow image publishing.

### Important APIs, Types, And Functions
Variables include `PROJECT`, `MACHINE`, `DEFAULT_PLATFORMS`, `SRC_BRANCH`, and `SRC_TAG`. Targets include `build`, `validate`, `test`, `ci`, `package`, `integration-test`, `sync-grpc-py`, `buildx-machine`, `workflow-image-build-push`, `workflow-image-build-push-secure`, and `workflow-manifest-image`.

### Control Flow
Build/test/ci targets call `docker buildx build` with Dockerfile targets, exporting artifacts for `build` and `ci`. Integration tests build the base image, then run it privileged with host `/dev`, `/proc`, `/tmp` bind propagation, and tmpfs tox/venv paths. gRPC sync runs a container command. Workflow image targets ensure a buildx machine, call `scripts/package` with push/image envs, and create multi-arch manifests from arch-specific tags.

### State, Persistence, And Dependencies
Targets create Docker build cache, local `bin/` and `coverage.out` artifacts, Docker images, and pushed registry images. Dependencies include Docker Buildx, curl to central dep-versions for `SRC_BRANCH`, git tags, and scripts under `scripts/`.

### Integration Points
GitHub Actions call `make ci`, `make sync-grpc-py`, `make integration-test`, `make workflow-image-build-push`, and `make workflow-manifest-image`. The Dockerfile supplies named build targets used here.

### Risks
`SRC_BRANCH` is computed by sourcing a remote script at make parse time, creating a network dependency even for local commands. Integration tests require privileged Docker and host device/proc access. Manifest creation assumes both arch images already exist. Buildx machine creation is best-effort and may reuse stale configuration.

### Test Signals
Signals include local and CI success for each target, artifact presence after `ci`, integration test container able to access required host mounts, generated Python stubs staying clean, and manifest target finding both arch images.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/Makefile -->
