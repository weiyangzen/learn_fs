# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp950.c lines 1-4046

## Scope

This chunk covers the beginning of Linux's generated CP950/Big5 NLS module. It includes the file header, Linux/NLS includes, the complete forward byte-to-Unicode table pages for CP950 lead bytes `0xA1` through `0xF9`, the `page_charset2uni` dispatch table, and the first reverse Unicode-to-charset table pages through most of `u2c_53`. The chunk ends inside `u2c_53`; executable conversion functions and module registration are outside this chunk.

## APIs And Dependencies

- The chunk declares no callable functions. Its public behavior is indirect: later `uni2char`, `char2uni`, and `struct nls_table` code use these static tables to implement the kernel NLS API for the `big5` alias.
- Includes at lines 10-14 pull in kernel module infrastructure, core kernel definitions, string helpers, NLS interfaces, and errno values. In this chunk, the visible dependency is mainly `wchar_t` from Linux NLS/types and `NULL` for dispatch tables.
- All visible data is `static const`, so it has internal linkage and read-only semantics once compiled into the module.

## Forward Charset-To-Unicode State

- `c2u_A1` begins at line 16 and maps CP950 lead byte `0xA1`, indexed by trail byte. It contains punctuation, full-width forms, arrows, box/geometry symbols, and other non-CJK symbols.
- The chunk defines complete `wchar_t c2u_XX[256]` pages for `XX = A1..AF`, `B0..BF`, `C0..C6`, `C9..CF`, `D0..DF`, `E0..EF`, and `F0..F9`.
- `c2u_C7` and `c2u_C8` are absent; `page_charset2uni` maps those lead-byte slots to `NULL`. `FA..FF` are also `NULL`.
- `0x0000` entries represent unmapped byte positions. Valid Big5/CP950 trails mostly appear in `0x40..0x7E` and `0xA1..0xFE`.
- `c2u_F9` includes CP950 extension and box-drawing mappings near the end, including Unicode box-drawing code points around `0x2550..0x2570`.

## Forward Dispatch Table

- `page_charset2uni[256]` at lines 3128-3161 is the first-level lookup table for double-byte decoding.
- Later decoding can read `page_charset2uni[first_byte]`; a `NULL` page is an invalid lead byte, while a non-`NULL` page maps the second byte.
- The `c2u_*` arrays are consumed through this dispatch table.

## Reverse Unicode-To-Charset State

- Reverse mapping begins at `u2c_02[512]` on line 3163. Each table stores two bytes per low-byte Unicode code point. `0x00, 0x00` means unmapped.
- Complete reverse pages visible here include `u2c_02`, `u2c_03`, `u2c_20`, `u2c_21`, `u2c_22`, `u2c_23`, `u2c_25`, `u2c_26`, `u2c_30`, `u2c_31`, `u2c_32`, `u2c_33`, `u2c_4E`, `u2c_4F`, `u2c_50`, `u2c_51`, and `u2c_52`.
- `u2c_53[512]` starts at line 3985 and is only partially inside this chunk. Lines 3985-4046 cover through low-byte comments `0xEC-0xEF`; the remaining `0xF0-0xFF` entries and closing brace continue in the next chunk.

## Control Flow

- There is no runtime control flow in this chunk. It is static table initialization.
- Implied decode flow: later code handles ASCII/single-byte cases, then uses `page_charset2uni[first_byte]`, rejects `NULL`, indexes by second byte, and rejects `0x0000`.
- Implied encode flow: later code uses a Unicode high byte to select `page_uni2charset`, indexes a `u2c_XX` page by low byte, and treats `0x00,0x00` as unmapped.

## Risks And Invariants

- Table generation integrity is the main risk; a misplaced value silently changes filename encoding/decoding behavior for filesystems using this NLS table.
- `0x0000` and `0x00,0x00` are sentinels and must remain distinguishable from valid mappings.
- Forward and reverse tables must remain mutually consistent. Reverse tables encode the chosen canonical CP950 byte sequence for `uni2char`.
- The chunk boundary splits `u2c_53`; merged reporting must treat lines 3985-4051 as one logical table.
- Later conversion functions must enforce unsigned indexing, input length, and page availability.

## Cross-Chunk References

- Lines after 4046 continue and close `u2c_53`, then define more `u2c_*` pages, `page_uni2charset`, case conversion tables, `uni2char`, `char2uni`, the `nls_table`, and module init/exit registration.
- The final per-file report should connect this chunk’s `page_charset2uni` to later `char2uni`, and this chunk’s early `u2c_*` pages to later `page_uni2charset` and `uni2char`.