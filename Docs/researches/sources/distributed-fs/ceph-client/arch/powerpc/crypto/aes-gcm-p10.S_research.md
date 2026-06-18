# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes-gcm-p10.S

Purpose: implements the Power10 VSX/crypto stitched AES-GCM encrypt/decrypt and GHASH update hot paths.

Important APIs/types/functions: assembly labels/symbols `__More_1x`, `__Loop_1x`, `__Loop_aes_1state`, `__Encrypt_1x`, `__Loop_aes_pstate`, `__Write_partial`, `__Encrypt_partial`, `__Inp_msg_less16`, `__Combine_continue`, `__Loop_aes_cpstate`, `__Write_combine_partial`, `__Encrypt_combine_partial`, `__Update_partial_ghash`, `__Clear_partial_flag`, `__no_update`, `__Process_encrypt`, `__Process_8x_enc`, `__PreLoop_aes_state`, and 15 more. Source size is 1236 lines / 25925 bytes.

Control flow is straight-line and loop-heavy assembly generated or hand written for crypto hot paths: callers enter exported symbols with pre-expanded keys/state, the code processes full blocks in vectorized loops, handles partial/tail cases where supported, and returns updated counters, hashes, or key schedules.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: `asm/ppc_asm.h`, `linux/linkage.h`. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include register clobbering, endian mistakes, counter/hash update errors, partial-block bugs, generated assembler drift, and CPU feature mismatches. Test signals are known-answer AES/GCM/GHASH vectors, objdump symbol checks, crypto manager selftests, and stress with unaligned buffers.
