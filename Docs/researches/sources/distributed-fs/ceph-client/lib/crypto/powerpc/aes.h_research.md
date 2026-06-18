# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes.h

## Purpose
Provides PowerPC AES architecture hooks for the generic AES library. It selects between SPE support when `CONFIG_SPE` is enabled and POWER8 vector crypto support otherwise, with generic fallback when the accelerated key format cannot be used.

## Important APIs, Types, and Functions
Defines `aes_preparekey_arch`, `aes_encrypt_arch`, `aes_decrypt_arch`, and `aes_mod_init_arch`. In the SPE branch it references `ppc_expand_key_*`, `ppc_generate_decrypt_key`, `ppc_encrypt_aes`, and `ppc_decrypt_aes`. In the POWER8 branch it exports and calls `aes_p8_set_encrypt_key`, `aes_p8_set_decrypt_key`, `aes_p8_encrypt`, `aes_p8_decrypt`, CBC/CTR/XTS helpers, `is_vsx_format`, and `rndkey_from_vsx`.

## Control Flow
For SPE, key preparation directly expands SPE schedules and encryption/decryption enters an SPE region around one assembly block call. For POWER8, module init enables a static key when CPU vector crypto is available. Key preparation uses VSX if the static key and `may_use_simd()` are true; otherwise it generates generic round keys and marks the POWER8 key format invalid with `nrounds = 0`. Encrypt/decrypt use POWER8 assembly when the key is in VSX format and SIMD is usable, convert VSX keys to generic format for rare non-SIMD contexts, or fall back to generic AES directly.

## State and Persistence
The `have_vec_crypto` static branch persists CPU feature availability after init. Prepared key objects persist either POWER8 VSX schedules or generic schedules. The POWER8 path disables preemption and page faults around kernel VSX use, while the SPE path disables preemption around SPE use.

## Dependencies and Integration Points
Includes PowerPC SIMD/VSX/SPE, CPU feature, preemption, and uaccess headers. It integrates with common AES types such as `struct aes_enckey`, `struct aes_key`, `union aes_enckey_arch`, and generic AES helpers from the crypto library.

## Risks
The dual key-format logic is subtle: keys prepared under VSX may later be used where SIMD is unavailable, requiring exact `rndkey_from_vsx` conversion. Pagefault and preemption boundaries must remain paired. CPU feature checks must match the assembly instruction set actually emitted by `aesp8-ppc.pl`.

## Test Signals
Run AES self-tests with forced SIMD-enabled and SIMD-disabled contexts, including decryption paths that convert VSX inverse keys. Boot/module init on CPUs with and without POWER8 vector crypto should validate static-key gating.
