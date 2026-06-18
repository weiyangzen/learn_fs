# sources/distributed-fs/ceph-client/fs/nls/nls_cp1250.c

## Purpose
`nls_cp1250.c` implements the Windows CP1250 NLS table for Central European and Slavic languages. It converts single-byte CP1250 data to Unicode and exact Unicode mappings back to CP1250 for filesystem filename handling.

## Important APIs, types, and functions
`charset2uni[256]` maps CP1250 bytes to Unicode. The high range includes `0x20ac`, typographic punctuation, caron/breve/ogonek/double-acute marks, and Central European Latin letters such as L with stroke, S/Z/C/R variants, and other Slavic characters. Some CP1250 byte positions are `0x0000`, marking undefined bytes. Reverse mapping uses `page00`, `page01`, `page02`, `page20`, and `page21`.

`uni2char()` and `char2uni()` provide the generated callback pair. `charset2lower` and `charset2upper` encode CP1250-aware byte case folding. `table` registers `.charset = "cp1250"`. `init_nls_cp1250()` registers the table, and `exit_nls_cp1250()` unregisters it.

## Control flow
The lifecycle is standard for a loadable NLS module. At runtime, byte decoding is one `charset2uni` lookup with zero treated as invalid. Unicode encoding selects a reverse page by high byte, checks for a populated page and nonzero entry, writes the byte, and returns one. No normalization or best-fit substitution is attempted; the comments explicitly indicate exact Unicode-to-charset mappings only.

## State and persistence behavior
The module is stateless after registration. Static tables are immutable and shared. It does not persist data; filesystems persist bytes, while this table determines their interpretation for callers.

## Dependencies and integration points
The file depends on the Linux NLS module ABI and the `nls_base.c` registry. FAT/VFAT and similar filesystems can load `"cp1250"` as an on-disk or I/O charset, use conversion callbacks for filename translation, and use case tables during case-insensitive lookup.

## Risks and test signals
Central European case folding and undefined byte behavior are the main risks. CP1250 is often confused with ISO-8859-2; tests should verify Windows-specific positions such as euro and smart quotes as well as accented letters. Useful tests include known mapping vectors, undefined byte rejection, reverse mapping for page 01 and page 02 characters, upper/lower table validation, buffer bound errors, module lifecycle, and filesystem filename round trips for Polish, Czech, Slovak, Hungarian, and related names.
