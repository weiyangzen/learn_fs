<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/plugincore/plugin.go -->
# sources/cloud-native/stargz-snapshotter/service/plugincore/plugin.go

## Purpose
Contains the containerd plugin registration and initialization logic for the `stargz` snapshotter.

## Important APIs, Types, And Functions
- `Config` embeds `service.Config` and adds `RootPath`, CRI keychain proxy socket path, and CRI-compatible registry config.
- `RegisterPlugin` registers a `SnapshotPlugin` with ID `stargz`.
- Init function sets platforms, resolves root, configures Docker/kube/CRI credentials, optionally serves a CRI image-service proxy socket, and constructs the snapshotter service.
- `newCRIConn` dials a containerd/CRI Unix socket with default message sizes and bounded gRPC backoff.

## Control Flow
During plugin init, the config is type-checked, root is selected from containerd properties or override, credentials are assembled, the optional CRI proxy is started on a Unix socket after removing any stale path, and `service.NewStargzSnapshotterService` is called with CRI-style registry hosts.

## State And Persistence
Exports the selected root through plugin metadata. If CRI keychain proxy is enabled, it creates/removes a Unix socket path and runs a gRPC server goroutine. Snapshotter and filesystem state live under the selected root.

## Dependencies And Integration Points
Integrates containerd plugin registry, CRI API, gRPC, Docker config, kubeconfig keychain, CRI keychain, resolver CRI config, and the service constructor.

## Risks And Edge Cases
CRI keychain requires both enable flag and proxy socket path. Stale socket removal is destructive to that path. If backend CRI address is absent, init fails. Plugin init starts goroutines whose lifecycle follows containerd.

## Test Signals
Signals include successful plugin registration, root export, optional keychain setup, Unix socket creation, backend CRI dial options, and snapshotter construction with configured registry hosts.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/plugincore/plugin.go -->
