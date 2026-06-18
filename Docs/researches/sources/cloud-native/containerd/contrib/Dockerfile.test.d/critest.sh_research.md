<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/critest.sh -->
# sources/cloud-native/containerd/contrib/Dockerfile.test.d/critest.sh

## Purpose
Runs CRI conformance tests inside Dockerfile.test environment under a generated systemd service.

## Important APIs, Types, And Functions
Shell functions `echo_exit_code` and `start` plus embedded service unit content.

## Control Flow
Writes/enables a service for docker-entrypoint, starts it, tails or reports logs, and exits with captured status.

## State And Persistence
Creates systemd unit files and test logs inside the image/container.

## Dependencies And Integration Points
bash, systemd, crictl/critest environment, docker-entrypoint script.

## Risks And Test Signals
Assumes systemd is available in the test container. Failures require log inspection. Source size reviewed: 47 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/critest.sh -->
