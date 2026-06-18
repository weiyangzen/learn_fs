<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/NodeList.h -->
## sources/distributed-fs/beegfs/client_module/source/common/nodes/NodeList.h

**Purpose:** Provides a thin typed wrapper over `PointerList` for lists of `Node*`. **APIs/types:** `NodeList` contains `PointerList`; inline functions initialize, uninitialize, append a node pointer, remove the head, and return length. **Control flow/state:** it does not own or refcount nodes itself; ownership/ref behavior is determined by callers. **Dependencies/integration:** used wherever ordered node pointer lists are needed and paired with `NodeListIter.h`. **Risks/tests:** because it is an untyped cast wrapper, misuse with non-node pointers or missing node refs can lead to dangling entries; tests should focus on caller ownership and iteration correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/NodeList.h -->
