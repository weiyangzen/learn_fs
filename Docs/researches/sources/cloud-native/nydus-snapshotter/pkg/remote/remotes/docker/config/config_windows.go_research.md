# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/config_windows.go

## Purpose
Provides Windows-specific host directory and TLS root-pool behavior for registry host configuration.

## Important APIs, Types, And Functions
`hostPaths(root, host)` produces Windows-compatible paths by removing colons after Docker-style port mangling. `rootSystemPool` returns a new empty `x509.CertPool`.

## Control Flow
The Windows implementation tries a colon-free port directory, a colon-free literal host directory, and `_default`. TLS CA material is then populated from configured cert files instead of the platform system pool.

## State And Persistence
No runtime state. It only participates in filesystem lookup and TLS setup.

## Dependencies And Integration Points
Compiled only on Windows and used by `HostDirFromRoot` plus `ConfigureHosts` in `hosts.go`.

## Risks And Edge Cases
The empty root pool means configured CA files are especially important for private registries. Colon-stripping can make host-directory names differ from Unix, so cross-platform config layouts must account for that.

## Test Signals
No dedicated Windows-only test is present in this subset; behavior is structurally parallel to Unix and validated indirectly by shared host parser tests where platform path conversion applies.
