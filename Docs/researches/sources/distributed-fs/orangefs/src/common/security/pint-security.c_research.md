<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-security.c -->
# sources/distributed-fs/orangefs/src/common/security/pint-security.c

## Purpose
Implements real OrangeFS security initialization, OpenSSL threading setup, capability signing/verification, credential signing/verification, and key/certificate loading for key-based or certificate-based security modes.

## Important APIs, Types, And Functions
Exports `PINT_security_initialize`, `PINT_security_finalize`, optional `PINT_security_cache_ca_cert`, `PINT_init_capability`, `PINT_sign_capability`, `PINT_verify_capability`, `PINT_server_to_server_capability`, `PINT_init_credential`, `PINT_sign_credential`, `PINT_verify_credential`, and `PINT_security_error`. Internal helpers set up OpenSSL thread callbacks, dynamic locks, load private keys, and load public-key keystores.

## Control Flow
Initialization is guarded by `security_init_mutex`, configures OpenSSL algorithms/errors/threading, initializes the public-key hash, requires server key config, then either loads private/public key files and validates host aliases or initializes the certificate trust store, loads CA/private key material, extracts the CA public key, and initializes LDAP. Capability signing sets issuer-provided fields, computes timeout, signs issuer/fsid/timeout/op mask/handle list with SHA1/RSA, and records signature size. Capability verification checks null and timeout cases, finds the public key from CA or keystore, and verifies the same field sequence. Credential signing allocates an `S:` issuer, sets timeout, signs uid/groups/issuer/timeout, and verification checks timeout, optional certificate trust/cache, and signature with the issuer public key.

## State And Persistence
Global state includes initialization status, OpenSSL mutex array, private key, certificate-mode CA cert/public key, and the security public-key hash table. Persistent inputs are server configuration, key files, keystore files, CA files, and LDAP settings. The module does not itself persist generated signatures beyond returned structures.

## Dependencies And Integration Points
Depends on OpenSSL EVP/X509/ERR/PEM APIs, server config manager, `security-hash`, `security-util`, certificate utilities, LDAP mapping, optional certificate cache, gossip, and generated PVFS request/security types. It is the real implementation selected by `security/module.mk.in`.

## Risks And Test Signals
Risks include SHA1/RSA-only support, complex OpenSSL-version conditionals, global lifetime leaks on some error paths, unsigned credentials accepted in certificate mode for limited operations, key/cert config hard failures, and timeout bypass configuration. Tests should cover idempotent initialize/finalize, missing/invalid key files, keystore parsing, host alias validation, capability and credential sign/verify success/failure, expired timeout behavior, cert-cache hit/miss verification, LDAP initialization errors, and OpenSSL threaded use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-security.c -->
