<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/hosts.go -->
# sources/cloud-native/moby/daemon/hosts.go

Purpose: adapts Docker daemon registry configuration into containerd `docker.RegistryHost` records. It combines containerd-style `certs.d` host configuration with Moby's legacy mirror, custom certificate, and insecure registry settings.

Important APIs and control flow: `Daemon.RegistryHosts` calls containerd `ConfigureHosts` with `registry.CertsDir()`, then calls `mergeLegacyConfig` when daemon mirrors or insecure registries are configured. `mergeLegacyConfig` only modifies the single default host case, adds Docker Hub mirrors via `mirrorsToRegistryHosts`, loads TLS roots and client key pairs with `loadTLSConfig`, and wraps insecure transports with HTTP fallback. `mirrorsToRegistryHosts` normalizes mirror URLs, default schemes, and legacy `/v2` path behavior. `loadTLSConfig` scans `.crt`, `.cert`, and matching `.key` files into a `tls.Config`.

State and persistence: no daemon state is mutated except the returned host transport objects. It reads registry certificate directories on disk and daemon registry service configuration.

Dependencies and integration: integrates Moby registry config, containerd remotes/docker host resolution, Go TLS/x509 pools, and HTTP transports used by pull/push/build resolver paths.

Risks: legacy merge is intentionally skipped when containerd already supplies multiple hosts, so operator precedence is subtle. Insecure registry handling sets `InsecureSkipVerify` and HTTP fallback by design. Certificate loading tolerates missing or permission-denied directories but fails on malformed client key pairs. Mirror path normalization preserves legacy behavior that can append `/v2` even to paths that already contain it in the middle.

Test signals: `hosts_test.go` covers mirror URL normalization and capability shaping. TLS and insecure-registry branches are mainly covered through registry integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/hosts.go -->
