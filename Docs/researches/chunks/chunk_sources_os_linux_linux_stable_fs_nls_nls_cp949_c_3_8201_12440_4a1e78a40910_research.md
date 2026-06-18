# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp949.c lines 8201-12440

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux-stable`.

## Chunk Role

This chunk is static Unicode-to-CP949 mapping data for the Linux NLS `cp949` module. It contains no executable functions, locks, allocations, or module registration logic. Its exported effect is through later lookup wiring: `uni2char()` indexes `page_uni2charset[ch]`, then reads two bytes from the selected `u2c_XX` table at `cl * 2` and `cl * 2 + 1`.

The chunk begins inside `u2c_7A` and ends inside `u2c_C6`. Whole tables introduced in this range are `u2c_7B` through `u2c_C6`; `u2c_7A` starts in the prior chunk and `u2c_C6` continues in the next chunk.

## APIs And Data Contracts

- `static const unsigned char u2c_XX[512]`: each table maps a Unicode page `0xXX00..0xXXff` to 256 two-byte CP949/EUC-KR output sequences.
- Indexing contract: for Unicode `uni`, high byte `ch = (uni >> 8) & 0xff` chooses `u2c_ch` through `page_uni2charset[]`; low byte `cl = uni & 0xff` chooses a two-byte pair.
- Sentinel contract: `0x00, 0x00` means "unmapped"; later `uni2char()` returns `-EINVAL` when the selected pair is all zero.
- Nonzero pairs are emitted as exactly two bytes. There is no single-byte ASCII path through these tables; ASCII is handled by `uni2char()` only when no page table exists and `ch == 0 && cl`.

## Data Covered

- Partial `u2c_7A`: lines 8201-8261 cover the remainder of Unicode page `0x7A`, with sparse mappings and many zero sentinels.
- Sparse CJK-extension pages: `u2c_7B` through `u2c_9F` are mostly sparse tables with many unmapped entries. Within the exact chunk, these pages include 1,861 mapped pairs and 5,624 zero pairs.
- Hangul syllable pages: `u2c_AC` through `u2c_C5` are dense, fully mapped tables in this chunk. They cover Unicode pages from the Hangul syllables block beginning at `U+AC00`.
- Partial `u2c_C6`: lines 12405-12440 cover offsets `0x00..0x87` of Unicode page `0xC6`, all mapped in this partial range; the table continues after the chunk.

The byte patterns in the dense Hangul region show contiguous CP949 assignments such as `0xB0,0xA1` onward in `u2c_AC`, continuing into lead-byte ranges `0x9D`, `0x9E`, and `0x9F` by `u2c_C5`/`u2c_C6`. This is generated lookup data, not hand-coded control flow.

## Control Flow

No local control flow exists in this chunk. Runtime flow is external:

1. `uni2char()` receives a Unicode `wchar_t`.
2. It selects `page_uni2charset[ch]`.
3. If the selected pointer names one of the tables in this chunk, it copies the two bytes at the low-byte offset.
4. If both bytes are zero, conversion fails with `-EINVAL`; otherwise conversion succeeds with length `2`.

## State And Dependencies

- State is immutable `.rodata`: all arrays are `static const`.
- There is no per-call, per-mount, global mutable, or thread-local state in the chunk.
- Internal dependency: `page_uni2charset[]` later in the file must reference these arrays at indices matching their suffixes.
- External dependencies are the Linux NLS interface and error semantics used by later code: `<linux/nls.h>` and `<linux/errno.h>`.

## Risks And Cross-Chunk References

- Table truncation or misalignment is the primary risk. Each complete `u2c_XX` table must contain exactly 512 bytes.
- Cross-chunk boundaries are sensitive: this chunk starts after the declaration of `u2c_7A` and ends before `u2c_C6` is complete.
- Sparse CJK pages have many unmapped entries; callers must tolerate `-EINVAL` for Unicode values CP949 cannot encode.
- Prior chunk defines the beginning of `u2c_7A`; later chunk completes `u2c_C6` and defines `page_uni2charset[]`, `uni2char()`, `char2uni()`, and module registration.
- Earlier file sections define the reverse `c2u_XX` tables used by `char2uni()`.