# sources/cloud-native/fuse-overlayfs/tests/alpine.sh

## Purpose
`tests/alpine.sh` builds the project Alpine container image and runs the unlink test inside it, validating behavior in an Alpine/musl container environment.

## Important APIs, Types, And Functions
The script selects `docker` or `podman`, builds `../Containerfile.alpine` as `fuse-overlayfs:alpine`, then runs the image privileged with `/unlink.sh` mounted from the test directory and `EXPECT_UMOUNT_STATUS=1`.

## Control Flow
It changes to the test directory, enables shell tracing/errors, detects a container runtime, builds the image from the repository root context, and runs the test entrypoint in `/tmp`.

## State And Persistence
Persistent host state is limited to the local container image tag and any runtime build cache. The container run is `--rm`; test filesystem state is inside the container except the mounted unlink script.

## Dependencies And Integration Points
Depends on Docker or Podman, privileged container execution, `Containerfile.alpine`, and `tests/unlink.sh`. It validates packaging/runtime compatibility rather than a narrow Rust function.

## Risks
Requires privileged container support and network/package availability during image build. Runtime choice changes behavior between Docker and Podman. Failures can be environmental rather than code regressions.

## Test Signals
Pass means the Alpine image builds and the unlink/umount scenario completes with the expected status. It indirectly exercises mount, unlink, and cleanup behavior in a distribution-specific environment.
