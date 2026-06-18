# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/hosts.go

## Purpose
Builds a `docker.RegistryHosts` function from Docker/containerd host configuration. It supports `hosts.toml`, Docker cert-directory fallback, custom credentials, default TLS/client setup, headers, mirrors, capabilities, and Docker Hub/default-host normalization.

## Important APIs, Types, And Functions
`HostOptions`, `ConfigureHosts`, `HostDirFromRoot`, `loadHostDir`, `parseHostsFile`, `parseHostConfig`, `loadCertFiles`, and helper conversion functions form the API. Internal `hostConfig` and `hostFileConfig` model parsed registry endpoints.

## Control Flow
`ConfigureHosts` resolves a host directory, loads `hosts.toml` or cert files, appends a default host if needed, constructs a default transport/client, and attaches authorizers. For each host, it applies scheme/host/path/capabilities/header and clones the transport when host-specific TLS material is needed. `parseHostsFile` preserves TOML host order using line positions, parses mirror entries first, and appends root `server` config last. `parseHostConfig` normalizes missing schemes to HTTPS, appends `/v2` unless `override_path` is set, interprets capability strings, converts relative cert paths, and validates header/client shapes.

## State And Persistence
Configuration is read from the filesystem on each host lookup. Runtime state is held in created HTTP clients, TLS configs, and authorizers, with no file writes.

## Dependencies And Integration Points
Integrates with `docker.RegistryHost`, `docker.NewDockerAuthorizer`, containerd logging, `errdefs.ErrNotFound`, Go TLS/http transports, and `go-toml`. Host capabilities directly affect resolver, fetcher, pusher, and referrer selection.

## Risks And Edge Cases
`hosts.toml` parse failure silently falls back to cert files after logging, which can hide misconfiguration. TLS config cloning mutates a cloned transport but starts from a shared default config pointer. `skip_verify` is intentionally supported but security-sensitive. Empty configured host lists mean no endpoints, while nil host lists mean synthesize defaults.

## Test Signals
`hosts_test.go` validates Docker Hub defaults, ordered TOML host parsing, path/override behavior, capabilities, headers, CA/client cert variants, and legacy cert-directory fallback.
