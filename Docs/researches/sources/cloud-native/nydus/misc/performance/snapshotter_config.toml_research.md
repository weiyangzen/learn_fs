<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/snapshotter_config.toml -->
# sources/cloud-native/nydus/misc/performance/snapshotter_config.toml

## Purpose

This TOML configures the containerd Nydus snapshotter for performance and takeover tests.

## Important APIs, Types, and Functions

It sets root/address, dedicated daemon mode, cleanup policy, system/debug endpoints, daemon paths/config, fs driver, recover policy, thread count, log rotation, optional cgroup memory limit, metrics address, remote auth controls, snapshot flags, cache manager behavior, signature validation, and experimental stargz/referrers/backend-source/tarfs settings.

## Control Flow

The snapshotter reads this config at service startup. `recover_policy` controls daemon failure handling and is modified by `prepare.sh` for takeover tests. The daemon section points to nydusd/nydus-image binaries and the nydusd config.

## State and Persistence Behavior

Snapshotter state is under `/var/lib/containerd/io.containerd.snapshotter.v1.nydus`, sockets under `/run/containerd-nydus`, logs rotate according to configured caps, and metrics bind on `:9110`.

## Dependencies and Integration Points

It integrates with containerd proxy plugin, systemd unit, nydusd binary/config, nydus-image, cache manager, Kubernetes/CRI auth options, and experimental tarfs support.

## Risks and Test Signals

Dedicated mode, cgroups, metrics, and debug endpoints affect host resources. Several experimental features are disabled by default. Static paths must match installed binaries from `prepare.sh`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/snapshotter_config.toml -->
