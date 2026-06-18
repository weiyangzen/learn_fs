# sources/distributed-fs/ceph-client/arch/arm64/lib/strchr.S

Purpose: simple ARM64 `strchr` implementation returning the first occurrence of a character in a NUL-terminated string.

Important APIs/types/functions: `__pi_strchr`, weak alias `strchr`, byte loop, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: masks the character to 8 bits, loads bytes one at a time until the byte equals the target or is NUL, backs up to the matching position, and returns either that address or zero.

State and persistence: read-only string scan. No persistent state.

Dependencies/integration: exported kernel string helper; assumes caller supplies a valid NUL-terminated string.

Risks: no bound is enforced, so unterminated or invalid strings can fault. Character comparison treats input as unsigned byte.

Test signals: target before NUL, target is NUL, absent target, empty string, high-bit character values, and comparison with generic `strchr`.
