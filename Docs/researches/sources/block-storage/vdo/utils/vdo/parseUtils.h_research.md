# File Research: sources/block-storage/vdo/utils/vdo/parseUtils.h

Declares VDO userspace parse helpers.

Key details:
- Defines `UdsConfigStrings` with `sparse` and `memorySize` string fields.
- Declares integer, 64-bit integer, size, and index-config parsers.
- Includes `indexer.h` and `encodings.h`, tying parsed UDS settings to the persisted `struct index_config`.

Research relevance:
- Used by formatting and sizing tools to turn command-line strings into validated numeric/UDS configuration.
