# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_util.h

Purpose: Provides the inline assembly wrapper for the s390 DFLTCC instruction plus utility helpers for bitset checks and parameter eligibility.

Important APIs/functions:
- `dfltcc()` wraps the `.insn rrf,0xb9390000` DFLTCC instruction using fixed registers r0-r5 and returns the condition code.
- `is_bit_set()` and `turn_bit_off()` inspect/edit QAF bitsets.
- `dfltcc_are_params_ok()` checks compression level mask, 32 KiB window, and default strategy.
- Declares `oesc_msg()`.

Control flow:
- `dfltcc()` copies pointer/length operands into register variables, runs inline assembly, then writes updated operands back to caller-provided pointers.
- After the instruction, it unpoisons parameter and output memory for KMSAN according to function type.
- The return value is the top two bits of the condition-code register captured by `ipm`.

State and persistence:
- No persistent local state. It mutates caller parameter blocks, stream pointers/lengths, and output memory.

Dependencies and integration:
- Includes `dfltcc.h`, `<linux/kmsan-checks.h>`, and `<linux/zutil.h>`.
- Used by query, dynamic table generation, compression, and expansion wrappers.

Risks:
- Register constraints and clobbers must match the architecture instruction ABI. Any compiler or inline-asm mistake can corrupt operands.
- KMSAN unpoison size calculations must match hardware writes, especially sub-byte compressed output.
- `dfltcc_are_params_ok()` limits hardware compression to known-safe zlib configurations; relaxing it requires hardware-format validation.

Test signals:
- s390 build and runtime hardware instruction smoke tests.
- KMSAN builds covering QAF/GDHT/CMPR/XPND paths.
- Parameter rejection tests for unsupported levels, strategies, and window sizes.
