# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3_kek_passphrase_test.go

## Purpose
This test file verifies passphrase-based KEK wrapping for SSE-S3. It locks in that `SetKEKPassphrase` enables encrypted KEK round trips, random salts prevent identical wrapped output, and no-passphrase mode remains the legacy plaintext-hex path.

## Important APIs, Types, and Functions
Tests call `NewSSES3KeyManager`, `SetKEKPassphrase`, `wrapKEK`, and `unwrapKEK`. Main tests are `TestSetKEKPassphraseEnablesEncryptedRoundTrip`, `TestSetKEKPassphraseDifferentInstancesNoCollision`, and `TestNoPassphraseKeepsLegacyHexDecodePath`.

## Control Flow
The first test sets a passphrase, wraps a deterministic 32-byte KEK, unwraps it, asserts v2 format detection, and compares bytes. The second creates two managers with the same passphrase, wraps identical KEKs, asserts ciphertext differs due to random salt/nonce, then verifies each manager can unwrap its own output. The third verifies a default manager has no passphrase and that `wrapKEK` fails instead of producing output.

## State and Persistence Behavior
No filer state is written. The tests exercise only in-memory wrapping payloads that would normally be stored in `/etc/s3/sse_kek`.

## Dependencies and Integration Points
The tests cover the passphrase plumbing used by `InitializeGlobalSSES3KeyManager` and `loadSuperKeyFromFiler` migration paths. They indirectly verify HKDF-derived wrapping keys and AES-GCM wrapping.

## Risks and Edge Cases
The tests do not cover legacy v1 fixed-salt unwrapping, plaintext-to-wrapped migration, or failed filer updates. They also do not test wrong-passphrase unwrap failure. They are still a strong signal that passphrase setup reaches the key manager before wrapping is attempted.

## Test Signals
Passing tests mean v2 wrapped payloads self-roundtrip, same passphrase plus same KEK does not produce byte-identical payloads across instances, and wrapping without a passphrase fails explicitly.
