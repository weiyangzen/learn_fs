# sources/cloud-native/moby/daemon/daemon_linux.go

## Purpose
Implements Linux-only daemon helpers for plugin exec-root selection, stale mount cleanup, `resolv.conf` defaulting, interface address lookup, recursive read-only mount support detection, and rootless network namespace execution.

## Important APIs, Types, And Functions
- `getPluginExecRoot` returns `/run/docker/plugins` to avoid Unix socket path-length issues.
- `cleanupMountsByID`, `cleanupMountsFromReaderByID`, `cleanupMounts`, `getCleanPatterns`, and `shouldUnmountRoot` remove stale container and daemon-root mounts.
- `setupResolvConf` selects the libnetwork-aware resolver path when unset.
- `ifaceAddrs` reads addresses from a named link through libnetwork netlink handles.
- `kernelSupportsRecursivelyReadOnly` and `supportsRecursivelyReadOnly` validate kernel and OCI runtime support for recursive read-only mounts.
- `runInNetNS` executes a function inside RootlessKit's detached network namespace when present.

## Control Flow
Mount cleanup scans `/proc/self/mountinfo`, limits matches to `daemon.root`, matches known container mount patterns or a specific mount ID, and calls an injected unmount function. General cleanup also conditionally unmounts the daemon root if it was made shared by daemon startup and the unmount marker exists. Recursive read-only support probes by mounting a temporary tmpfs and calling `mount_setattr` with `AT_RECURSIVE`, caching the result once.

## State And Persistence
Can unmount container shm/rootfs mounts and the daemon root bind mount, and removes the `unmount-on-shutdown` marker written by Unix root propagation setup. RRO probing creates and unmounts a temporary mount. Resolver setup mutates daemon config.

## Dependencies And Integration Points
Uses `/proc/self/mountinfo`, `moby/sys/mount`, `mountinfo`, libnetwork `resolvconf`, RootlessKit helpers, vishvananda netlink, OCI runtime feature metadata from `configStore.Runtimes`, and Linux `mount_setattr`.

## Risks And Edge Cases
Regex-based cleanup must avoid unmounting unrelated paths, so it checks the daemon root prefix. Root cleanup only unmounts shared root mounts with a marker. RRO support can fail because of older kernels, missing permissions, or runtime feature absence. Rootless netns execution depends on RootlessKit exposing a detached namespace path.

## Test Signals
`daemon_linux_test.go` uses mountinfo fixtures to ensure only expected shm/rootfs mounts are cleaned, validates Linux rejection of Hyper-V isolation, verifies daemon-root unmount marker behavior, and tests `ifaceAddrs` in an isolated network namespace.
