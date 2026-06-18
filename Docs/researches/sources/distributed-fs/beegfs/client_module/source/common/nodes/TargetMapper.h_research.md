<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/TargetMapper.h -->
## sources/distributed-fs/beegfs/client_module/source/common/nodes/TargetMapper.h

**Purpose:** Declares the target ID to node ID mapper. **APIs/types:** `TargetMapper` contains an `RWLock` and private rb-root of `TargetMapping`; public APIs initialize, map one target, sync a list, collect target IDs, and look up the owner node. **Control flow/state:** all public operations perform their own locking and represent absence as a zero `NumNodeID`. **Dependencies/integration:** includes app, serialization, lists, string toolkit, and common types where `TargetMapping` is defined. **Risks/tests:** target ID 0 is not explicitly rejected here; validation is expected at higher layers. Tests should verify lock-protected lookup during map/sync and ownership of mapping allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/TargetMapper.h -->
