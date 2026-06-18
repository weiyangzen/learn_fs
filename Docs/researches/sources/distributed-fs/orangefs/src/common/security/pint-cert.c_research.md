<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-cert.c -->
# sources/distributed-fs/orangefs/src/common/security/pint-cert.c

## Purpose
Manages the global OpenSSL X509 trust store used by certificate-mode OrangeFS security and verifies peer certificates against that store.

## Important APIs, Types, And Functions
Exports `PINT_init_trust_store`, `PINT_add_trusted_certificate`, `PINT_cleanup_trust_store`, and `PINT_verify_certificate`. Internal `verify_certificate_cb` logs X509 verification errors with subject, error depth, and OpenSSL error text.

## Control Flow
Initialization creates an `X509_STORE`. Trusted certificates are added with `X509_STORE_add_cert`. Verification creates an `X509_STORE_CTX`, installs the logging callback, initializes it with the global store and target certificate, calls `X509_verify_cert`, cleans up the context, and returns `0` or `-PVFS_ESECURITY`.

## State And Persistence
State is the global `X509_STORE *trust_store`; it is in memory only and is freed on cleanup. Trusted certificate contents originate from configuration-driven files loaded elsewhere.

## Dependencies And Integration Points
Depends on OpenSSL X509 store APIs, `pint-security` error logging, gossip, and PVFS errors. Used by certificate security initialization, credential verification, and UID mapping.

## Risks And Test Signals
Risks include global store lifetime, repeated initialization without cleanup, OpenSSL API differences, and callback installation on the shared store. Tests should verify CA load, trusted/untrusted certificate outcomes, cleanup/reinitialize, and logged diagnostics for expired or wrong-chain certificates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-cert.c -->
