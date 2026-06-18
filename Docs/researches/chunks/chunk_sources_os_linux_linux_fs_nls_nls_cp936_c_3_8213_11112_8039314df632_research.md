# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp936.c lines 8213-11112

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/linux/linux` is explicitly in scope.
- Source span read: lines 8213-11112 of `fs/nls/nls_cp936.c`.
- This is chunk 3 of the oversized CP936/GB2312 Linux NLS module. It starts at the tail of `u2c_7A[512]`, then completes the Unicode-to-CP936 mapping tables, defines the Unicode-page dispatch table, byte-wise case tables, conversion callbacks, NLS table registration, and module metadata.
- This report is chunk-only and does not create or replace the final per-file report.

## APIs And Entry Points

- `uni2char(...)` encodes Unicode to CP936 bytes and returns bytes written or `-ENAMETOOLONG`/`-EINVAL`.
- `char2uni(...)` decodes CP936 to Unicode and returns bytes consumed or `-ENAMETOOLONG`/`-EINVAL`.
- `table` registers charset `"cp936"` with alias `"gb2312"`, conversion callbacks, and case tables.
- `init_nls_cp936()` / `exit_nls_cp936()` register and unregister the NLS table.
- Module metadata exposes the GB2312 alias and dual BSD/GPL license.

## Data Structures

- Completes `u2c_7A[512]`, then defines `u2c_7B` through `u2c_9F`, plus sparse pages `u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FE`, and `u2c_FF`.
- `u2c_*[512]` pages store two-byte CP936 output at `Unicode_low_byte * 2`; `{0x00, 0x00}` means unmapped.
- `page_uni2charset[256]` dispatches Unicode high-byte pages to `u2c_*` tables or `NULL`.
- `charset2lower[256]` and `charset2upper[256]` are ASCII-only byte case maps; bytes `0x80..0xff` are identity.

## Control Flow

`uni2char()` checks output length, special-cases `U+20AC` to byte `0x80`, handles Unicode page `0x00` through `u2c_00` with ASCII fallback including `U+0000`, then dispatches other pages through `page_uni2charset`. It requires two bytes of output space before table-based two-byte writes and rejects zero-pair mappings.

`char2uni()` rejects empty input. With one input byte, it maps `0x80` to `U+20AC` and every other byte directly. With two or more bytes, it uses `page_charset2uni[ch]` from earlier chunks when available and `cl != 0`; zero Unicode table results are invalid. Otherwise it falls back to one-byte decoding.

## State And Dependencies

- All lookup tables are static immutable file-local data.
- Depends on chunks 1 and 2 for `c2u_*`, `page_charset2uni`, and earlier `u2c_*` pages.
- Depends on Linux NLS registration APIs via `register_nls()` / `unregister_nls()`.
- No allocation, locking, reference counts, or mutable conversion state.

## Risks And Edge Cases

- Table corruption silently changes filename transcoding behavior.
- `uni2char()` writes two table bytes before checking for `{0x00, 0x00}`, so output may be modified on `-EINVAL`.
- `char2uni()` treats a lone high byte as a one-byte character, not an incomplete sequence error.
- Trail byte `0x00` falls back to one-byte lead-byte decoding.
- Unicode handling is effectively limited to low 16 bits of `wchar_t`.
- `U+0000` is valid through ASCII fallback, while zero table entries are sentinels.
- No normalization or non-ASCII case folding is performed.

## Cross-Chunk References

- Chunk 1 defines early byte-to-Unicode `c2u_*` tables.
- Chunk 2 completes `page_charset2uni` and starts reverse `u2c_*` tables through partial `u2c_7A`.
- This chunk owns the final reverse tables, dispatch table, callbacks, and module lifecycle; full file behavior requires merging all three chunks.