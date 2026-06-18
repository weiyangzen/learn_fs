<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/camellia_glue.c -->
# sources/distributed-fs/ceph-client/arch/sparc/crypto/camellia_glue.c

## Purpose
This file registers Camellia cipher and skcipher implementations accelerated by SPARC64 Camellia opcodes.

## Important APIs, Types, and Functions
`struct camellia_sparc64_ctx` stores encryption and decryption key tables plus key length. Key setup uses `camellia_set_key()` and `camellia_set_key_skcipher()`. Single-block cipher APIs are `camellia_encrypt()` and `camellia_decrypt()`. Skcipher paths are `__ecb_crypt()`, `ecb_encrypt()`, `ecb_decrypt()`, `cbc_encrypt()`, and `cbc_decrypt()`. Module setup uses `sparc64_has_camellia_opcode()`, `camellia_sparc64_mod_init()`, and `camellia_sparc64_mod_fini()`.

## Control Flow
Key setup validates 16/24/32-byte keys and calls the assembly key expansion to fill encrypt/decrypt schedules. Cipher and skcipher paths choose encrypt or decrypt tables, select 3-grand-round assembly for 128-bit keys or 4-grand-round assembly for longer keys, walk request buffers, process full blocks, return leftovers to the skcipher walker, and clear FPRS. Module init gates registration on `HWCAP_SPARC_CRYPTO` plus ASR26 `CFR_CAMELLIA`, then registers both the single-block cipher and ECB/CBC skciphers.

## State and Persistence Behavior
Each crypto transform owns its key schedules. Request state is limited to buffer walkers and IVs. Hardware VIS/FPU state is transient and cleared after operations. Registered algorithms persist until module exit.

## Dependencies and Integration Points
It depends on the crypto API, SPARC64 Camellia assembly entry points, opcode capability bits, FPU state helpers, ELF hwcap, and `crop_devid.c` device-table aliasing.

## Risks
Algorithm registration must unwind correctly if skcipher registration fails after cipher registration. Key schedule length and assembly function selection must match key size. As with AES, stale FPU state or incorrect scatterlist remainder handling can affect unrelated kernel code or corrupt crypto output.

## Test Signals
Run crypto manager Camellia tests for cipher, `ecb(camellia)`, and `cbc(camellia)` with 128/192/256-bit keys, scatterlist splits, IV mutation checks, unsupported CPU load failure, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/camellia_glue.c -->
