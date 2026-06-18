<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/resolver/cri.go -->
# sources/cloud-native/stargz-snapshotter/service/resolver/cri.go

## Purpose
Builds registry host configuration from containerd CRI-compatible registry settings, including mirrors, host config directories, TLS files, and auth parsing.

## Important APIs, Types, And Functions
- `Registry`, `Mirror`, `RegistryConfig`, `AuthConfig`, and `TLSConfig` mirror CRI registry config shapes.
- `RegistryHostsFromCRIConfig` returns `source.RegistryHosts` either from `config_path` hosts files or deprecated mirrors/configs.
- `hostDirFromRoots`, `toRuntimeAuthConfig`, `getTLSConfig`, `defaultScheme`, `addDefaultScheme`, `registryEndpoints`, and `ParseAuth` implement CRI-compatible helpers.

## Control Flow
If `ConfigPath` has entries, host files drive configuration and inline auth is added as a credential fallback. Otherwise endpoints are built from host-specific or wildcard mirrors plus the default registry endpoint, retryable HTTP clients are configured with optional TLS, authorizers are attached, and pull/resolve hosts are returned.

## State And Persistence
No state is persisted. TLS and hosts directory files are read when registry hosts are configured or used.

## Dependencies And Integration Points
Depends on containerd Docker resolver/config helpers, CRI runtime auth types, retryable HTTP, TLS/x509, and stargz `source.RegistryHosts`. Used by `plugincore` for CRI-compatible plugin registry configuration.

## Risks And Edge Cases
`ConfigPath` causes mirror/TLS fields to be ignored except inline auth fallback. TLS cert/key must be provided as a pair. Base64 auth parsing trims NULs from passwords. Endpoint defaulting must handle localhost and Docker Hub default hosts correctly.

## Test Signals
Signals include correct endpoint ordering, wildcard mirror fallback, default endpoint insertion, HTTP scheme for localhost, TLS file load errors, host directory lookup across roots, and auth parsing for username/password, identity token, and base64 auth.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/resolver/cri.go -->
