# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp932.c lines 4153-7934

## Scope

This report covers only `sources/os/linux/linux-stable/fs/nls/nls_cp932.c` lines 4153-7934 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely. The chunk starts in the tail of the `u2c_6B` Unicode-to-CP932 page, completes the remaining reverse mapping data, defines the reverse page dispatch table and byte case tables, and ends with the NLS conversion callbacks plus module registration. I did not create the merged per-file report.

## APIs And Entry Points

- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)`: Linux NLS encoder callback for Unicode to CP932. It returns `1` or `2` bytes written, `-ENAMETOOLONG` when `boundlen` cannot hold the result, and `-EINVAL` for unmapped Unicode.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)`: Linux NLS decoder callback for CP932 to Unicode. It returns `1` or `2` bytes consumed, `-ENAMETOOLONG` for missing input bytes, and `-EINVAL` for invalid or unmapped byte sequences.
- `table`: `struct nls_table` exported to the NLS core with `.charset = "cp932"` and `.alias = "sjis"`.
- `init_nls_cp932()` / `exit_nls_cp932()`: module lifecycle callbacks that call `register_nls(&table)` and `unregister_nls(&table)`.
- `MODULE_ALIAS_NLS(sjis)`: exposes the Shift-JIS alias for module autoload.

## Mapping Data

Most of this chunk is immutable generated lookup data for Unicode-to-CP932 conversion:

- Tail of `u2c_6B`, then `u2c_6C` through `u2c_9F`: 512-byte pages keyed by Unicode low byte. Each code point consumes two table bytes, either a CP932 two-byte sequence or `{0x00, 0x00}` for no mapping.
- Sparse special pages `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`: cover isolated compatibility/private/fullwidth mappings. `u2c_FA` contains many IBM/NEC extension reverse mappings to `0xED`/`0xEE` byte ranges; `u2c_FF` covers fullwidth ASCII, halfwidth kana-related forms, and some fullwidth compatibility punctuation.
- `page_uni2charset[256]`: high-byte dispatch table for reverse conversion. It points to Unicode pages defined in both chunks, including earlier pages from chunk 1 (`u2c_03`, `u2c_04`, `u2c_20`...`u2c_6A`) and this chunk's later pages (`u2c_6B`...`u2c_9F`, `u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FF`).
- `charset2lower[256]` and `charset2upper[256]`: byte-wise case tables. They fold only ASCII letters; bytes `0x80` through `0xff` remain identity values.

The data is read-only file-local state. There is no allocation, locking, reference counting, or filesystem object state in this chunk.

## Control Flow

`uni2char()` splits the input `wchar_t` into `ch = (uni >> 8) & 0xff` and `cl = uni & 0xff`, so only the low 16 bits participate in conversion.

Encoding path:

1. Rejects zero or negative output capacity with `-ENAMETOOLONG`.
2. Maps Unicode halfwidth katakana/punctuation `U+FF61..U+FF9F` directly to single CP932 bytes `0xA1..0xDF`.
3. Looks up `page_uni2charset[ch]`. If a page exists, it requires `boundlen >= 2`, copies the two-byte pair at `cl * 2`, rejects `{0x00, 0x00}` as unmapped, and otherwise returns `2`.
4. If no page exists and `ch == 0`, maps ASCII `U+0000..U+007F` to one byte, or tries chunk-1 `u2c_00hi` for `U+00A0..U+00FF`.
5. Returns `-EINVAL` for all other unmapped cases.

`char2uni()` decodes in the opposite direction:

1. Rejects zero or negative input length with `-ENAMETOOLONG`.
2. Maps bytes `0x00..0x7F` directly to Unicode.
3. Maps bytes `0xA1..0xDF` to `U+FF61..U+FF9F`.
4. Requires a second byte for all remaining leading bytes.
5. Uses chunk-1 `page_charset2uni[ch]` and the second byte as an index into the selected `c2u_*` table. A `NULL` lead page, zero trail byte, or resulting `U+0000` is invalid.

Module control flow is minimal: `module_init()` registers the static table at load time and `module_exit()` unregisters it at unload time.

## Dependencies

Visible external dependencies are Linux kernel NLS/module interfaces from the file includes and the NLS core functions `register_nls()` and `unregister_nls()`. The conversion callbacks depend heavily on data from chunk 1:

- `page_charset2uni` and all `c2u_*` CP932-to-Unicode pages are required by `char2uni()`.
- `u2c_00hi` and earlier `u2c_*` Unicode pages are required by `uni2char()` through `page_uni2charset`.

The data also depends on CP932-specific compatibility mappings rather than plain Shift-JIS only. The registered alias is `"sjis"`, but the table content includes Microsoft CP932 extensions and compatibility ranges.

## Risks And Edge Cases

- Table correctness is the main behavioral risk. A wrong two-byte cell can corrupt filenames, break round trips, or create unexpected display/collision behavior on filesystems mounted with `iocharset=cp932`/`sjis`.
- `uni2char()` writes two output bytes before checking for the `{0x00, 0x00}` unmapped sentinel, so callers may see `out` modified even when the function returns `-EINVAL`.
- `char2uni()` treats a decoded `U+0000` table entry as invalid, while single-byte input `0x00` validly decodes to `U+0000`; this relies on the ASCII fast path.
- Trail byte `0x00` is rejected for two-byte sequences before table lookup.
- Case folding is ASCII-only. Japanese fullwidth letters, kana, and multibyte CP932 sequences are not case-normalized by these tables.
- `wchar_t` values above `U+FFFF` are truncated for lookup because only `ch` and `cl` are used.
- Forward and reverse tables are independent generated data. The file performs no runtime consistency check that every `char2uni()` mapping reverses through `uni2char()`.

## Cross-Chunk References

Chunk 1 defines the file header, CP932-to-Unicode tables, `page_charset2uni`, `u2c_00hi`, and the early Unicode-to-CP932 pages through most of `u2c_6B`. This chunk completes `u2c_6B`, defines the rest of the reverse pages, builds `page_uni2charset`, and owns all executable conversion and module-registration code.

The final per-file report for `sources/os/linux/linux-stable/fs/nls/nls_cp932.c` must merge both chunks to describe the complete bidirectional table set. This chunk alone cannot validate the decoder tables because `char2uni()` dispatches into chunk-1 data.