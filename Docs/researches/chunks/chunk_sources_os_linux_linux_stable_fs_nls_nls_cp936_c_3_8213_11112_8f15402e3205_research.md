# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp936.c lines 8213-11112

## Scope

This chunk covers lines 8213-11112 of `sources/os/linux/linux-stable/fs/nls/nls_cp936.c` for `learn_fs` subset A. It starts at the tail of `u2c_7A`, contains the remaining Unicode-to-CP936 byte-pair tables, defines the Unicode page dispatch table and ASCII-only case maps, and ends with the NLS conversion callbacks plus module registration metadata.

The file is an automatically generated CP936/GB2312 translation table with a small handwritten-looking wrapper around Linux's NLS API. This chunk is the only visible part of the requested range that contains executable control flow.

## APIs And Entry Points

- `uni2char()` converts one Unicode code point to one or two CP936 bytes.
- `char2uni()` converts one CP936 byte sequence to one Unicode code point.
- `table` advertises charset `"cp936"`, alias `"gb2312"`, conversion callbacks, and byte-wise case maps.
- `init_nls_cp936()` registers the table with `register_nls(&table)`.
- `exit_nls_cp936()` unregisters it with `unregister_nls(&table)`.
- Module macros expose initialization, exit, description, license, and `gb2312` NLS alias metadata.

## Data Layout

The chunk contains `u2c_*[512]` tables for Unicode high-byte pages `0x7B` through `0x9F`, plus sparse pages `0xDC`, `0xF9`, `0xFA`, `0xFE`, and `0xFF`. It also begins with the final bytes of `u2c_7A`, declared in the previous chunk. Each table stores 256 two-byte CP936 results indexed as `low_byte * 2`; `0x00, 0x00` marks an unmapped Unicode code point.

`page_uni2charset[256]` maps Unicode high bytes to these `u2c_*` tables or `NULL`. `charset2lower[256]` and `charset2upper[256]` only fold ASCII letters; bytes `0x80-0xff` are identity-preserved.

## Control Flow

`uni2char()` rejects `boundlen <= 0`, special-cases `U+20AC` to byte `0x80`, handles Unicode page `0x00` through `u2c_00` with ASCII fallback, and otherwise dispatches through `page_uni2charset[ch]`. Missing pages or `0x00, 0x00` entries return `-EINVAL`; insufficient output space returns `-ENAMETOOLONG`.

`char2uni()` rejects empty input, decodes one-byte input directly with a `0x80 -> U+20AC` exception, and for two-byte input dispatches through `page_charset2uni[ch]`. If a lead-byte table exists and the second byte is nonzero, a zero Unicode result is invalid. Otherwise it falls back to single-byte decoding.

## State And Dependencies

All local state is immutable static data. There is no allocation, locking, or per-instance state.

Dependencies include earlier `c2u_*` tables and `page_charset2uni[256]`, earlier `u2c_*` tables such as `u2c_00`, Linux NLS APIs from `<linux/nls.h>`, errno values from `<linux/errno.h>`, and module infrastructure from `<linux/module.h>`.

## Risks And Edge Cases

- Malformed two-byte input with a missing lead-byte table may be consumed as one byte rather than rejected.
- A zero second byte disables two-byte decoding and falls back to single-byte decoding.
- `U+0000` can encode as byte `0x00`; callers must not assume output is NUL-free.
- Generated `0x00, 0x00` sentinels are semantically meaningful and fragile to manual edits.
- Case conversion is byte-local and ASCII-only, not multibyte-aware.

## Cross-Chunk References

- This chunk starts inside `u2c_7A`; its declaration and most entries are in the previous chunk.
- `char2uni()` depends on `page_charset2uni` and `c2u_*` arrays declared before this chunk.
- `uni2char()` depends on earlier `u2c_*` arrays and the tables completed here.
- This chunk closes the source file; the final per-file report should merge earlier generated table context with this chunk’s callback and module-registration behavior.