# sources/distributed-fs/ceph-client/fs/nls/mac-roman.c

## Purpose
`mac-roman.c` is the NLS module for the classic Macintosh Roman charset, registered as `macroman`. It is the general Western Macintosh single-byte mapping used for legacy filenames and metadata conversion in filesystems that request this code page.

## Important APIs, types, and functions
`charset2uni[256]` maps bytes to Unicode and includes Western Latin accents, typographic punctuation, currency symbols, mathematical operators, Greek pi/omega symbols, Apple private-use style entries in page `0xf8`, and ligatures in page `0xfb`. Reverse mapping is larger than many sibling files: `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, `pagef8`, and `pagefb` are reachable through `page_uni2charset`.

`uni2char()` and `char2uni()` are the generated callback pair used by `struct nls_table`. `charset2lower` and `charset2upper` define Mac Roman byte case folding. `table` binds `.charset = "macroman"` to those callbacks. `init_nls_macroman()` registers the table, and `exit_nls_macroman()` unregisters it.

## Control flow
Load-time control flow is only module registration. Runtime conversion is table driven: byte input becomes Unicode with one indexed read; Unicode input becomes a byte by splitting the code point into a page selector and offset. The reverse path only succeeds when `page_uni2charset[ch]` exists and its entry for `cl` is nonzero. All successful conversions consume or produce exactly one byte.

## State and persistence behavior
The module stores no per-mount or per-call state. It relies on static immutable mapping tables and the external global NLS registry. It does not persist data; it only interprets byte sequences supplied by filesystem code.

## Dependencies and integration points
The file plugs into the generic Linux NLS registry and is likely to be used by FAT/VFAT and other legacy-media paths when `iocharset=macroman` or equivalent configuration is requested. It depends on `nls_base.c` for registration, module pinning, lookup by charset name, and unload handling.

## Risks and test signals
Mac Roman has broad symbol coverage, so reverse pages beyond basic Latin are easy to regress during regeneration. Case-folding must be checked for accented Latin bytes, not just ASCII. The NLS convention that byte zero is invalid means embedded NUL is not representable. Useful tests include known Mac Roman mapping vectors, round trips for accents, ligatures, and page `0xf8`/`0xfb` entries, case-insensitive filename comparison, invalid Unicode rejection, and error behavior for too-small output buffers.
