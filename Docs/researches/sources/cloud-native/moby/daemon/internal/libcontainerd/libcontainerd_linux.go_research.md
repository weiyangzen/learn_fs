## sources/cloud-native/moby/daemon/internal/libcontainerd/libcontainerd_linux.go

Purpose: Linux constructor shim for the daemon's libcontainerd client abstraction.

Important API: `NewClient(ctx, cli, stateDir, ns, b)` returns `remote.NewClient(ctx, cli, stateDir, ns, b)`.

Control flow and state: No branching; Linux always uses the remote containerd client wrapper with the supplied `*containerd.Client`.

Dependencies and integration: Depends on containerd v2 client, daemon internal `remote` libcontainerd implementation, and libcontainerd types. Used by daemon startup code that wants platform-neutral client construction.

Risks: Passing a nil `cli` on Linux is not handled here and is delegated to `remote.NewClient`, unlike Windows which supports a local fallback. No direct tests in this subset.

Persistence: State is owned by remote client implementation, not this shim.
