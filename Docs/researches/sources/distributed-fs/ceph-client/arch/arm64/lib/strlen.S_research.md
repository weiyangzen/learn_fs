# sources/distributed-fs/ceph-client/arch/arm64/lib/strlen.S

Purpose: optimized ARM64 `strlen` with page-crossing care and hardware-tag KASAN granule awareness.

Important APIs/types/functions: `__pi_strlen`, weak alias `strlen`, `MIN_PAGE_SIZE` selection, first-16-byte probe, main 32-byte loop, non-ASCII accurate loop, page-cross path, parallel NUL detection, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: checks whether the first unaligned 16-byte load crosses the minimum page or MTE granule boundary. If safe, it probes two words for early NUL. Longer strings enter an aligned 32-byte loop using a fast ASCII NUL check, falling back to a precise check when high-bit bytes are present. If the first access would cross a boundary, it reads from an aligned address and masks bytes before `srcin`.

State and persistence: read-only string scan. No persistent state.

Dependencies/integration: exported string API; depends on MTE granule definitions when `CONFIG_KASAN_HW_TAGS` is enabled and endian handling macros.

Risks: unbounded scan can fault on invalid or unterminated strings. The page/granule cross guard is critical for KASAN HW tags. Fast non-ASCII detection must not miss NUL bytes.

Test signals: strings of length 0..64 and large, start addresses near page and MTE-granule boundaries, non-ASCII bytes, big-endian builds, KASAN HW tags, and comparison with generic `strlen`.
