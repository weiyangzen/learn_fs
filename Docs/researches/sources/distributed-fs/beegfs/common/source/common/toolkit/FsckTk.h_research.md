<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FsckTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/FsckTk.h

Purpose: Declares fsck conversion enums and helpers.

Important APIs/types: `FsckStripePatternType`, `FetchFsckChunkListStatus`, and class `FsckTk` with stripe-pattern and dir-entry conversion functions.

Control flow/state/persistence: Stateless conversion interface. Pattern creation in the implementation returns heap ownership to callers.

Dependencies/integration: Includes metadata and striping types. Used by BeeGFS fsck and repair tooling.

Risks/test signals: Tests should pin enum mapping and ownership expectations, especially as new stripe or dir entry types are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FsckTk.h -->
