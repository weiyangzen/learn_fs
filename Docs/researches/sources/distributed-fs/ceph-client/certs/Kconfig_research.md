<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/Kconfig -->
# sources/distributed-fs/ceph-client/certs/Kconfig

## Purpose

`certs/Kconfig` defines kernel configuration options for module signing keys, system trusted keyrings, extra certificates, secondary trust, blacklists, revocation certificates, authenticated blacklist updates, and OpenSSL ML-DSA capability probing.

## Important APIs, Types, And Functions

This is Kconfig data, not C code. Important symbols are `MODULE_SIG_KEY`, `MODULE_SIG_KEY_TYPE_RSA`, `MODULE_SIG_KEY_TYPE_ECDSA`, `MODULE_SIG_KEY_TYPE_MLDSA_44`, `MODULE_SIG_KEY_TYPE_MLDSA_65`, `MODULE_SIG_KEY_TYPE_MLDSA_87`, `SYSTEM_TRUSTED_KEYRING`, `SYSTEM_TRUSTED_KEYS`, `SYSTEM_EXTRA_CERTIFICATE`, `SYSTEM_EXTRA_CERTIFICATE_SIZE`, `SECONDARY_TRUSTED_KEYRING`, `SECONDARY_TRUSTED_KEYRING_SIGNED_BY_BUILTIN`, `SYSTEM_BLACKLIST_KEYRING`, `SYSTEM_BLACKLIST_HASH_LIST`, `SYSTEM_REVOCATION_LIST`, `SYSTEM_REVOCATION_KEYS`, `SYSTEM_BLACKLIST_AUTH_UPDATE`, and `OPENSSL_SUPPORTS_ML_DSA`.

## Control Flow

Kconfig dependency resolution controls which certificate objects are built and which runtime keyring paths are compiled. Module signing key type selection is a `choice`. ML-DSA options depend on `OPENSSL_SUPPORTS_ML_DSA`, which probes the host OpenSSL binary. Secondary keyring and revocation options depend on the foundational trusted or blacklist keyrings.

## State And Persistence Behavior

The selected symbols persist in the kernel `.config` and determine build artifacts and runtime policy. They influence whether generated signing keys, compiled-in X.509 blobs, revocation lists, and runtime keyring write permissions exist.

## Dependencies And Integration Points

These options integrate with `certs/Makefile`, module signature code, IMA appraisal, asymmetric key parsing, PKCS#7 parsing, system data verification, and crypto algorithms such as ECDSA and ML-DSA.

## Risks And Edge Cases

Misconfigured `MODULE_SIG_KEY` can fail builds or omit intended trust anchors. Enabling secondary trust broadens the trust surface unless restrictions are understood. ML-DSA support depends on host toolchain capability. Authenticated blacklist updates require system data verification and must not allow unsigned deny-list changes.

## Test Signals

Test signals include `oldconfig` dependency behavior, builds with generated RSA/ECDSA/ML-DSA keys, PKCS#11 key URIs, empty and populated trusted/blacklist/revocation inputs, and expected object inclusion from `certs/Makefile`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/Kconfig -->
