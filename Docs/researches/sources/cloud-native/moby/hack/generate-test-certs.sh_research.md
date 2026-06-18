# sources/cloud-native/moby/hack/generate-test-certs.sh

## Purpose
Generates trusted CA, server, and client TLS certificates for integration tests.

## Important APIs and Types
Uses `openssl genrsa`, `openssl req`, `openssl x509`, and temporary extension config files under `integration/testdata/https`.

## Control Flow, State, and Persistence
The script creates a CA key/cert, server key/CSR/options/cert, client key/CSR/options/cert, then removes CA serial, CA key, configs, and CSRs. SANs include wildcard, localhost, IPv4 loopback, and IPv6 loopback; server and client certs get appropriate extended key usages.

## Dependencies, Integration Points, Risks, and Test Signals
Supports HTTPS daemon/client integration data and symlinked integration-cli fixtures. Risks include non-deterministic key/cert output, OpenSSL behavior drift, certificate expiry, and leaving private CA key only transiently. Tests that use TLS fixtures validate the generated artifacts.
