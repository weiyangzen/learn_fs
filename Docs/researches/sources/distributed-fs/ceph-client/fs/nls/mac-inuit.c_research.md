# sources/distributed-fs/ceph-client/fs/nls/mac-inuit.c

## Purpose
`mac-inuit.c` implements the `macinuit` NLS table for Macintosh Inuit/Inuktitut text. It is a single-byte charset adapter that maps high-byte values to Unicode Canadian Aboriginal Syllabics code points and selected Latin/symbol characters, enabling filename conversion when a filesystem is configured for this legacy Macintosh encoding.

## Important APIs, types, and functions
`charset2uni[256]` is the forward byte-to-Unicode table. The high half prominently maps into Unicode pages `0x14`, `0x15`, and `0x16` for syllabics, with additional punctuation, trademark/copyright symbols, `0x0141`, and `0x0142`. Reverse conversion uses `page00`, `page01`, `page14`, `page15`, `page16`, `page20`, and `page21` through `page_uni2charset`.

The conversion callbacks are the generated `uni2char()` and `char2uni()` functions. `uni2char()` enforces a one-byte output buffer, rejects missing reverse pages or zero entries, and returns one byte on success. `char2uni()` rejects entries that map to `0x0000`. `table` registers `.charset = "macinuit"` with conversion and byte-case tables. `init_nls_macinuit()` and `exit_nls_macinuit()` are the module lifecycle hooks.

## Control flow
The module follows the common NLS table pattern. Initialization registers the table; consumers load it by the `macinuit` name; each conversion is a stateless table lookup. Unlike multibyte encodings, there is no shift state, lead-byte handling, combining logic, or normalization. Case conversion is table based and byte oriented; most syllabic bytes map to themselves because the charset does not have ASCII-like upper/lower pairs for those symbols.

## State and persistence behavior
There is no mutable file-local state. Mapping data and case tables are `static const`, and all persistence remains in the filesystem using this translation layer. Registry state is external in the NLS core and only changes at module load/unload.

## Dependencies and integration points
The file depends on the NLS module ABI and is loaded through the same `load_nls()` path as other charset modules. It can be used by FAT/VFAT-style filename conversion or any kernel user of `struct nls_table`. Because it includes Unicode-generated data and license text, maintainers should regenerate it from authoritative tables rather than manually edit individual code points.

## Risks and test signals
The risk profile is dominated by table correctness for syllabic code points and reverse page coverage. Missing reverse entries make Unicode names impossible to encode even if byte-to-Unicode decoding works. Test coverage should include representative byte ranges that map to pages 14, 15, and 16; round-trip checks for syllabic characters; invalid Unicode inputs outside populated pages; ASCII passthrough except NUL; and module lifecycle registration. Filesystem tests should create, lookup, and compare names containing syllabics.
