# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp936.c lines 1-3840

## Scope

This chunk covers the opening 3,840 lines of the generated ReactOS Ext2 NLS source for code page 936. The file belongs to `sources/windows/reactos`, which is included by `Docs/research_subset_a.md`.

The visible range contains the file provenance comment, Linux NLS headers, and the first large block of CP936 byte-to-Unicode lookup tables. It starts `static wchar_t c2u_81[256]` and continues through the beginning of `static wchar_t c2u_ED[256]`; the range ends in the middle of `c2u_ED`.

## APIs and Entry Points

- No callable function or exported API is defined in this chunk.
- The chunk declares static data arrays named `c2u_81` through `c2u_ED`, one array per possible high byte/lead byte of the CP936 double-byte encoding.
- The arrays are intended for later use through `page_charset2uni[256]`, which is declared after the complete `c2u_*` table block outside this chunk.
- Later file code, outside this range, wires the tables into Linux-style NLS callbacks `char2uni` and `uni2char`, then registers a `struct nls_table` for charset `cp936` with alias `gb2312`.

## Control Flow

There is no local control flow in this chunk. Runtime behavior is table-driven:

- A later decoder reads the first byte of an input string as `ch`.
- If `page_charset2uni[ch]` points to one of these `c2u_*` arrays, the second byte `cl` indexes directly into the 256-entry `wchar_t` page.
- A nonzero table value is a Unicode code point; `0x0000` represents an unmapped or invalid byte pair.

Because the range is only data, all branch behavior, input length checks, ASCII fallback, and NLS registration happen in later chunks.

## State and Data Flow

- The chunk stores immutable mapping state as `static wchar_t` arrays, though the declarations are not `const`.
- Each complete table maps `CP936 high byte + low byte` to one Unicode `wchar_t` value.
- Most arrays reserve low-byte ranges `0x00-0x3F` as `0x0000`, with populated mappings beginning at low byte `0x40`.
- Many rows deliberately end with `0x0000` at low byte `0x7F` and `0xFF`, matching invalid CP936 byte positions.
- Visible Unicode outputs include CJK unified ideographs, compatibility/private compatibility values such as `0xF91B`, `0xF92D`, `0xF978`, `0xFA15`, and mixed GBK/CP936 extension mappings.
- `c2u_A4` through `c2u_AF` are shorter initializer blocks than the regular 35-line pages, relying on zero-fill for omitted trailing entries.
- The chunk ends after the first 80 initialized entries of `c2u_ED`; the remainder of `c2u_ED` is in the next chunk.

Complete arrays in this chunk:

- `c2u_81` through `c2u_A3`
- `c2u_A4` through `c2u_AF`, with sparse/truncated initializers
- `c2u_B0` through `c2u_EC`

Partial array in this chunk:

- `c2u_ED`, starting at line 3830 and continuing beyond line 3840

## Dependencies

- Includes Linux kernel/NLS headers: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`.
- Depends on `wchar_t` and Linux NLS infrastructure supplied by those headers.
- Depends on later local declarations of `page_charset2uni`, reverse `u2c_*` tables, case-folding tables, `char2uni`, `uni2char`, and `struct nls_table`.
- The opening comment says the table was automatically generated from Microsoft CP936/Unicode data; maintainers should treat it as generated mapping data rather than hand-authored logic.

## Risks and Edge Cases

- The data is declared `static` but not `const`, so it may occupy writable storage even though it is lookup-only.
- A split or merge error around this chunk boundary would leave `c2u_ED` incomplete and break compilation or corrupt the mapping table.
- Consumers must distinguish `0x0000` as an invalid mapping sentinel from valid Unicode output; the later decoder rejects `0x0000` after table lookup.
- Sparse/truncated arrays rely on C zero-initialization. Mechanical regeneration or conversion to another format must preserve that behavior.
- Mapping correctness is security-relevant for filesystem names: wrong byte-to-Unicode conversion can cause name aliasing, failed lookup, or inconsistent case handling when filenames contain CP936 multibyte sequences.
- These tables do not perform bounds checks themselves. Safety depends on later code only indexing arrays with `unsigned char` values and checking input length before reading a second byte.

## Cross-Chunk References

- Next chunk must continue and close `c2u_ED`, then continue the remaining `c2u_EE` through `c2u_FE` pages.
- Later chunks define `page_charset2uni[256]`, which maps lead bytes `0x81-0xFE` to the `c2u_*` arrays declared here and leaves other lead bytes `NULL`.
- Later chunks define reverse Unicode-to-CP936 `u2c_*` tables and `page_uni2charset[256]`; those are the counterpart path for `uni2char`.
- Later chunks define `charset2lower` and `charset2upper`, which provide byte-level case conversion for the registered NLS table.
- The final executable behavior appears near the end of the file in `uni2char`, `char2uni`, `init_nls_cp936`, `exit_nls_cp936`, `module_init`, and `module_exit`; this chunk only supplies part of their lookup state.