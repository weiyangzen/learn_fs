<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_modsig.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_modsig.c

## Purpose
Supports IMA appraisal of module-style appended PKCS#7 signatures embedded at the end of files.

## Important APIs, Types, And Functions
- `struct modsig` stores parsed PKCS#7 message, digest algorithm, digest pointer/size, and raw PKCS#7 bytes.
- `ima_read_modsig()` locates and parses an appended module signature.
- `ima_collect_modsig()` supplies detached file data to PKCS#7 and retrieves the digest.
- `ima_modsig_verify()`, `ima_get_modsig_digest()`, `ima_get_raw_modsig()`, `ima_free_modsig()`.

## Control Flow
`ima_read_modsig()` checks for `MODULE_SIGNATURE_MARKER`, validates the module signature footer with `mod_check_sig()`, allocates a flexible `modsig`, parses the PKCS#7 payload, and copies raw signature bytes. Later, collection strips the marker/footer/signature from the signed data, supplies detached data to PKCS#7, and asks PKCS#7 for the digest. Verification delegates to PKCS#7 signature verification against the selected keyring.

## State And Persistence
`struct modsig` is per-operation heap state and is freed after appraisal/measurement. Raw signature bytes may be included in IMA templates that support modsig fields, but this file itself does not persist state.

## Dependencies And Integration Points
Depends on module signature format constants, `mod_check_sig()`, PKCS#7 parser/verifier APIs, asymmetric key support, and callers in `ima_main.c`/`ima_appraise.c` that allow modsig policy.

## Risks And Edge Cases
Malformed or too-short buffers return `-ENOENT` or parser errors. Digest algorithm is unknown until collection supplies detached data. Size arithmetic must correctly exclude signature trailer bytes or verification will cover the wrong data.

## Test Signals
Use files with valid appended module signatures under IMA modsig policy, verify appraisal success, inspect measurement templates containing modsig data where configured, and test malformed marker/footer/signature cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_modsig.c -->
