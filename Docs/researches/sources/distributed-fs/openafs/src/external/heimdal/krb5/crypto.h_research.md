# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto.h

Purpose: internal krb5 crypto interface header defining descriptor structures, flags, usage macros, external algorithm descriptors, and EVP schedule storage.

Important APIs/types/functions: defines `_krb5_key_data`, `krb5_crypto_data`, `F_KEYED`, `F_CPROOF`, `F_DERIVED`, `F_VARIANT`, `F_PSEUDO`, `F_SPECIAL`, `F_DISABLED`, and `F_WEAK`. Defines `salt_type`, `_krb5_key_type`, `_krb5_checksum_type`, `_krb5_encryption_type`, and `_krb5_evp_schedule`. Declares checksum and enctype descriptor symbols and the `_krb5_checksum_types`/`_krb5_etypes` registries.

Control flow: not executable, but it defines the function-pointer contract used by `crypto.c`: key randomization, scheduling, cleanup, checksum/verify, encrypt, EVP cipher lookup, string-to-key, and PRF. Usage macros map Kerberos key usages into encryption, integrity, and checksum constants.

State and persistence behavior: structures describe per-crypto key state and process-global descriptor records. `krb5_crypto_data` persists selected enctype, base key, and cached usage keys until destroy.

Dependencies and integration points: consumed by all `crypto-*.c` files and `crypto.c`; depends on krb5 and EVP types from `krb5_locl.h`.

Risks: any ABI or semantic change here affects all crypto descriptors. Flag combinations define security behavior, including disabled and weak algorithm handling. Function pointers must match descriptor sizes and key schedule layout.

Test signals: build coverage across algorithm macros, descriptor table integrity checks, and compile-time validation that every declared descriptor is provided in the selected build.
