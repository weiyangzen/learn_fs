# File Research: sources/block-storage/thin-provisioning-tools/src/devtools/damage_generator.rs

This file contains devtool support for intentionally damaging metadata space-map reference counts.

It can find blocks with a target reference count and rewrite their bitmap entries to a different count, creating metadata leak/corruption scenarios for testing repair/check tooling.

Important behavior:
- `find_blocks_of_rc()` scans metadata space-map bitmap entries for ref counts below 3, or the ref-count B-tree for higher counts.
- `adjust_bitmap_entries()` rewrites selected bitmap entries and updates their checksums.
- `create_metadata_leaks()` randomly selects blocks with an expected refcount and changes them to an actual refcount.

Integration points:
- Uses metadata space-map structures, B-tree walking, `IoEngine`, and checksum code.
- Exposed only under the `devtools` feature through `devtools/mod.rs`.

Risks and notes:
- High-refcount mutation paths are explicitly `todo!()`.
- The implemented path handles expected and actual refcounts below or equal to the bitmap-small/overflow boundary only where no B-tree updates are needed.
- This intentionally corrupts metadata and is not normal production repair code.
