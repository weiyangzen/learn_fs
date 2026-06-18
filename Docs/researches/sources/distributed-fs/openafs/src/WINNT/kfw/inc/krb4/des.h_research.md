## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/des.h

Purpose: Declares the Kerberos IV DES block, key schedule, checksum, encryption, key-parity, and random-key interfaces used by legacy K4 and AFS token code.

Important APIs/types/functions: Defines `des_cblock[8]`, `des_key_schedule[16]`, `DES_KEY_SZ`, `DES_ENCRYPT`, `DES_DECRYPT`, and compatibility aliases such as `C_Block`, `Key_schedule`, `key_sched`, and `cbc_cksum`. Declares `quad_cksum`, `des_key_sched`, `des_ecb_encrypt`, `des_pcbc_encrypt`, `des_is_weak_key`, `des_fixup_key_parity`, `des_check_key_parity`, `des_new_random_key`, random generator seed/init functions, and `des_cbc_cksum`.

Control flow: Header-only declaration surface. Runtime users typically derive or obtain a `des_cblock`, call `des_key_sched`, then pass the schedule to CBC/PCBC/ECB or checksum routines.

State and persistence: The random generator APIs imply process-local PRNG state in the DES library. No persistence is declared here.

Dependencies and integration points: Includes `mit_copy.h` and `conf.h`; depends on K4 calling-convention macros and `KRB_INT32`. Used by `krb4/krb.h` and by AFS/Kerberos IV token compatibility.

Risks: DES is obsolete cryptography. Key schedule layout is ABI-sensitive and old `FAR` annotations matter for legacy builds. `des_cblock_print` depends on `stdout` but this header does not include `stdio.h`.

Test signals: ABI-size checks for `des_cblock` and `des_key_schedule`; tests for weak-key and parity handling; known-answer tests for DES CBC/PCBC/checksums; compile tests with and without `NCOMPAT`.
