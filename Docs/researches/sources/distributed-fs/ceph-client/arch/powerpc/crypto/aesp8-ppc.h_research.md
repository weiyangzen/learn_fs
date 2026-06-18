# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aesp8-ppc.h

Purpose: declares shared Power8 AES assembly entry points and key structures for CBC/CTR/XTS glue.

Important APIs/types/functions: no exported symbols; behavior is expressed through build rules or linker script sections. Source size is 7 lines / 218 bytes.

Control flow enters through Linux crypto API setkey/encrypt/decrypt callbacks, validates request constraints, enables the relevant PowerPC vector/SPE facility only around accelerated blocks, walks scatterlists, and falls back to generic algorithms when SIMD cannot be used safely.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: `linux/types.h`, `crypto/aes.h`. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include using vector/SPE state when preemption or page faults are unsafe, fallback recursion or request-size mistakes, bad IV/tag handling, scatterlist tail bugs, and key validation gaps. Test signals are crypto selftests, tcrypt vectors, AF_ALG tests, forced !crypto_simd_usable fallback, invalid key/auth-size cases, scatterlist fragmentation, and module load/unload.
