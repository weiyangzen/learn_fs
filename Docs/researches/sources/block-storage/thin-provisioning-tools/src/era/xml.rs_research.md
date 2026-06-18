# File Research: sources/block-storage/thin-provisioning-tools/src/era/xml.rs

This file implements XML serialization and parsing for era metadata IR.

`XmlWriter<W>` implements `MetadataVisitor` and writes:
- `<superblock uuid=... block_size=... nr_blocks=... current_era=...>`
- `<writeset era=... nr_bits=...>`
- Compact `<marked block_begin=... len=...>` ranges or verbose `<bit block=... value=...>` entries.
- `<era_array>` and `<era block=... era=...>` entries.

Parsing:
- `parse_superblock()`, `parse_writeset()`, `parse_writeset_bit()`, `parse_writeset_blocks()`, and `parse_era()` validate known attributes.
- `handle_event()` dispatches quick-xml events to a `MetadataVisitor`.
- `read()` streams XML into the visitor until EOF or visitor stop.

Integration points:
- Dump emits XML through `XmlWriter`.
- Restore reads XML through `read()` into `Restorer`.
- Uses shared XML attribute parsing helpers from `crate::xml`.

Risks and notes:
- `parse_superblock()` reports missing `nr_blocks` with attribute name `"nr_cache_blocks"`, likely a diagnostic typo.
- Attribute iteration uses `unwrap()` on XML attributes, so malformed attribute objects can panic rather than return `anyhow`.
