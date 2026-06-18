# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp932.c lines 4153-7934

## Scope

This chunk is the second and final chunk of `nls_cp932.c`. It starts in the tail of the generated `u2c_6B` Unicode-to-charset page and then contains the remaining Unicode-to-CP932 lookup pages, the Unicode page dispatch table, ASCII-only case-folding tables, both NLS conversion callbacks, and the module registration metadata for the `cp932` / `sjis` native-language-support table.

## APIs and Entry Points

- `uni2char()` is the Unicode-to-CP932 encoder. It returns bytes written, `-ENAMETOOLONG` for too-small output buffers, or `-EINVAL` for unmapped Unicode.
- `char2uni()` is the CP932-to-Unicode decoder. It returns bytes consumed, `-ENAMETOOLONG` for insufficient input, or `-EINVAL` for invalid/unmapped bytes.
- `table` binds charset `"cp932"`, alias `"sjis"`, conversion callbacks, and case tables into Linux NLS.
- `init_nls_cp932()` registers the table; `exit_nls_cp932()` unregisters it.
- `MODULE_ALIAS_NLS(sjis)` exposes the Shift-JIS alias.

## Data, State, and Control Flow

This chunk is mostly immutable generated lookup data: the tail of `u2c_6B`, `u2c_6C` through `u2c_9F`, sparse pages `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`, plus `page_uni2charset[256]`.

`uni2char()` splits `wchar_t` into high/low bytes, handles `U+FF61..U+FF9F` as one-byte halfwidth katakana, dispatches through `page_uni2charset`, rejects `{0x00, 0x00}` sentinel pairs, and special-cases ASCII plus `u2c_00hi` for `U+00A0..U+00FF`.

`char2uni()` decodes ASCII directly, maps bytes `0xA1..0xDF` to `U+FF61..U+FF9F`, then uses previous-chunk `page_charset2uni` and `c2u_*` tables for two-byte sequences.

Case tables are byte-wise and ASCII-only; all bytes `0x80..0xff` are identity mappings.

## Dependencies

- Includes Linux module/NLS/errno interfaces.
- Depends on chunk 1 for `page_charset2uni`, all `c2u_*` reverse tables, `u2c_00hi`, and earlier `u2c_*` pages.
- Depends on `fs/nls/nls_base.c` registration behavior: `register_nls()` inserts `table` into the global NLS list, and `unregister_nls()` removes it.

## Risks and Edge Cases

- Generated tables are trusted; no runtime consistency check confirms forward and reverse mappings agree.
- `uni2char()` writes two bytes before detecting `{0x00, 0x00}` as unmapped, so buffers may be modified on `-EINVAL`.
- ASCII NUL maps successfully as one byte, while table-derived Unicode `0x0000` means invalid.
- `char2uni()` rejects zero trail bytes before lookup.
- `wchar_t` values are effectively truncated to low 16 bits by `ch`/`cl` extraction.
- No Unicode normalization or Japanese/fullwidth case folding is performed.

## Cross-Chunk References

Chunk 1 owns the reverse CP932-to-Unicode tables and early forward pages. This chunk completes the forward table set and owns the actual conversion callbacks and module lifecycle. Any final per-file correctness review must merge both chunks because the two mapping directions are independently table-driven.