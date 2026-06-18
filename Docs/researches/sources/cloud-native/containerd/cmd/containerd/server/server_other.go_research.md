# sources/cloud-native/containerd/cmd/containerd/server/server_other.go

Purpose: supplies a no-op server process config hook on non-Linux platforms.

Important APIs/functions: `apply(context.Context, *srvconfig.Config) error` returns nil.

Control flow: `server.New()` can call `apply()` unconditionally across platforms.

State and persistence: none.

Dependencies/integration: selected by `!linux`.

Risks: OOM score and cgroup config are ignored outside Linux.

Test signals: no local tests; stub behavior is trivial.
