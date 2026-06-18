# sources/cloud-native/moby/daemon/container_operations_unix.go

## Purpose
Provides Linux/FreeBSD implementations for container operation helpers: legacy links, IPC namespace setup, tmpfs/secrets/config mounts, direct process killing, sandbox path setup, and platform feature flags for default networking.

## Important APIs, Types, And Functions
- `setupLinkedContainers` and `addLegacyLinks` manage deprecated bridge link environment variables and `/etc/hosts` entries.
- `getIPCContainer`, `getPIDContainer`, `setupContainerDirs`, `setupIPCDirs`, `setupSecretDir`, `createSecretsDir`, `remountSecretDir`, and `cleanupSecretDir` prepare IPC, tmpfs, secrets, and configs.
- `killProcessDirectly` sends SIGKILL and detects missing/zombie processes.
- `enableIPOnPredefinedNetwork` and `serviceDiscoveryOnDefaultNetwork` return Linux/FreeBSD defaults.
- `buildSandboxPlatformOptions` selects origin hosts/resolv.conf paths and sets container `HostsPath`/`ResolvConfPath`.
- `initializeNetworkingPaths` shares network namespace file paths for `--network container:`.

## Control Flow
Container setup creates mount roots, configures IPC based on host/container/private/shareable modes, writes secrets/config data into a tmpfs, fixes ownership under user namespace remapping, remounts secrets read-only with EBUSY retries, and returns mounts for the OCI spec. Networking setup chooses host/user-defined/default DNS behavior, then writes libnetwork sandbox path options. Legacy link setup updates hosts files before default-network endpoint joins and propagates parent/child link labels.

## State And Persistence
Mutates container paths such as `ShmPath`, `HostsPath`, `ResolvConfPath`, and secret/config directories under the container root. It creates and unmounts tmpfs mounts, writes secret/config payload files, relabels them for SELinux, and can update hosts entries inside existing sandboxes.

## Dependencies And Integration Points
Depends on Unix syscalls, `moby/sys/mount`, idmapping/user helpers, SELinux labels, libnetwork bridge/link support, daemon link index, process utilities, and daemon config. It integrates with container start, legacy link behavior, secret/config injection, and runtime kill fallback paths.

## Risks And Edge Cases
Secret tmpfs remount races are handled with retries, but failures can leave start failures and require cleanup. IPC donor validation must reject non-running/restarting/non-shareable containers. Direct SIGKILL cannot kill zombies and returns a system error with guidance. Environment-controlled legacy link variables retain deprecated behavior and can affect container environments.

## Test Signals
No direct tests in this subset for most helpers. `container_unix_test.go` covers host-network port warning behavior in nearby validation. Broader daemon integration tests should cover IPC modes, secrets/configs, links, DNS file generation, and process kill behavior.
