# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_tpm2.c

## Purpose

`trusted_tpm2.c` implements TPM 2.0 sealing and unsealing for trusted keys. It encodes TPM2 private/public blobs into the Linux TPMSealedData ASN.1 format, decodes that format on load, and issues TPM2 `Create`, `Load`, and `Unseal` commands with authorization sessions.

## Important APIs, Types, and Functions

`tpm2_key_encode()` emits the TPMSealedData sequence with OID, optional emptyAuth tag, parent handle, public blob, and private blob. `tpm2_key_decode()` and decoder callbacks `tpm2_key_parent()`, `tpm2_key_type()`, `tpm2_key_pub()`, and `tpm2_key_priv()` parse the ASN.1 representation. `tpm2_buf_append_auth()` appends manual policy/password auth sessions. `tpm2_seal_trusted()` builds and transmits `TPM2_CC_CREATE`. `tpm2_load_cmd()` loads the sealed object and returns a transient handle. `tpm2_unseal_cmd()` executes `TPM2_CC_UNSEAL`. `tpm2_unseal_trusted()` ties load, unseal, flush, and TPM op lifetime together.

## Control Flow

Seal validates the selected hash and parent handle, gets TPM ops, starts an auth session, builds sensitive and public sized buffers, sets object attributes based on policy and migratability, appends optional policy digest, sends `Create`, validates the HMAC response, and encodes the returned private/public blob into `payload->blob`. Unseal first decodes the new ASN.1 format or falls back to old raw format. It validates blob sizes, derives migratable state from public attributes, starts an auth session, loads the object under the parent key, then unseals it. Policy-handle unseal has a special path for external policy sessions and may send a plaintext password because nonce/HMAC material is unavailable.

## State and Persistence Behavior

The persistent representation is the ASN.1 TPMSealedData blob in `payload->blob`, with old raw blob compatibility. Unseal creates a transient TPM object handle and always flushes it after use. `payload->old_format` controls how the migratable flag is recovered. TPM operation references are acquired and released around seal/unseal.

## Dependencies and Integration Points

The file depends on TPM2 buffer/session helpers, ASN.1 encoder/decoder infrastructure, OID registry, unaligned access helpers, and option fields parsed in `trusted_tpm1.c`. It integrates with generated `tpm2key.asn1.h`.

## Risks and Test Signals

ASN.1 size handling, TPM buffer overflow flags, and policy-session authentication are high-risk. The policyhandle FIXME documents a weaker password path for externally created sessions. Tests should cover new and old blob formats, emptyAuth and password auth, policy digest/handle flows, non-migratable attributes, malformed ASN.1, TPM response truncation, and transient handle flushing on failures.
