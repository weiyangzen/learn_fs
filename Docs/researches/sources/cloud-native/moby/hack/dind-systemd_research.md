# sources/cloud-native/moby/hack/dind-systemd

## Purpose
Systemd-based Docker-in-Docker entrypoint for privileged test containers.

## Important APIs and Types
Writes systemd unit files for `docker-entrypoint.target`, `docker-entrypoint.service`, and optional firewalld log collection. Uses `container=docker`, `FIREWALLD`, and quoted command storage.

## Control Flow, State, and Persistence
The script requires a command and TTY, mounts `/tmp`, makes root propagation shared, mounts securityfs when possible, optionally configures firewalld trusted zone and log collection, persists environment and command under `/etc`, creates a systemd service that runs the command and exits systemd with the command's status, masks/unmasks selected services, then execs systemd.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on privileged container capabilities, systemd binaries, writable `/etc/systemd`, and optional firewalld. Risks include command quoting bugs, service exit-status translation, mutable system configuration, and privileged securityfs/mount propagation. CI jobs needing systemd semantics and firewall behavior are the primary signal.
