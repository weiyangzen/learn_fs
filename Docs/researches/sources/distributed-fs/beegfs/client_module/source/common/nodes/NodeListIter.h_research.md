<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/NodeListIter.h -->
## sources/distributed-fs/beegfs/client_module/source/common/nodes/NodeListIter.h

**Purpose:** Supplies typed iteration over `NodeList`. **APIs/types:** `NodeListIter` wraps `PointerListIter`; inline functions initialize from a list, advance, return current `Node*`, and test end. **Control flow/state:** iteration mirrors the underlying pointer-list iterator and performs no locking or ref acquisition. **Dependencies/integration:** includes `NodeList` and `Node.h`, so callers get typed values for node-list traversal. **Risks/tests:** callers must not mutate/free nodes concurrently unless the owning store protocol allows it; tests should cover empty lists, end handling, and traversal after removals according to pointer-list semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/NodeListIter.h -->
