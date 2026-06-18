## sources/cloud-native/moby/daemon/internal/libcontainerd/libcontainerd_windows.go

Purpose: Windows constructor shim for the daemon's libcontainerd client abstraction.

Important API: `NewClient(ctx, cli, stateDir, ns, b)` returns a local client when `cli == nil`; otherwise it returns `remote.NewClient`.

Control flow and state: One branch selects `local.NewClient(ctx, b)` for nil containerd clients and remote wrapper for real containerd clients.

Dependencies and integration: Depends on containerd v2 client, internal local and remote libcontainerd implementations, and shared libcontainerd types. Supports Windows daemon modes where no external containerd client is provided.

Risks: Behavior differs from Linux nil-client handling. Callers relying on the local fallback must be Windows-specific. No direct tests in this subset.

Persistence: Client state is managed by local/remote implementations, not this shim.
