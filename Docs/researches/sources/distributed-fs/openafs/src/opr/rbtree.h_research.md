# sources/distributed-fs/openafs/src/opr/rbtree.h

Purpose: public node/tree structures and function declarations for OPR red/black trees.

Important APIs/types/functions: `struct opr_rbtree_node` has left, right, parent, and red fields. `struct opr_rbtree` stores root. Declares traversal, insert, remove, and replace functions.

Control flow: no runtime logic in the header.

State and persistence: state is caller-owned embedded tree nodes.

Dependencies/integration: used with `rbtree.c`; callers must provide search/comparison logic around it.

Risks and test signals: because there is no type-safe container macro here, callers must manage embedding and key comparisons carefully. Compile and invariant tests cover integration.
