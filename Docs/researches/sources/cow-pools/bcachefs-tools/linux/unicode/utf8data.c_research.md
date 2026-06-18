# File Research: sources/cow-pools/bcachefs-tools/linux/unicode/utf8data.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-3268, source bytes 262070, report `Docs/researches/chunks/chunk_sources_cow_pools_bcachefs_tools_linux_unicode_utf8data_c_1_1_3268_fe075f187e2d_research.md`
- chunk 2: lines 3269-4124, source bytes 69216, report `Docs/researches/chunks/chunk_sources_cow_pools_bcachefs_tools_linux_unicode_utf8data_c_2_3269_4124_1c474454cf03_research.md`

## Chunk Research

### Chunk 1: lines 1-3268

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

The `utf8data[]` payload is a compact trie plus leaf/decomposition data. Visible embedded section markers show the chunk includes these generated subregions:

- `nfdicf_30100`
- `nfdi_30100`
- `nfdicf_30200`
- `nfdi_30200`
- `nfdicf_c0100`
- the beginning and much of `nfdi_c0100`

The byte stream contains trie navigation bytes, generation indexes, canonical combining class values, NUL-terminated decomposition strings, and UTF-8 decomposition outputs. The visible data includes decomposition/casefold mappings for Latin, Greek, Cyrillic, Armenian, Georgian, Cherokee, fullwidth Latin, Old Italic, Deseret, CJK compatibility ideographs, Hebrew marks, Japanese kana voiced/semi-voiced forms, and multiple Indic/SE Asian/Tibetan/Myanmar-script sequences.

## Control Flow

There is no runtime control flow in this chunk. Runtime consumers interpret the static data as follows:

- `utf8_load()` in `linux/unicode/utf8-core.c` stores `&utf8_data_table` in `struct unicode_map::tables`, checks `utf8version_is_supported()`, and selects per-normalization `struct utf8data` entries with `find_table_version()`.
- `utf8version_is_supported()` in `linux/unicode/utf8-norm.c` scans `um->tables->utf8agetab` backward until the leading zero sentinel and accepts exact version matches.
- `utf8nlookup()` in `linux/unicode/utf8-norm.c` starts at `um->tables->utf8data + um->ntab[n]->offset`, walks the encoded trie, and returns a leaf for valid UTF-8 code point sequences.
- `utf8nlen()` and `utf8byte()` use leaf generation values (`LEAF_GEN`) to compare against `utf8agetab` and `um->ntab[n]->maxage`; code points newer than the selected Unicode version are treated as too new for normalization.
- Leaves with canonical combining class `DECOMPOSE` expose `LEAF_STR(leaf)`, a decomposition string stored in this byte array. Hangul has a special marker and is decomposed algorithmically outside this generated data.

## State And Invariants

- All state here is immutable static storage. There is no allocation, locking, mutation, or per-call state in the chunk.
- `utf8agetab[]`, `utf8nfdicfdata[]`, `utf8nfdidata[]`, and `utf8data[]` must remain mutually consistent: generation indexes in trie leaves index `utf8agetab[]`, while selected table offsets must point to valid trie roots in `utf8data[]`.
- `utf8data[]` is declared with fixed size `64256`; this chunk only covers its prefix. The closing array initializer is later in the file.
- The generated bytecode assumes the interpreter constants in `utf8-norm.c` (`OFFLEN`, `RIGHTPATH`, `TRIENODE`, `LEAF_GEN`, `LEAF_CCC`, `LEAF_STR`, etc.) match the generator's encoding.
- The version arrays are searched from the end and rely on a zero sentinel at index 0. Removing or reordering the initial `0` would affect `utf8version_is_supported()`.

## Dependencies

- Local ABI dependency: `utf8n.h` defines `struct utf8data`, `struct utf8data_table`, `UTF8_NFDI`, `UTF8_NFDICF`, and the `utf8_data_table` extern declaration.
- Public Unicode API dependency: `include/linux/unicode.h` defines `UNICODE_AGE()`, `UTF8_LATEST`, `enum utf8_normalization`, and `struct unicode_map`.
- Runtime dependency: `utf8-core.c` and `utf8-norm.c` must agree with this generated data's table shape and trie encoding.
- Kernel-compat dependency: `ARRAY_SIZE` from `<linux/kernel.h>` is used later in this file when constructing `utf8_data_table`; that wrapper is outside this chunk.

## Risks

