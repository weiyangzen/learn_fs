# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/grouper/BlockGrouper.java

Purpose: schema-aware helper for forming block groups and determining whether erased blocks are recoverable.

Important APIs and control flow: `setSchema()` stores schema; `getRequiredNumDataBlocks()` and `getRequiredNumParityBlocks()` return schema counts. `makeBlockGroup()` wraps data/parity arrays in `ECBlockGroup`. `anyRecoverable()` returns true when erased count is greater than zero and no more than parity count.

State and persistence: stores one schema reference; no persistence.

Dependencies and integration: created by `ErasureCodec.createBlockGrouper()` and used by EC managers to shape encoding/recovery work.

Risks and test signals: test recoverability boundaries, null/unset schema behavior, and data/parity array sizing outside this class. The recoverability rule is generic; codec-specific constraints such as XOR one-erasure assumptions may need upper-layer checks.
