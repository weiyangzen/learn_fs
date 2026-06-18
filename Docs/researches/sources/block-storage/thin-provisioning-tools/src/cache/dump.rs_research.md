# File Research: sources/block-storage/thin-provisioning-tools/src/cache/dump.rs

Converts binary cache metadata into the cache intermediate representation, normally written as XML. It handles both cache metadata formats and can optionally tolerate/repair traversal errors while dumping.

Main components:
- `format1::MappingEmitter`: emits valid v1 mappings and records valid cache blocks in a `FixedBitSet`.
- `format2::MappingEmitter`: reads dirty state from a separate checked dirty bitset and emits valid v2 mappings.
- `HintEmitter`: emits hints only for cache blocks that had valid mappings.
- `OutputVisitor`: wraps another `MetadataVisitor` and adds output-context error handling.
- `CacheDumpOptions`: input path, optional output path, engine options, and repair flag.

Core flow:
- Reads the cache superblock.
- Emits an IR superblock containing block size, cache block count, policy name, and hint width.
- Emits mappings using v1 inline dirty flags or v2 dirty bitset.
- Emits hints filtered to valid mappings.
- Emits superblock end and EOF.
- `dump` writes XML to a requested output file or stdout via `cache::xml::XmlWriter`.

Notable details:
- v2 dump requires `dirty_root`; missing root is an error.
- If dirty bitset entries are damaged during repair-mode dumping, dirty defaults to true.
- Discard IR methods exist, but this dump path does not emit discard ranges.
