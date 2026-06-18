<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/NumNodeID.h -->
## sources/distributed-fs/beegfs/client_module/source/common/nodes/NumNodeID.h

**Purpose:** Defines the numeric BeeGFS node identifier wrapper used throughout client mappings and messages. **APIs/types:** `NumNodeID` contains `uint32_t value`; inline helpers set, compare, test zero, and stringify via `StringTk_uintToStr`; externs serialize/deserialize. **Control flow/state:** the wrapper prevents raw integer ambiguity while still being layout-compatible for serialized owner fields. **Dependencies/integration:** used by `Node`, `TargetMapper`, `EntryInfo`, `PeerInfoMsg`, and request routing. **Risks/tests:** callers must free strings returned by `NumNodeID_str`; tests should cover zero semantics and compatibility with `NodeOrGroup` owner serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/NumNodeID.h -->
