# sources/distributed-fs/openafs/src/crypto/rfc3961/kernel/algs.c

This kernel-specific file limits RFC3961 algorithms to the minimal set needed in kernel space. It exports `_krb5_checksum_types` with SHA1 and AES128/AES256 HMAC-SHA1 checksum types, and `_krb5_etypes` with AES256-CTS-HMAC-SHA1 and AES128-CTS-HMAC-SHA1 encryption types. It also computes `_krb5_num_checksums` and `_krb5_num_etypes`.

There is no dynamic control flow or persistence; state is static global algorithm tables consumed by Heimdal crypto lookup routines. Dependencies are `krb5_locl.h` and upstream symbols for the selected checksum/encryption implementations.

Integration is kernel RFC3961 dispatch. Risks are unsupported enctypes/checksums being unavailable in kernel even if public headers list them, and table order affecting default/preferred algorithm selection. Test signals are kernel tests for AES128/AES256 enctypes and clean rejection of DES/ARCFOUR/MD5 paths.
