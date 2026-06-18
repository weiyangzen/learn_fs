# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h lines 16911-18412

## Scope

This report covers only ordered chunk 3 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h`, lines 16911-18412, within learn_fs subset A (`Docs/research_subset_a.md`). I read the requested line range completely and used adjacent context only to identify the enclosing declaration, table type, header guards, and kiconv table contract. This chunk is static conversion data, not executable kernel logic.

## APIs And Exported Data

The chunk is the tail of `static kiconv_table_array_t kiconv_cp950hkscs_utf8[]`, declared earlier in the same header under `_KERNEL`. Adjacent context identifies:

- `KICONV_CP950HKSCS_UTF8_MAX` as `18322`, the advertised maximum mapping count for this CP950HKSCS-to-UTF-8 table.
- `kiconv_cp950hkscs_utf8[]` as a `static` header-defined table whose entries have a 32-bit CP950HKSCS key and a four-byte UTF-8 byte array (`uchar_t u8[4]`) from `kiconv_cck_common.h`.

Lines 16911-18403 contribute 1493 final mapping entries. The first entry in this chunk maps CP950HKSCS key `0xf577` to UTF-8 bytes `E9 B6 9F`; the final entry maps `0xfefe` to `E7 A7 94`. Lines 18404-18412 close the array, the `_KERNEL` conditional, the C++ `extern "C"` wrapper, and the `_SYS_KICONV_CP950HKSCS_UTF8_H` header guard.

No functions, macros, typedefs, enums, syscalls, ioctls, locks, callbacks, or VFS/filesystem APIs are defined in this range.

## Control Flow

There is no runtime control flow in this chunk: no branches, loops, calls, allocation, locking, or error paths. Runtime behavior is indirect through whichever CP950HKSCS-to-UTF-8 converter includes this generated header and searches `kiconv_cp950hkscs_utf8[]`.

Lookup-sensitive behavior is implied by the table contract in `kiconv_cck_common.h`: `kiconv_table_array_t` is intended for CCK-encoding-to-UTF-8 mappings, and common code exposes `kiconv_binsearch()`. The key column in this chunk remains sorted in ascending CP950HKSCS order, with valid-code gaps preserved rather than filled.

## State And Data Layout

The state contributed by this chunk is immutable conversion-table state embedded in kernel text/data by inclusion. Each initializer has the form:

`0x<cp950hkscs>, { <utf8 byte 1>, <utf8 byte 2>, <utf8 byte 3> }`

Although `kiconv_table_array_t.u8` has four bytes, this chunk supplies three-byte UTF-8 sequences; the fourth byte is zero-initialized by C aggregate rules.

The chunk spans the high CP950HKSCS key range, including CJK ideograph mappings, box drawing/block glyphs around `0xf9dd`-`0xf9fe`, and many private-use UTF-8 mappings beginning with `EE 80 xx` through `EE 8C xx`. Several CP950HKSCS code positions are absent in the high ranges; those holes are part of the encoding map and must not be compacted into assumed contiguous indexes.

## Dependencies

Direct dependencies include `kiconv_cck_common.h`, `_KERNEL`, the header guard, C++ compatibility wrapper, and illumos typedefs such as `uchar_t` and `uint32_t`.

Related source context shows `kiconv.c` registering normalized code name `cp950hkscs` with code id `17`, `kiconv_utf8_cp950hkscs.h` providing the reverse table, and `usr/src/uts/common/sys/Makefile` installing this header. I did not find a direct C include of this specific header under `usr/src/uts`, so consumers are described conservatively as include-time users of the installed kernel mapping header.

## Risks And Cross-Chunk References

Table order is semantically important for binary-search-style consumers. Missing key positions are meaningful, private-use mappings are compatibility-sensitive, and the three-byte initializer style relies on the fourth `u8` byte being zero-initialized. Because the table is `static` in a header, each including object can receive a private copy.

This chunk starts mid-table; chunks 1 and 2 contain the file header, `KICONV_CP950HKSCS_UTF8_MAX`, the table declaration, and earlier key ranges. This chunk completes the table and closes the file. There is no later chunk after line 18412.