# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-sse.c

Purpose: implements the SSE2 dynamic backend for EC GF combination code. It emits vectorized loops that operate 16 bytes at a time using SSE registers.

Important APIs: the file exports `ec_code_gen_sse`, an `ec_code_gen_t` named `"sse"` requiring CPU flag `"sse2"`. Its callbacks are `ec_code_sse_prolog`, `epilog`, `load`, `store`, `copy`, `xor2`, and `xorm`; `xor3` is left `NULL`, causing the neutral builder to synthesize XOR3 through copy plus XOR2.

Control flow: `prolog` records the loop address. Each load chooses between linear addressing from `REG_SI + REG_DX` and interleaved addressing through a cached base pointer loaded from a source-pointer array. `store` writes to `REG_DI`, `copy` and `xor2` move/xor SSE registers, and `xorm` XORs memory into an SSE register. `epilog` advances source and destination offsets by 16, tests `REG_DX` against `width - 1`, branches back while more of the chunk remains, then returns.

State and integration: per-builder fields `linear`, `base`, `width`, `bits`, `loop`, and `address` drive emitted addressing. It depends on `ec-code-intel.c` for instruction bytes and on `ec-code.c` for scheduling GF operations. Risks include unaligned SSE memory assumptions, loop termination relying on power-of-two width, and stale `builder->base` for interleaved source arrays. Test signals should compare SSE output to C fallback over linear and interleaved layouts, run with misaligned buffers if supported, and verify CPU detection only selects this backend when `sse2` appears.
