# sources/distributed-fs/juicefs/pkg/meta/config_test.go

## Purpose

This file tests the sensitive-field behavior of `Format`: encryption, redaction, decryption failure after redaction, supported encryption algorithms, and UUID conflict handling during format updates.

## Important Tests

`TestRemoveSecret` creates a format with `SecretKey`, `EncryptKey`, and `SessionToken`, encrypts it, calls `RemoveSecret`, and asserts all three fields become `"removed"`. It then verifies that `Decrypt` returns an error containing `"secret was removed"` instead of silently producing invalid values.

`TestEncrypt` iterates over `object.AES256GCM_RSA`, `object.CHACHA20_RSA`, and `object.SM4GCM`. For each algorithm label it encrypts a format and verifies secrets are no longer plaintext, then decrypts and verifies exact restoration. The first two algorithm constants use the default AES-GCM branch in `newCipher`; SM4 uses the SM4-GCM branch.

`TestFormat_Update_KeyConflict` builds an old format with UUID A and a new format with UUID B plus a secret. It encrypts the new format, calls `update(old, false)`, and asserts the new format adopts UUID A while remaining encrypted. A final decrypt must recover the original secret, proving `update` rekeys encrypted secrets correctly when UUID is the only conflict.

## State And Persistence Behavior

All tests mutate `Format` structs in memory but model persistent metadata transitions. The UUID conflict test is especially important because persisted format updates happen around encrypted credentials; losing the old UUID/key relationship would break future mounts. Redaction is treated as irreversible for encrypted fields.

## Dependencies And Integration Points

The tests import `pkg/object` for encryption algorithm constants and `testify/assert` for key-conflict assertions. They directly cover `Format.Encrypt`, `Format.Decrypt`, `Format.RemoveSecret`, and the unexported `Format.update`.

## Risks And Test Signals

These tests give strong signals for happy-path encryption and UUID rekeying but do not cover malformed base64, truncated ciphertext, empty UUIDs, or `CheckCliVersion`. They also do not verify randomness/non-determinism of nonces. A failure here usually indicates a compatibility risk for stored credentials or CLI-safe format display.
