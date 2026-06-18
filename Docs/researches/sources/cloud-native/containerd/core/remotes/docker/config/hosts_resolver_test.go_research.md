<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/hosts_resolver_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/config/hosts_resolver_test.go

Purpose: integration-style resolver tests for `hosts.toml` server/mirror config, TLS roots, bearer token flow, and per-host headers.

Important APIs/types/functions: `TestResolverWithHostsDir`, `testResolverWithHostsDir`, `runBasicTest`, `newTLSServer`, `testContent`, `testManifest`, and related helpers.

Control flow: each scenario creates upstream, mirror, server, and token TLS test servers. A generated `hosts.toml` defines a server and mirror with distinct headers. The resolver resolves an image and assertions verify which endpoint handled requests and which headers were sent to registry and token endpoints.

State and persistence: writes a temporary host directory and `hosts.toml`; creates in-memory TLS servers and content descriptors/manifests.

Dependencies and integration points: exercises `ConfigureHosts`, `HostDirFromRoot`, Docker resolver, `NewDockerAuthorizer`, token fetching, TLS root pools, and `RegistryHost` capability ordering.

Risks covered: server entry prevents upstream calls, mirror priority over server, server fallback when mirror disabled, per-host headers do not bleed across endpoints, and token requests inherit the selected host headers.

Test signals: high-value behavioral signal for config/auth integration. It relies on local test servers and copied resolver test helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/hosts_resolver_test.go -->
