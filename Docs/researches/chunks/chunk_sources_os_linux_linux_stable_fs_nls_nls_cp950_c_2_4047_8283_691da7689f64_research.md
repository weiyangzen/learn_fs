# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp950.c lines 4047-8283

## Scope

This chunk is generated-style static data for Linux's CP950/Big5 NLS module. It contains no functions, module registration, exported symbols, dynamic state, allocation, locking, or I/O. The covered line range is part of the Unicode-to-charset reverse mapping area:

- The tail of `u2c_53[512]`, covering Unicode high byte `0x53` low-byte entries `0xF0..0xFF`.
- Complete reverse pages `u2c_54[512]` through `u2c_91[512]`.
- Nearly all of `u2c_92[512]`, covering entries `0x00..0xFB`; the final `0xFC..0xFF` row and closing brace are in the next chunk.

Each table page maps one 16-bit Unicode high-byte page to CP950 byte pairs for encoding.

## APIs And Data Structures

The chunk defines internal immutable arrays only:

- `static const unsigned char u2c_XX[512]` for Unicode pages `0x53..0x92` in this slice.
- Each page has 256 logical slots, two bytes per low-byte Unicode value.
- Slot `cl` is read at `u2c_XX[cl * 2]` and `u2c_XX[cl * 2 + 1]`.
- `{0x00, 0x00}` is the unmapped sentinel, not a valid CP950 output.

Adjacent context shows these arrays are later wired into `page_uni2charset[256]`, then consumed by `uni2char()`. That callback splits `wchar_t` into high byte `ch` and low byte `cl`, selects `page_uni2charset[ch]`, emits the selected two-byte pair, and rejects `{0x00, 0x00}` with `-EINVAL`.

## Control Flow

There is no runtime control flow in this chunk. Runtime behavior is table-driven by later code:

1. `uni2char()` checks output length.
2. It indexes `page_uni2charset` by Unicode high byte.
3. If a page exists, it reads this chunk's two-byte slot by Unicode low byte.
4. It returns two CP950 bytes or rejects unmapped slots.
5. If no page exists and the high byte is zero, later code falls back to single-byte ASCII handling.

This chunk therefore contributes data to the encode path only. The decode path uses the earlier `c2u_*` and `page_charset2uni` tables, not these `u2c_*` pages directly.

## State And Dependencies

All visible state is `static const`, module-local, and read-only after compilation. The tables depend on the surrounding generated file convention:

- Previous chunk defines the header/includes, CP950-to-Unicode tables, `page_charset2uni`, earlier reverse pages, and the beginning of `u2c_53`.
- This chunk continues the reverse Unicode-to-CP950 table sequence for the main CJK ranges.
- Next chunk completes `u2c_92`, defines later reverse pages, `page_uni2charset`, case-conversion tables, `uni2char()`, `char2uni()`, the `nls_table`, and module init/exit registration.

## Risks And Invariants

- Table integrity is the central risk. A one-byte edit silently changes filename transcoding for filesystems using the `cp950`/`big5` NLS table.
- The endpoint tables are split across chunks: `u2c_53` begins before this chunk and `u2c_92` ends after it. Any syntax or completeness check must merge adjacent chunks.
- The reverse tables must remain consistent with the forward `c2u_*` tables, although duplicate/compatibility mappings may make the reverse direction a generated canonical choice rather than a perfect inverse.
- `{0x00, 0x00}` must remain reserved for unmapped Unicode slots because later `uni2char()` uses that exact pair as the error condition.
- The design is 16-bit-page based. Later code masks `wchar_t` into high/low bytes, so non-BMP code points are outside this table layout.

## Cross-Chunk References

- Previous chunk: lines 3985-4046 contain the start of `u2c_53`; lines 4047-4051 here complete it.
- Next chunk: line 8284 completes `u2c_92`, and later lines build `page_uni2charset` that references every complete `u2c_*` page, including those defined here.
- Final per-file research should connect this chunk's immutable reverse pages to `uni2char()` and contrast them with the earlier forward `char2uni()` tables.