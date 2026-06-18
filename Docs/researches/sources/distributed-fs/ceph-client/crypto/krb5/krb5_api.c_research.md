<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/krb5_api.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/krb5_api.c

Purpose: Exposes the public kernel Kerberos 5 crypto API: enctype lookup, buffer sizing, transform preparation, encryption/decryption, MIC generation/verification, and module selftest startup.

Important APIs/types/functions: `krb5_supported_enctypes[]` lists AES128/256 SHA1, AES128/256 SHA2, and Camellia128/256 CMAC enctypes. Exported functions include `crypto_krb5_find_enctype()`, `crypto_krb5_how_much_buffer()`, `crypto_krb5_how_much_data()`, `crypto_krb5_where_is_the_data()`, `crypto_krb5_prepare_encryption()`, `crypto_krb5_prepare_checksum()`, `crypto_krb5_encrypt()`, `crypto_krb5_decrypt()`, `crypto_krb5_get_mic()`, and `crypto_krb5_verify_mic()`.

Control flow: Callers find an enctype by numeric ID, compute buffer layout, prepare an AEAD or shash by deriving profile-specific keys, then call encrypt/decrypt or MIC helpers. The top-level cryptographic operations validate basic scatterlist bounds and dispatch to `krb5->profile` methods. Module init runs `krb5_selftest()` when configured.

State and persistence behavior: The supported enctype array and module metadata are static. Prepared crypto handles returned to callers hold derived key state and must be freed by callers with crypto API free functions. Temporary derived key buffers are freed after transform setup.

Dependencies and integration points: Exports symbols for network filesystem clients and other in-kernel Kerberos users. Integrates with crypto AEAD/shash allocation by algorithm names from enctype tables and maps missing algorithms to `-ENOPKG`.

Risks: Buffer offset/length helpers must match profile implementations exactly or callers may allocate too little space or authenticate wrong bytes. The API trusts caller scatterlists after bounds checks. Key buffers must be freed on all error paths. Optional selftests mean unsupported vectors can escape if disabled.

Test signals: Lookup each supported enctype, prepare encryption/checksum transforms, encrypt/decrypt and MIC round trips over scatterlists, invalid offset/length warnings returning `-EMSGSIZE`, missing algorithm handling, and module-load selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/krb5_api.c -->
