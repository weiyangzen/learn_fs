# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/hosts_test.go

## Purpose
Validates registry host configuration parsing and Docker-compatible cert-directory fallback.

## Important APIs, Types, And Functions
Tests cover `ConfigureHosts`, `parseHostsFile`, `loadHostDir`, and comparison helpers `compareRegistryHost`, `compareHostConfig`, and `printHostConfig`.

## Control Flow
`TestDefaultHosts` checks that `docker.io` maps to `https://registry-1.docker.io/v2` with pull/resolve/push. `TestParseHostFile` feeds a rich TOML document, then compares the ordered host configs for mirrors, default server, headers, cert paths, client keypair variants, `skip_verify`, and `override_path`. `TestLoadCertFiles` creates temp Docker cert directories with `.crt`, `.cert`, and `.key` files and verifies fallback parsing.

## State And Persistence
Uses temporary directories for cert-file tests. No persistent state is modified.

## Dependencies And Integration Points
Imports `docker.HostCapability*` constants and `logtest` context. The expected values encode the contract consumed by resolver/fetcher/pusher host selection.

## Risks And Edge Cases
The test suite locks down host ordering, which is important because mirrors are tried before the default server. The embedded test private key is only file content for parser coverage, not used as a valid TLS identity in network tests.

## Test Signals
These are direct unit tests for config behavior and are strong signals for compatibility with containerd-style `hosts.toml` and Docker cert layouts.
