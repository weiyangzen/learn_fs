# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 62959-63457

## Scope

This chunk covers the final 499 lines of the illumos kernel GB18030-to-UTF-8 mapping header. It is within `sources/os/illumos/illumos-gate`, which is included by `Docs/research_subset_a.md`.

The range is entirely table data plus closing preprocessor/C++ guards. It contains the tail of `static kiconv_table_array_t kiconv_gbk4_utf8[]`, the four-byte GB18030 mapping table declared earlier in the same file. The visible entries map packed four-byte GB18030 keys from `0x8430F230` through `0x8431A439` to three-byte UTF-8 byte sequences from `{ 0xEF, 0xB5, 0xBE }` through `{ 0xEF, 0xBF, 0xBF }`.

## APIs and Entry Points

- No callable functions, macros, or public entry points are defined in this chunk.
- The data belongs to `kiconv_gbk4_utf8[]`, declared earlier as a `static kiconv_table_array_t` array under `#ifdef _KERNEL`.
- The associated size constant visible earlier in the file is `KICONV_GBK4_UTF8_MAX` with value `39421`.
- `kiconv_table_array_t` is defined in `sys/kiconv_cck_common.h` as a `uint32_t key` plus `uchar_t u8[4]`.

## Control Flow

There is no local control flow. Runtime behavior is supplied by conversion code elsewhere that includes this header and searches or indexes the static table.

The table is ordered by ascending packed GB18030 key. Within most subranges, UTF-8 bytes advance monotonically, but this chunk also shows intentional mapping gaps and jumps, such as `0x84318538` to `0x84318539`, `0x84319534` to `0x84319535`, and `0x8431A233` to `0x8431A234`.

## State and Data Flow

- Input state is encoded as a packed 32-bit GB18030 four-byte key.
- Output state is an inline UTF-8 byte array; all visible mappings emit three-byte UTF-8 sequences beginning with `0xEF`.
- The final data entry is `0x8431A439 -> { 0xEF, 0xBF, 0xBF }`, followed by `};`.
- The chunk closes `_KERNEL`, the optional C++ `extern "C"` block, and `_SYS_KICONV_GB18030_UTF8_H`.

## Dependencies

- Depends on `kiconv_table_array_t`, `uint32_t`, and `uchar_t`.
- Depends on consumers honoring `KICONV_GBK4_UTF8_MAX` and sorted key order.
- The table is only visible under `_KERNEL`.
- Direct non-header references to `kiconv_gbk4_utf8` were not visible in the searched paths; consumers are likely include-time users of this static header data.

## Risks and Edge Cases

- `static` table data in a header can duplicate storage per including translation unit.
- The table reaches UTF-8 encodings for upper `U+FFxx` values through `U+FFFF`; policy validation, if required, must happen outside this table.
- Lookup code must not infer contiguous Unicode progression because visible jumps skip reserved/unmapped ranges.
- The fourth `u8[4]` byte is implicitly zero for these three-byte mappings and should be treated as padding/terminator-like state, not payload.

## Cross-Chunk References

- Earlier chunks define the header guards, constants, `kiconv_gbk_utf8[]`, and earlier portions of `kiconv_gbk4_utf8[]`.
- Adjacent preceding lines continue the same table and lead into this chunk at `0x8430F230`.
- This chunk closes the four-byte table and the file; no later chunks remain for this source file.
- The final per-file report should merge this with earlier chunk reports rather than deriving file-level behavior from this tail alone.