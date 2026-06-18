## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/des.h

Purpose: MIT Kerberos V distribution's Kerberos IV DES compatibility header, with newer ABI guards and Windows/Mac handling.

Important APIs/types/functions: Defines `DES_INT32`/`DES_UINT32`, `des_cblock`, a safer `des_key_schedule[16]`, DES constants and K4 compatibility aliases, and prototypes for `des_key_sched`, `des_pcbc_encrypt`, `des_quad_cksum`, `des_cbc_cksum`, `des_string_to_key`, `afs_string_to_key`, password reading, ECB/CBC encryption, parity, weak-key, random-key, and `des_cblock_print_file`.

Control flow: Consumers build a key schedule from an 8-byte key, then call encryption/checksum routines. The header suppresses public prototypes for internal crypto builds via `KRB5INT_CRYPTO_DES_INT`.

State and persistence: Declares random generator seed/init APIs with implementation-owned process state. No persistent data.

Dependencies and integration points: Includes `<win-mac.h>` on Windows and `stdio.h` for `FILE`. Used by `KerberosIV/krb.h` and K4 compatibility inside K5/OpenAFS code.

Risks: DES is obsolete. The header documents historical ABI changes, especially key schedule layout and return types, so mixing library/header versions can corrupt memory or link incorrectly. Mac packing pragmas affect structure layout.

Test signals: ABI-size checks, known-answer DES tests, random-key seed behavior, compile tests with `_WIN32`, `KRB4`, `NCOMPAT`, and `KRB5INT_CRYPTO_DES_INT`.
