<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-cert.h -->
# sources/distributed-fs/orangefs/src/common/security/pint-cert.h

## Purpose
Declares the certificate trust-store API for certificate-mode OrangeFS security.

## Important APIs, Types, And Functions
Declares `PINT_init_trust_store`, `PINT_add_trusted_certificate`, `PINT_cleanup_trust_store`, and `PINT_verify_certificate` over OpenSSL `X509` objects.

## Control Flow
Security initialization creates the store, adds configured CA material, verification checks peer certificates, and finalization frees the store.

## State And Persistence
No state is declared in the header, though `pint-cert.c` owns a global trust store.

## Dependencies And Integration Points
Includes OpenSSL `x509.h`; used by `pint-security.c`, `pint-uid-map.c`, and certificate-mode verification paths.

## Risks And Test Signals
Risks are header availability in non-certificate builds and OpenSSL API compatibility. Compile coverage and trusted/untrusted certificate verification tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-cert.h -->
