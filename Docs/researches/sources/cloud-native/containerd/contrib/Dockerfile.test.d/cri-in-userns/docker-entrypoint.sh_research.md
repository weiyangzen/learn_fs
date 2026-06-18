<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/cri-in-userns/docker-entrypoint.sh -->
# sources/cloud-native/containerd/contrib/Dockerfile.test.d/cri-in-userns/docker-entrypoint.sh

## Purpose
Entrypoint for CRI tests running containerd inside a user namespace test image.

## Important APIs, Types, And Functions
Shell script with setup steps for containerd, rootless/userns environment, and test command execution.

## Control Flow
Validates environment, prepares directories/config, starts required services/daemons, then executes the provided test workflow.

## State And Persistence
Mutates container filesystem paths, daemon sockets, runtime directories, and process tree inside the test container.

## Dependencies And Integration Points
bash, containerd, CRI tooling, user namespace support, mounted cgroup/runtime directories.

## Risks And Test Signals
Requires privileged/userns-capable environment; cleanup depends on container lifecycle. Test signal is the CRI-in-userns job. Source size reviewed: 63 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/cri-in-userns/docker-entrypoint.sh -->
