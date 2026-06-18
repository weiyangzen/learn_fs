# sources/distributed-fs/ceph-client/arch/arm64/lib/strncmp.S

Purpose: optimized ARM64 `strncmp`, comparing at most a caller-provided limit of bytes from two strings.

Important APIs/types/functions: `__pi_strncmp`, weak alias `strncmp`, zero-limit fast return, aligned and mutual-aligned loops, misaligned word comparison, syndrome/limit checks, endian-specific result paths, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: returns zero for limit zero, then chooses aligned/misaligned strategy based on source alignment. Aligned loops subtract eight from the limit per word, detect differences and NUL in parallel, and use a syndrome to decide whether the first significant byte lies before the limit. Misaligned sources compare bytes until `src1` alignment, then combine shifted aligned reads from `src2` in several steps while masking irrelevant bytes.

State and persistence: reads caller strings up to the bounded comparison pattern. No persistent state.

Dependencies/integration: exported string API; assumes source ranges are valid for the accesses implied by the optimized algorithm and uses endian assembler helpers.

Risks: limit accounting near `ULONG_MAX` and misaligned source combinations is complex. Big-endian result generation cannot rely on the same syndrome trick when NUL is present. Page-boundary behavior depends on caller-valid string memory.

Test signals: zero limit, equal prefixes shorter/longer than limit, difference at each byte before/after limit, NUL before limit, all alignments, high-bit bytes, big-endian builds, and randomized comparison with generic `strncmp`.
