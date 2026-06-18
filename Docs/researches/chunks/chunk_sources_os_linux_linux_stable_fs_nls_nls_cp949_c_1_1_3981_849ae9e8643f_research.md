# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp949.c lines 1-3981

## Scope

This chunk covers the file prologue, kernel/NLS includes, and the first large block of CP949-to-Unicode translation data. It is generated table content, not procedural filesystem code. The range ends in the middle of the `c2u_F1` initializer, so `c2u_F1` is incomplete in this chunk and must be joined with the next chunk for a complete table view.

## APIs and Data Definitions

- Includes: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`. The direct type dependency visible here is `wchar_t`, used for Unicode code points in the charset-to-Unicode pages.
- Defines static read-only arrays named `c2u_XX`, each representing one CP949 lead-byte page and indexed by the second byte. The visible completed pages are `c2u_81` through `c2u_F0`, with no `c2u_C9` page in this range.
- Each array is declared as `static const wchar_t c2u_XX[256]`, but several initializers intentionally provide fewer than 256 explicit literals; C zero-initialization fills the remainder. This appears in compact sparse pages such as `c2u_A2`, `c2u_A6`, `c2u_A7`, `c2u_AA`, `c2u_AB`, `c2u_AC`, and `c2u_AD`-`c2u_AF`.
- The chunk starts `c2u_F1` at line 3968 and includes entries only through second-byte range `0x60-0x67` at line 3981. The visible part of `c2u_F1` has 104 explicit entries, all `0x0000`.

## Table Semantics

- `0x0000` is used as the invalid/unmapped sentinel for byte pairs that are not assigned in CP949. This is especially common in control-byte regions, separator gaps, and sparse Hanja/compatibility pages.
- Pages `0x81`-`0xA0` mostly map CP949 extension byte pairs to Hangul syllables in the Unicode Hangul Syllables block, beginning at values such as `0xAC02`.
- Pages `0xA1`-`0xA9` mix Hangul extension entries with punctuation, fullwidth ASCII, Hangul compatibility jamo, Greek, box drawing, units, enclosed forms, and other compatibility symbols.
- Pages `0xAA` and `0xAB` contain Japanese Hiragana and Katakana ranges after CP949 extension entries.
- Page `0xAC` includes Cyrillic upper/lowercase blocks after extension entries.
- Pages `0xCA` and later in this chunk carry Hanja/CJK ideographs and compatibility ideographs, with many zero-filled low-byte slots before valid mappings begin around second byte `0xA1`.
- Many completed pages follow the same lead-byte layout: low second-byte positions are zero-filled, then assigned code points appear in the printable/trailing-byte ranges, followed by a final zero at `0xFF`.

## Control Flow

There is no executable control flow in lines 1-3981. The only "flow" is data lookup implied by the table shape:

1. A later decoder will select a page by CP949 lead byte.
2. It will index that page by the following byte.
3. A nonzero `wchar_t` result is a Unicode mapping; `0x0000` indicates an invalid or unmapped byte pair.

The actual `char2uni`, `uni2char`, `struct nls_table`, module init/exit, and reverse Unicode-to-charset tables are outside this chunk.

## State and Lifetime

- All visible state is `static const` translation data with internal linkage.
- The arrays are immutable after compilation and safe for concurrent lookup without locking.
- There is no allocation, reference counting, module registration, or mutable global state in this chunk.

## Dependencies

- Kernel NLS infrastructure is implied by `<linux/nls.h>` and by the naming/layout expected by the later conversion callbacks.
- Module infrastructure is included here but only used in later chunks for registration metadata and init/exit functions.
- The generated table source is documented as Microsoft's CP949 Unicode mapping data in the file comment.

## Risks and Invariants

- Correctness is entirely table-driven. A single wrong literal, missing page pointer, or shifted initializer would silently corrupt filename/metadata charset conversion for Korean CP949/EUC-KR users.
- Sparse initializers rely on C zero-fill semantics. This is valid but important: changing these tables mechanically without preserving implicit trailing zeroes can alter invalid-byte behavior.
- `0x0000` cannot represent U+0000 as a valid decoded result here; it is treated as "no mapping" by the expected decoder contract.
- The chunk boundary is risky for automated analysis because it splits `c2u_F1`; consumers must not treat line 3981 as the end of that table.
- Because the data is generated, manual edits should be avoided unless validated against the authoritative CP949 mapping and the reverse `u2c_*` tables in later chunks.

## Cross-Chunk References

- `c2u_F1` continues after line 3981 and completes in the next chunk.
- Later chunks define the remaining `c2u_*` pages, reverse `u2c_*` Unicode-to-CP949 tables, page pointer tables, case conversion tables, and the NLS callback functions that consume this data.
- The merge report should connect this chunk's `c2u_*` data to the later `char2uni()` implementation and `page_charset2uni`/equivalent page selection table, because this chunk alone does not show how the arrays are selected at runtime.