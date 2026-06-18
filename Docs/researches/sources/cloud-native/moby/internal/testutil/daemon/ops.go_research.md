# sources/cloud-native/moby/internal/testutil/daemon/ops.go

## Purpose
Defines functional options for configuring test daemon instances.

## Important APIs, Types, And Functions
- `Option func(*Daemon)` is the configuration primitive.
- Options configure containerd socket, user namespace remap, cgroup namespace mode, test logger, experimental/init flags, dockerd binary, Swarm ports/listen address/iptables/default address pools/data path port, environment-derived settings, storage driver, rootless user, OOM score, extra environment variables, and resolv.conf content.

## Control Flow
Each option returns a closure that mutates fields on a `Daemon` before startup. `WithUserNsRemap` contains special storage-driver compatibility logic for `DOCKER_GRAPHDRIVER=overlayfs`. `WithRootlessUser` panics if the named user cannot be found.

## State And Persistence
Options only mutate the in-memory `Daemon` configuration. Some options later cause persistent effects during daemon construction/startup, such as writing a resolv.conf override or changing rootless ownership.

## Dependencies And Integration Points
Integrates test environment metadata, OS user lookup, netip prefixes, and daemon startup argument assembly in `daemon.go`.

## Risks And Edge Cases
`WithRootlessUser` panics instead of returning an error. `WithEnvVars` appends variables and can create duplicates unless later replaced by `SetEnvVar`. User namespace storage-driver workaround is tied to a documented issue.

## Test Signals
Configuration is validated indirectly by tests that start daemons with these options and observe expected behavior, such as Swarm ports, experimental mode, init mode, or custom resolv.conf.
