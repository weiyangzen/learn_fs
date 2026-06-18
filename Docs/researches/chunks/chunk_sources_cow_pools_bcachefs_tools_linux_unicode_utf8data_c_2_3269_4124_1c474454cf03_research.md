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