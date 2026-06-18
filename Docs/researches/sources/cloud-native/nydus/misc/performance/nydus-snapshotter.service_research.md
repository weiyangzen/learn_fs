<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/nydus-snapshotter.service -->
# sources/cloud-native/nydus/misc/performance/nydus-snapshotter.service

## Purpose

This systemd unit starts the containerd Nydus snapshotter gRPC service for performance tests.

## Important APIs, Types, and Functions

The unit describes service ordering after network and before containerd, sets `HOME=/root`, runs `/usr/local/bin/containerd-nydus-grpc --config /etc/nydus/config.toml`, restarts always with one-second delay, uses `KillMode=process`, and strongly lowers OOM score.

## Control Flow

Systemd starts the process as a simple service and restarts it on exit. Containerd can then connect to the configured socket.

## State and Persistence Behavior

Logs go to journald. Runtime state is managed by the snapshotter config and process.

## Dependencies and Integration Points

It is installed by `misc/prepare.sh` and paired with `containerd_config.toml` proxy plugin settings.

## Risks and Test Signals

`Before=containerd.service` only matters if dependencies/order are used correctly. `OOMScoreAdjust=-999` protects the process strongly and may be inappropriate outside controlled performance tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/nydus-snapshotter.service -->
