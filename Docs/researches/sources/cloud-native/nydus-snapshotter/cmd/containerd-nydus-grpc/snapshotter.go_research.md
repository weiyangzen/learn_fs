# sources/cloud-native/nydus-snapshotter/cmd/containerd-nydus-grpc/snapshotter.go

Purpose: initialize and serve the snapshotter gRPC service.

Flow: `Start` creates a cancellable context, constructs `snapshot.NewSnapshotter`, installs signal handling, initializes optional kube secret and kubelet credential providers, then calls `Serve`. `Serve` removes stale socket files only if they are sockets, registers the containerd snapshots service, listens on Unix socket, chowns it, optionally adds CRI image proxy auth, and closes snapshotter/listener on stop.

State/dependencies: owns the Unix socket path and snapshotter lifecycle; no durable data beyond socket. Depends on containerd gRPC snapshotservice, auth, signals, snapshot.

Risks/tests: refuses to overwrite non-socket files at the socket path. Listener close is expected to break `rpc.Serve` on shutdown.
