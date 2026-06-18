<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/Kconfig -->
# sources/distributed-fs/ceph-client/crypto/krb5/Kconfig

Purpose: Defines build configuration for the Kerberos 5 crypto library and its optional selftests.

Important APIs/types/functions: `config CRYPTO_KRB5` is a tristate option selecting crypto manager, Kerberos encryption wrapper, authenc, skcipher, hash metadata, HMAC, CMAC, SHA1, SHA256, SHA512, CBC, CTS, AES, and Camellia. `config CRYPTO_KRB5_SELFTESTS` is a bool depending on `CRYPTO_KRB5`.

Control flow: Kconfig selection determines whether the Kerberos crypto module is built and which dependent algorithms are guaranteed available. Enabling selftests compiles and runs additional module-load checks through `krb5_selftest()`.

State and persistence behavior: No runtime state. It persists only as kernel build configuration.

Dependencies and integration points: Intended for network filesystems, as stated in help text. It ensures the Kerberos implementation can instantiate all encryption/checksum names referenced by the profile files.

Risks: Adding an enctype without updating Kconfig selects can produce runtime `-ENOPKG` when a dependent cipher/hash is missing. Selftests are optional, so production builds may lack module-load vector validation.

Test signals: Kconfig dependency resolution, allmodconfig/build tests, module load with and without `CRYPTO_KRB5_SELFTESTS`, and runtime crypto allocation for all selected AES/Camellia/HMAC/CMAC/CTS/CBC algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/Kconfig -->
