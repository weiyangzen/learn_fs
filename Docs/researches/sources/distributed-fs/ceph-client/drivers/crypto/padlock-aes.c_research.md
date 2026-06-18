<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/padlock-aes.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/padlock-aes.c

Purpose: registers VIA PadLock ACE AES cipher and ECB/CBC skcipher implementations using x86 `rep xcrypt*` instructions with CPU-feature gating and erratum workarounds.

Important APIs and functions: `aes_set_key()` validates key size, prepares PadLock control words, stores encryption/decryption expanded keys, and invalidates per-CPU cached control words. `padlock_aes_encrypt()`/`padlock_aes_decrypt()` implement single-block cipher API. `ecb_aes_encrypt()`/`ecb_aes_decrypt()` and `cbc_aes_encrypt()`/`cbc_aes_decrypt()` walk skcipher virtual mappings and issue PadLock instructions. `padlock_reset_key()` forces hardware key reload when the per-CPU control word changes.

Control flow: module init checks `X86_FEATURE_XCRYPT` and `XCRYPT_EN`, registers the base AES cipher plus ECB/CBC skcipher algorithms, and enables larger prefetch-copy workarounds for VIA Nano family/model/stepping 6/15/2. Encryption chunks use direct instruction calls unless the PadLock prefetch window would cross a page boundary, in which case stack-aligned copy buffers are used.

State and persistence: transform context stores aligned encryption and decryption key schedules, control words, and pointer to decryption key data. Per-CPU `paes_last_cword` caches the last control word used by hardware.

Dependencies and integration: x86 CPU feature matching, PadLock alignment constants, AES software key expansion fallback for key schedules, skcipher walk API, and raw inline assembly opcodes.

Risks and test signals: PadLock prefetch can read beyond the requested block; page-boundary copy guards are critical. The decrypt single-block path resets/stores the encrypt control word around decrypt state, so control-word cache tests matter. Test AES known vectors for 128/192/256-bit keys, ECB/CBC multi-page buffers, page-end inputs, VIA Nano stepping 2 workaround, CPU hotplug/per-CPU cache invalidation after setkey, and module load on unsupported CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/padlock-aes.c -->
