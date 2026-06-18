# File Research: sources/block-storage/thin-provisioning-tools/src/cache/restore.rs

Converts cache XML/IR into binary cache metadata. It owns the `Restorer` visitor used by `cache_restore`, `cache_repair`, and synthetic metadata generation.

Main structures:
- `CacheRestoreOptions`: input XML, output device, metadata version, engine options, report, and `omit_clean_shutdown`.
- `Restorer`: stateful `MetadataVisitor` with array builders for mappings, v2 dirty bitset, hints, discard root, pending roots, buffered dirty word, and section state.
- Internal `Section` state machine enforces superblock/mappings/hints/finalized ordering.

Restore behavior:
- On `superblock_b`, allocates the superblock block, initializes mapping and hint arrays, optionally initializes v2 dirty array, and creates an empty discard bitset root.
- On mapping, writes a valid `Mapping`; v1 stores dirty in mapping flags, v2 records dirty in a packed bitset.
- On hint, converts hint data to the fixed 4-byte `Hint`.
- On finalization, completes arrays, builds metadata space map, constructs binary `cache::superblock::Superblock`, and writes it at block 0.
- Discard visitor methods currently accept and ignore discard events.
- EOF requires prior finalization.

Notable details:
- `hint` uses `try_into().unwrap()` on hint data, so malformed XML hint widths can panic rather than return a structured error.
- Restored metadata uses zero discard geometry and an empty discard root.
