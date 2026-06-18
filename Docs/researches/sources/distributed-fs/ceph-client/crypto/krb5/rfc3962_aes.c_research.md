<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc3962_aes.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/rfc3962_aes.c

Purpose: Defines the RFC3962 AES CTS HMAC-SHA1 Kerberos enctypes for AES-128 and AES-256.

Important APIs/types/functions: Exports `krb5_aes128_cts_hmac_sha1_96` and `krb5_aes256_cts_hmac_sha1_96` as `struct krb5_enctype` metadata. Each binds Kerberos etype/ctype numbers, algorithm names (`krb5enc(hmac(sha1),cts(cbc(aes)))`, `hmac(sha1)`, `sha1`, `cts(cbc(aes))`), key lengths, block/confounder/checksum/hash/PRF lengths, identity random-to-key, and `rfc3961_simplified_profile`.

Control flow: There is no executable function flow. `krb5_api.c` includes these const objects in the supported enctype table, and profile code uses their fields to allocate transforms and size buffers.

State and persistence behavior: Static const enctype metadata only. Prepared transforms created from these fields hold runtime key state elsewhere.

Dependencies and integration points: Depends on `internal.h` declarations and the RFC3961 simplified profile. Kconfig selects AES, CTS, CBC, SHA1, HMAC, and Kerberos encryption wrapper support needed by these names.

Risks: Any mismatch in key/checksum lengths or algorithm names breaks interoperability. SHA1-HMAC-96 is legacy but required for Kerberos compatibility. The metadata assumes identity random-to-key for AES.

Test signals: Kerberos AES-SHA1 known-answer tests, enctype lookup by numeric etype, transform allocation by listed names, key derivation vectors, and encrypt/decrypt/MIC vectors for both 128- and 256-bit variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc3962_aes.c -->
