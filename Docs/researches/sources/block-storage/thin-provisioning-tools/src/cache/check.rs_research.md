# File Research: sources/block-storage/thin-provisioning-tools/src/cache/check.rs

Implements binary cache metadata validation. It checks the superblock, cache mappings, optional hints, discard bitset, and metadata space map, with limited repair support for metadata leaks and the `needs_check` flag.

Main structures:
- `CacheCheckOptions`: input device, engine options, skip flags, `ignore_non_fatal`, `auto_repair`, `clear_needs_check`, and report handle.
- `format1::MappingChecker`: validates v1 mappings, including valid/dirty flags, invalid entries, origin bounds, and duplicate origin blocks.
- `format2::MappingChecker`: validates v2 mappings with a separate checked dirty bitset, forbids dirty bits on unmapped blocks, validates origin bounds and duplicates.
- `HintChecker`: placeholder array visitor that currently accepts hint blocks without semantic checks.

Core flow:
- Opens an `IoEngine` with write access only when auto-repair or clearing `needs_check`.
- Reads cache superblock at `SUPERBLOCK_LOCATION` and rejects v2+ superblocks without a dirty bitset root.
- Infers origin block count from discard geometry only when clean shutdown and discard fields are populated.
- Walks mapping arrays with metadata space-map accounting, selecting v1 or v2 logic by `sb.version`.
- Walks hint array when present and policy hint width is 4 bytes.
- Walks discard bitset when present.
- If full checks ran, unpacks the metadata space-map root and detects leaks against observed metadata references.
- With `auto_repair` or `clear_needs_check`, repairs metadata leaks and clears `needs_check`.

Notable details:
- Unknown cache metadata versions error out.
- Hints are structurally walked but not semantically validated.
- Skip flags bypass metadata space-map leak checking because complete reference accounting requires all relevant roots.
