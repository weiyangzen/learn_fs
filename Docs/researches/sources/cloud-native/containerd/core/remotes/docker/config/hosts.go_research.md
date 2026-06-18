<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/hosts.go -->
# sources/cloud-native/containerd/core/remotes/docker/config/hosts.go

Purpose: builds Docker registry host configuration from defaults, `hosts.toml`, Docker-style certificate directories, TLS settings, headers, credentials, and per-host client customization.

Important APIs/types/functions: `UpdateClientFunc`, `hostConfig`, `HostOptions`, `ConfigureHosts`, `updateTLSConfigFromHost`, `HostDirFromRoot`, `hostDirectory`, `loadHostDir`, `hostFileConfig`, `parseHostsFile`, `parseHostConfig`, `getSortedHosts`, `makeStringSlice`, `makeAbsPath`, and `loadCertFiles`.

Control flow: `ConfigureHosts` returns a `docker.RegistryHosts` closure. For a requested host it loads host configs from `HostDir`, defaults to Docker Hub or the requested host when no config exists, builds a default transport/client/authorizer, then creates `docker.RegistryHost` entries. Per-host TLS, dial timeout, or headers cause a cloned client/transport and a separate authorizer with merged auth headers. HTTP endpoints with TLS configuration and non-80 ports are upgraded to HTTPS plus `docker.NewHTTPFallback`.

State and persistence: reads `hosts.toml`, CA certs, client cert/key files, and directory listings. It does not persist config; returned registry hosts carry clients, TLS roots/certs, headers, and authorizers in memory.

Dependencies and integration points: used by Docker resolver configuration. Integrates `docker.RegistryHost` capabilities, `docker.NewDockerAuthorizer`, `docker.DefaultHTTPTransport`, `docker.NewHTTPFallback`, pelletier TOML parser, x509/tls, and Docker cert directory conventions.

Config semantics: `parseHostsFile` preserves host table order using the TOML unstable parser, parses mirror hosts first, and appends root `server` config last. `parseHostConfig` normalizes server URLs, appends `/v2` unless `override_path` is true, maps capabilities (`pull`, `resolve`, `push`, `referrers`), resolves relative cert paths, supports multiple CA/client forms, headers as string or string list, and `dial_timeout`.

Risks: TLS configs are mutated on cloned transports; bad cert files fail host resolution. `getSortedHosts` depends on unstable TOML APIs. `HostDirFromRoot` first existing path wins. Header types and cert/client TOML shapes are strict. Localhost default skip-verify/fallback logic is nuanced and easy to regress.

Test signals: `hosts_test.go` covers Docker Hub defaults, detailed TOML parsing, cert file discovery, and HTTP fallback matrix. `hosts_resolver_test.go` covers real resolver behavior with server/mirror/token headers. `docker_fuzzer_test.go` fuzzes parser robustness.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/hosts.go -->
