# sources/cloud-native/ostree/src/libostree/bupsplit.c

Purpose: This C file implements bup-style content-defined chunk boundary detection using a rolling checksum. OSTree can use it to split content into stable chunks for delta/static-delta style operations.

Important APIs, types, and functions: Internal `Rollsum` holds `s1`, `s2`, a `BUP_WINDOWSIZE` byte window, and a window offset. `rollsum_add`, `rollsum_init`, `rollsum_roll`, and `rollsum_digest` implement the rolling checksum. Public `bupsplit_sum` computes a digest over a buffer slice. Public `bupsplit_find_ofs` scans a buffer for a chunk boundary and optionally reports boundary strength in `bits`.

Control flow: `bupsplit_find_ofs` initializes the rolling checksum, rolls each input byte, checks whether low bits of `s2` match the boundary mask `(BUP_BLOBSIZE - 1)`, computes additional matching bits when requested, and returns the boundary offset as `count + 1`; if no boundary is found it returns 0. `bupsplit_sum` rolls from `ofs` to `len` and returns the digest.

State and persistence behavior: All state is stack-local and deterministic for the input bytes. No persistent state or allocation is used.

Dependencies and integration points: Depends on `bupsplit.h` constants, `stdint.h`, `memory.h`, and C integer arithmetic. The code is imported from bup/librsync-style algorithms and carries a separate license block.

Risks: `bupsplit_find_ofs` takes `int len`, so very large buffers must be chunked by callers. Rolling checksum arithmetic intentionally wraps unsigned values; changing types can alter results. Boundary behavior is part of delta efficiency and compatibility expectations.

Test signals: No direct test in this subset. Algorithmic tests should verify stable boundaries for known byte sequences and edge cases with no boundary.
