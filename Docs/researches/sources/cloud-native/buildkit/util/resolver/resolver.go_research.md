<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/resolver.go -->
# sources/cloud-native/buildkit/util/resolver/resolver.go

Purpose: converts BuildKit registry config into containerd Docker registry hosts, configures TLS/HTTP clients, supports mirrors, and provides HTTPS-to-HTTP fallback for insecure localhost/plain HTTP behavior.

Important APIs and types: `NewRegistryConfig`, `fillInsecureOpts`, `loadTLSConfig`, `newMirrorRegistryHost`, `newDefaultClient`, `newDefaultTransport`, `httpFallback`, `isTLSError`, and `isPortError`.

Control flow: `NewRegistryConfig` returns a `docker.RegistryHosts` callback that emits configured mirrors first, then the canonical registry host, rewriting `docker.io` to `registry-1.docker.io`. TLS config loading reads CA files, client cert/key pairs, and `.crt`/`.cert` files from TLS config directories. Insecure config sets `InsecureSkipVerify`; plain HTTP config switches scheme or wraps HTTPS transport with fallback. `httpFallback` tries HTTPS first per host, then retries HTTP on TLS/port errors and remembers the host.

State and persistence: TLS config is built from filesystem certificate paths at resolver creation time. `httpFallback` stores one host string protected by a mutex.

Dependencies and integration: uses containerd docker remotes, BuildKit resolver config, tracing transport wrapper, Go TLS/x509/http transports, and OS filesystem APIs.

Risks: insecure mode disables certificate verification. HTTP fallback only retries without a specified port for connection-refused/timeouts, preventing unexpected port changes. Directory scanning ignores missing/permission-denied TLS directories but fails on other read errors.

Test signals: `resolver_test.go` validates mirror host/path parsing and `/v2` path joining for configured mirrors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/resolver.go -->
