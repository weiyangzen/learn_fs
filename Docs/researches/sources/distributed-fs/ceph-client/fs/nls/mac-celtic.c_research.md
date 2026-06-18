# sources/distributed-fs/ceph-client/fs/nls/mac-celtic.c

## Purpose
This generated NLS module registers the `macceltic` single-byte Macintosh Celtic codepage. It translates bytes to Unicode and exact Unicode code points back to bytes for legacy Mac/HFS filenames.

## Important APIs, Types, And Functions
The key data are `charset2uni[256]`, sparse reverse pages `page00`, `page01`, `page03`, `page1e`, `page20`, `page21`, `page22`, `page25`, `page26`, `page_uni2charset[256]`, and placeholder `charset2lower`/`charset2upper` tables. `uni2char()` validates output space and looks up the high-byte page plus low-byte index. `char2uni()` maps one input byte through `charset2uni`. `struct nls_table table` names the charset `macceltic`; module init/exit call `register_nls()` and `unregister_nls()`.

## Control Flow
Loading the module registers the table with the NLS core. Filesystems call `uni2char` or `char2uni` through that table. Conversion is single-byte and returns `1` on success, `-ENAMETOOLONG` for no output space, and `-EINVAL` for unmapped code points or byte zero.

## State, Persistence, And Dependencies
All mapping state is read-only static data generated from Unicode mapping files. There is no persistent runtime state. Dependencies are `linux/nls.h`, module infrastructure, and errno values.

## Integration Points
`CONFIG_NLS_MAC_CELTIC` in Kconfig and `mac-celtic.o` in the NLS Makefile control availability. HFS-family and other NLS consumers can request `macceltic` by name.

## Risks
The mapping is exact-only, so Unicode normalization or visually equivalent composed/decomposed forms are not handled. Byte `0x00` maps to Unicode NUL but `char2uni()` treats resulting zero as invalid, which is consistent with pathname expectations. Case maps are sentinel-filled, so callers should not expect meaningful case folding from this table.

## Test Signals
Tests should round-trip every nonzero byte with a reverse mapping, verify selected Celtic/Welsh code points including Euro and W/Y diacritics, exercise unmapped Unicode returning `-EINVAL`, and load/unload the module repeatedly.
