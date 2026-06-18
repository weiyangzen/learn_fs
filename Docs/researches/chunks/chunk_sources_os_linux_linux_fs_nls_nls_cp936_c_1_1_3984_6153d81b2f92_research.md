# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp936.c lines 1-3984

## Scope

This chunk covers the beginning of Linux's CP936/GB2312 NLS module source. The visible code is almost entirely generated static decode data: byte-pair lead-byte tables named `c2u_XX` that map CP936 second bytes to Unicode `wchar_t` values. The chunk starts with module/kernel/NLS includes and ends in the middle of `c2u_F1`, so this report intentionally does not describe the complete file implementation as a standalone unit.

## APIs And External Interfaces

- Includes: `linux/module.h`, `linux/kernel.h`, `linux/string.h`, `linux/nls.h`, and `linux/errno.h` are declared at lines 10-14.
- No callable functions, exported symbols, module init/exit code, or `struct nls_table` definitions are present within lines 1-3984.
- The visible public-facing behavior is data-only: static `const wchar_t` translation arrays used later by `char2uni()` through `page_charset2uni[]`.

## Data Tables

- `c2u_81` starts at line 16 and establishes the recurring table shape: 256 `wchar_t` entries indexed by CP936 trail byte. Invalid/unassigned entries are `0x0000`.
- The chunk defines complete lead-byte tables from `c2u_81` through `c2u_F0`, plus the first visible rows of `c2u_F1`.
- Symbol/compatibility zones appear in `A1-A9`: punctuation/math, Roman numerals, fullwidth ASCII, Hiragana/Katakana, Greek, Cyrillic, box drawing, phonetic/diacritic, Bopomofo-like symbols, and CJK units.
- `AA-AF` include shorter valid ranges with trailing zero fill; later tables return to full GBK/CP936 character ranges.
- Lines 3938-3972 define complete `c2u_F0`.
- Lines 3974-3984 start `c2u_F1` and cover only offsets `0x00-0x4F`; the table continues in the next chunk.

## Control Flow

There is no executable control flow in this chunk. The implied later lookup is:

- First CP936 byte selects a table pointer such as `c2u_81`.
- Second byte indexes that table.
- `0x0000` means unmapped/invalid.

Adjacent context confirms `char2uni()` later selects `page_charset2uni[ch]`, indexes by `cl`, rejects `0x0000`, and returns two consumed bytes for double-byte mappings.

## State And Dependencies

- All tables here are `static const`, immutable, and file-local.
- No runtime state, allocation, locks, reference counts, or mutable globals are introduced.
- Depends on later `page_charset2uni[]` to make these arrays reachable.
- Depends on later NLS registration to expose charset `"cp936"` and alias `"gb2312"`.

## Risks And Cross-Chunk References

- `0x0000` is both invalid sentinel and Unicode NUL, so double-byte table lookups cannot represent Unicode NUL.
- `0x7F` is consistently zeroed and should be rejected as an invalid trail byte.
- Malformed low trail bytes rely on zero entries plus later rejection.
- The chunk boundary is inside the `c2u_F1` initializer; this chunk is not syntactically complete by itself.
- Next chunk must continue and close `c2u_F1`, then define later decode tables and the reverse/registration logic.