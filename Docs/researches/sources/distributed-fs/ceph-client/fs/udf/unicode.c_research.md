# sources/distributed-fs/ceph-client/fs/udf/unicode.c

## Purpose
`unicode.c` converts between UDF OSTA Compressed Unicode CS0 and Linux filenames, with UTF-8/NLS support, surrogate handling, illegal-character replacement, and CRC-based name mangling for uniqueness after truncation or translation.

## Important APIs, types, and functions
Public APIs are `udf_dstrCS0toChar`, `udf_get_filename`, and `udf_put_filename`. Internal helpers include `get_utf16_char`, `udf_name_conv_char`, `udf_name_from_CS0`, and `udf_name_to_CS0`. It uses constants for Unicode planes, surrogate masks, illegal mark `_`, extension mark `.`, CRC mark `#`, and five-character CRC suffixes.

## Control flow
CS0-to-host conversion validates compression id 8 or 16, decodes one- or two-byte UTF-16 units including surrogate pairs, optionally translates `/` and invalid characters to `_`, tracks whether CRC mangling is needed, preserves a short extension when possible, and appends `#XXXX` from `crc_itu_t` when names are truncated, illegal, or become `.`/`..`. Host-to-CS0 conversion uses the configured NLS `char2uni` or UTF-8 decoder, starts in 8-bit compression, retries with 16-bit compression when needed, and emits surrogate pairs for codepoints above BMP.

## State and persistence
No private state exists. The file translates persistent FID and volume dstring names into VFS names and writes newly created names back into FIDs.

## Dependencies and integration points
It depends on `UDF_SB(sb)->s_nls_map`, kernel UTF-8 helpers, NLS callbacks, CRC helpers, and name length constants from `udfdecl.h`. `namei.c`, `symlink.c`, and `super.c` are primary consumers.

## Risks and test signals
Risks include name collisions after mangling, truncation around multibyte output, malformed surrogate pairs, NLS conversion failures, and incorrect dstring length handling. Test signals include ASCII, BMP, non-BMP, invalid UTF-8, invalid CS0 compression ids, odd CS0 byte lengths, names containing `/`, names mapping to `.` or `..`, long extensions, and non-UTF8 `iocharset`.
