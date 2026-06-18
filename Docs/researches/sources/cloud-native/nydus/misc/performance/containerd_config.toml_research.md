<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/containerd_config.toml -->
# sources/cloud-native/nydus/misc/performance/containerd_config.toml

## Purpose

This containerd config enables the Nydus snapshotter as the CRI and transfer unpack snapshotter for performance testing.

## Important APIs, Types, and Functions

It sets containerd version/root/state/debug level, configures CRI `snapshotter = "nydus"`, keeps snapshot annotations, disables discard of unpacked layers, adds local transfer unpack config for linux, and defines proxy plugin `nydus` at `/run/containerd-nydus/containerd-nydus-grpc.sock`.

## Control Flow

Containerd reads this file at startup and routes snapshot operations to the external Nydus proxy plugin. Export `enable_remote_snapshot_annotations` allows remote snapshot metadata propagation.

## State and Persistence Behavior

Containerd state lives under `/var/lib/containerd` and `/run/containerd`. Snapshotter state is external to the proxy plugin address.

## Dependencies and Integration Points

It integrates with `nydus-snapshotter.service`, `snapshotter_config.toml`, and containerd CRI.

## Risks and Test Signals

The file appears to concatenate the proxy export line and service unit text if copied incorrectly in surrounding output, but the source file itself is a short TOML. Static socket paths and debug logging are test-focused.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/containerd_config.toml -->
