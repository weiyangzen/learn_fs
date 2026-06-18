# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_tpm1.c

## Purpose

`trusted_tpm1.c` provides the TPM-backed trusted-key provider and contains the TPM 1.2 command construction, HMAC authentication, PCR locking, option parsing, and dispatch glue that also routes TPM 2.0 systems to `trusted_tpm2.c`.

## Important APIs, Types, and Functions

Global state includes the selected `tpm_chip *chip` and PCR-bank `digests`. TPM 1.2 helpers include `TSS_rawhmac()`, `TSS_authhmac()`, `TSS_checkhmac1()`, `TSS_checkhmac2()`, `trusted_tpm_send()`, `osap()`, `oiap()`, `tpm_seal()`, and `tpm_unseal()`. High-level helpers `key_seal()` and `key_unseal()` wrap the TPM 1.2 paths. `getoptions()` parses `keyhandle`, `keyauth`, `blobauth`, `pcrinfo`, `pcrlock`, `migratable`, `hash`, `policydigest`, and `policyhandle`. `trusted_tpm_seal()` and `trusted_tpm_unseal()` dispatch to TPM 2.0 or TPM 1.2. `trusted_key_tpm_ops` exposes the backend.

## Control Flow

Initialization obtains the default TPM chip, allocates digest descriptors for PCR extension, and registers the common trusted key type. Seal parses options and rejects missing TPM 1.2 key handles, then calls `tpm2_seal_trusted()` on TPM 2.0 systems or `key_seal()` on TPM 1.2. TPM 1.2 sealing creates an OSAP session, derives authorization material, builds a `TPM_ORD_SEAL` AUTH1 command, sends it, verifies response HMAC, and copies the returned blob. Unseal creates two OIAP sessions, builds an AUTH2 `TPM_ORD_UNSEAL` command, verifies both response HMACs, copies plaintext, and extracts the embedded migratable flag. Optional `pcrlock` extends a PCR after seal or unseal.

## State and Persistence Behavior

TPM-backed payload persistence is the TPM sealed blob. TPM 1.2 stores the migratable flag at the end of the sealed plaintext; TPM 2.0 stores or infers it through TPM2 attributes in the companion file. Global chip and digest references live until module exit. Authorization data and work buffers are freed with sensitive clearing where appropriate.

## Dependencies and Integration Points

Dependencies include the TPM core, TPM command constants, SHA-1/HMAC helpers, hash metadata, trusted-key core, and TPM2 helper functions from `trusted_tpm2.c`. It integrates with `CAP_SYS_ADMIN` for PCR locking and `tpm_get_random()` for backend RNG.

## Risks and Test Signals

TPM 1.2 packet offsets and HMAC coverage are fragile; endian mistakes or unchecked response sizes can break security. PCR lock is privileged and changes platform state. TPM 2.0 option parsing must reject TPM 1.x-incompatible hash/policy options. Test with TPM 1.2 and TPM 2.0 create/load/update, auth failures, PCR policy mismatch, pcrlock permission checks, malformed hex options, no default TPM, and key length limits.
