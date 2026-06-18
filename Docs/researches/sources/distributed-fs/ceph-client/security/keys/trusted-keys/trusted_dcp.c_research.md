# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_dcp.c

## Purpose

`trusted_dcp.c` implements trusted-key sealing for NXP Data Co-Processor hardware. DCP only exposes hardware-bound AES operations, so this backend defines its own blob format: a random blob encryption key encrypts the trusted payload with AES-GCM, and DCP encrypts that blob key with an OTP or UNIQUE device key.

## Important APIs, Types, and Functions

`struct dcp_blob_fmt` stores version, encrypted blob key, nonce, payload length, and encrypted payload plus GCM tag. `trusted_dcp_seal()` creates the blob. `trusted_dcp_unseal()` validates and decrypts it. `do_dcp_crypto()` runs `ecb-paes-dcp` for the blob key. `do_aead_crypto()` runs `gcm(aes)` for payload encryption/authentication. `test_for_zero_key()` detects insecure zero/test key state unless `dcp_skip_zk_test` is set. `dcp_trusted_key_ops` registers non-migratable backend callbacks.

## Control Flow

Seal computes the final blob size, allocates a temporary AES-128 blob key, fills the blob version and nonce, AEAD-encrypts `p->key`, encrypts the temporary blob key with DCP, stores payload length, and wipes the temporary key. Unseal checks the version and expected length, decrypts the blob key through DCP, uses it to AEAD-decrypt the payload into `p->key`, and wipes the temporary key. Init optionally logs OTP-key use, runs the zero-key test, and registers the trusted key type.

## State and Persistence Behavior

Persistent key material is stored only in the custom DCP blob in `p->blob`; clear temporary blob keys are explicitly zeroed. Module parameters select OTP versus UNIQUE device key and whether to skip the zero-key test. DCP-backed trusted keys are non-migratable because the encrypted blob key is hardware-bound.

## Dependencies and Integration Points

The backend depends on the Linux crypto API, `ecb-paes-dcp`, `gcm(aes)`, DCP platform support, random bytes, and the trusted-key core. It is selected by `CONFIG_TRUSTED_KEYS_DCP`.

## Risks and Test Signals

Blob version/length validation is critical because malformed blobs drive flexible payload parsing. AEAD tag failure must not expose partial plaintext. The zero-key test is a platform safety gate. Test signals include secure-mode and insecure-mode boot behavior, OTP/UNIQUE modes, malformed blob versions/lengths/tags, crypto allocation failures, and keyctl create/load round trips.
