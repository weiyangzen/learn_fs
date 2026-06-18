# sources/cloud-native/moby/contrib/dockerd-rootless.sh

## Purpose
Launches `dockerd` in rootless mode through RootlessKit with selected network, port, mount, and namespace settings.

## APIs, Types, And Functions
The script exposes environment-driven configuration such as RootlessKit state dir, network driver, MTU, port driver, slirp4netns sandbox/seccomp flags, host loopback policy, and detach-netns mode. `mount_directory` is a key helper for child-context bind mounts.

## Control Flow, State, And Integration
The script validates writable `XDG_RUNTIME_DIR` and `HOME`, prevents setup-tool subcommands from being misrouted, selects available network/port drivers, configures RootlessKit arguments, mounts necessary directories, and execs dockerd in a rootless namespace. Persistent/runtime state lives under the RootlessKit state dir and user Docker data paths.

## Risks And Test Signals
Risks include environment misconfiguration, unavailable helpers, network-driver compatibility, leaked mounts, and security tradeoffs around host loopback or detach-netns. Integration is with RootlessKit, slirp4netns, pasta, vpnkit, gvisor-tap-vsock, and dockerd rootless mode.
