# sources/distributed-fs/ceph-client/fs/nls/nls_cp949.c lines 12441-13947

## Purpose

This chunk is the tail of the Linux NLS CP949/EUC-KR charset module. It completes the Unicode-to-CP949 reverse mapping tables, publishes them through `page_uni2charset`, defines the CP949 conversion callbacks (`uni2char()` and `char2uni()`), installs ASCII-only case-folding tables, and registers the charset as an `nls_table` named `cp949` with alias `euc-kr`.

The visible source is mostly generated table data. The important behavior is that the generated data is consumed by small, table-driven conversion routines used by VFS/filesystem NLS callers when translating filenames or other filesystem-visible byte strings between Unicode and Korean CP949.

## Important APIs, Types, And Data

- `static const unsigned char u2c_C6[512]` through `u2c_D7[512]`: reverse mappings for Unicode high-byte pages `0xC6` through `0xD7`. Each Unicode low byte indexes two output bytes at `cl * 2` and `cl * 2 + 1`, so every page has room for 256 two-byte CP949 encodings. These pages primarily cover Hangul syllables and map into CP949 lead/trail-byte pairs such as `0xBF 0xB4`, `0xC0 0xFA`, `0xC8 0xD3`, and many extension ranges.
- `static const unsigned char u2c_DC[512]`: a sparse page for Unicode high byte `0xDC`; this chunk contains only zero mappings. Because `uni2char()` treats `0x00,0x00` as unmappable, this page acts as an explicit invalid-page table for the few indexed entries present in the generated source.
- `static const unsigned char u2c_F9[512]`, `u2c_FA[512]`, and `u2c_FF[512]`: mappings for compatibility/private/fullwidth Unicode pages. `u2c_F9` is densely populated with two-byte CP949 values for compatibility ideographs. `u2c_FA` is sparse and includes many `0x00,0x00` holes. `u2c_FF` maps fullwidth ASCII and Hangul compatibility jamo positions to CP949 pairs, with unmapped holes represented by zero pairs.
- `static const unsigned char *const page_uni2charset[256]`: top-level dispatch table for Unicode-to-charset conversion. It maps the Unicode high byte to the correct `u2c_*` page pointer or `NULL` when that high-byte page has no generated reverse mappings.
- `charset2lower[256]` and `charset2upper[256]`: CP949 byte-wise case tables. They only fold ASCII Latin bytes (`A-Z` and `a-z`); all bytes `0x80` through `0xff` are identity-mapped. This matches the byte-oriented NLS API but does not attempt Korean case behavior.
- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)`: NLS callback converting one Unicode code point to one or two CP949 bytes.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)`: NLS callback converting one CP949 character sequence to a Unicode code point using the forward `page_charset2uni` tables defined earlier in the file.
- `static struct nls_table table`: exports the charset metadata and function pointers to the kernel NLS registry.
- `init_nls_cp949()` / `exit_nls_cp949()`: module lifecycle hooks that call `register_nls(&table)` and `unregister_nls(&table)`.
- `MODULE_ALIAS_NLS(euc-kr)`: makes this module loadable through the NLS alias path for EUC-KR users while the table charset name remains `cp949`.

## Control Flow

`uni2char()` is the reverse conversion path:

1. Rejects zero or negative output capacity with `-ENAMETOOLONG`.
2. Splits the input `wchar_t` into `ch = (uni >> 8) & 0xff` and `cl = uni & 0xff`.
3. Looks up `page_uni2charset[ch]`.
4. If a reverse page exists, requires at least two output bytes, reads the generated pair at `cl * 2`, rejects `0x00,0x00` with `-EINVAL`, writes two output bytes, and returns `2`.
5. If no reverse page exists but the Unicode character is nonzero ASCII (`ch == 0 && cl`), writes the low byte as a one-byte character and returns `1`.
6. Otherwise returns `-EINVAL`.

`char2uni()` is the forward conversion path:

1. Rejects zero or negative input capacity with `-ENAMETOOLONG`.
2. If only one input byte is available, treats that byte as a one-byte character and returns it as Unicode.
3. Otherwise reads the first two bytes as `ch` and `cl`, looks up `page_charset2uni[ch]`, and when both a lead-byte page and nonzero trail byte exist, returns the indexed Unicode value unless it is `0x0000`.
4. If there is no valid double-byte table entry, it falls back to treating the first byte as a one-byte character and returns `1`.

The module lifecycle is straightforward: `module_init()` registers the static table with the kernel NLS subsystem; `module_exit()` unregisters the same table. There is no allocation, file I/O, or runtime mutation in this chunk.

