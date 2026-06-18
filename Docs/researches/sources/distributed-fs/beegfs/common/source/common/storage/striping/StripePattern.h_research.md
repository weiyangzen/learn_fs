<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/StripePattern.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/StripePattern.h

Purpose: Defines the abstract base class and serialized header for BeeGFS stripe patterns.

Important APIs/types: `StripePatternType`, `StripePatternHeader`, and `StripePattern` provide chunk size, storage pool ID, polymorphic serialization, target indexing by file offset, clone/equality hooks, and target-vector access/update APIs. `HasNoPoolFlag` encodes no-pool compatibility in high bits of the serialized type.

Control flow/state/persistence: Serialization writes a placeholder length, header, derived content, then backfills length. Deserialization is implemented in the `.cpp`. `getChunkStart` uses bit arithmetic and assumes chunk size is a power of two.

Dependencies/integration: Central to inode metadata, file layout, fsck, storage pool assignment, and network messages that move file layout.

Risks/test signals: Chunk size validity and non-empty target vectors are caller-critical. Tests should verify length backfill, v6/v7 storage pool compatibility, power-of-two chunk sizes, target index math, and equality across derived types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/StripePattern.h -->
