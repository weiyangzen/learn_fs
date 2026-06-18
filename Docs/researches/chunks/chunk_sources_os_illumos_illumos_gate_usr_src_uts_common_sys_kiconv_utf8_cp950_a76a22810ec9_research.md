# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_cp950hkscs.h lines 1-13705

## Scope

This chunk is the first 13,705 lines of the illumos kernel UTF-8 to CP950HKSCS conversion table header. It is within subset A because `sources/os/illumos/illumos-gate` is included by `Docs/research_subset_a.md`.

The file is 18,477 lines total. This chunk contains the license/header guard area and the first 13,624 mapping entries of the `kiconv_utf8_cp950hkscs[]` initializer. The array continues after this chunk; this report does not cover the remaining tail or the final closing guards except where needed for cross-chunk continuity.

## Public Surface In This Chunk

- Header guard: `_SYS_KICONV_UTF8_CP950HKSCS_H`.
- C++ linkage wrapper: `extern "C"` around the kernel-only declarations.
- Kernel-only guard: all declarations are under `#ifdef _KERNEL`.
- Mapping count macro: `KICONV_UTF8_CP950HKSCS` is defined as `18387`, the full table entry count for the whole file, not just this chunk.
- Static mapping table: `static kiconv_table_t kiconv_utf8_cp950hkscs[] = { ... }` starts at line 81 and remains open at line 13705.

## Data Shape And Invariants

This chunk is data-only: no functions, branches, loops, or mutable variables are declared here. Each entry maps a packed UTF-8 byte sequence key to a packed CP950HKSCS code value.

Observed properties across lines 82-13705:

- Entries in this chunk: 13,624.
- Malformed entry lines: 0.
- Duplicate UTF-8 keys: 0.
- UTF-8 keys are sorted with no descending transitions.
- Key range: `0x0000` through `0xE8BC9E`.
- Value range: `0x003f` through `0xfefe`.
- Targets: 13,623 double-byte CP950-family values plus the initial single-byte `0x003f`.

The sorted-key invariant matters because `kiconv_cck_common.h` exposes `kiconv_binsearch(uint32_t key, void *tbl, size_t nitems)` for CCK conversion tables.

## Dependencies

- `kiconv_table_t` is defined in `usr/src/uts/common/sys/kiconv_cck_common.h` as `{ uint32_t key; uint32_t value; }`.
- `kiconv.h` defines the kernel kiconv module framework, descriptors, operation tables, and state structures.
- `kiconv.c` assigns `"cp950hkscs"` code ID `17` and registers UTF-8 `<->` CP950HKSCS conversions under `KICONV_MODULE_ID_TC`, module name `"kiconv_tc"`.
- `kiconv_cp950hkscs_utf8.h` is the sibling reverse-direction table.
- `usr/src/uts/common/sys/Makefile` lists this header for the sys header set.
- The file carries CDDL and Unicode data permission notices.

Direct in-tree references to `kiconv_utf8_cp950hkscs` by symbol name were not found outside this header in visible `usr/src`; the visible contract is the static table, count macro, and common CCK conversion API.

## Control Flow Impact

The chunk has no executable control flow, but it feeds kernel conversion behavior:

1. kiconv resolves `"cp950hkscs"` to code ID `17`.
2. UTF-8 to CP950HKSCS conversion is routed through the Traditional Chinese kiconv module family.
3. A UTF-8 input sequence is packed into an integer key.
4. The key is looked up in `kiconv_utf8_cp950hkscs[]`.
5. The mapped CP950HKSCS value is emitted, while buffer bounds and invalid-input policy are handled by common conversion wrappers.

Framework behavior visible nearby includes UTF-8 validation, BOM handling, `EILSEQ`, `EINVAL`, `E2BIG`, and optional replacement via `KICONV_REPLACE_INVALID`.

## State

This chunk declares no mutable runtime state. The array has internal linkage because it is `static`, so an including translation unit gets a private table instance.

Runtime state lives outside this file in kiconv descriptors, module lists, and locks. The table is effectively read-only after compile time, though it is not declared `const`.

## Risks And Cross-Chunk References

- `KICONV_UTF8_CP950HKSCS` is the full table count, while this chunk contains only the first 13,624 entries.
- Binary search depends on sorted, duplicate-free keys; this must remain true across the next chunk.
- The forward table should stay consistent with `kiconv_cp950hkscs_utf8.h`.
- Because this is `static` data in a header, broad inclusion can duplicate memory.
- This chunk ends mid-initializer after `0xE8BC9E, 0xbdfe,`.
- The next line is `0xE8BC9F, 0xbdf9,`, continuing the same table.