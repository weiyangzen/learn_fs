<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/extract-cert.c -->
# sources/distributed-fs/ceph-client/certs/extract-cert.c

## Purpose

`extract-cert.c` is a host build utility that extracts X.509 certificates in DER form from PEM files or PKCS#11 URIs. Kbuild uses it to produce certificate blobs embedded into the kernel for trusted and revocation keyrings.

## Important APIs, Types, And Functions

The program entry point is `main()`. `write_cert()` writes one DER certificate to the output BIO and optionally logs its subject. `load_cert_pkcs11()` loads one certificate from a PKCS#11 URI using either OpenSSL 3 providers and `OSSL_STORE` or the legacy pkcs11 engine path. `format()` prints usage and exits.

Global state includes `wb`, `cert_dst`, `verbose`, and, for engine builds, `key_pass`.

## Control Flow

`main()` initializes OpenSSL, reads `KBUILD_VERBOSE` and optionally `KBUILD_SIGN_PIN`, validates two arguments, and handles three cases. Empty source creates an empty destination file. `pkcs11:` sources load one certificate with the provider/engine path and write it. Other sources are opened as PEM and read in a loop with `PEM_read_bio_X509()`, writing every certificate until a clean `PEM_R_NO_START_LINE` end condition after at least one write.

## State And Persistence Behavior

The utility persists DER output to the destination file and otherwise keeps only process-local OpenSSL/BIO state. It does not modify input PEM files or PKCS#11 tokens.

## Dependencies And Integration Points

It depends on libcrypto/OpenSSL, optional pkcs11 provider or engine APIs, and `scripts/ssl-common.h` for error handling. Kbuild compiles it as a host program and invokes it from `certs/Makefile`.

## Risks And Edge Cases

Host OpenSSL version changes select different PKCS#11 code paths. Missing pkcs11 support is a fatal error for PKCS#11 sources. PEM parsing treats an immediate failure as an error but a no-start-line after prior certificates as normal EOF. Output is opened lazily only when a certificate is written, except for empty input.

## Test Signals

Tests should cover empty source, single and multi-certificate PEM files, invalid PEM files, PKCS#11 provider/engine availability, PIN handling through `KBUILD_SIGN_PIN`, verbose logging, and output DER concatenation accepted by kernel X.509 loaders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/extract-cert.c -->
