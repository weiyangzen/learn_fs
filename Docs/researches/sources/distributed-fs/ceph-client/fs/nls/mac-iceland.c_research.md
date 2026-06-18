# sources/distributed-fs/ceph-client/fs/nls/mac-iceland.c

## Purpose
`mac-iceland.c` provides the NLS implementation for the classic Macintosh Icelandic code page, registered as `maciceland`. It maps single-byte Macintosh Icelandic filename characters to Unicode and back for filesystem code that requests this charset.

## Important APIs, types, and functions
`charset2uni[256]` maps bytes to Unicode. The ASCII/control range is identity-like except for byte zero being represented as invalid, while the high range carries Latin letters and symbols needed by Mac Icelandic, including Icelandic/Nordic characters, typographic punctuation, mathematical symbols, ligatures, `0x0178`, `0x2044`, and `0x20ac`. Reverse mappings are split across `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`, with `page_uni2charset` pointing only at populated Unicode pages.

The public surface is the `struct nls_table table` for `"maciceland"`. `uni2char()` and `char2uni()` are the standard one-byte generated NLS callbacks. `charset2lower` and `charset2upper` encode byte-preserving case conversion. `init_nls_maciceland()` registers the table at module init, and `exit_nls_maciceland()` unregisters it.

## Control flow
On module initialization, the table is inserted into the global NLS table list. Consumers obtain it by name and call `char2uni()` while decoding byte strings or `uni2char()` while encoding Unicode. `char2uni()` performs one array lookup and rejects `0x0000`. `uni2char()` rejects empty output buffers, derives `ch = uni >> 8` and `cl = uni & 0xff`, looks up the page, then writes one byte only if the page exists and the entry is nonzero.

## State and persistence behavior
The file keeps no dynamic state. All charset, reverse, and casefold tables are immutable. Runtime state is limited to module registration in `nls_base.c`; there is no on-disk persistence and no caching inside this module.

## Dependencies and integration points
The module uses the Linux NLS ABI from `<linux/nls.h>` and returns kernel errno values from `<linux/errno.h>`. It integrates with NLS loading by charset name and with filesystems that store or expose filenames in Mac Icelandic. Its behavior must remain compatible with `nls_base.c` registry locking and module owner pinning.

## Risks and test signals
High-risk areas are exact byte assignments for Icelandic-specific letters, reverse mappings for symbols outside page 00, and case table correctness for accented Latin letters. Because zero in reverse pages signals unmapped, accidental valid mappings to byte zero cannot be represented. Test signals include module load/unload, known byte-to-Unicode vectors for Icelandic characters such as eth/thorn and accented vowels, reverse vectors from Unicode to bytes, case-insensitive comparisons, invalid Unicode page rejection, and buffer-size error behavior.
