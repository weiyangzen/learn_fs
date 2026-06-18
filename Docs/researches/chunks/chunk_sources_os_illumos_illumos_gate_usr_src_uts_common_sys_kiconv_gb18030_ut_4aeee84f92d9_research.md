# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 55470-62958

## Scope

This report covers lines 55470-62958 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h` for `learn_fs` subset A. The slice is entirely inside the kernel-only `static kiconv_table_array_t kiconv_gbk4_utf8[]` initializer, which begins earlier at line 24027 and maps packed GB18030 four-byte codes to UTF-8 byte arrays.

The reviewed range contains 7,489 complete mapping rows. It starts at key `0x8334F931 -> ED 80 94` (`U+D014`) and ends at key `0x8430F139 -> EF B5 BD` (`U+FD7D`). The chunk boundary is clean: line 55469 is the immediately preceding table row, `0x8334F930 -> ED 80 93`, and line 62959 continues with the next row, `0x8430F230 -> EF B5 BE`.

## Public Surface And APIs

This chunk introduces no macros, type definitions, functions, extern declarations, or standalone APIs. Its only contribution is static initializer data for the existing GB18030 four-byte-to-UTF-8 lookup table.

Relevant declarations outside this chunk:

- `KICONV_GBK4_UTF8_MAX (39421)` declares the total number of four-byte GB18030 mappings in the full table.
- `kiconv_gbk4_utf8[]` is a `static kiconv_table_array_t` table visible only when this header is included under `_KERNEL`.
- `kiconv_table_array_t` is declared in `kiconv_cck_common.h` as `{ uint32_t key; uchar_t u8[4]; }`.

Every row initializes a packed four-byte GB18030 key and a three-byte UTF-8 output sequence. The `u8[4]` field's remaining byte is zero-filled by C aggregate initialization.

## Data Layout

All rows in this chunk follow the same initializer shape:

```c
	0x8334F931,	{ 0xED, 0x80, 0x94 },
```

Observed row properties:

- Mapping rows: 7,489.
- First row: line 55470, `0x8334F931 -> ED 80 94` (`U+D014`).
- Last row: line 62958, `0x8430F139 -> EF B5 BD` (`U+FD7D`).
- Key order: strictly ascending throughout the chunk.
- UTF-8 initializer width: all rows in the requested range use three bytes.
- Format check: no malformed initializer lines were found in the requested range.

The UTF-8 output range is mostly ascending by Unicode code point, but not perfectly contiguous. Important visible transitions:

- Lines 55470-57497 continue dense mappings from `U+D014` through `U+D7FF`, ending immediately before the surrogate range.
- Line 57498 jumps from `U+D7FF` to `U+E76C`, intentionally skipping surrogate code points and earlier private-use code points.
- Lines 57498-57579 contain sparse Private Use Area mappings around `U+E76C` through `U+E865`, with several expected gaps.
- The table later enters compatibility and presentation-form ranges, including CJK compatibility-style output around `U+F900` and following blocks.
- Lines 61874-62107 contain additional sparse compatibility-code-point gaps.
- Lines 62897-62958 continue through `U+FD40`-style presentation forms and end at `U+FD7D`.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior comes from the surrounding kiconv implementation that consumes the table:

1. GB18030 byte validation is defined outside this header, notably by byte-class macros in `kiconv_sc.h`.
2. A valid four-byte GB18030 sequence is packed into a `uint32_t` key.
3. Conversion code searches `kiconv_gbk4_utf8[]`; the strict key ordering preserved here is necessary for binary-search lookup through `kiconv_binsearch()`.
4. On match, the row's `u8` bytes are copied to the output buffer.
5. Buffer-limit handling, replacement behavior, and errno setting are implemented by the converter code and shared kiconv helpers, not by this data table.

This chunk's behavioral role is therefore indirect but important: it preserves a large ordered segment of lookup data for kernel GB18030-to-UTF-8 conversion.

## State And Dependencies

State in this chunk is immutable static initializer data compiled into translation units that include the header. There is no mutable state, locking, allocation, reference counting, I/O, or error handling inside the range.

Dependencies visible from adjacent file context and related headers:

- The enclosing header guard is `_SYS_KICONV_GB18030_UTF8_H`.
- The table declarations are under `_KERNEL`.
- `kiconv_table_array_t` and `kiconv_binsearch()` are declared in `uts/common/sys/kiconv_cck_common.h`.
- GB18030 validation helpers and plane constants live in `uts/common/sys/kiconv_sc.h`, including the four-byte byte-class macros and `KICONV_SC_PLANE1_GB18030_START`.
- `uts/common/sys/Makefile` installs/exports this table header alongside the reverse-direction `kiconv_utf8_gb18030.h`.
- `uts/common/os/kiconv.c` registers GB18030-related encoding names for the kernel iconv subsystem.

## Risks And Invariants

Important invariants for this chunk:

- Every row must remain syntactically complete because the file is a direct C initializer.
- Keys must remain strictly sorted for binary-search consumers.
- `KICONV_GBK4_UTF8_MAX` must match the total row count of the complete `kiconv_gbk4_utf8[]` table, not this chunk's count.
- UTF-8 byte arrays must remain semantically correct; many edits would still compile while silently changing character conversion behavior.
- Gaps in Unicode output are expected in this region and should not be flagged as ordering defects by validators that understand the mapping table.

Risks visible here:

- Generated-data drift: one incorrect key or byte sequence can corrupt conversion for a specific GB18030 character while leaving the table syntactically valid.
- Boundary risk: this chunk starts and ends mid-table, so full validation must include adjacent chunks and the final table terminator.
- Unicode-special-range risk: the dense run stops before surrogate code points, then resumes in private-use and compatibility/presentation blocks; audits must distinguish intentional sparse mapping from missing rows.
- Static-header duplication risk remains a file-level property: because this is a `static` table in a header, including it in multiple kernel translation units can duplicate storage.

## Cross-Chunk References

Previous chunk(s) must account for:

- The license/header guard, `_KERNEL` guard, `KICONV_GBK_UTF8_MAX`, and `KICONV_GBK4_UTF8_MAX`.
- The complete two-byte `kiconv_gbk_utf8[]` table ending at line 24025.
- Start of `kiconv_gbk4_utf8[]` at line 24027.
- Rows before this range, ending immediately before this chunk at line 55469 with `0x8334F930 -> ED 80 93`.

Next chunk(s) must continue with:

- The row after this chunk at line 62959, `0x8430F230 -> EF B5 BE`.
- Remaining `kiconv_gbk4_utf8[]` mappings through the table close at line 63449.
- Closing `_KERNEL`, C++ `extern "C"`, and header guard directives at the end of the file.