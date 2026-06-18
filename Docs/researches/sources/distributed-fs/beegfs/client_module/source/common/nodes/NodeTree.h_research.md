<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/NodeTree.h -->
## sources/distributed-fs/beegfs/client_module/source/common/nodes/NodeTree.h

**Purpose:** Declares the typed rb-tree container and iterator for `Node` objects keyed by `NumNodeID`. **APIs/types:** `NodeTree` stores `rb_root nodes` plus `size`; `NodeTreeIter` stores the current `rb_node*` with inline begin/next/value/end helpers. **Control flow/state:** the iterator starts at `rb_first` and advances with `rb_next`, returning the containing `Node`. **Dependencies/integration:** requires `Node.h` and Linux rb-tree APIs; node store code supplies synchronization. **Risks/tests:** iterator value is invalid at end and tree mutation during iteration follows kernel rb-tree caveats; tests should validate size behavior and traversal order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/NodeTree.h -->
