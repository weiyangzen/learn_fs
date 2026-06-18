<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/config_unix.go -->
# sources/cloud-native/containerd/core/remotes/docker/config/config_unix.go

Purpose: Unix host directory search layout for Docker registry `certs.d`/`hosts.toml` configuration.

Important APIs/types/functions: `hostPaths(root, host)` returns candidate directories.

Control flow: converts a host with port through `hostDirectory` (`host:5000` to `host_5000_`) and, when that differs, checks it first. Then checks the literal host directory and `_default`.

State and persistence: read-only path construction; actual filesystem probing is in `HostDirFromRoot`.

Dependencies and integration points: used by `hosts.go` to locate host-specific registry config on non-Windows platforms.

Risks: both sanitized and literal forms may exist; first match wins. IPv6/colon behavior relies on `hostDirectory`.

Test signals: `hosts_test.go` and resolver tests exercise host directory lookup through `HostDirFromRoot`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/config_unix.go -->
