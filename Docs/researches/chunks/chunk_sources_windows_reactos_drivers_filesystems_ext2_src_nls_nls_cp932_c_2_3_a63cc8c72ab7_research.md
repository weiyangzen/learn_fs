# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp932.c lines 3984-7946

## Scope

This chunk is the second ordered slice of the ReactOS ext2 CP932/SJIS NLS module. It starts in the middle of the Unicode-to-charset table section, at the tail of `u2c_68`, and runs through the end of the file. The scope is within `Docs/research_subset_a.md` because `sources/windows/reactos` is part of subset A.

The chunk contains mostly generated static data plus the executable conversion and module-registration code:

- Unicode high-byte pages `u2c_69` through `u2c_9F`, plus sparse special pages `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`.
- The `page_uni2charset[256]` dispatch table that maps Unicode high bytes to the `u2c_*` pages.
- ASCII-oriented `charset2lower[256]` and `charset2upper[256]` casefold tables.
- `uni2char`, `char2uni`, `struct nls_table table`, `init_nls_cp932`, `exit_nls_cp932`, and module metadata.

## APIs And Data Contracts

- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)` implements the NLS Unicode-to-CP932 callback. It returns a positive byte count on success and negative errno-style values on failure.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)` implements the reverse CP932-to-Unicode callback.
- `table` exposes the charset as `"cp932"` with alias `"sjis"` through the kernel-style `struct nls_table` interface.
- `init_nls_cp932` calls `register_nls(&table)`, and `exit_nls_cp932` calls `unregister_nls(&table)`.
- `MODULE_ALIAS_NLS(sjis)` advertises the SJIS alias for module autoloading.

The data pages use a compact two-byte-per-low-byte contract. For Unicode page `0xHH`, `u2c_HH[cl * 2]` and `u2c_HH[cl * 2 + 1]` contain the CP932 byte pair for Unicode `0xHHcl`. A pair of `0x00, 0x00` means unmapped.

## Control Flow

`uni2char` rejects non-positive output bounds, handles U+FF61..U+FF9F as one-byte CP932 halfwidth katakana, dispatches other mapped Unicode pages through `page_uni2charset`, handles ASCII and Latin-1 high characters specially, and otherwise returns `-EINVAL`.

`char2uni` mirrors this: ASCII is identity, CP932 `0xA1..0xDF` maps to U+FF61..U+FF9F, and two-byte input is resolved through earlier `page_charset2uni` tables. There is no filesystem I/O, allocation, locking, or per-mount state in this chunk.

## State And Dependencies

- `u2c_69` through `u2c_9F` cover dense CJK/Japanese Unicode pages U+6900 through U+9FFF.
- `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF` are sparse/special Unicode pages, including compatibility ideographs and fullwidth forms.
- `page_uni2charset` depends on arrays from this and earlier chunks, including `u2c_03`, `u2c_04`, `u2c_20` through `u2c_68`.
- `uni2char` depends on earlier `u2c_00hi`.
- `char2uni` depends on earlier `page_charset2uni`.
- The chunk begins with the tail of `u2c_68`; `u2c_69` starts at line 3991. Line 7946 is the file end, so no later chunk exists.

## Risks And Edge Cases

- `uni2char` checks `boundlen < 2` before checking whether a two-byte table entry is unmapped, so some unmapped characters return `-ENAMETOOLONG` with a one-byte output buffer instead of `-EINVAL`.
- Sparse/partially initialized pages rely on C zero-initialization.
- Tables are mutable `static unsigned char` rather than `const`.
- The table is named `"cp932"` but aliases `"sjis"`, so callers expecting strict Shift-JIS may receive CP932 extensions.
- Case tables only fold ASCII bytes; they do not perform Unicode or width-aware normalization.

## Research Notes

This chunk is primarily NLS conversion data plus registration glue, not ext2 filesystem logic. Correctness depends on consistency between these forward `u2c_*` pages and the reverse tables from earlier chunks.