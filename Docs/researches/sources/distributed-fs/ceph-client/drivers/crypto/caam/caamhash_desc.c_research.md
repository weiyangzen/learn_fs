# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamhash_desc.c

## Purpose
`caamhash_desc.c` contains shared descriptor constructors for CAAM hash operations. It centralizes the descriptor command sequences used by both the classic job-ring ahash implementation and the DPAA2 QI2 ahash implementation.

## Important APIs, Types, And Functions
The exported functions are `cnstr_shdsc_ahash()` for MDHA class-2 hashes/HMACs and `cnstr_shdsc_sk_hash()` for symmetric-key hash algorithms implemented with class-1 AES XCBC/CMAC. Both take a descriptor buffer, `struct alginfo`, operation state (`OP_ALG_AS_*`), digest/context sizes, and other mode-specific metadata. `cnstr_shdsc_ahash()` also accepts `import_ctx` and SEC era because pre-era-6 HMAC uses split keys while era 6+ can use descriptor key protocol generation.

## Control Flow
`cnstr_shdsc_ahash()` initializes a serial shared descriptor, conditionally loads or derives HMAC key material for all states except update, optionally imports previous class-2 context, appends the class-2 operation, calculates variable input length, consumes message bytes from the sequence input FIFO, and stores digest/context bytes to sequence output. `cnstr_shdsc_sk_hash()` initializes a save-context descriptor, emits a shared-state skip jump, loads immediate or DMA key material depending on INIT versus UPDATE/FINAL and XCBC versus CMAC, optionally restores class-1 context, runs the class-1 operation, consumes message bytes, stores context, and for XCBC INIT saves K1 back to key memory.

## State And Persistence Behavior
The functions do not own runtime state; they write command words into caller-provided descriptor buffers. Persistent behavior is encoded in descriptor sharing semantics: skip jumps avoid reloading shared key/context after the descriptor has been shared, and `HDR_SAVECTX` supports class-1 context reuse. Key and context DMA addresses referenced through `alginfo` remain caller-owned.

## Dependencies And Integration Points
The constructors depend on `desc_constr.h` helpers such as `init_sh_desc`, `append_jump`, `append_key_as_imm`, `append_proto_dkp`, `append_seq_load`, `append_operation`, `append_seq_fifo_load`, and `append_seq_store`. They integrate with `caamhash.c` and `caamalg_qi2.c`, which choose descriptor state variants and DMA-sync the generated descriptors before hardware use.

## Risks
Descriptor length and command ordering are hardware-contract sensitive. Incorrect `import_ctx`, digest size, context length, era, or `alginfo` key fields will produce descriptors that either fail in hardware or compute incorrect hashes. The era split between precomputed split-key loading and DKP must remain aligned with CAAM hardware support. XCBC has extra key-save behavior for INIT that must match the caller's key DMA mapping direction.

## Test Signals
Descriptor-level confidence comes from ahash Crypto API selftests across HMAC SHA/MD5, unkeyed SHA/MD5, XCBC-AES, and CMAC-AES on both first/update/final and digest paths. Debug descriptor dumps and CAAM status decoding help diagnose bad command sequences.
