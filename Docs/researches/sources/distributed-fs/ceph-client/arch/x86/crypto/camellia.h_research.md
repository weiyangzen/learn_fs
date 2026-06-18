# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia.h

Purpose: Architecture-local Camellia interface header defining the context layout and assembler/glue contracts shared across scalar, AVX, and AVX2 implementations.

Important APIs/types/functions: defines key/block sizes, `CAMELLIA_TABLE_BYTE_LEN`, `CAMELLIA_PARALLEL_BLOCKS`, and `struct camellia_ctx` containing `u64 key_table[34]` plus `u32 key_length`. Declares `__camellia_setkey`, scalar block functions, 2-way functions, 16-way AVX/AES-NI functions, and `camellia_decrypt_cbc_2way`. Provides inline wrappers that hide the boolean XOR parameter for encryption.

Control flow: no standalone execution. The inline wrappers route normal encrypt calls to `__camellia_enc_blk(..., false)` and CBC/XOR helpers to `__camellia_enc_blk(..., true)`, and similarly for 2-way operation.

State and persistence: establishes the persistent transform state layout. The key table stores expanded subkeys; `key_length` controls whether 24- or 32-round schedules are used by both C and assembly.

Dependencies and integration points: included by Camellia glue and assembly-coupled C code in this directory. Includes `crypto/b128ops.h`, Linux crypto/kernel headers, and exposes symbols used across separate modules through `EXPORT_SYMBOL_GPL` in `camellia_glue.c` and AVX glue.

Risks: this header is an ABI contract with hand-written assembly. Changing `CAMELLIA_TABLE_BYTE_LEN`, field order, prototypes, or wrapper semantics requires synchronized assembly offset changes. The header declares 16-way functions but the AVX2 glue also declares 32-way functions locally.

Test signals: build tests catch prototype drift; runtime vectors for scalar, 2-way, 16-way, and 32-way paths catch layout or key-length mistakes.
