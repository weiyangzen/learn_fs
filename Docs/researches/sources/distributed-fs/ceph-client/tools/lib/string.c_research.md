# sources/distributed-fs/ceph-client/tools/lib/string.c

Purpose: Supplies user-space copies or fallbacks for kernel string/memory helpers needed by tools code.

Important APIs/types/functions: `memdup()` duplicates a memory region. `strtobool()` parses common boolean strings. Weak `strlcpy()` provides BSD-compatible bounded copy if libc lacks it. `skip_spaces()`, `strim()`, `remove_spaces()`, and `strreplace()` manipulate strings in place. `memchr_inv()` finds the first byte not equal to a value, using `check_bytes8()` and 64-bit scanning.

Control flow: Most functions are linear scans over strings/buffers. `memchr_inv()` checks short buffers byte-by-byte, aligns to 8 bytes, scans 64-bit words for any mismatch, then checks the suffix.

State and persistence: Stateless except mutations to caller-provided strings and allocated buffer from `memdup()`.

Dependencies/integration: Includes libc `stdlib/string/errno` and Linux headers for `bool`, `u8/u64`, ctype, and weak symbol attributes. Intended to satisfy shared tools library dependencies.

Risks: `memchr_inv()` casts possibly unaligned memory to `u64 *` after manual alignment, which assumes alignment calculations and architecture behavior are correct. `remove_spaces()` removes only ASCII space, not all whitespace. `strtobool()` inspects `s[1]` for `o/O`, so one-character `"o"` safely reads NUL but returns invalid. `strim()` mutates input and should not receive string literals.

Test signals: Exercise boolean strings, zero-size copy, weak override behavior, whitespace trimming, all-space strings, `memchr_inv()` on aligned/unaligned buffers, short buffers, and not-found cases.
