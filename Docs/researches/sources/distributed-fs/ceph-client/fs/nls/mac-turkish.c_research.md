# sources/distributed-fs/ceph-client/fs/nls/mac-turkish.c

## Purpose
`mac-turkish.c` provides the Macintosh Turkish NLS module, registered as `macturkish`. It maps legacy single-byte Turkish Macintosh filenames to Unicode and encodes Unicode back to the charset where exact mappings exist.

## Important APIs, types, and functions
`charset2uni[256]` holds forward byte mappings. The table is Mac Roman-like in structure but differs for Turkish letters and related case pairs such as dotted/dotless I and other Turkish-specific Latin characters. Reverse conversion is split into `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`, selected through `page_uni2charset`.

`uni2char()` and `char2uni()` implement the NLS callback contract. The `charset2lower` and `charset2upper` arrays are especially important here because Turkish case behavior differs from simple ASCII assumptions. `table` registers the callbacks under `.charset = "macturkish"`. `init_nls_macturkish()` calls `register_nls()`, and `exit_nls_macturkish()` calls `unregister_nls()`.

## Control flow
On module load, registration makes the table discoverable. Runtime control flow is a one-character conversion path: byte-to-Unicode indexes `charset2uni`; Unicode-to-byte derives a reverse page and byte offset. Missing mappings and zero entries return `-EINVAL`, and an output bound of zero or less returns `-ENAMETOOLONG`. There is no multibyte parsing or locale-sensitive dynamic logic.

## State and persistence behavior
The file is stateless aside from module registration. Static tables are read-only and shared by all callers. No filesystem state is written by this module, and no conversion history is retained.

## Dependencies and integration points
It depends on `<linux/nls.h>` and the core registry in `nls_base.c`. Filesystems that support configurable NLS charsets use the `macturkish` table through `struct nls_table` callbacks and byte case helpers. The exact mapping comes from generated Unicode charset data, so integration compatibility is table-data compatibility rather than algorithm complexity.

## Risks and test signals
Turkish-specific case folding is the key behavioral risk. Incorrect upper/lower tables can break case-insensitive lookup even if round-trip conversion works. Other risks include accidentally inheriting values from Mac Roman during regeneration, missing reverse mappings for Turkish letters, and the invalid-NUL convention. Tests should cover dotted and dotless I byte mappings, other Turkish Latin letters, lower/upper table behavior, invalid Unicode pages, `boundlen` handling, module registration, and filename lookup on a case-insensitive filesystem path.