## State And Persistence

All mapping data in this chunk is `static const` and compiled into the module image. There is no persistent on-disk state, no dynamic cache, and no per-mount mutable state. The only externally visible state transition is whether the `cp949` NLS table is currently registered in the kernel NLS registry.

The conversion routines write only to caller-provided output locations (`out` or `uni`) and return byte counts or negative errno values. The case-folding arrays are immutable lookup tables referenced by the registered `nls_table`.

## Dependencies And Integration Points

This chunk depends on earlier tables in the same file:

- `page_charset2uni[256]` and `c2u_*` forward tables, used by `char2uni()`.
- Earlier `u2c_*` reverse pages referenced by `page_uni2charset`, such as `u2c_01`, `u2c_4E`, `u2c_AC`, and many others.

Kernel integration is through standard NLS headers and module infrastructure:

- `<linux/nls.h>` defines `struct nls_table`, `register_nls()`, and `unregister_nls()`.
- `<linux/errno.h>` supplies `-ENAMETOOLONG` and `-EINVAL`.
- `<linux/module.h>` supplies `module_init`, `module_exit`, and module metadata macros.

Filesystem users do not call these functions directly. They request an NLS table by charset name or alias, then use the function pointers in `struct nls_table` for filename encoding/decoding. The `.alias = "euc-kr"` and `MODULE_ALIAS_NLS(euc-kr)` entries are therefore important compatibility points for configurations that ask for EUC-KR but expect CP949-compatible behavior.

## Risks And Edge Cases

- The generated reverse tables are correctness-critical. A single wrong byte pair silently changes filename round-trip behavior for affected Unicode characters.
- Zero pairs are semantic, not padding only. `uni2char()` rejects any generated `0x00,0x00` pair with `-EINVAL`, so sparse pages like `u2c_FA`, `u2c_FF`, and the mostly zero `u2c_DC` must preserve holes exactly.
- `uni2char()` only emits one-byte output for nonzero ASCII when there is no reverse page. Unicode NUL (`U+0000`) is rejected because the ASCII fallback requires `cl` to be nonzero.
- `char2uni()` falls back to a one-byte character if the first byte has no forward page, if the second byte is zero, or if the first byte is available but only one byte is bounded. This can intentionally allow partial/truncated byte strings to consume one byte instead of failing, but it also means tests must check return length as well as Unicode output.
- `char2uni()` indexes the second byte directly into a 256-entry forward table. Lead-byte validity is controlled entirely by whether `page_charset2uni[ch]` is non-NULL.
- `uni2char()` requires two bytes of output capacity for any mapped non-ASCII Unicode page, even if a generated pair would contain an ASCII-looking byte. Capacity checks must therefore include both one-byte ASCII and two-byte mapped cases.
- Case conversion is ASCII-only. Any caller expecting locale-aware Korean case behavior will not get it from this table; high bytes are identity-mapped.
- The file is generated, so manual edits risk breaking the bijection between `c2u_*` and `u2c_*` tables or diverging from the upstream generation source.

## Test Signals

Useful validation should exercise both table data and callback behavior:

- Round-trip known CP949/Hangul pairs that land in this chunk's pages, for example Unicode high pages `0xC6` through `0xD7`, through `uni2char()` then `char2uni()`.
- Check sparse invalid entries in `u2c_FA`, `u2c_FF`, and `u2c_DC` return `-EINVAL` from `uni2char()`.
- Verify ASCII behavior: `U+0041` maps to one byte `0x41`; one-byte input `0x41` maps back to `U+0041`; Unicode NUL is rejected by `uni2char()`.
- Verify output/input bound handling: `uni2char()` returns `-ENAMETOOLONG` for two-byte mappings when `boundlen <= 1`, and `char2uni()` returns `-ENAMETOOLONG` only when `boundlen <= 0`.
- Confirm alias registration by loading/requesting `cp949` and `euc-kr` NLS names and checking that both resolve to this table.
- Compare selected generated entries against an authoritative CP949 mapping source, especially fullwidth page `0xFF` and compatibility page `0xF9`, where sparse mappings are easy to regress.

## Cross-Chunk Notes

This chunk cannot fully establish the charset's correctness alone because `char2uni()` depends on `page_charset2uni` and the `c2u_*` forward tables declared earlier. The final merged file report should reconcile forward and reverse coverage, especially round-trip consistency between the earlier `c2u_*` pages and the `u2c_*` pages completed here.
