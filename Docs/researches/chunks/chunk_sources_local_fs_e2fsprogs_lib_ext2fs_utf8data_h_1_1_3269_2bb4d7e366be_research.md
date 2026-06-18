# Chunk Research: sources/local-fs/e2fsprogs/lib/ext2fs/utf8data.h lines 1-3269

## Scope

This report covers lines 1-3269 of `sources/local-fs/e2fsprogs/lib/ext2fs/utf8data.h` for `learn_fs` subset A. The file is generated data, not handwritten control code. The chunk begins at the file header and continues through the first 3269 lines of the `utf8data[64256]` byte array, ending inside the large `nfdi_c0100` payload. It does not include the end of the byte array or the closing declaration at line 4109.

## Public Surface And APIs

This chunk defines static objects consumed by `lib/ext2fs/nls_utf8.c`:

- `static const unsigned int utf8vers = 0xc0100;` records the latest supported Unicode version encoded as `UNICODE_AGE(12, 1, 0)`.
- `static const unsigned int utf8agetab[]` maps compact leaf generation indexes to encoded Unicode versions.
- `static const struct utf8data utf8nfdicfdata[]` maps max-age values to offsets in `utf8data` for NFD + default-ignorable filtering + full casefold normalization.
- `static const struct utf8data utf8nfdidata[]` maps max-age values to offsets in `utf8data` for NFD + default-ignorable filtering without casefold.
- `static const unsigned char utf8data[64256]` starts the packed trie bytecode backing both normalization forms.

The header refuses direct inclusion unless `__INCLUDED_FROM_UTF8NORM_C__` is defined. In this repository, `nls_utf8.c` defines that macro, declares `struct utf8data`, includes this header, then undefines the macro.

## Data Layout Visible In This Chunk

The byte array contains labeled subtrees:

- `nfdicf_30100` at line 87.
- `nfdi_30100` at line 144.
- `nfdicf_30200` at line 201.
- `nfdi_30200` at line 246.
- `nfdicf_c0100` at line 291, offset `3200`.
- `nfdi_c0100` at line 1388, offset `20736`.

The `utf8nfdicfdata[]` and `utf8nfdidata[]` offsets align with these labels. The chunk ends inside `nfdi_c0100`.

## Control Flow

There is no executable control flow in this header. The consumer in `nls_utf8.c` uses the data as follows:

1. `utf8nfdi(maxage)` and `utf8nfdicf(maxage)` select a `struct utf8data` root by Unicode version.
2. `utf8nlookup(data, hangul, s, len)` starts at `utf8data + data->offset`.
3. Trie bytes drive branch decisions over UTF-8 input bytes.
4. Leaf bytes provide generation, canonical combining class, and decomposition string.
5. Callers use `utf8agetab[LEAF_GEN(leaf)]` for max-age checks.
6. Decomposition strings are emitted by cursor logic; Hangul decomposition is algorithmic in `nls_utf8.c`.

## State, Dependencies, Risks

All state is immutable static const generated data. Key invariants are valid offsets, valid generation indexes into `utf8agetab[]`, NUL-terminated embedded decompositions, and a final byte count matching `utf8data[64256]`.

Dependencies are supplied by `nls_utf8.c`: `struct utf8data`, trie bitfield macros, leaf macros, and normalization cursor code. Downstream APIs are declared in `utf8n.h`.

Main risks are generated-data drift, stale inclusion comment naming `nls_utf8-norm.c` while this tree uses `nls_utf8.c`, version-table mismatch, mishandling empty decompositions for default-ignorable code points, and accidental removal of meaningful zero bytes.

## Cross-Chunk References

Later chunk(s) must continue `nfdi_c0100` from line 3270 through the closing initializer at line 4109 and confirm the declared array size and final payload integrity.