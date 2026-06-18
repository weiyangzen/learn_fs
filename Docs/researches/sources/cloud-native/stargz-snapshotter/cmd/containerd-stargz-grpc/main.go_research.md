# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/main.go

Purpose: Main daemon for the containerd stargz snapshotter gRPC service. It loads config, configures filesystem/keychain/FUSE manager modes, serves snapshotter APIs, metrics, debug endpoints, and systemd notifications.

Important APIs/types: `snapshotterConfig`, `FuseManagerConfig`, `main`, and `serve`. Flags configure address, config path, log level, root, and version.

Control flow: `main` parses flags, configures logging, loads TOML, validates support, creates a gRPC server, forces direct mode when passthrough is enabled, configures keychains, then branches between detached FUSE manager mode and in-process service mode. In FUSE manager mode it starts or connects to manager and creates a snapshotter with restoration behavior based on whether the manager was newly started. Otherwise it configures CRI keychain socket if needed, filesystem options, and `service.NewStargzSnapshotterService`.

State and persistence: Uses root directories for snapshotter data, optional FUSE manager DB/log, and optional metadata DB. Removes listening sockets before binding.

Dependencies and integration: Integrates containerd snapshot service, stargz service, keychains, fsopts, fusemanager, bbolt, metrics, debug server, systemd notify, and Unix signals.

Risks: Many fatal configuration paths terminate the process. Cleanup semantics differ on SIGINT/SIGTERM and FUSE manager mode. Socket removal can remove stale or unexpected filesystem entries at configured paths.

Test signals: No direct tests; daemon-level integration tests would be needed.
