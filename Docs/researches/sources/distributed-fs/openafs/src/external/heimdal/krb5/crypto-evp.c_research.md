# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-evp.c

Purpose: implements the generic EVP scheduling and encryption helpers used by AES, DES, DES3, and RC4 key types.

Important APIs/types/functions: `_krb5_evp_schedule()` initializes encryption and decryption `EVP_CIPHER_CTX` objects from a key type's `evp()` cipher. `_krb5_evp_cleanup()` cleans those contexts. `_krb5_evp_encrypt()` performs normal in-place ciphering with caller IV or zero IV. `_krb5_evp_encrypt_cts()` implements CBC ciphertext stealing for AES CTS and related enctypes.

Control flow: scheduling creates separate encrypt/decrypt contexts. Normal encryption resets the IV on the selected context, then calls `EVP_Cipher()`. CTS validates length, handles exactly one block as normal CBC, and otherwise performs the final two-block CTS transformation differently for encryption and decryption while updating the caller IV when supplied.

State and persistence behavior: EVP contexts are stored in the per-key schedule allocated by `crypto.c`. The static `zero_ivec` is read-only. No file or process state is persisted.

Dependencies and integration points: depends on EVP cipher APIs and `_krb5_evp_schedule` storage defined in `crypto.h`. Called through enctype descriptor function pointers.

Risks: EVP contexts are reused, so IV reinitialization must happen before every operation. CTS boundary cases are fragile, especially one-block, two-block, and non-block-multiple lengths. Allocation failure in zero-IV setup is returned, while some EVP failures are not explicitly checked.

Test signals: CBC round trips with explicit and null IV, AES CTS known-answer tests for exact one block, partial final block, and long multi-block messages, plus IV update checks.
