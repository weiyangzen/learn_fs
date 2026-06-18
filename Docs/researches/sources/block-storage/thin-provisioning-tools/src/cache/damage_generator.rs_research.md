# File Research: sources/block-storage/thin-provisioning-tools/src/cache/damage_generator.rs

Development helper for deliberately corrupting cache metadata. It supports one operation: creating metadata space-map leaks.

Key elements:
- `DamageOp::CreateMetadataLeaks { nr_blocks, expected_rc, actual_rc }`.
- `CacheDamageOpts`: engine options, selected operation, and output path.
- `damage_metadata`: opens the output metadata device writable, reads the cache superblock, unpacks the metadata space-map root, and delegates to `devtools::damage_generator::create_metadata_leaks`.

This module is feature-oriented test/dev infrastructure, not a production repair path.
