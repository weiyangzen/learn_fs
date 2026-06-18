# sources/cloud-native/soci-snapshotter/service/resolver/cri.go

Purpose: CRI-compatible registry host configuration and auth parsing for SOCI resolver. It ports containerd CRI registry config behavior to build `docker.RegistryHost` lists with mirrors, TLS, auth, and config-path support.

Important APIs/types/functions: config structs `Registry`, `Mirror`, `RegistryConfig`, `AuthConfig`, and `TLSConfig`. Main builder `RegistryHostsFromCRIConfig` returns `RegistryHosts`. Helpers include `hostDirFromRoots`, `toRuntimeAuthConfig`, `getTLSConfig`, `addDefaultScheme`, `registryEndpoints`, `ParseAlphaAuth`, and `ParseAuth`.

Control flow: if `ConfigPath` is set, host configuration delegates to containerd `ConfigureHosts` with a multi-credential callback combining external keychains and static auth config. Otherwise, for each mirror/default endpoint, it parses URL, applies registry TLS config to a retryable client's transport, creates a Docker authorizer with credentials, defaults path to `/v2`, and returns pull/resolve-capable registry hosts. Endpoint resolution applies host-specific or wildcard mirrors, adds default schemes, and appends Docker default host if not already present.

State and persistence: no persistent state; reads CA/cert/key files while constructing TLS config.

Dependencies/integration points: used by plugin and service resolver setup. Integrates containerd remotes/docker, Docker config host-dir support, CRI runtime `AuthConfig`, retryablehttp, TLS/x509, filesystem certificate files, and project credential chain helpers.

Risks: mirror/config behavior is copied from older containerd CRI versions and may drift from current containerd semantics. `TLSConfig.InsecureSkipVerify` is supported and can weaken verification. Static auth in `config.Configs[host]` is only appended in ConfigPath mode; non-ConfigPath mode relies on passed credential functions. Auth parsing trims NUL bytes from decoded password.

Test signals: this file has no direct tests in the listed set; auth parsing and registry behavior need coverage through resolver/plugin integration tests.
