# sources/distributed-fs/ceph-client/crypto/des_generic.c

## Purpose
`des_generic.c` registers generic DES and Triple-DES EDE single-block cipher algorithms. It is a thin crypto API wrapper around DES key schedule and block routines from `<crypto/internal/des.h>`.

## Important APIs, Types, And Functions
- `des_setkey()` calls `des_expand_key()` and maps weak-key handling to crypto flags.
- `des3_ede_setkey()` calls `des3_ede_expand_key()` with the same weak-key flag behavior.
- `crypto_des_encrypt()` / `crypto_des_decrypt()` and `crypto_des3_ede_encrypt()` / `crypto_des3_ede_decrypt()` invoke internal DES routines using transform context.
- `des_algs[2]` registers `des` / `des-generic` and `des3_ede` / `des3_ede-generic` as `CRYPTO_ALG_TYPE_CIPHER`.

## Control Flow
Setkey expands the supplied key into the transform context. If the lower-level expansion reports `-ENOKEY`, the wrapper either rejects it as `-EINVAL` when `CRYPTO_TFM_REQ_FORBID_WEAK_KEYS` is set or accepts it otherwise. Other errors clear the context. Encrypt and decrypt are direct single-block calls.

## State And Persistence
The transform context stores a `struct des_ctx` or `struct des3_ede_ctx` key schedule. State lasts for the transform lifetime. No IV, request, or persistent global state is stored beyond algorithm registration.

## Dependencies And Integration Points
DES is exposed as a base cipher for templates such as ECB, CBC, CTR, and authenc combinations. Testmgr includes standalone DES/DES3 vectors and composed mode vectors.

## Risks And Edge Cases
DES is cryptographically obsolete, and weak-key handling is flag-dependent. Context wipe on key setup error is important to avoid retaining prior schedules. The file does not implement mode-level padding or IV handling; consumers must use templates correctly.

## Test Signals
`testmgr.h` includes `des_tv_template`, `des3_ede_tv_template`, DES/DES3 CBC and CTR vectors, and AEAD/authenc combinations. Tests should verify weak-key rejection when `CRYPTO_TFM_REQ_FORBID_WEAK_KEYS` is requested and normal encrypt/decrypt known-answer vectors.
