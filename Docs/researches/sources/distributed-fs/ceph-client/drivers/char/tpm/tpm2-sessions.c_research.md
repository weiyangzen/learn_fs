<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-sessions.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-sessions.c

## Purpose
Implements optional TPM2 HMAC authorization sessions and first-parameter encryption/decryption for kernel-originated TPM2 transactions, based on a salted session derived from a TPM NULL primary key.

## Important APIs, Types, And Functions
Important exported helpers are `tpm_buf_append_name()`, `tpm_buf_append_auth()`, `tpm_buf_append_hmac_session()`, `tpm_buf_fill_hmac_session()`, `tpm_buf_check_hmac_response()`, `tpm2_end_auth_session()`, `tpm2_start_auth_session()`, and `tpm2_sessions_init()`. Core internal pieces include `struct tpm2_auth`, `name_size()`, `tpm2_read_public()`, `tpm2_KDFa()`, `tpm2_KDFe()`, `tpm_buf_append_salt()`, `tpm2_parse_start_auth_session()`, `tpm2_load_null()`, `tpm2_parse_create_primary()`, and `tpm2_create_primary()`.

## Control Flow
Initialization creates a fixed ECC P-256 NULL primary, validates its template/name, saves its context, and stores the public key coordinates. Starting a session loads or recreates the NULL key, generates caller nonce and ECDH salt, sends `StartAuthSession`, derives the session key, and stores `chip->auth`. Command construction records names for handles, appends the HMAC session placeholder, optionally encrypts the first parameter, computes `cpHash`, and fills the HMAC. Response checking parses the session area, computes `rpHash`, verifies the TPM HMAC, optionally decrypts the first response parameter, and either resets or frees the auth session.

## State And Persistence
`chip->auth` holds active session handle, nonces, salt/scratch, session key, passphrase, AES key schedule, attributes, ordinal, and up to three handle names. `chip->null_key_context`, `null_key_name`, and public EC coordinates persist after initialization to bootstrap later sessions.

## Dependencies And Integration Points
Compiled only when `CONFIG_TCG_TPM2_HMAC` enables the heavy implementation; otherwise `tpm.h` provides a no-op init. It integrates TPM2 command helpers, TPM2 context load/save, Linux random, SHA256/HMAC, ECDH P-256, AES-CFB, and TPM2 command-attribute metadata.

## Risks And Edge Cases
The initial NULL primary creation cannot itself be session protected, so the file exposes `null_name` for userspace verification. Handle names must be appended with `tpm_buf_append_name()` or HMACs are wrong. Session offsets and parameter sizes are fragile, and failures must flush sessions and sensitive memory. Unsupported name algorithms or changed NULL primary names disable the chip.

## Test Signals
PCR extend and RNG with HMAC enabled, HMAC mismatch fault injection, encrypted request and response parameter tests, NULL primary context reload and recreation, tampered NULL key name, too many handles, unsupported name algorithms, command failure cleanup, and sysfs `null_name` verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-sessions.c -->
