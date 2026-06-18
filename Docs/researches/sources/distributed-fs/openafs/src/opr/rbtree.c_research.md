# sources/distributed-fs/openafs/src/opr/rbtree.c

Purpose: function-based red/black tree implementation with parent pointers and NULL leaves.

Important APIs/types/functions: exports `opr_rbtree_init`, `opr_rbtree_first`, `opr_rbtree_last`, `opr_rbtree_next`, `opr_rbtree_prev`, `opr_rbtree_insert`, `opr_rbtree_remove`, and `opr_rbtree_replace`. Internal helpers include `update_parent_ptr`, rotations, `swapnode`, `insert_recolour`, and `remove_recolour`.

Control flow: callers perform their own key search and pass the parent/child slot to `opr_rbtree_insert`; the implementation links the node red and recolors/rotates. Removal handles leaf, two-child, and one-child cases, using successor replacement for two-child nodes and recoloring when a black node is removed. Iteration finds min/max and successor/predecessor via child and parent traversal.

State and persistence: tree/node links and color bits are embedded in caller-owned objects. No allocation or persistence.

Dependencies/integration: includes `rbtree.h` and platform config. Intended as a reusable primitive.

Risks and test signals: no comparator is embedded, so caller search correctness is essential. `remove_recolour` assumes sibling nodes exist in cases where red/black invariants require them. Tests should validate ordering, insert/remove permutations, replacement, and invariants.
