# sources/cloud-native/nydus-snapshotter/misc/snapshotter/config.toml

Purpose: default packaged snapshotter configuration for fusedev mode.

Structure: version 1, standard root/socket, dedicated daemon mode, system controller enabled, nydusd paths/config, fusedev driver, failover/recover policy, cgroup memory config, log rotation, metrics, remote auth/mirrors, snapshot options, cache manager, signature validation, and experimental stargz/referrer/index/backend-source/tarfs toggles.

State/dependencies: read by main binary and tests; points to `/etc/nydus` and `/run/containerd-nydus` paths.

Integration points: systemd units, Dockerfile, Makefile install, config tests.

Risks/tests: config tests assert much of this file exactly. Operational risks include root path length, auth mode exclusivity, and feature toggles requiring matching runtime support.
