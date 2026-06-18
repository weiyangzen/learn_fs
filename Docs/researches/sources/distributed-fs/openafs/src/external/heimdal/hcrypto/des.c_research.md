## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/des.c

Purpose: Heimdal hcrypto DES implementation with OpenSSL/libdes-compatible APIs. It covers key parity and weak-key checks, DES key schedule generation, single DES, 3DES EDE, CBC/PCBC/CFB64 modes, CBC checksum, legacy string-to-key/password helpers, and an internal IP/FP sanity test.

Important APIs/functions: key APIs include `DES_set_odd_parity`, `DES_check_key_parity`, `DES_is_weak_key`, `DES_set_key`, `DES_set_key_unchecked`, `DES_set_key_checked`, and `DES_key_sched`. Block/mode APIs include `DES_encrypt`, `DES_ecb_encrypt`, `DES_ecb3_encrypt`, `DES_cbc_encrypt`, `DES_pcbc_encrypt`, `DES_ede3_cbc_encrypt`, `DES_cfb64_encrypt`, and `DES_cbc_cksum`. Legacy password/key helpers are `DES_string_to_key` and `DES_read_password`. Internal helpers include `load`, `store`, `IP`, `FP`, `_des3_encrypt`, `desx`, and `bitswap8`.

Control flow: key setup loads the 8-byte key into two 32-bit words, uses generated PC1 tables to split C/D halves, rotates by DES schedule, uses PC2 tables to form 16 pairs of subkey words, and stores them in S-box-friendly order. `DES_encrypt()` applies initial permutation, `desx()` for 16 rounds, and final permutation. CBC/PCBC/3DES modes loop over full blocks and zero-pad partial final blocks; 3DES performs EDE order for encryption and reverse order for decryption. CFB64 maintains byte offset `*num`, encrypts IV as keystream, and updates IV differently for encrypt/decrypt. `DES_string_to_key()` folds password bytes into a key, fixes parity, avoids weak keys, computes a CBC checksum, and fixes parity again.

State and persistence: caller-owned `DES_key_schedule` stores 32 round-key words. IVs for 3DES CBC and CFB64 are persisted back to caller; single DES CBC and PCBC clear local `uiv` but notably do not store final IV back in `DES_cbc_encrypt()`/`DES_pcbc_encrypt()`, whereas `DES_ede3_cbc_encrypt()` does. `DES_cfb64_encrypt()` persists both `iv` and `num`. Weak-key table and S/P boxes are static read-only-by-convention data.

Dependencies: `<config.h>`, `krb5-types.h`, `roken.h` for `ct_memcmp`, `ui.h` for `UI_UTIL_read_pw_string`, and generated `des-tables.h`. Uses standard C library, `assert`, and abort for `_DES_ipfp_test()`.

Integration points: public declarations live in `des.h`; EVP hcrypto provider wraps DES-CBC and DES-EDE3-CBC. Kerberos legacy code may use PCBC, CBC checksum, and string-to-key. Symbol names are renamed through `des.h` to `hc_` names.

Risks: DES and RC4-era APIs are cryptographically legacy; comments warn DES is withdrawn and PCBC/checksum/string-to-key should remain legacy. Table-driven DES and weak-key comparison are not uniformly constant-time except `DES_is_weak_key()` uses `ct_memcmp`. `DES_set_key_unchecked()` skips parity/weak-key validation. Partial-block modes zero-pad silently, which may not match protocol padding. The IV persistence difference between single DES CBC and 3DES CBC is a compatibility subtlety and potential caller surprise. Stack key material is only partially zeroized in some functions.

Test signals: FIPS DES and 3DES known-answer vectors, parity/weak-key checks, key schedule validation, CBC/PCBC/CFB64 round trips including partial blocks and `num` continuation, CBC checksum vectors, string-to-key compatibility vectors, `_DES_ipfp_test()`, and EVP DES integration.
