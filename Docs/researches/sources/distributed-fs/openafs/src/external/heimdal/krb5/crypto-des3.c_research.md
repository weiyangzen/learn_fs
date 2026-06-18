# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-des3.c

Purpose: defines triple-DES Kerberos key types, checksums, enctypes, and random-to-key conversion.

Important APIs/types/functions: `DES3_random_key()` generates three non-weak DES blocks with odd parity. `keytype_des3` is used for old DES3 when enabled, while `keytype_des3_derived` uses derived-key salts. `_krb5_checksum_rsa_md5_des3` and `_krb5_checksum_hmac_sha1_des3` provide keyed checksums. Enctype descriptors cover `des3-cbc-md5`, `des3-cbc-sha1`, `old-des3-cbc-sha1`, and pseudo `des3-cbc-none`. `_krb5_DES3_random_to_key()` maps 21 random bytes into 24 DES key bytes with parity and weak-key correction.

Control flow: generic crypto selects DES3 descriptors, schedules EVP `EVP_des_ede3_cbc`, applies either old or derived keying semantics, and encrypts through `_krb5_evp_encrypt()`. Random-to-key fills each 8-byte DES block from 7 bytes plus parity synthesis.

State and persistence behavior: descriptor state is global and immutable apart from flags. Key material and schedules are per-crypto context and wiped by generic cleanup.

Dependencies and integration points: depends on DES APIs, shared DES checksum helpers, EVP, salt arrays, and conditional `DES3_OLD_ENCTYPE` inclusion.

Risks: triple-DES is legacy but not marked weak in the same way as single DES. Old enctypes lack modern derived-key behavior. Random-to-key bit packing is subtle and must preserve parity and weak-key handling.

Test signals: DES3 random-to-key vectors, DES3 CBC round trips, HMAC-SHA1-DES3 checksum verification, and build variants with and without old DES3 enctypes.
