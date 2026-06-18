# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h lines 49452-61208

## Scope

This report covers only `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h` lines 49452-61208 for learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the enclosing declaration, type, guards, whole-table count, and neighboring chunk boundaries.

The chunk is entirely inside the kernel-only `static kiconv_table_t kiconv_utf8_gb18030[]` initializer declared earlier in the file. It contains 11,757 mapping rows and no declarations, functions, macros, comments, or preprocessor directives of its own.

## APIs And Exported Data

No callable API is defined in this range. The chunk contributes immutable entries to `kiconv_utf8_gb18030[]`, whose adjacent context defines:

- `KICONV_UTF8_GB18030_MAX (63361)`, the full row-count contract for the table.
- `kiconv_utf8_gb18030[]`, a `static kiconv_table_t` array compiled only under `_KERNEL`.
- `kiconv_table_t`, from `sys/kiconv_cck_common.h`, as `{ uint32_t key; uint32_t value; }`.

Each row maps a packed UTF-8 byte sequence in `key` to a packed GB18030 byte sequence in `value`. This chunk starts at `0xEC8599 -> 0x8331FA30` and ends at `0xEF9D85 -> 0x8339D238`.

## Data Covered

Structural checks over the requested line range found:

- 11,757 initializer rows; every line matches the same `0xKEY, 0xVALUE,` shape.
- UTF-8 key range: `0xEC8599` through `0xEF9D85`.
- GB18030 value range by numeric value: minimum two-byte value `0xA140`, maximum four-byte value `0x8339D238`.
- No duplicate UTF-8 keys and no duplicate GB18030 values inside the chunk.
- GB18030 value widths: 9,689 four-byte mappings and 2,068 two-byte mappings.
- UTF-8 leading-byte distribution: `0xEC` 3,751 rows, `0xED` 2,048 rows, `0xEE` 4,096 rows, `0xEF` 1,862 rows.

Most entries are algorithmic GB18030 four-byte mappings in ranges beginning with `0x8331` through `0x8339`. The chunk also contains substantial two-byte compatibility mappings. Visible examples include the transition from `0xED9FBF -> 0x8336C738` to `0xEE8080 -> 0xAAA1`, the later wrap from `0xEE9385 -> 0xFEFE` to `0xEE9386 -> 0xA140`, and mixed private-use/compatibility runs around `0xEE9Dxx` through `0xEEA1xx`.

## Control Flow

There is no local executable control flow: no branches, loops, calls, allocations, locks, or mutable operations appear in this chunk.

Runtime behavior is supplied by the generic kernel kiconv code outside this header. Adjacent common declarations expose `kiconv_binsearch()` and UTF-8-to-CCK wrapper functions that operate on `kiconv_table_t` arrays. The chunk therefore participates in conversion by being searched for a packed UTF-8 key; on match, the paired GB18030 value is emitted by converter glue outside this file.

The UTF-8 key side is sorted by encoded byte sequence, which is a behavioral invariant for binary-search use. Apparent UTF-8 numeric jumps such as `0xEC85BF -> 0xEC8680` are normal UTF-8 byte-sequence progression that skips invalid continuation-byte forms. GB18030 values are not globally sorted because the table is keyed by UTF-8, and because standard two-byte mappings interrupt the generated four-byte ranges.

## State And Dependencies

The only state in this chunk is immutable static initializer data. Because the array is declared `static` in a header, each including kernel translation unit can receive its own internal-linkage copy.

Direct dependencies and surrounding contracts:

- `_KERNEL` must be defined for the enclosing table to exist.
- `kiconv_table_t`, `uint32_t`, and related kernel integer typedefs must be available before this header's table declaration.
- Common UTF-8 validation and conversion wrapper declarations live in `sys/kiconv_cck_common.h`.
- The header is listed with related kiconv data headers in `uts/common/sys/Makefile`.
- Charset-name registration for `gb18030` is visible in `uts/common/os/kiconv.c`, while this table is the UTF-8-to-GB18030 data payload.
- The reverse-direction mapping is in `kiconv_gb18030_utf8.h`; it should be considered a companion table, not a proof that every mapping here round-trips identically.

## Risks And Invariants

Important invariants:

- The full table must retain exactly `KICONV_UTF8_GB18030_MAX` rows.
- Rows must remain sorted by `key`, not by GB18030 `value`.
- Packed literals must preserve byte order expected by the converter.
- Two-byte and four-byte GB18030 values must both be handled correctly by output code; this chunk contains both forms.

Risks:

- Manual edits are high-risk because one wrong literal silently changes kernel filename/string conversion in GB18030 locales.
- Sorting by the wrong field would break lookup despite making the GB18030 side look cleaner.
- Naive validators may misclassify the `0xEE...` private-use UTF-8 key range or the mixed two-byte GB18030 compatibility values as anomalies; they are intentional mapping data.
- The `static` header table can duplicate a large amount of read-only data if included broadly.
- The chunk begins and ends mid-array, so it cannot independently verify opening guards, closing guards, or whole-file row count without adjacent chunks.

## Cross-Chunk References

- Earlier chunks define the license/header guards, `_KERNEL` gate, `KICONV_UTF8_GB18030_MAX`, and the start of `kiconv_utf8_gb18030[]`.
- The immediately preceding line before this chunk maps `0xEC8598 -> 0x8331F939`; this chunk continues at `0xEC8599 -> 0x8331FA30`.
- The next chunk begins at line 61209 with `0xEF9D86 -> 0x8339D239` and later closes the table and file guards at the end of the source file.
- Common conversion semantics should be merged from `kiconv_cck_common.h` research and cross-checked with the companion reverse table `kiconv_gb18030_utf8.h`.