- Generated-data drift: manual edits are explicitly prohibited by the file header. Any byte-level change can silently corrupt validation, normalization, casefolding, or version gating.
- Cross-file coupling: `utf8-norm.c` interprets bytes using hard-coded bit masks and leaf semantics. Regenerating with a different encoder without updating the interpreter would cause invalid traversal or wrong decompositions.
- Offset sensitivity: `utf8nfdicfdata[]` and `utf8nfdidata[]` use raw offsets into `utf8data[]`; inserting/removing bytes in one generated subregion requires all later offsets to be regenerated.
- Version behavior: versions older than `UTF8_LATEST` intentionally use older table roots. Mistakes in `maxage` or offsets could make bcachefs-tools accept or normalize names differently from the intended Unicode version.
- Chunk boundary: this chunk ends while `utf8data[]` is still open. Any complete-file reasoning about the exported `utf8_data_table`, final array length, or trailing generated data requires later chunks.

## Cross-Chunk References

- Later lines in this same file close `utf8data[]` and define `const struct utf8data_table utf8_data_table`, binding the arrays from this chunk into the runtime-visible table.
- Later chunks contain the remainder of `nfdi_c0100` and additional generated trie/decomposition subregions needed by offsets `20736` and beyond.
- `utf8-core.c` relies on the exported `utf8_data_table`; this chunk provides the backing arrays but not the export.
- `utf8-norm.c` is the primary interpreter for the byte array in this chunk and documents the trie/leaf format used by this generated payload.

### Chunk 2: lines 3269-4124

# Chunk Research: sources/cow-pools/bcachefs-tools/linux/unicode/utf8data.c lines 3269-4124

## Scope

This chunk covers the final 856 lines of generated UTF-8 normalization data in `utf8data.c`. Lines 3269-4108 are the tail of `static const unsigned char utf8data[64256]`; lines 4110-4124 publish that byte table and the companion version/offset tables through `utf8_data_table`.

The file is explicitly generated code. This chunk should be treated as table payload plus one exported descriptor, not as hand-authored algorithmic logic.

## APIs And Symbols

- `utf8data[64256]`: this chunk contains the terminal slice of the private bytecode/trie payload consumed by the Unicode normalization engine.
- `utf8_data_table`: defined at lines 4110-4121 as the public `const struct utf8data_table` descriptor for this generated data file.
- `EXPORT_SYMBOL_GPL(utf8_data_table)`: exports the descriptor to GPL-compatible kernel users at line 4122.
- `MODULE_DESCRIPTION("UTF8 data table")` and `MODULE_LICENSE("GPL v2")`: module metadata at lines 4123-4124.

No functions, callbacks, syscalls, or direct filesystem entry points are implemented in this chunk.

## Data And State

The chunk is immutable static data. It has no runtime-owned state, locks, allocation, reference counts, error paths, or mutation. Runtime state lives in consumers that hold pointers into this table, especially `struct unicode_map`.

The descriptor at lines 4110-4121 binds `.utf8agetab`, `.utf8nfdicfdata`, `.utf8nfdidata`, and `.utf8data` into one exported table matching `struct utf8data_table` in `utf8n.h`.

## Control Flow

There is no local executable control flow except static initialization. Effective control flow is external: `utf8_load()` assigns `um->tables = &utf8_data_table`, selects version entries, and `utf8-norm.c` walks trie data from `um->tables->utf8data + um->ntab[n]->offset`.

## Dependencies

- Earlier file includes: `<linux/module.h>`, `<linux/kernel.h>`, `"utf8n.h"`.
- Uses `ARRAY_SIZE`.
- Consumed by `utf8-core.c` and `utf8-norm.c`.
- Export depends on kernel module/export infrastructure.

## Risks And Invariants

- Generated data must remain synchronized with `utf8nfdicfdata[]`, `utf8nfdidata[]`, and `utf8agetab[]`.
- Consumers do pointer arithmetic into `utf8data[]`; `struct utf8data_table` carries no explicit byte-table length.
- Any byte corruption can alter normalization/casefold results or trie traversal.
- Validation should compare generated output or run Unicode normalization tests, not rely on visual review.

## Cross-Chunk References

- Earlier chunks define the companion arrays and the beginning/middle of `utf8data[]`.
- This chunk closes the final `nfdi_c0100` payload and exports the aggregate descriptor.
- Algorithmic behavior belongs to consumers in `utf8-core.c` and `utf8-norm.c`; this chunk is backing data only.
