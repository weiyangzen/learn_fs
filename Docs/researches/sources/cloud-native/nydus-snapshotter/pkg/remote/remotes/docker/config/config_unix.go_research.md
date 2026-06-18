# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/config_unix.go

## Purpose
Provides Unix, non-Windows host configuration helpers for Docker registry host directory discovery and system certificate pool loading.

## Important APIs, Types, And Functions
`hostPaths(root, host)` returns candidate registry config directories, including Docker's port-mangled directory form and `_default`. `rootSystemPool` delegates to `x509.SystemCertPool`.

## Control Flow
`HostDirFromRoot` in `hosts.go` calls `hostPaths` in order. For `host:port`, `hostDirectory` turns it into `host_port_`, and this Unix implementation tries that directory before the literal host and `_default`.

## State And Persistence
No state is held. It only maps filesystem paths and returns the OS certificate pool used by TLS setup.

## Dependencies And Integration Points
Used by `ConfigureHosts` when loading `hosts.toml`, `.crt`, `.cert`, and `.key` files from Docker-style cert directories. It is selected by the `!windows` build tag.

## Risks And Edge Cases
Path ordering determines which cert directory wins. System certificate loading can fail depending on OS trust store availability and is surfaced to host configuration.

## Test Signals
Covered indirectly by `hosts_test.go` on Unix platforms through default host directory and certificate-file parsing behavior.
