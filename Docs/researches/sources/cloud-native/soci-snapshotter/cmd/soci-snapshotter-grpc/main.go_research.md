## sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/main.go

Purpose: main daemon for the SOCI snapshotter gRPC service.

Important APIs/types/functions: `buildApp`, `serve`, `getMetadataStore`, `getCriConn`, `listen`, `listenUnix`, and `listenFd`.

Control flow: CLI/env flags set socket, config, log level, and root. The action configures logging, loads config, checks snapshotter support, registers namespace interceptors, builds credential keychains, opens metadata DB, creates `service.NewSociSnapshotterService`, registers containerd snapshots gRPC, starts optional metrics/debug endpoints, listens on Unix or systemd fd, handles signals, and conditionally closes snapshotter on SIGINT.

State and persistence: creates root directories, socket files, optional metrics socket, and Bolt metadata DB at `root/metadata.db`.

Dependencies and integration: containerd snapshotservice API, gRPC, systemd activation/notify, Docker/kube/CRI keychains, resolver, metadata, service, fs, and config packages.

Risks and test signals: fatal logging inside command action complicates library-style testing; metrics/debug goroutines report through one error channel and can stop serve. Tests cover env overrides for config path and log level, not full daemon serving.
