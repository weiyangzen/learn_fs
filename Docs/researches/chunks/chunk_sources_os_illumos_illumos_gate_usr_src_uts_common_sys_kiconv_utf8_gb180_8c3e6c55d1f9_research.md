# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h lines 1-11564

## Scope

This chunk covers the start of `kiconv_utf8_gb18030.h`, from the license and include guards through the first 11,483 entries of the UTF-8 to GB18030 kernel conversion table. The chunk ends in the middle of the table at line 11564, so the array terminator, `_KERNEL` close, C++ linkage close, and outer include-guard close are cross-chunk dependencies.

## Purpose and APIs

- Defines `KICONV_UTF8_GB18030_MAX` as `63361`, the whole-file maximum mapping number from UTF-8 to GB18030.
- Starts `static kiconv_table_t kiconv_utf8_gb18030[]`.
- Each row maps a packed UTF-8 byte sequence key to a packed GB18030 value.
- First row is a special/default mapping: `0x0000 -> 0x0000003F`, commented as non-identical conversion fallback.

## Control Flow and State

There is no runtime control flow in this chunk. Its behavior is compile-time table data guarded by `_KERNEL`.

Visible structure:

- Outer include guard: `_SYS_KICONV_UTF8_GB18030_H`.
- Optional C++ `extern "C"` wrapping.
- Kernel-only macro and table under `#ifdef _KERNEL`.
- The table remains open at the chunk boundary.

Visible data properties:

- 11,483 table entries in this chunk.
- 11,035 mappings produce four-byte GB18030 values.
- 448 mappings produce two-byte GB/GBK-compatible values.
- Keys are strictly increasing in the visible range.
- Coverage runs from special `0x0000`, then UTF-8 `0xC280` through `0xE2B599` / Unicode U+0080 through U+2D59.

## Dependencies

- Requires `kiconv_table_t`, defined in `kiconv_cck_common.h` as `{ uint32_t key; uint32_t value; }`.
- Depends on including kernel conversion infrastructure for integer types and lookup/serialization behavior.
- Installed with related kernel iconv headers via `usr/src/uts/common/sys/Makefile`.
- Related files include `kiconv_gb18030_utf8.h` for reverse mapping and `kiconv_sc.h` for GB18030 byte validation helpers.

## Risks

- Consumers likely depend on sorted keys for lookup; visible entries satisfy that invariant.
- `KICONV_UTF8_GB18030_MAX` is not the chunk count.
- The static header table can create private copies in each including translation unit.
- Packed integer values require correct byte-count and byte-order serialization by conversion code.
- Generated table edits are high-risk; validation should check sorted keys, counts, sentinel, final closure, and representative mappings.

## Cross-Chunk References

- Later chunks must close `kiconv_utf8_gb18030[]`.
- Later chunks must verify the final entry and total count against `KICONV_UTF8_GB18030_MAX`.
- Later chunks must confirm ordering continues after `0xE2B599`.
- Later chunks contain the closing `_KERNEL`, C++ linkage, and include-guard directives.