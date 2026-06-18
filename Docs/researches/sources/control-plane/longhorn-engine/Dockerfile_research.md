<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/Dockerfile -->
## sources/control-plane/longhorn-engine/Dockerfile

### Purpose
The Longhorn Engine Dockerfile defines reproducible build, validation, test, and artifact stages for CI and packaging. It builds a SUSE BCI Golang environment with native storage dependencies, liblonghorn, TGT, integration-test tooling, and Longhorn instance manager.

### Important APIs, Types, And Functions
Stages include `golangci-lint`, `base`, `build`, `validate`, `test`, `build-artifacts`, and `ci-artifacts`. Important args/envs are `TARGETARCH`, `SRC_BRANCH`, `SRC_TAG`, proxy args, `ARCH`, `GOFLAGS=-mod=vendor`, `PROTOBUF_VER_PY`, and `LONGHORN_INSTANCE_MANAGER_BRANCH`.

### Control Flow
The base stage installs repositories and packages, conditionally installs AMD64-only packages, copies `golangci-lint`, downloads architecture-specific MinIO and gRPC health probe binaries, builds libqcow, configures Python/pip and tox dependencies, clones dep-versions and checks out a matching tag when present, builds liblonghorn and TGT from dep-versions scripts, pre-warms integration tox, builds longhorn-instance-manager, installs Docker buildx, copies the repo, and sets entrypoint/CMD. Later stages run `scripts/build`, `scripts/validate`, or `scripts/test`, then scratch stages export binaries and coverage/validation markers.

### State, Persistence, And Dependencies
The image build downloads packages and source archives from SUSE/openSUSE, MinIO, AWS S3, GitHub, and dep-versions repositories. Build outputs are binaries under `bin/`, `coverage.out`, and `/validate.done` copied into scratch artifact stages.

### Integration Points
`Makefile` targets build this Dockerfile's named stages. GitHub Actions use the Dockerfile through `make ci`, `make integration-test`, and package/image workflows. Native dependencies support Longhorn engine features including TGT/iSCSI, qcow, RDMA libraries, qemu tools, filesystem utilities, and integration tests.

### Risks
Many external downloads are not checksum-pinned beyond the base image and syntax image digests. `SRC_BRANCH` default is master and dep-versions branch/tag resolution affects native dependency versions. The `ln -sf ... &` line backgrounds the first symlink command, which is unusual and can race with the subsequent pip command. Building instance-manager from its master branch can introduce drift. Privileged/runtime assumptions are deferred to integration tests.

### Test Signals
Signals include successful multi-arch base build, libqcow/liblonghorn/TGT build success, tox environment creation, instance-manager build, `scripts/build`, `scripts/validate`, `scripts/test`, artifact export contents, and image package compatibility.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/Dockerfile -->
