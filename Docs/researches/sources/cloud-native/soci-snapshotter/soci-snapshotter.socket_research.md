# sources/cloud-native/soci-snapshotter/soci-snapshotter.socket

Purpose: this systemd socket unit defines the Unix socket used to activate and connect to the SOCI snapshotter gRPC daemon.

Important fields: `[Socket]` listens on `/run/soci-snapshotter-grpc/soci-snapshotter-grpc.sock` and sets `SocketMode=0660`. `[Install]` enables it under `sockets.target`.

Control flow and integration: when a client connects to the socket, systemd can activate the matching service, which uses `--address fd://` to receive the socket descriptor. Containerd configuration must point to the same path for the proxy snapshotter.

State and persistence: the socket path is under `/run`, so it is runtime-only. Permissions allow owner/group read-write access; group ownership is not specified here and will be determined by systemd defaults or packaging overrides.

Dependencies: paired with `soci-snapshotter.service` by systemd naming conventions. Requires systemd socket activation support in the daemon.

Risks: lack of explicit `SocketUser`/`SocketGroup` means access control depends on unit manager defaults. Containerd must have permission to connect to the socket. The unit itself does not create persistent directories; systemd normally manages runtime socket parent creation, but packaging should verify the path.

Test signals: no direct tests in this subset. Operational validation should check socket creation, mode, daemon activation, and containerd access.
