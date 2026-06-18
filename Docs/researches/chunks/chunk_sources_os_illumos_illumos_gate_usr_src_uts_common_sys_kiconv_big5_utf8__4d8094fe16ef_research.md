# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_big5_utf8.h lines 1-8444

## Scope

This report covers lines 1-8444 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_big5_utf8.h` for `learn_fs` subset A. The file is a kernel iconv data header for BIG-5 to UTF-8 conversion. This chunk starts at the license and include guard, opens the kernel-only mapping table, and ends inside the table initializer at key `0xd7cb`. It does not include the closing table initializer, `_KERNEL` guard close, C++ extern close, or header guard close.

The reviewed line slice has 8,363 mapping rows. The whole file declares 13,718 rows, matching `KICONV_BIG5_UTF8_MAX`, so later chunk(s) must account for the remaining 5,355 rows.

## Public Surface And APIs

This chunk exposes two kernel-only declarations when `_KERNEL` is defined:

- `#define KICONV_BIG5_UTF8_MAX (13718)` records the total mapping-table item count for BIG-5 to UTF-8 conversion.
- `static kiconv_table_array_t kiconv_big5_utf8[] = { ... }` begins a translation table from BIG-5 code values to UTF-8 byte arrays.

The data type comes from `kiconv_cck_common.h`:

- `kiconv_table_array_t` has `uint32_t key` and `uchar_t u8[4]`.
- Rows in this chunk use a BIG-5 code as `key` and a UTF-8 byte initializer as `u8`.
- Most rows initialize three UTF-8 bytes; 118 rows in this chunk initialize two bytes and rely on C zero-fill for the rest of `u8[4]`.

The header is wrapped for C++ with `extern "C"`, but this chunk declares static data only, not callable functions.

## Data Layout Visible In This Chunk

The file begins with CDDL and Unicode data-file permission notices, then a Sun modification notice. The include guard is `_SYS_KICONV_BIG5_UTF8_H`.

The mapping table starts at line 81. The first row is:

- `0x0000 -> EF BF BD`, replacement character `U+FFFD`, used as a sentinel/fallback mapping row.

The actual BIG-5 table begins at `0xa140` and proceeds in ascending key order through this chunk's final key `0xd7cb`. The visible ranges include standard BIG-5 punctuation, symbols, kana-like and Greek/Cyrillic blocks, Bopomofo, radicals, and a large run of CJK ideograph mappings represented as UTF-8 byte triples.

Within lines 1-8444:

- Mapping rows counted: 8,363.
- First key: `0x0000`.
- Last key: `0xd7cb`.
- Duplicate keys found in this chunk: none.
- Key ordering checked as strictly ascending.
- UTF-8 byte initializer widths: 8,245 rows with three explicit bytes, 118 rows with two explicit bytes.

The chunk boundary is clean at the end of a table row:

- line 8444: `0xd7cb, { 0xE8, 0xA8, 0xAC },`
- line 8445 continues with `0xd7cc`, so the next chunk can continue row-by-row without repairing a split initializer.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is supplied by the kernel iconv implementation that consumes CCK conversion tables:

1. BIG-5 input validation is defined separately in `kiconv_tc.h` with `KICONV_TC_IS_BIG5_1st_BYTE()` and `KICONV_TC_IS_BIG5_2nd_BYTE()`.
2. A BIG-5 byte pair is combined into a table key.
3. Generic CCK conversion code can binary-search a sorted `kiconv_table_array_t` table using `kiconv_binsearch()`.
4. On match, the `u8` byte array is copied to the UTF-8 output stream.
5. On failure, caller policy decides whether to report an invalid sequence or use replacement behavior.

The conversion-name registry in `uts/common/os/kiconv.c` maps `big5`, `cp950`, and `950` to the same code ID, making this table part of the traditional Chinese BIG-5/CP950 kernel conversion surface.

## State And Dependencies

All state in this chunk is immutable static table data compiled into each translation unit that includes this header under `_KERNEL`.

Direct dependencies visible or required by this chunk:

- `_KERNEL`: hides the table from non-kernel builds.
- `kiconv_table_array_t`: supplied by `uts/common/sys/kiconv_cck_common.h`.
- `uchar_t` and `uint32_t`: supplied through illumos kernel/system type headers included before this generated data header.
- `uts/common/sys/Makefile`: exports `kiconv_big5_utf8.h` alongside related kiconv table headers.
- `kiconv_utf8_big5.h`: companion reverse-direction table, with `KICONV_UTF8_BIG5_MAX (13711)`.
- `kiconv_hkscs_utf8.h` and `kiconv_cp950hkscs_utf8.h`: adjacent Traditional Chinese variants for HKSCS/CP950-HKSCS.
- `kiconv_tc.h`: Traditional Chinese byte-validation macros for BIG-5 and EUC-TW.

## Risks And Invariants

The main invariants are table count, sorted keys, valid UTF-8 byte sequences, and agreement between `KICONV_BIG5_UTF8_MAX` and the full initializer length.

Risks visible in this chunk:

- Generated-data drift: hand edits can silently break individual mappings while preserving C syntax.
- Count mismatch: `KICONV_BIG5_UTF8_MAX` is 13,718, but this chunk only contains the first 8,363 rows; validation must include later chunk(s).
- Include-time duplication: the table is `static` in a public-style header, so every including translation unit gets a private copy. That is likely intentional for the kiconv module pattern but raises footprint risk if included broadly.
- Zero-fill dependence: rows with two-byte UTF-8 initializers depend on `u8[4]` zero-initialization for termination/padding. Consumers must not assume every row has three explicit bytes.
- Encoding validity depends on external BIG-5 byte checks. This table maps keys; it does not itself reject malformed byte sequences.
- Symbol discoverability is weak in this checkout: direct textual references to `kiconv_big5_utf8` outside this header were not found under `usr/src`, so consumers may include or generate references indirectly.

## Cross-Chunk References

Later chunk(s) must continue from `0xd7cc` at line 8445 through the closing row `0xf9dc` and table terminator at line 13800. They should verify:

- Remaining row count is 5,355.
- Whole-file row count remains exactly 13,718.
- No duplicate or nonascending BIG-5 keys appear after `0xd7cb`.
- Closing preprocessor structure remains `#endif /* _KERNEL */`, C++ close, and `#endif /* _SYS_KICONV_BIG5_UTF8_H */`.