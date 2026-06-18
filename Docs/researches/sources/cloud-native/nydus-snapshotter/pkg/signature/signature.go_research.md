# sources/cloud-native/nydus-snapshotter/pkg/signature/signature.go

## Purpose
Verifies Nydus bootstrap signatures stored in image labels, optionally enforcing that signatures are present.

## Important APIs, Types, And Functions
`Verifier`, `NewVerifier`, `Verifier.Verify`, and private `getFromLabel`.

## Control Flow
`NewVerifier` returns a passive verifier when validation is disabled. When validation is enabled, it requires a public key path, reads the key, and initializes a signer verifier. `Verify` decodes the base64 signature from `label.NydusSignature`; missing signature is allowed unless `force` is true. If a signer exists and signature exists, it opens the bootstrap file and verifies it.

## State And Persistence
The verifier stores a signer and force flag. It reads public key and bootstrap files but writes nothing.

## Dependencies And Integration Points
Integrates with Nydus label constants and `pkg/utils/signer`. Used by bootstrap/image validation paths that need supply-chain integrity checks.

## Risks And Edge Cases
When validation is disabled, a present signature is ignored because signer is nil. Missing signature enforcement only happens when `force` is true. Base64 decoding errors surface directly. File existence is checked during verifier construction for the public key and during verification for the bootstrap.

## Test Signals
No active tests in this subset. A commented older function documents previous inline verification flow.
