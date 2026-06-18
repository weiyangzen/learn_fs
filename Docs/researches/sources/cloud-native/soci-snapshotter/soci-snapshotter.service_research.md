# sources/cloud-native/soci-snapshotter/soci-snapshotter.service

Purpose: this systemd unit starts the SOCI snapshotter gRPC daemon as a containerd-adjacent service.

Important fields: `[Unit]` describes the service, links documentation, starts after `network.target`, and orders before `containerd.service` so containerd can connect to the snapshotter. `[Service]` uses `Type=notify`, executes `/usr/local/bin/soci-snapshotter-grpc --address fd://`, and restarts on failure with a five-second delay. `[Install]` enables it for `multi-user.target`.

Control flow and integration: the `fd://` address implies socket activation from the paired `soci-snapshotter.socket`. With socket activation, systemd owns the Unix socket and passes the file descriptor to the daemon. The ordering before containerd matters because containerd snapshotter plugin configuration expects the socket to be available early.

State and persistence: no direct persistent state is configured here. Runtime state is owned by the daemon's configured root and systemd restart state.

Dependencies: depends on systemd notify support in the daemon and the matching socket unit. It indirectly depends on `/usr/local/bin/soci-snapshotter-grpc` existing and having required privileges for mounts and content operations.

Risks: the service file has no explicit `Requires=` or `Also=` relationship to the socket, so packaging/install configuration must ensure both units are installed and enabled as intended. It also has no hardening settings, environment file, or explicit user, which may be deliberate because snapshotter mount operations need privileges but should be reviewed by packagers.

Test signals: no tests in this subset validate unit installation or socket activation. Manual or integration tests should verify `systemctl enable --now soci-snapshotter.socket` and containerd startup ordering.
