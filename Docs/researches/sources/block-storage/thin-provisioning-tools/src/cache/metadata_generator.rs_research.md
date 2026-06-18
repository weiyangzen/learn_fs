# File Research: sources/block-storage/thin-provisioning-tools/src/cache/metadata_generator.rs

Development module for generating synthetic cache metadata and mutating selected superblock fields.

Main types:
- `MetadataGenerator` trait with `generate_metadata`.
- `CacheGenerator`: block size, cache block count, origin block count, resident/dirty percentages, metadata version, hotspot size.
- `CacheFormatOpts`, `MetadataOp`, and `CacheGenerateOpts`.

Generation behavior:
- Emits an IR superblock with policy `smq` and 4-byte hints.
- Chooses resident cache blocks randomly.
- Chooses origin blocks in randomly placed hotspot runs, then pairs origin blocks with cache blocks.
- Emits sorted mappings by cache block, with dirty state based on configured percentage.
- Emits default 4-byte hints for resident cache blocks.
- Restores generated IR into binary metadata through `cache::restore::Restorer`.

Mutation operations:
- Set `needs_check`.
- Set `clean_shutdown`.
- Set superblock version directly. Comments warn this does not convert formats and can intentionally create invalid/leaky metadata.
