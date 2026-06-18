<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/cert-util.c -->
# sources/distributed-fs/orangefs/src/common/security/cert-util.c

## Purpose
Provides OpenSSL utility functions for loading, saving, converting, copying, and cleaning OrangeFS certificate and key structures.

## Important APIs, Types, And Functions
Exports `PINT_load_cert_from_file`, `PINT_load_key_from_file`, `PINT_save_cert_to_file`, `PINT_save_pubkey_to_file`, `PINT_save_privkey_to_file`, `PINT_cert_to_X509`, `PINT_X509_to_cert`, `PINT_copy_cert`, `PINT_copy_key`, `PINT_cleanup_cert`, and `PINT_cleanup_key`. `PINT_save_key_to_file` is the internal common save helper.

## Control Flow
Load/save functions open PEM files and call OpenSSL PEM read/write APIs. Conversion from internal certificate to X509 creates a memory BIO over DER bytes and decodes it; conversion from X509 writes DER into a memory BIO, allocates a `PVFS_certificate`, and copies pending BIO bytes. Copy helpers allocate destination buffers and deep-copy byte arrays. Cleanup frees internal buffers and zeroes sizes.

## State And Persistence
The file reads and writes certificate/key files, including unencrypted private keys. In-memory allocations are transferred to callers, who must free with OpenSSL APIs or the provided cleanup helpers as appropriate.

## Dependencies And Integration Points
Depends on OpenSSL PEM/BIO/X509/EVP APIs and PVFS security types. Used by certificate-mode security initialization, credential verification, LDAP mapping, certificate cache, and trust-store setup.

## Risks And Test Signals
Risks include mixed positive `errno` returns versus negative PVFS error codes, unencrypted private-key output, partial cleanup on allocation failures, and API drift across OpenSSL versions. Tests should load/save valid and invalid PEM files, round-trip X509/internal certificates, copy empty and non-empty buffers, and verify cleanup can be called repeatedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/cert-util.c -->
