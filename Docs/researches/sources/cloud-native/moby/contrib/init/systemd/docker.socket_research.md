# sources/cloud-native/moby/contrib/init/systemd/docker.socket

## Purpose
Defines the systemd socket unit for Docker API socket activation.

## APIs, Types, And Functions
The socket listens on `/run/docker.sock`, sets mode `0660`, owner `root`, and group `docker`, and installs into `sockets.target`.

## Control Flow, State, And Integration
Systemd creates and owns the Unix socket before dockerd starts. The service unit consumes it via `-H fd://`. Persistent state is the enabled socket unit and socket filesystem node.

## Risks And Test Signals
Risks include incorrect socket path on systems where `/var/run` is not `/run`, group permission exposure, and service/socket mismatch. Integration is with Docker CLI access and systemd socket activation.
