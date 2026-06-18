# sources/cloud-native/containerd/cmd/ctr/commands/namespaces/namespaces_other.go

Purpose: provides non-Linux namespace delete option behavior.

Important APIs/functions: `deleteOpts()` returns nil.

Control flow: namespace remove command can call it unconditionally across platforms.

State and persistence: none beyond normal namespace deletion in caller.

Dependencies/integration: selected by `!linux`.

Risks: `--cgroup` has no platform-specific effect outside Linux.

Test signals: no local tests.
