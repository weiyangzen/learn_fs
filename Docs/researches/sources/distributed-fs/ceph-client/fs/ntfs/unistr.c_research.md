# sources/distributed-fs/ceph-client/fs/ntfs/unistr.c

## Purpose
Implements legacy NTFS Unicode name comparison, collation, duplication, and conversion between loaded Linux NLS encodings and NTFS little-endian UTF-16 strings.

## Important APIs, Types, And Functions
`ntfs_are_names_equal()` and `ntfs_names_are_equal()` compare fixed-length names either case-sensitively via `ntfs_ucsncmp()` or case-insensitively via `ntfs_ucsncasecmp()` and the volume upcase table. `ntfs_collate_names()` implements NTFS index collation and rejects invalid ANSI characters in the first name using `legal_ansi_char_array`. `ntfs_file_compare_values()` adapts file-name attributes to collation. `ntfs_nlstoucs()` allocates and converts NLS/UTF-8 input to little-endian UTF-16. `ntfs_ucstonls()` converts UTF-16 back to NLS/UTF-8, growing allocated output for non-UTF-8 encodings if needed. `ntfs_ucsndup()` duplicates bounded UTF-16 strings.

## Control Flow
Comparison functions iterate code units, endian-convert each character, optionally upcase table entries within range, and return lexical ordering. Conversion from NLS to UTF-16 uses the UTF-8 kernel helper when `vol->nls_utf8` is set, otherwise calls `nls->char2uni()` per source character. Conversion back uses `utf16s_to_utf8s()` for UTF-8 or `nls->uni2char()` with dynamic buffer growth for other NLS maps.

## State And Persistence
No persistent state is owned here, but conversions create heap buffers that callers store in NTFS attributes, volume labels, dentries, and lookup keys. The routines depend on `vol->nls_map`, `vol->nls_utf8`, and `vol->upcase`.

## Dependencies And Integration Points
Used by directory/index lookup, volume label writes, mount-time label reads, file-name attribute comparisons, and case-insensitive lookup. Depends on the `ntfs_name_cache` slab from `super.c` and on Linux NLS/UTF-8 helpers.

## Risks And Edge Cases
Invalid or unconvertible characters map to `-EILSEQ`; overlong names return `-ENAMETOOLONG`. Callers must free buffers with the correct allocator: cache for normal NTFS names, `kvfree()` for larger max-name conversions, and `kfree()` for NLS output. Collation only validates invalid characters in `name1`, matching index insertion/search semantics but requiring correct argument ordering. Surrogate handling is delegated to kernel UTF helpers.

## Test Signals
Test case-sensitive and case-insensitive equality, invalid NTFS characters, names at `NTFS_MAX_NAME_LEN`, UTF-8 and non-UTF-8 NLS conversion, unconvertible characters, output buffer growth, embedded NUL behavior, and big-endian conversion.
