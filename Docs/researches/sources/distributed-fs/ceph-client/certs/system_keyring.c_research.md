<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/system_keyring.c -->
# sources/distributed-fs/ceph-client/certs/system_keyring.c

## Purpose

`system_keyring.c` creates and populates the kernel trusted keyrings and provides PKCS#7 signature verification against builtin, secondary, machine, or platform trust roots. It is central to module signature checking and other system data verification paths.

## Important APIs, Types, And Functions

Restriction functions include `restrict_link_by_builtin_trusted()`, `restrict_link_by_digsig_builtin()`, `restrict_link_by_builtin_and_secondary_trusted()`, `restrict_link_by_digsig_builtin_and_secondary()`, and, with machine keyring support, `restrict_link_by_builtin_secondary_and_machine()`.

Initialization and loading functions are `system_trusted_keyring_init()`, `load_module_cert()`, `load_system_certificate_list()`, `add_to_secondary_keyring()`, `set_machine_trusted_keys()`, and `set_platform_trusted_keys()`. Verification APIs are `verify_pkcs7_message_sig()` and exported `verify_pkcs7_signature()`.

Global keyring pointers include `builtin_trusted_keys`, optional `secondary_trusted_keys`, optional `machine_trusted_keys`, and optional `platform_trusted_keys`.

## Control Flow

`system_trusted_keyring_init()` runs as a `device_initcall()`, allocates `.builtin_trusted_keys`, optionally allocates `.secondary_trusted_keys` with a restriction, and links builtin trust into secondary trust. `load_system_certificate_list()` runs later, selects the embedded certificate range, and loads certificates into the builtin keyring. `load_module_cert()` separately loads module certificates for IMA appraise-modsig when needed.

Restriction callbacks route key additions through signature verification against the configured trust root and optionally require digitalSignature usage. Secondary trust permits linking builtin and machine keyrings into the secondary ring so searches can traverse them.

`verify_pkcs7_signature()` parses raw PKCS#7, delegates to `verify_pkcs7_message_sig()`, then frees the message. Message verification supplies detached data, verifies PKCS#7 structure for the intended usage, rejects revoked signing keys via the revocation list, resolves the requested trust keyring, validates signer trust, and optionally exposes embedded content through a callback.

## State And Persistence Behavior

Trusted keyrings persist for the lifetime of the kernel. Certificates embedded by `system_certificates.S` are loaded during init. Secondary and machine/platform links persist after setup. There is no filesystem persistence here; trust state comes from compiled-in blobs and keyring additions allowed by restrictions.

## Dependencies And Integration Points

The file depends on kernel key management, asymmetric key type support, X.509 loading, PKCS#7 parsing/verification, revocation checks from blacklist code, and `keys/system_keyring.h`. Callers include module signature verification, firmware/system data verification, IMA, and integrity keyring setup.

## Risks And Edge Cases

Trust routing must match caller intent. `VERIFY_USE_SECONDARY_KEYRING` falls back to builtin if secondary is absent; platform trust returns `-ENOKEY` if unavailable. Revocation checks must happen before trust success is accepted. Keyring allocation failures panic because missing trust roots break core security assumptions. Secondary keyring policy can broaden trust if machine keyrings are linked without appropriate constraints.

## Test Signals

Tests should cover boot allocation/loading of builtin and secondary keyrings, valid and invalid certificate chains, digitalSignature usage restrictions, machine/platform keyring selection, revoked PKCS#7 signers, detached-data mismatch, embedded-content callback handling, absent secondary/platform keyrings, and exported verification return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/system_keyring.c -->
