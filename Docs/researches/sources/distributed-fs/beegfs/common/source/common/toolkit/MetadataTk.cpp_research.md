<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MetadataTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MetadataTk.cpp

Purpose: Implements metadata owner lookup across metadata nodes.

Important APIs/functions: `referenceOwner` resolves and references the metadata node owning a path and fills `EntryInfo`. `findOwnerStep` sends one `FindOwnerMsg` to a node. `findOwner` iteratively follows owner handoffs until the requested depth is reached.

Control flow/state/persistence: The search starts at the root node or mirrored root primary, sends find-owner requests, and advances by returned `EntryInfoWithDepth`. It aborts on errors, unknown nodes, non-progressing depth, or exceeding `METADATATK_OWNERSEARCH_MAX_STEPS`. No local persistence.

Dependencies/integration: Uses `NodeStoreServers`, `RootInfo`, `MirrorBuddyGroupMapper`, `MessagingTk`, `FindOwnerMsg/Resp`, and metadata constants. Central for ctl/client-side metadata routing.

Risks/test signals: Concurrent namespace changes can cause non-progressing depth or owner changes. Tests should cover root lookup, mirrored root, multi-hop lookup, unknown next node, communication failure, max-step guard, and entry info flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MetadataTk.cpp -->
