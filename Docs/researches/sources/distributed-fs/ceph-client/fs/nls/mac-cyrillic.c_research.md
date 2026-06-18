# sources/distributed-fs/ceph-client/fs/nls/mac-cyrillic.c

## Purpose
This generated NLS module registers the `maccyrillic` Macintosh Cyrillic codepage, translating legacy Mac Cyrillic filename bytes to and from Unicode.

## Important APIs, Types, And Functions
The direct table `charset2uni[256]` contains ASCII, symbols, Cyrillic code points, Numero sign, Euro, and related characters. Reverse lookup uses `page00`, `page01`, `page04`, `page20`, `page21`, and `page22` through `page_uni2charset[256]`; page `0x04` is the main Cyrillic block. `uni2char()` and `char2uni()` are registered in `struct nls_table table` with `.charset = "maccyrillic"`.

## Control Flow
Loading calls `register_nls(&table)`, and unloading calls `unregister_nls(&table)`. Conversion callbacks use constant-time table indexing for single-byte characters and return kernel errno values for insufficient space or unmapped input.

## State, Persistence, And Dependencies
Mapping state is static and read-only. There is no persistence beyond module registration. Dependencies are the kernel NLS core and module loader.

## Integration Points
The Kconfig symbol `NLS_MAC_CYRILLIC` and Makefile object `mac-cyrillic.o` control inclusion. Consumers request the table by the name `maccyrillic`, commonly for HFS-family legacy filenames.

## Risks
Cyrillic codepage compatibility depends on exact historical mappings, including Ukrainian/Serbian/Macedonian extensions and symbol entries. The table does not normalize Unicode or provide transliteration. Placeholder case maps mean case-insensitive comparisons require separate logic.

## Test Signals
Test round trips for the full Cyrillic alphabet range, selected extended Cyrillic code points, Euro and Numero sign, all mapped nonzero bytes, `-EINVAL` on unmapped Unicode, and module load/unload behavior.
