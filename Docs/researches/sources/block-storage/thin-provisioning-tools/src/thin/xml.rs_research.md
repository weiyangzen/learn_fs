# File Research: sources/block-storage/thin-provisioning-tools/src/thin/xml.rs

## Purpose
Implements thin metadata XML serialization and parsing using the thin intermediate representation visitor interface.

## Main Components
- `XmlWriter<W>` wraps `quick_xml::Writer<W>` with two-space indentation.
- `METADATA_VERSION` defaults emitted XML superblocks to version `2` when the IR superblock has no explicit version.
- `impl MetadataVisitor for XmlWriter<W>` serializes superblocks, shared definitions, devices, mappings, shared refs, and EOF flush.
- `parse_superblock()`, `parse_device()`, `parse_single_map()`, `parse_range_map()`, and `parse_def()` convert XML element attributes into IR structs.
- `handle_event()` maps `quick_xml` events onto visitor calls.
- `read()` streams an XML input into any `MetadataVisitor`.
- `SBVisitor` and `read_superblock()` provide a lightweight way to extract the first XML superblock.

## XML Model
The writer emits:
- `<superblock uuid time transaction flags? version data_block_size nr_data_blocks metadata_snap?>`
- `<def name>`
- `<device dev_id mapped_blocks transaction creation_time snap_time>`
- empty `<single_mapping origin_block data_block time>` for length 1 mappings,
- empty `<range_mapping origin_begin data_begin length time>` for longer mappings,
- empty `<ref name>`.

The parser recognizes the same element set. Unknown attributes or unknown tags are errors. Text and comments are ignored after trimming.

## Behavior
Parsing is streaming and visitor-driven. A visitor can stop traversal by returning `Visit::Stop`; this is used by `SBVisitor` after the first superblock start tag. EOF calls `visitor.eof()` and stops.

Required attributes are enforced with shared XML helpers. Optional superblock attributes are `flags`, `version`, and `metadata_snap`. Required attributes include core sizing and identity fields such as `uuid`, `time`, `transaction`, `data_block_size`, and `nr_data_blocks`.

## Dependencies and Interactions
This file is used by dump/restore/shrink paths that consume or produce XML metadata. It depends on `crate::thin::ir` for the metadata visitor and data structs, and on top-level `crate::xml` helpers for attribute conversion and validation.

## Research Notes
Several `attributes()` loops call `unwrap()` on XML attribute results, so malformed attribute decoding can panic rather than returning an `anyhow` error. `read_superblock()` also unwraps the collected superblock after `read()`, so an XML input with no superblock would panic.
