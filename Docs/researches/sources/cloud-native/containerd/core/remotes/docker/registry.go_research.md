<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/registry.go -->
# sources/cloud-native/containerd/core/remotes/docker/registry.go

## Purpose
Defines registry host configuration, trust capabilities, default registry construction, localhost matching, and default HTTP transport settings for Docker remotes.

## Important APIs, Types, And Functions
- `HostCapabilities` bitmask values: pull, resolve, push, and referrers.
- `RegistryHost` carries HTTP client, authorizer, host, scheme, path, capabilities, and headers.
- `RegistryHosts` maps a namespace host to ordered registry hosts/mirrors.
- `Registries` chains multiple `RegistryHosts` providers and returns the first non-empty result.
- `RegistryOpt` helpers configure authorizer, plain HTTP match, host translation, and client.
- `ConfigureDefaultRegistries` builds default `/v2` HTTPS hosts, including Docker Hub translation to `registry-1.docker.io`.
- `MatchAllHosts`, `MatchLocalhost`, and `DefaultHTTPTransport` provide common defaults.

## Control Flow
Callers pass `ResolverOptions.Hosts` or let `NewResolver` call `ConfigureDefaultRegistries`. Host capabilities determine which hosts are trusted for resolve, pull, push, or referrers. `RegistryHost.isProxy` detects when `ns=` should be appended for proxy/mirror requests.

## State And Persistence
No persistent state. Each resolver holds host configuration returned from the provided function.

## Dependencies And Integration Points
Used by resolver, fetcher, pusher, and referrers host filtering. The transport config feeds HTTP clients and fallback wrappers. Capability comments encode the trust model: mirrors may be pull-only and should not resolve mutable names unless trusted.

## Risks And Edge Cases
`MatchLocalhost` intentionally does not support odd IP encodings and returns errors for malformed host:port forms. Misconfigured capabilities can create security issues, such as resolving tags through an untrusted mirror or pushing to a mirror.

## Test Signals
`registry_test.go` covers bitmask inclusion and localhost matching for IPv4, IPv6, host:port, invalid IPs, and non-local hosts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/registry.go -->
