# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp949.c lines 1-3837

## Scope

This chunk covers the opening 3,837 lines of the generated ReactOS Ext2 NLS source for code page 949. The file belongs to `sources/windows/reactos`, which is included by `Docs/research_subset_a.md`.

The visible range contains the provenance comment, Linux NLS includes, and the first large byte-to-Unicode lookup-table block for CP949/EUC-KR-compatible multibyte decoding. It starts at `static wchar_t c2u_81[256]` and runs through the beginning of `static wchar_t c2u_ED[256]`; the chunk ends inside `c2u_ED` after the `0x60-0x67` row.

## APIs and Entry Points

- No callable function or exported symbol is defined in this chunk.
- The chunk declares static lookup pages `c2u_81` through `c2u_ED`, one page per possible first byte / lead byte in the CP949 byte stream.
- These arrays are consumed later by `page_charset2uni[256]`, outside this chunk, which dispatches `rawstring[0]` to the matching `c2u_*` page.
- Later code outside this range wires the table data into Linux-style NLS callbacks `char2uni` and `uni2char`, then registers `struct nls_table table` with charset `"cp949"` and alias `"euc-kr"`.

## Control Flow

There is no local control flow in this range. Runtime behavior is table-driven:

- A later decoder checks input length and reads `rawstring[0]` as the lead byte.
- If `page_charset2uni[lead]` is non-`NULL` and the second byte is nonzero, the second byte indexes directly into one of these 256-entry `wchar_t` pages.
- A nonzero table entry is returned as the Unicode value and consumes two bytes.
- A `0x0000` table entry is rejected by the later decoder as an invalid/unmapped double-byte sequence.
- If no page exists for the lead byte, later code falls back to a one-byte identity mapping.

## State and Data Flow

- The chunk stores generated mapping state as file-local `static wchar_t` arrays. They are lookup-only in practice but are not declared `const`.
- Complete regular Hangul-extension pages `c2u_81` through `c2u_A1` each provide 256 initializer values, with 178 nonzero mappings per page. Their populated ranges mostly begin after invalid low-byte slots and map into Hangul syllables from `U+AC02` through `U+C90E`.
- Symbol and compatibility pages `c2u_A2` through `c2u_AF` are more irregular and sparse. Visible mappings include punctuation, arrows, mathematical symbols, fullwidth ASCII, halfwidth Hangul jamo, Roman numerals, Greek, box drawing, circled numbers, hiragana, katakana, Cyrillic, and enclosed CJK/unit symbols.
- Hangul pages `c2u_B0` through `c2u_C8` continue generated syllable mappings from roughly `U+CE9A` through `U+D79D`.
- There is no `c2u_C9` page in this file; later dispatch leaves lead byte `0xC9` as `NULL`.
- CJK/hanja extension pages `c2u_CA` through `c2u_EC` each contain 94 nonzero mappings, mostly in low-byte positions `0xA1-0xFE`.
- The chunk starts `c2u_ED` at line 3824 but only includes its first 104 zero initializer values through low-byte `0x67`.

## Dependencies

- Includes `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`.
- Depends on `wchar_t`, Linux errno constants, module metadata macros, and the NLS `struct nls_table` ABI.
- Depends on later local declarations of `page_charset2uni`, reverse `u2c_*` tables, `page_uni2charset`, byte case maps, `char2uni`, `uni2char`, and module init/exit registration.
- The opening comment identifies the table as automatically generated from Microsoft Unicode code page data.

## Risks and Edge Cases

- The lookup arrays are not `const`, so they may occupy writable storage despite being immutable lookup data.
- Sparse pages rely on `0x0000` sentinels and C zero-initialization; regeneration must preserve unmapped slots.
- The chunk boundary splits `c2u_ED`, so merge errors around line 3837 can break compilation or corrupt lead byte `0xED`.
- Mapping correctness is filesystem-visible: wrong conversion can cause failed lookups, filename aliasing, inconsistent case behavior, or broken round trips.
- Tables do no bounds checking; safety depends on later code using `unsigned char` indexes and checking input length.

## Cross-Chunk References

- The next chunk continues and closes `c2u_ED`, then defines remaining forward pages `c2u_EE` through `c2u_FD`.
- Later `page_charset2uni[256]` maps lead bytes `0x81-0xFD` to these pages, with `NULL` holes such as `0xC9`, `0xFE`, and `0xFF`.
- Later reverse tables `u2c_*` and `page_uni2charset[256]` implement Unicode-to-CP949 conversion.
- Later `charset2lower` and `charset2upper` provide byte-level case conversion.
- Final runtime wiring appears near the end of the file in `uni2char`, `char2uni`, `init_nls_cp949`, `exit_nls_cp949`, `module_init`, `module_exit`, and `MODULE_ALIAS_NLS(euc-kr)`.