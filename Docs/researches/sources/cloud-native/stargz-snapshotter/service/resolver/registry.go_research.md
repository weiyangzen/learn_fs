<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/resolver/registry.go -->
# sources/cloud-native/stargz-snapshotter/service/resolver/registry.go

## Purpose
Defines stargz snapshotter's native registry resolver configuration and converts it into containerd Docker registry hosts.

## Important APIs, Types, And Functions
- `Config` maps registry hostnames to `HostConfig` and a global request timeout.
- `MirrorConfig` describes mirror host, insecure mode, per-host timeout, and extra headers.
- `Credential` is a `(host, ref) -> username, secret` callback.
- `RegistryHostsFromConfig` returns a `source.RegistryHosts` closure.
- `multiCredsFuncs` chains credential providers by first non-empty result.
- `makeStringSlice` validates and converts header array values.

## Control Flow
For a requested reference, the closure appends configured mirrors and the original host, builds a retryable client with timeout semantics, converts headers, attaches a Docker authorizer, switches scheme to HTTP for localhost/insecure mirrors, rewrites `docker.io` to `registry-1.docker.io`, and returns pull/resolve hosts.

## State And Persistence
No persistent state. HTTP clients and headers are created per registry-host resolution.

## Dependencies And Integration Points
Used by `service.NewFileSystem` unless custom registry hosts are supplied. It connects keychain credentials to containerd's Docker resolver.

## Risks And Edge Cases
Negative timeout disables HTTP timeout. Header values must be strings or arrays of strings. Credential provider order matters. Mirror host strings are not URL parsed here, so they must be compatible with containerd `docker.RegistryHost` expectations.

## Test Signals
Expected tests cover timeout defaults/overrides/no-timeout, HTTP selection for insecure/local mirrors, Docker Hub rewrite, header conversion failures, and credential chaining precedence.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/resolver/registry.go -->
