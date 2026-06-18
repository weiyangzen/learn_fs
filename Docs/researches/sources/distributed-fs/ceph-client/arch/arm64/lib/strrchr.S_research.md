# sources/distributed-fs/ceph-client/arch/arm64/lib/strrchr.S

Purpose: simple ARM64 `strrchr` implementation returning the last occurrence of a character before the terminating NUL.

Important APIs/types/functions: `__pi_strrchr`, weak alias `strrchr`, byte loop with last-match register, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: masks the target character to one byte, initializes last-match to zero, scans byte by byte until NUL, updates the last-match address whenever the byte equals the target, and returns the saved address.

State and persistence: read-only string scan. No persistent state.

Dependencies/integration: exported kernel string helper; assumes a valid NUL-terminated string.

Risks: as implemented, it stops before testing the terminating NUL as a match, so callers searching for `'\0'` should be covered by tests against expected kernel semantics. Unbounded invalid strings can fault.

Test signals: multiple matches, no match, empty string, target near terminator, target `'\0'`, high-bit character values, and comparison with generic `strrchr`.
