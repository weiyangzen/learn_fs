# File Research: sources/block-storage/thin-provisioning-tools/src/thin/human_readable_format.rs

This file implements a human-readable metadata writer over the common `MetadataVisitor` interface.

Key elements:
- `HumanReadableWriter<W: Write>` owns a writer.
- `superblock_b()` prints a single `begin superblock` line with uuid, time, transaction, flags, version, data block size, number of data blocks, and optional metadata snapshot.
- `device_b()` prints device ID, mapped block count, transaction, creation time, and snapshot time.
- `map()` prints thin/data ranges and mapping time.
- `ref_shared()` prints shared subtree references.
- `eof()` flushes the writer.
- Uses metadata version `2` as the default if IR does not provide one.

Interactions:
- Selected by `thin/dump.rs` when output format is `human_readable`.
- Implements `thin::ir::MetadataVisitor`.

Risks and notes:
- `map()` computes `m.thin_begin + m.len - 1`; zero-length maps would underflow, though map producers normally avoid zero-length entries.
- This is output-only and does not provide a parser.
