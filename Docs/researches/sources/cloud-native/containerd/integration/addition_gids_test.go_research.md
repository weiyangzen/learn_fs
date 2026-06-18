# sources/cloud-native/containerd/integration/addition_gids_test.go

## Purpose
This Linux integration test validates CRI supplemental group handling against container-visible `id` output.

## Important APIs, Types, and Functions
`TestAdditionalGids` defines cases using `WithSupplementalGroups`, `WithRunAsUser`, `WithRunAsGroup`, and `WithRunAsUsername`. It uses `PodSandboxConfigWithCleanup`, `ContainerConfig`, runtime service create/start/status calls, and log inspection.

## Control Flow
The test ensures the BusyBox image exists, creates a sandbox with a log directory, creates a container running `id`, waits until it exits, reads its log file, and checks the expected group list.

## State and Persistence
State is created in CRI sandbox/container services and a temporary pod log directory. Container logs are the assertion source.

## Dependencies and Integration Points
Depends on CRI runtime service helpers, integration images, Kubernetes CRI API types, and Linux build tag.

## Risks
Expected group names depend on image `/etc/group` contents. Timing depends on container exit and log flush. It is Linux-only.

## Test Signals
Covers default groups, supplemental groups, numeric users/groups, username resolution, and combined username plus supplemental group behavior.
