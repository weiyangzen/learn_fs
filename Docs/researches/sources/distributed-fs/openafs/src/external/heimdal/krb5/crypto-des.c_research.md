# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-des.c

Purpose: defines single-DES key handling, legacy checksum types, and DES enctypes when weak crypto support is compiled in.

Important APIs/types/functions: `krb5_DES_random_key()`, `krb5_DES_schedule_old()`, and `krb5_DES_random_to_key()` implement DES key generation, old schedule setup, parity, and weak-key avoidance. Checksum descriptors include `_krb5_checksum_crc32`, `_krb5_checksum_rsa_md4`, `_krb5_checksum_rsa_md4_des`, and `_krb5_checksum_rsa_md5_des`. Enctype descriptors include DES CBC CRC/MD4/MD5/NONE plus CFB64 and PCBC pseudo enctypes.

Control flow: random keys are generated until not weak and then parity-adjusted. Random-to-key copies input, sets odd parity, and XORs weak keys. DES CBC helpers reset IVs either to zero or the key bytes before in-place EVP encryption. CFB64 and PCBC use legacy DES APIs directly.

State and persistence behavior: descriptors are global; key schedules are per-crypto context. No durable state is written.

Dependencies and integration points: compiled under `HEIM_WEAK_CRYPTO`; references shared DES helpers, EVP DES CBC, CRC helpers, MD4/MD5, and generic crypto table registration.

Risks: all DES enctypes are marked `F_DISABLED|F_WEAK` and some are pseudo protocol helpers. Enabling them is security-sensitive. Old DES APIs and weak-key/parity behavior are compatibility-critical. Some checksum digest failures abort.

Test signals: weak-crypto enable/disable checks, DES parity and weak-key tests, CBC CRC/MD4/MD5 round trips under weak builds, and verification that disabled enctypes are rejected by default.
