# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-modes.S

## Purpose
Provides SPE-backed AES single-block and mode operations for PowerPC: ECB, CBC, CTR, and XTS. It wraps the lower-level `ppc_encrypt_block` and `ppc_decrypt_block` helpers with mode-specific data loading, IV/tweak handling, endian conversion, and register preservation.

## Important APIs, Types, and Functions
Exports `_GLOBAL(ppc_encrypt_aes)`, `_GLOBAL(ppc_decrypt_aes)`, `_GLOBAL(ppc_encrypt_ecb)`, `_GLOBAL(ppc_decrypt_ecb)`, `_GLOBAL(ppc_encrypt_cbc)`, `_GLOBAL(ppc_decrypt_cbc)`, `_GLOBAL(ppc_crypt_ctr)`, `_GLOBAL(ppc_encrypt_xts)`, and `_GLOBAL(ppc_decrypt_xts)`. Register aliases are imported from `aes-spe-regs.h`. Macros include endian-aware `LOAD_DATA`, `SAVE_DATA`, `LOAD_IV`, `SAVE_IV`, `INITIALIZE_CRYPT`, `FINALIZE_CRYPT`, `START_KEY`, `ENDIAN_SWAP`, and `GF128_MUL`.

## Control Flow
Single-block encrypt/decrypt loads one 16-byte block, xors the first round key, branches to the core block routine, xors the final round key, and stores output. ECB loops whole 16-byte blocks until `rLN` drops below one block. CBC encryption xors input with the current IV and stores each ciphertext as the next IV; CBC decryption processes from the end backward so previous ciphertext is available for chaining, then handles the first block against the original IV. CTR encrypts counter blocks, xors input with the keystream, increments the 128-bit counter, and has a bytewise partial-block tail. XTS optionally encrypts the IV with the tweak key, xors each block with the tweak, encrypts/decrypts, xors the tweak again, then multiplies the tweak by x in GF(2^128) per block.

## State and Persistence
The mode routines update caller-provided IV/tweak buffers for CBC, CTR, and XTS. Stack frames save nonvolatile GPR/SPE state and `FINALIZE_CRYPT` wipes saved sensitive stack slots before returning. No persistent globals are modified.

## Dependencies and Integration Points
Depends on `aes-spe-regs.h`, `PPC_AES_4K_ENCTAB`, `PPC_AES_4K_DECTAB`, and the lower-level SPE AES core functions in the same PowerPC crypto directory. The C AES glue calls these routines inside an SPE-enabled, preemption-disabled region.

## Risks
CBC and XTS assume whole-block input, while CTR accepts partial bytes; callers must satisfy each mode contract. The table backend can leak through cache timing. IV/tweak state is modified in place, so interrupted or retried higher-level calls must respect that side effect. Endian pointer adjustment macros differ substantially between BE and LE and are high-risk for off-by-one errors.

## Test Signals
Use mode known-answer tests for AES-ECB/CBC/CTR/XTS, especially CTR partial tails, CBC decrypt with multiple blocks, and XTS tweak progression. Cross-check IV/tweak output buffers after calls, not just ciphertext/plaintext.
