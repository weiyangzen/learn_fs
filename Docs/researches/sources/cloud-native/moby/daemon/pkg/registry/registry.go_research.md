<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/registry.go -->
# sources/cloud-native/moby/daemon/pkg/registry/registry.go

## Purpose
Implements registry client TLS configuration, certificate directory loading, request headers, and HTTP transport creation.

## Important APIs, Types, And Functions
`hostCertsDir`, `newTLSConfig`, `hasFile`, `loadTLSConfig`, `Headers`, and `newTransport` are the key functions.

## Control Flow
TLS config starts from Docker server defaults and toggles `InsecureSkipVerify` for insecure endpoints. Secure endpoints load `.crt` CA files and `.cert`/`.key` client pairs from host-specific cert dirs, validating matching pairs. Headers returns transport request modifiers for user-agent and meta headers. Transport creation uses proxy, dial timeout, TLS handshake timeout, idle timeout, and OpenTelemetry instrumentation.

## State, Dependencies, And Integration Points
Reads certificate files from `CertsDir()` but persists nothing. Integrates with registry service endpoints, auth clients, plugin resolvers, and image distribution code.

## Risks And Test Signals
Malformed cert directories become invalid-parameter errors. Windows strips colons from host cert dirs. Direct tests are not in this subset; registry integration tests and mock registry helpers exercise transports.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/registry.go -->
