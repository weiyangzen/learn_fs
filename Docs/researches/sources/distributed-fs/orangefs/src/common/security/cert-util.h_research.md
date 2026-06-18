<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/cert-util.h -->
# sources/distributed-fs/orangefs/src/common/security/cert-util.h

## Purpose
Declares certificate and key utility functions used by OrangeFS security code.

## Important APIs, Types, And Functions
The header exposes file load/save helpers for X509 certificates and EVP keys, conversion helpers between `PVFS_certificate` and `X509`, deep-copy helpers for `PVFS_certificate` and `PVFS_security_key`, and cleanup functions for those internal structures.

## Control Flow
Consumers call these helpers while initializing trust, converting credentials for verification, caching certificate identity mappings, or persisting generated keys/certificates.

## State And Persistence
No state is declared. Persistence is implied by the file path arguments used by the implementation.

## Dependencies And Integration Points
Includes OpenSSL `evp.h`/`x509.h`, `pvfs2-config.h`, and `pvfs2-types.h`. It is compiled into library and server builds when certificate security is enabled.

## Risks And Test Signals
Risks are declaration drift against OpenSSL API changes and unclear ownership transfer for allocated output parameters. Compile coverage plus conversion/load/save round-trip tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/cert-util.h -->
