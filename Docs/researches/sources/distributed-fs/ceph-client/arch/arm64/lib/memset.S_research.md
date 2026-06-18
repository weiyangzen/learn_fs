# sources/distributed-fs/ceph-client/arch/arm64/lib/memset.S

Purpose: optimized ARM64 implementation of `memset` with special zero-fill DC ZVA and optional MOPS acceleration.

Important APIs/types/functions: `__pi_memset_generic`, `__pi_memset`, aliases `__memset` and `memset`, byte replication setup, small/tail/large store loops, `.Lzero_mem` DC ZVA path, MOPS `setp/setm/sete`, and exports.

Control flow: expands the byte value to a 64-bit pattern, handles <=15 bytes with scalar stores, aligns the destination, uses pair stores for nonzero or shorter zero fills, and for large zero fills reads `dczid_el0` to use DC ZVA when permitted and useful. MOPS-capable CPUs use set instructions through alternatives.

State and persistence: writes the destination buffer. No persistent state.

Dependencies/integration: core memory API, cache-line constants, DC ZVA, FEAT_MOPS, and alternative patching.

Risks: DC ZVA path intentionally aligns and may over-store inside the requested range; boundary arithmetic must prevent overruns. MOPS and generic return value must preserve original destination. Non-cacheable memory callers may have different expectations, so callers must use appropriate APIs.

Test signals: memset tests for all sizes/alignments/values, zero fills across ZVA sizes, nonzero large fills, MOPS matrix, and memory sanitizer/KASAN range checks.
