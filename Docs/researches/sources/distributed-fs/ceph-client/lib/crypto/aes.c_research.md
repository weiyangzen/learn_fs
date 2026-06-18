# sources/distributed-fs/ceph-client/lib/crypto/aes.c

## Purpose
This file implements the generic AES block cipher library, exports S-box and T-table data, provides key preparation/encryption/decryption wrappers, and implements AES-CMAC, AES-XCBC-MAC, and AES-CBC-MAC helper APIs.

## Important APIs, Types, and Functions
Exported data includes `crypto_aes_sbox`, `crypto_aes_inv_sbox`, `aes_enc_tab`, and `aes_dec_tab`. Exported APIs include `aes_expandkey()`, `aes_preparekey()`, `aes_prepareenckey()`, `aes_encrypt()`, `aes_decrypt()`, `aes_cmac_preparekey()`, `aes_xcbcmac_preparekey()`, `aes_cmac_update()`, `aes_cmac_final()`, `aes_cbcmac_update()`, and `aes_cbcmac_final()`. Internal helpers include `aes_expandkey_generic()`, `aes_encrypt_generic()`, `aes_decrypt_generic()`, MixColumns helpers, and optional arch hooks from `aes.h`.

## Control Flow
Key preparation validates key length, computes round count, and either calls an arch `aes_preparekey_arch()` or the generic key expansion. Encryption/decryption wrappers call arch hooks that may be generic or accelerated. CMAC preparation derives subkeys by encrypting zero and multiplying in GF(2^128); update paths buffer partial blocks, run CBC-MAC blocks, and finalization applies the complete/incomplete final subkey before one last AES encryption. Module init runs architecture init and optional FIPS CMAC selftest.

## State and Persistence
Persistent state lives in caller-owned key/context structs: AES round keys, inverse keys, CMAC subkeys, CBC-MAC chaining value, partial block, and counters. File-scope static data is immutable. No on-disk persistence exists.

## Dependencies and Integration Points
It depends on `<crypto/aes.h>`, `<crypto/aes-cbc-macs.h>`, crypto utils, unaligned access helpers, module exports, and optional arch headers selected through `CONFIG_CRYPTO_LIB_AES_ARCH`. AES-GCM and AES-CFB in this subset build on these APIs.

## Risks and Test Signals
Risks include table-based AES cache timing leakage on CPUs without AES instructions, key-length validation mistakes, CMAC final-block edge cases, namespace export misuse, and arch/generic behavior divergence. Test signals include crypto selftests, FIPS CMAC test, AES known-answer vectors, in-place CMAC/CBC-MAC updates, and arch fallback comparison.
