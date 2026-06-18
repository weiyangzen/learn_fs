# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aesp10-ppc.pl

Purpose: generates Power10 AES key schedule and block encrypt assembly through the ppc-xlate translator.

Important APIs/types/functions: functions `gen_block`; assembly labels/symbols `rcon`, `Lconsts`, `Lset_encrypt_key`, `Loop128`, `L192`, `Loop192`, `L256`, `Loop256`, `Ldone`, `Lenc_key_abort`, `Ldeckey`, `Ldec_key_abort`; build variables/targets `$flavour`, `$LITTLE_ENDIAN`, `$0`, `$FRAME`, `$prefix`, `$sp`, `$vrsave`, `$code.`, `$code.`. Source size is 585 lines / 15452 bytes.

Control flow is straight-line and loop-heavy assembly generated or hand written for crypto hot paths: callers enter exported symbols with pre-expanded keys/state, the code processes full blocks in vectorized loops, handles partial/tail cases where supported, and returns updated counters, hashes, or key schedules.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include register clobbering, endian mistakes, counter/hash update errors, partial-block bugs, generated assembler drift, and CPU feature mismatches. Test signals are known-answer AES/GCM/GHASH vectors, objdump symbol checks, crypto manager selftests, and stress with unaligned buffers.
