# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 32218-39351

## Scope

This chunk is inside the illumos kernel-only EUC-TW/CNS11643 to UTF-8 conversion header. The requested range is entirely static mapping data plus one table boundary:

- Lines 32218-35911: tail of `static kiconv_table_array_t kiconv_cns5_utf8[]`.
- Lines 35912-35913: close of plane 5 table.
- Lines 35914-35916: start of `static kiconv_table_array_t kiconv_cns6_utf8[]`, including its `0x0000` replacement-character sentinel.
- Lines 35917-39351: early/middle portion of plane 6 mappings.

## APIs And Data Types

No callable API, macro, or executable function is defined in this chunk. The data belongs to the kernel character conversion subsystem.

Entries use `kiconv_table_array_t`:

```c
typedef struct {
	uint32_t key;
	uchar_t u8[4];
} kiconv_table_array_t;
```

Each mapping stores a CNS11643/EUC-TW two-byte key and UTF-8 output bytes. Three-byte UTF-8 entries rely on C zero-initialization for the unused fourth byte; four-byte mappings fill all bytes.

## Table Coverage

Mechanical scan found 7,130 initializers including the plane-6 sentinel, or 7,129 real CNS keys:

- `kiconv_cns5_utf8`: 3,694 entries, `0xD5B5` through `0xFCD1`.
- `kiconv_cns6_utf8`: 3,436 entries including sentinel, `0x0000` through `0xC5D5`.
- Plane 6 real entries here: 3,435 entries, `0xA1A1` through `0xC5D5`.

UTF-8 byte lengths:

- 6,830 four-byte mappings.
- 300 three-byte mappings.

Real CNS keys are monotonically increasing within each table segment. Apart from the intentional `0x0000` sentinel, keys use valid EUC/CNS byte ranges.

## Control Flow And State

There is no local control flow. External EUC-TW parsing identifies the CNS plane and key, then looks up the selected `kiconv_cnsN_utf8` table.

The chunk contributes immutable static kernel storage. It has no mutable state, locks, allocations, or runtime initialization.

## Dependencies

- `_KERNEL` controls compilation of these tables.
- `kiconv_table_array_t` defines the storage layout.
- `KICONV_CNS5_UTF8_MAX` and `KICONV_CNS6_UTF8_MAX` must match full table sizes and sentinel conventions.
- `kiconv_tc.h` provides EUC-TW validation and plane parsing macros.
- `kiconv.c` registers encoding name `euctw` with code id `16`.

## Risks

- Sentinel handling matters: `kiconv_cns6_utf8` starts with `0x0000 -> EF BF BD`.
- Consumers must not blindly emit all four `u8` bytes for three-byte UTF-8 mappings.
- Because arrays are `static` in a header, each includer can receive a private copy unless build structure avoids that.
- Data errors are behavioral bugs: one wrong key, byte, comma, or ordering change can silently corrupt conversion.
- Mappings are documented as Unicode 3.2/Unihan 3.2.0, so updating to newer Unicode data requires reverse-table compatibility review.

## Cross-Chunk References

- Previous chunks contain the file header, max-count macros, planes 1-4, and the beginning of plane 5 through `0xD5B4`.
- This chunk completes plane 5 and starts plane 6.
- Later chunks continue plane 6 after `0xC5D5`, then define planes 7 and 15.
- Reverse conversion data lives in `kiconv_utf8_euctw.h`; round-trip behavior depends on consistency between the two headers.