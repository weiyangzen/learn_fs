# File Research: sources/block-storage/thin-provisioning-tools/src/cache/repair.rs

Implements cache metadata repair by dumping readable metadata and restoring it into a fresh output metadata device.

Main flow:
- `CacheRepairOptions`: input, output, engine options, report.
- Opens input read-only and output writable.
- Reads input cache superblock to preserve metadata version.
- Creates a fresh metadata space map and `WriteBatcher` for output.
- Constructs `cache::restore::Restorer` with the input version.
- Calls `dump_metadata(input_engine, restorer, sb, true)` so dump traversal runs in repair mode and feeds restore directly.

This is a binary-to-binary rebuild path through the cache IR visitor interface.
