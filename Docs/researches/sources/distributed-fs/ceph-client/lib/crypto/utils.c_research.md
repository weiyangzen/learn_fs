# sources/distributed-fs/ceph-client/lib/crypto/utils.c

Purpose: shared crypto utility implementation for bytewise XOR operations behind `crypto_xor()` and `crypto_xor_cpy()`.

Important APIs/types/functions: exports `__crypto_xor(u8 *dst, const u8 *src1, const u8 *src2, unsigned int len)` with `EXPORT_SYMBOL_GPL`. It uses `get_unaligned()`/`put_unaligned()` when efficient unaligned access is configured.

Control flow: on architectures without efficient unaligned access, it computes the relative alignment among `dst`, `src1`, and `src2`, byte-walks until destination alignment matches the relative alignment, then processes as many 64-bit, 32-bit, and 16-bit chunks as alignment permits. Remaining bytes are XORed one at a time. On efficient-unaligned systems, it directly uses unaligned word loads/stores in the wide loops.

State and persistence: no persistent state; only writes to caller-provided `dst`. Aliasing of `dst` with a source is explicitly allowed.

Dependencies: `<crypto/utils.h>`, export/module headers, unaligned access helpers, `CONFIG_64BIT`, and `CONFIG_HAVE_EFFICIENT_UNALIGNED_ACCESS`.

Integration points: common helper for block cipher modes, hash/MAC glue, and any crypto code using the public XOR wrappers.

Risks: alignment logic is subtle; incorrect `relalign` handling can fault on strict-alignment architectures or lose wide-loop optimization. Source/destination overlap is only safe for aliases matching the documented use, not arbitrary partially overlapping ranges. The 64-bit loop is compile-time gated but still sensitive to unaligned helper correctness.

Test signals: no local tests in this subset. Expected validation comes indirectly from crypto self-tests and consumers of `crypto_xor()`/`crypto_xor_cpy()` under varied alignments.
