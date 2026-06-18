# sources/distributed-fs/ceph-client/arch/arm64/lib/strnlen.S

Purpose: optimized ARM64 `strnlen`, returning string length capped at a maximum count.

Important APIs/types/functions: `__pi_strnlen`, weak alias `strnlen`, aligned 16-byte loop, misaligned first-block handling, parallel NUL detection, endian correction, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: zero limit returns zero. Otherwise it aligns the base down to 16 bytes, computes a bounded word count without overflow, masks bytes before the string for misaligned starts, scans two words per iteration for NUL, and returns the smaller of found length and limit.

State and persistence: read-only bounded scan. No persistent state.

Dependencies/integration: exported string API; depends on ARM64 unaligned access behavior and endian macros.

Risks: overflow-safe limit word calculation is important for huge limits. Misaligned masking must ignore bytes before `srcin` without hiding real NULs. As with other string routines, caller must provide accessible memory up to NUL or limit.

Test signals: limit zero, NUL before/at/after limit, no NUL up to limit, unaligned starts, large limits near word overflow boundaries, big-endian builds, and generic implementation comparisons.
