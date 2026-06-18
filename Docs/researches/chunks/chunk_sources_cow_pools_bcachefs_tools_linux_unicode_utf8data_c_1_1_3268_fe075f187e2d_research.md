# Chunk Research: sources/cow-pools/bcachefs-tools/linux/unicode/utf8data.c lines 1-3268

## Scope

This chunk is the first 3,268 lines of generated Unicode normalization data for the in-tree Linux Unicode support copied into `bcachefs-tools`. It is in subset A because `sources/cow-pools/bcachefs-tools` is included by `Docs/research_subset_a.md`.

The chunk does not define executable functions. It defines static lookup tables and the beginning of a large bytecode/trie payload consumed by the Unicode normalization implementation in adjacent files.

## APIs And Exports

- Includes `<linux/module.h>`, `<linux/kernel.h>`, and local `"utf8n.h"`.
- Defines `static const unsigned int utf8agetab[]` at lines 7-31. This is the supported Unicode age table, encoded with `UNICODE_AGE()`-compatible integer values: `0`, `1.1.0`, `2.0.0`, `2.1.0`, `3.0.0`, `3.1.0`, `3.2.0`, `4.0.0`, `4.1.0`, `5.0.0`, `5.1.0`, `5.2.0`, `6.0.0`, `6.1.0`, `6.2.0`, `6.3.0`, `7.0.0`, `8.0.0`, `9.0.0`, `10.0.0`, `11.0.0`, `12.0.0`, `12.1.0`.
- Defines `static const struct utf8data utf8nfdicfdata[]` at lines 33-57. Each entry maps a Unicode max-age to an offset in `utf8data[]` for the NFD + Default-Ignorable removal + full casefold normalization form (`UTF8_NFDICF`).
- Defines `static const struct utf8data utf8nfdidata[]` at lines 59-83. Each entry maps a Unicode max-age to an offset in `utf8data[]` for the NFD + Default-Ignorable removal normalization form (`UTF8_NFDI`).
- Begins `static const unsigned char utf8data[64256]` at line 85. This chunk contains the initial 3,184 lines of that byte array and stops before the array and exported wrapper are complete.
- No symbol is exported in this chunk. The public wrapper `const struct utf8data_table utf8_data_table` is outside the chunk near lines 4110-4120 and will be covered by a later chunk.

## Data Layout

`struct utf8data` is declared in `linux/unicode/utf8n.h` as:

- `maxage`: highest Unicode age supported by this table entry.
- `offset`: byte offset into `utf8data[]`.

The two version-index arrays have parallel age entries but different offsets:

- `utf8nfdicfdata`: early Unicode versions mostly point at offset `0`; version `3.2.0` points at `1792`; versions `4.0.0` and later point at `3200`.
- `utf8nfdidata`: versions through `3.1.0` point at `896`; version `3.2.0` points at `2496`; versions `4.0.0` and later point at `20736`.

The `utf8data[]` payload is a compact trie plus leaf/decomposition data. Visible embedded section markers show the chunk includes these generated subregions: `nfdicf_30100`, `nfdi_30100`, `nfdicf_30200`, `nfdi_30200`, `nfdicf_c0100`, and the beginning and much of `nfdi_c0100`.

## Control Flow

There is no runtime control flow in this chunk. Runtime consumers interpret the static data through `utf8_load()`, `utf8version_is_supported()`, `utf8nlookup()`, `utf8nlen()`, and `utf8byte()` in adjacent Unicode files.

`utf8nlookup()` starts at `um->tables->utf8data + um->ntab[n]->offset`, walks the encoded trie, and returns a leaf for valid UTF-8 code point sequences. Leaves carry generation, canonical combining class, and optional decomposition strings. Hangul is decomposed algorithmically outside this generated data.

## State And Dependencies

All state here is immutable static storage. There is no allocation, locking, mutation, or per-call state in the chunk.

The data depends on `utf8n.h` for table structs, `include/linux/unicode.h` for Unicode age/version definitions and normalization enums, and `utf8-norm.c` for the bytecode interpreter constants and leaf semantics.

## Risks

- Manual edits can silently corrupt validation, normalization, casefolding, or version gating.
- Raw offsets into `utf8data[]` mean inserting/removing bytes requires full regeneration.
- `utf8-norm.c` and this generated encoding are tightly coupled.
- This chunk ends while `utf8data[]` is still open; exported wrapper and complete-file validation require later chunks.

## Cross-Chunk References

Later lines in this file close `utf8data[]` and define `const struct utf8data_table utf8_data_table`, binding this chunk’s arrays into the runtime-visible table. Later chunks also contain the remainder of `nfdi_c0100` and additional generated trie/decomposition regions needed by higher offsets.