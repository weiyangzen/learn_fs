# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp950.c lines 1-4046

## Scope

This chunk covers the start of Linux's CP950/Big5 NLS module. The visible code is generated conversion data plus the first dispatch table for byte-to-Unicode decoding and the start of reverse Unicode-to-byte data. It does not include the executable conversion callbacks, NLS registration, case tables, or module init/exit definitions; those appear after this chunk.

## APIs And External Interfaces

- Includes at lines 10-14 bring in module metadata, kernel helpers, string declarations, the NLS interface, and errno values.
- No functions or exported symbols are defined in this chunk.
- The file-level external contract is implied by later `struct nls_table` use: these static tables back CP950/Big5 conversion callbacks for the kernel NLS layer.
- The comment identifies the table as automatically generated from Microsoft's codepage data. That matters because most edits should be regeneration/verification work, not hand changes to isolated literals.

## Byte-To-Unicode Tables

- Lines 16-3126 define complete `static const wchar_t c2u_XX[256]` pages for CP950 lead bytes: `A1-AF`, `B0-BF`, `C0-C6`, `C9-CF`, `D0-DF`, `E0-EF`, and `F0-F9`.
- There are no `c2u_C7` or `c2u_C8` tables in this chunk; the dispatch table leaves those lead-byte pages `NULL`.
- Each table is indexed by the second byte of a two-byte CP950 sequence. Unassigned entries are `0x0000`.
- Early pages cover punctuation, fullwidth ASCII, Greek, Bopomofo, math signs, box drawing, Roman numerals, and units. Later pages cover dense Traditional Chinese/CJK mappings plus CP950 extensions.

## Decode Dispatch Table

- Lines 3128-3161 define `page_charset2uni[256]`.
- The populated range starts at `0xA1`, maps `0xA1-0xC6`, skips `0xC7-0xC8`, maps `0xC9-0xF9`, and leaves `0xFA-0xFF` as `NULL`.
- Adjacent later code shows `char2uni()` uses this table, rejects `0x0000` entries, and otherwise consumes two bytes; missing pages fall back to one-byte output.

## Unicode-To-Byte Reverse Tables

- Lines 3163-4046 start `static const unsigned char u2c_XX[512]` reverse pages.
- Complete reverse tables visible here include `u2c_02`, `u2c_03`, `u2c_20`, `u2c_21`, `u2c_22`, `u2c_23`, `u2c_25`, `u2c_26`, `u2c_30` through `u2c_33`, and `u2c_4E` through `u2c_52`.
- `u2c_53` starts at line 3985, but this chunk ends inside it at line 4046. The rest continues in the next chunk.
- Reverse entries are byte pairs; `00 00` is the unmapped sentinel rejected later by `uni2char()`.

## State, Dependencies, And Risks

- All visible data is `static const`, file-local, immutable, and lock-free.
- No allocation, mutable state, module lifecycle code, or executable control flow appears in this chunk.
- Later chunks must provide `page_uni2charset`, case maps, conversion callbacks, `struct nls_table`, module init/exit, and `MODULE_ALIAS_NLS(big5)`.
- Main risks are generated-table corruption, dispatch-table slot misalignment, and incorrect conclusions from this chunk alone because the boundary splits `u2c_53`.