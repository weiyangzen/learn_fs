# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp950.c lines 8284-9483

## Scope

This chunk covers the tail of the generated Unicode-to-CP950 reverse mapping data and the complete runtime wiring for the Linux `cp950`/`big5` NLS module. Most lines are immutable lookup tables; the executable surface is limited to the two NLS conversion callbacks, table registration, and module metadata at the end of the file.

## APIs And Entry Points

- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)` is the NLS Unicode-to-charset encoder callback. It returns `1` or `2` bytes written, or `-ENAMETOOLONG` / `-EINVAL`.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)` is the NLS charset-to-Unicode decoder callback. It returns `1` or `2` input bytes consumed, or `-ENAMETOOLONG` / `-EINVAL`.
- `table` publishes the kernel `struct nls_table` for `.charset = "cp950"` with `.alias = "big5"`, the two callbacks, and byte case-folding tables.
- `init_nls_cp950()` and `exit_nls_cp950()` call `register_nls(&table)` and `unregister_nls(&table)`.
- `module_init`, `module_exit`, `MODULE_DESCRIPTION`, `MODULE_LICENSE`, and `MODULE_ALIAS_NLS(big5)` expose the module lifecycle and NLS alias.

## Mapping Data

The chunk starts by closing the final row of `u2c_92[512]` from the previous chunk. It then defines `u2c_93` through `u2c_9F`, plus sparse/special pages `u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FE`, and `u2c_FF`. These are reverse maps from Unicode high-byte pages to two-byte CP950 sequences; each Unicode low byte selects two adjacent array bytes, and `0x00,0x00` is the unmapped sentinel.

`page_uni2charset[256]` is the high-byte dispatch table used by `uni2char()`. It references reverse pages defined in this chunk and many pages from earlier chunks, including `u2c_02`, `u2c_03`, `u2c_20`-`u2c_33`, `u2c_4E`-`u2c_9F`, `u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FE`, and `u2c_FF`.

`charset2lower[256]` and `charset2upper[256]` are byte-level case maps. They fold ASCII letters only; bytes `0x80`-`0xff` remain identity, so CP950 multibyte data is not case-normalized.

## Control Flow

`uni2char()` splits the 16-bit `wchar_t` value into `ch = high byte` and `cl = low byte`. It first rejects `boundlen <= 0`. If `page_uni2charset[ch]` exists, it requires room for two output bytes, copies the pair at `cl * 2`, rejects the all-zero sentinel with `-EINVAL`, and returns `2`. If no reverse page exists and the Unicode high byte is zero with a nonzero low byte, it emits that low byte as a single-byte ASCII-compatible character and returns `1`. All other inputs return `-EINVAL`.

`char2uni()` rejects empty input, decodes a single available byte as identity Unicode, and otherwise reads two bytes. It selects `page_charset2uni[rawstring[0]]`, a forward map defined earlier in the file. If a table exists and the second byte is nonzero, it returns the table entry unless that entry is `0x0000`, which is invalid. Missing table or zero second byte falls back to one-byte identity for the first byte.

Module control flow is direct: init registers the static table with the NLS core; exit unregisters the same table.

## State And Dependencies

All conversion data in this chunk is `static const`; there is no mutable per-call state, allocation, locking, I/O, or reference counting in the callbacks. The only global runtime state change is registration of `table` with the Linux NLS core.

The chunk depends on earlier file definitions for `page_charset2uni` and many `u2c_*` pages referenced by `page_uni2charset`. It also depends on Linux headers for `struct nls_table`, `register_nls`, `unregister_nls`, module macros, `wchar_t`, and errno values.

## Risks And Edge Cases

- Table correctness is the main risk: a wrong byte pair silently changes filename transcoding.
- `uni2char()` rejects `U+0000` because the one-byte fallback requires `cl` to be nonzero and reverse-table zero pairs mean unmapped.
- `char2uni()` treats a single available lead byte as an identity character rather than reporting an incomplete multibyte sequence.
- `char2uni()` also falls back to one-byte identity when the first byte has no CP950 page table or the second byte is zero.
- Short initializer arrays such as `u2c_DC` rely on C zero-fill to mark the rest of the page unmapped.
- Forward and reverse tables are generated independently enough that duplicate or compatibility mappings may not round-trip uniquely.
- Conversion only uses the low 16 bits of `wchar_t`; non-BMP Unicode code points are outside this table design.

## Cross-Chunk References

- Previous chunk: supplies most of `u2c_92` and earlier reverse pages consumed by `page_uni2charset`.
- Earlier chunks: define CP950-to-Unicode `c2u_*` tables and `page_charset2uni`, which `char2uni()` requires.
- This chunk completes the file by adding the final reverse pages, dispatch/case tables, conversion callbacks, and module registration. The final per-file report should merge these findings with the earlier generated table coverage; this chunk intentionally does not create that merged report.