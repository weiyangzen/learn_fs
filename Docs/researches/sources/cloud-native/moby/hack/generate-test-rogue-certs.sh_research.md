# sources/cloud-native/moby/hack/generate-test-rogue-certs.sh

## Purpose
Generates rogue CA, server, and client TLS certificates for negative HTTPS integration tests.

## Important APIs and Types
Uses the same OpenSSL primitives as trusted cert generation but writes `*-rogue-*` files under `integration-cli/fixtures/https`.

## Control Flow, State, and Persistence
The script creates an "Evil Inc" CA, rogue server cert, rogue client cert, matching extension config files, then removes serial, CA private key, configs, and CSRs. Persisted outputs are rogue public CA/certs and private keys used by tests.

## Dependencies, Integration Points, Risks, and Test Signals
Used by tests that assert daemon/client TLS rejection of untrusted identities. Risks mirror the trusted generator: nondeterminism, OpenSSL compatibility, expiry, and fixture path assumptions. HTTPS negative integration tests are the validation signal.
