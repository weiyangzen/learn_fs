# File Research: sources/block-storage/thin-provisioning-tools/src/era/ir.rs

This file defines the in-memory intermediate representation and visitor interface for era metadata.

Data structures:
- `Superblock`: UUID, data block size, block count, current era.
- `Writeset`: era number and number of bits.
- `MarkedBlocks`: contiguous marked range.
- `Era`: data block and its era value.
- `Visit`: continue/stop control value.

`MetadataVisitor` defines callbacks for:
- Superblock begin/end.
- Writeset begin/end and writeset marked blocks.
- Era array begin/end and individual era entries.
- End-of-file.

Integration points:
- Used by XML parsing/writing, dump, restore, repair, and metadata generator paths.
- Provides a stable stream format between readers and writers.

Risks and notes:
- The visitor interface does not enforce ordering itself; implementations such as `Restorer` enforce section state.
