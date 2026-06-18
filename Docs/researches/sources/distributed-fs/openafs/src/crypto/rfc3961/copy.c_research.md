# sources/distributed-fs/openafs/src/crypto/rfc3961/copy.c

This file supplies a few copy/free helpers from Heimdal without importing a larger dependency file. `der_copy_octet_string` allocates and copies `krb5_data`; `copy_EncryptionKey` zeroes the destination, copies keytype, and copies keyvalue; `free_Checksum` frees the checksum data.

State is heap allocation owned by the caller and freed through `krb5_data_free`. Dependencies are `krb5_locl.h`, `malloc`, `memcpy`, `memset`, `ENOMEM`, and RFC3961 data/keyblock types. Integration is upstream crypto functions that expect ASN.1 copy helpers.

Risks include zero-length allocation behavior, no cleanup of partially initialized structures beyond simple cases, and dependence on the active malloc macro in kernel builds. Test signals are keyblock copy/free tests, zero-length data tests, and failure-path tests for allocation returning NULL.
