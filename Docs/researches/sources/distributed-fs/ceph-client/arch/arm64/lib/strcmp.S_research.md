# sources/distributed-fs/ceph-client/arch/arm64/lib/strcmp.S

Purpose: optimized ARM64 `strcmp` comparing two NUL-terminated strings with MTE-compatible access patterns.

Important APIs/types/functions: `__pi_strcmp`, weak alias `strcmp`, aligned loop, mutual-alignment path, misaligned path, parallel NUL detection, endian-sensitive syndrome handling, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: if the two strings share alignment, it compares 8-byte words after masking pre-string bytes. Otherwise it byte-aligns `src1`, carefully reads from aligned `src2` without crossing beyond its NUL, and combines shifted words. The first difference or NUL builds a syndrome; the routine locates the earliest significant byte and returns unsigned-byte subtraction.

State and persistence: reads both strings only. No persistent state.

Dependencies/integration: exported string API; assumes valid NUL-terminated strings, ARMv8 unaligned access support where used, and endian assembler helpers.

Risks: misaligned string logic must avoid reading past a valid page when `src2` is close to a boundary. Big-endian NUL-detection carry behavior requires byte reversal. No length bound means bad strings can fault.

Test signals: equal strings, differences at every offset, prefixes, empty strings, misalignment combinations, page-boundary strings, high-bit/non-ASCII bytes, big-endian builds, and MTE/KASAN compatibility.
