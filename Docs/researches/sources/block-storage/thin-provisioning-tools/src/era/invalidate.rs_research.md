# File Research: sources/block-storage/thin-provisioning-tools/src/era/invalidate.rs

This file implements `era_invalidate` style output: it emits XML ranges of data blocks changed since a threshold era.

Important components:
- `BitsetCollator` ORs writeset bit arrays into a composed bitset.
- `EraArrayCollator` marks blocks whose era-array value is at or above the threshold.
- `mark_blocks_since()` combines writesets at/after the threshold and, when needed, the era array.
- XML helpers emit `<blocks>`, `<range begin=... end=...>`, and single `<block block=...>` elements.

Public entry point:
- `invalidate(EraInvalidateOptions)`

Integration points:
- Opens metadata through `EngineBuilder`.
- Reads normal or metadata-snapshot superblock depending on engine options.
- Uses `ArrayWalker`, `btree_to_map`, `Writeset`, and shared XML attribute helpers.

Risks and notes:
- Writeset and era-array walking uses non-repair mode.
- Range output uses end-exclusive ranges.
- The `archived_begin` comparison determines when era-array data must supplement writesets.
