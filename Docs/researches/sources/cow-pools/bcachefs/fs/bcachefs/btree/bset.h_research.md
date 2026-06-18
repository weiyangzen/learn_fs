# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bset.h

This header declares and inlines the bset and btree-node iterator API.

Key contents:
- Documentation explains bkeys, bsets, btree-node iterators, and auxiliary search tree compression.
- `enum bset_aux_tree_type` distinguishes no aux tree, read-only aux tree, and read-write aux tree.
- `BSET_CACHELINE` is set to 256 bytes for lookup sampling granularity.
- Aux-data sizing helpers compute cachelines and auxiliary data bytes/u64s from btree node byte order.
- Iteration macros include `for_each_bset`, `for_each_bset_c`, and `bset_tree_for_each_key`.
- `bset_aux_tree_type()`, `bset_has_ro_aux_tree()`, `bset_has_rw_aux_tree()`, and `bch2_bset_set_no_aux_tree()` manage aux-tree state.
- `btree_node_set_format()` updates the node format, computes key bits/unpack constants, compiles an unpack function if enabled, and resets aux trees.
- Bset lifecycle and mutation declarations cover initialization, aux tree building, insert, and delete.
- `bkey_cmp_p_or_unp()` compares a left packed/unpacked key to a right packed key or unpacked position.
- `bch2_bkey_to_bset_inlined()` maps a key pointer to its containing bset via node offsets.
- Iterator declarations and inline helpers expose init, push, sort, advance, peek, previous, and unpacked-peek operations.
- `bkey_iter_cmp()` defines iterator ordering, including deleted-key tie-breaking.
- Accounting helpers maintain live u64s, per-bset u64s, and packed/unpacked key counts.
- Debug declarations expose node-key rendering, bset rendering, iterator dumping, accounting verification, and iterator verification.

Role:
- This is the hot inline companion to `bset.c`; most btree traversal code depends on these iterator and comparison helpers.
