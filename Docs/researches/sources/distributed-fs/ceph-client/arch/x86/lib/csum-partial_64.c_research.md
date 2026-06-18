# sources/distributed-fs/ceph-client/arch/x86/lib/csum-partial_64.c

Purpose: provides optimized 64-bit x86 Internet checksum routines for arbitrary memory and IP-style checksums.

Important APIs/functions: exports `csum_partial` and `ip_compute_csum`. Internal helpers `csum_finalize_sum()` and `update_csum_40b()` fold 64-bit accumulators and add five qwords using inline assembly carry chains.

Control flow: `csum_partial()` accumulates two parallel 40-byte lanes for lengths >=80 to improve instruction-level parallelism, handles a hot exact 40-byte path, then processes 32-, 16-, and 8-byte tails with inline assembly. Remaining 1-7 bytes are loaded with `load_unaligned_zeropad()` and masked by shift before final carry addition. `ip_compute_csum()` folds the partial checksum to a 16-bit checksum.

State and persistence behavior: pure read-only over the supplied buffer; no global state.

Dependencies/integration points: used by the networking stack when `CONFIG_GENERIC_CSUM` is not selected. Depends on checksum types, word-at-a-time helpers, exports, and x86 carry arithmetic.

Risks: unaligned tail loading must not fault beyond valid memory due to `load_unaligned_zeropad` expectations. Carry folding and endian behavior must match Internet checksum semantics. Optimized 40-byte path targets IPv6 headers and needs exact length handling.

Test signals: networking checksum selftests, comparisons against generic checksum for random buffers and all alignments/lengths, IPv6 header checksum cases, and KASAN validation for tail loads.
