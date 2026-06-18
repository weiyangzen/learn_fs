## sources/distributed-fs/ceph-client/mm/interval_tree.c

Purpose: implements interval trees for file-backed VMA mappings and anonymous VMA chains. These trees support efficient reverse mapping lookups by page offset ranges.

Important APIs and functions: `INTERVAL_TREE_DEFINE()` generates `vma_interval_tree_*` and private `__anon_vma_interval_tree_*` operations. The file implements `vma_interval_tree_insert_after()`, `anon_vma_interval_tree_insert()`, `anon_vma_interval_tree_remove()`, `anon_vma_interval_tree_iter_first()`, `anon_vma_interval_tree_iter_next()`, and debug-only `anon_vma_interval_tree_verify()`.

Control flow: VMA interval start is `vm_pgoff`; end is `vma_last_pgoff()`. `vma_interval_tree_insert_after()` inserts a VMA immediately after a previous VMA with the same start offset, updating augmented subtree-last values on the right/left descent and then rebalancing with `rb_insert_augmented()`. Anon-vma functions are wrappers around generated interval-tree functions and optionally cache start/last offsets for debug verification.

State and persistence: persistent state lives in `vm_area_struct.shared.rb`, `shared.rb_subtree_last`, and `anon_vma_chain.rb/rb_subtree_last`. The file does not allocate memory or own lifetime; callers manage locking and node lifetime.

Dependencies and integration: integrates with file mapping `i_mmap` trees, reverse mapping, anonymous VMA tracking, Linux rbtree augmented callbacks, and debug VM RB checks.

Risks and test signals: risks are corrupted augmented interval maxima, insertion ordering bugs for equal starts, and stale cached offsets under VMA changes. Tests should stress mmap/munmap/mremap of shared mappings, truncate/invalidate reverse mapping walks, anon COW/fork paths, and `CONFIG_DEBUG_VM_RB` verification.
