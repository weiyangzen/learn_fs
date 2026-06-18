<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/aes_glue.c -->
# sources/distributed-fs/ceph-client/arch/sparc/crypto/aes_glue.c

## Purpose
This file registers AES skcipher implementations accelerated by SPARC64 crypto opcodes for ECB, CBC, and CTR modes.

## Important APIs, Types, and Functions
`struct aes_ops` dispatches key loading and mode operations for 128/192/256-bit keys. `struct crypto_sparc64_aes_ctx` stores the expanded key, selected ops table, key length, and expanded-key length. Key and mode handlers include `aes_set_key_skcipher()`, `ecb_encrypt()`, `ecb_decrypt()`, `cbc_encrypt()`, `cbc_decrypt()`, `ctr_crypt_final()`, and `ctr_crypt()`. Module setup uses `sparc64_has_aes_opcode()`, `aes_sparc64_mod_init()`, and `aes_sparc64_mod_fini()`.

## Control Flow
`setkey` validates AES key length, chooses the ops table, expands the key, and records the expanded length. Mode functions walk scatterlists with `skcipher_walk_virt()`, load encrypt or decrypt keys into the SPARC floating-point/crypto register state, process full blocks through assembly, finish partial CTR tails with one ECB keystream block plus XOR, and clear FPRS with `fprs_write(0)`. Module init checks `sparc64_elf_hwcap` and ASR26 `CFR_AES` before registering skcipher algorithms.

## State and Persistence Behavior
Per-transform state is the expanded key in `crypto_sparc64_aes_ctx`; per-request state is the skcipher walk and IV. Hardware crypto/FPU register state is transient and explicitly cleared after operations. Module registration persists until unload.

## Dependencies and Integration Points
It depends on the kernel crypto skcipher API, generic AES constants, SPARC64 assembly routines, `fpumacro`, `opcodes`, `pstate`, ELF hardware capabilities, and `crop_devid.c` for module device-table aliasing.

## Risks
The code assumes opcode availability after init and relies on correct key-end pointer selection for decrypt operations. Failing to clear FPRS can leak/dirty floating-point state. CTR partial-block handling must increment the counter exactly once. Algorithm priority can shadow generic AES, so selftest failures would affect normal crypto users.

## Test Signals
Run crypto selftests for `ecb(aes)`, `cbc(aes)`, and `ctr(aes)` with 128/192/256-bit keys, scatter-gather splits, misaligned buffers, partial CTR lengths, and unsupported-hardware module load paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/aes_glue.c -->
