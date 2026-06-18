# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp950.c lines 4047-8283

## Scope

This chunk is generated-style static lookup data for the Linux NLS CP950/Big5 module. It contains no executable functions, exported symbols, module metadata, or registration code. The line range covers Unicode-to-charset reverse mapping tables:

- The tail of `u2c_53[512]`, beginning at Unicode page `0x53` low-byte entries `0xF0..0xFF`.
- Full `u2c_54[512]` through `u2c_91[512]`.
- Nearly all of `u2c_92[512]`, from entries `0x00..0xFB`; the final `0xFC..0xFF` row and closing brace are just after this chunk.

The data is part of the reverse direction used to encode Unicode code points into CP950 byte pairs.

## APIs And Data Structures

The chunk defines internal `static const unsigned char` table data only. Each `u2c_XX[512]` table represents one Unicode high-byte page `0xXX`, with 256 two-byte CP950 results:

- `0x00, 0x00` is the unmapped sentinel.
- Byte offset `low * 2` is the first CP950 byte.
- Byte offset `low * 2 + 1` is the second CP950 byte.

Adjacent code shows the consumer contract: `uni2char()` indexes `page_uni2charset[ch]`, reads the pair at `cl * 2`, and rejects `{0x00, 0x00}` with `-EINVAL`.

## Control Flow

There is no runtime branch, loop, allocation, locking, or I/O in this chunk. Runtime behavior is table-driven later by `uni2char()`:

1. Split `wchar_t` into high and low bytes.
2. Use the high byte to select one `u2c_*` page.
3. Use the low byte to select a CP950 byte pair.
4. Return two bytes, `-EINVAL`, or `-ENAMETOOLONG`.

## State And Dependencies

All state here is immutable module-local data. Earlier chunks define the file header, forward `c2u_*` tables, `page_charset2uni`, and early reverse pages through most of `u2c_53`. Later code defines `page_uni2charset`, case tables, `uni2char()`, `char2uni()`, `struct nls_table`, and module init/exit.

## Risks And Edge Cases

- A single wrong byte pair silently changes filename transcoding.
- The chunk starts mid-`u2c_53` and ends mid-`u2c_92`, so syntax and table completeness require adjacent chunks.
- Forward and reverse mappings are independent generated tables; this chunk alone cannot prove inversion correctness.
- `uni2char()` only uses the low 16 bits of `wchar_t`, so non-BMP Unicode values are outside this table design.

## Cross-Chunk References

- Previous chunk: earlier reverse pages plus CP950-to-Unicode data used by `char2uni()`.
- Next chunk: completes `u2c_92`, defines later `u2c_*` pages, then the dispatch table and NLS callbacks.
- Final per-file merge should describe this as a generated static NLS mapping module driven by immutable mapping arrays and small conversion callbacks.