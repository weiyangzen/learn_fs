# sources/distributed-fs/ceph-client/lib/crypto/s390/aes.h

## Purpose

This s390 architecture header accelerates AES block encryption and decryption through CP Assist for Cryptographic Functions. It was read as a complete 106-line file.

## Important APIs, Types, and Functions

It defines static keys `have_cpacf_aes128`, `have_cpacf_aes192`, and `have_cpacf_aes256`; implements `aes_preparekey_arch`, `aes_encrypt_arch`, `aes_decrypt_arch`, helper `aes_crypt_s390`, and `aes_mod_init_arch`.

## Control Flow

Key preparation stores the raw key when CPACF supports the selected key length, because the CPACF KM instruction consumes raw AES keys. Unsupported key sizes fall back to generic expanded round keys. Encryption and decryption try `cpacf_km()` first through `aes_crypt_s390`; if the matching static key is disabled, generic AES round-key encryption or decryption is used.

## State and Persistence Behavior

Static keys persist after init. Per-key state stores either raw key bytes for CPACF use or generic expanded round keys depending on feature support at preparation time.

## Dependencies and Integration Points

The header depends on `<asm/cpacf.h>`, s390 CPU feature probing, and generic AES helpers. It is included by the shared AES library's architecture hook path.

## Risks and Edge Cases

The key representation depends on runtime feature support at key preparation time; encrypt/decrypt must use the same static-key assumptions. CPACF query coverage by key length is essential. Raw key retention has secret-memory implications equivalent to expanded-key retention.

## Test Signals

AES known-answer tests, AES-CMAC/CBC-MAC KUnit coverage, s390 builds with and without MSA, and generic fallback comparison validate the hook.
