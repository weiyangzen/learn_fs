# sources/distributed-fs/ceph-client/fs/xfs/scrub/dabtree.c

Purpose: Implements a generic directory/attribute btree scrub walker for XFS DA btrees. It validates DA node/leaf structure, hash ordering, parent hash coverage, sibling linkage, block ownership, CRC-era padding, block-type expectations, and delegates leaf-record checks to directory or attribute-specific scrubbers.

Important APIs, types, and functions: Public APIs are `xchk_da_process_error()`, `xchk_da_set_corrupt()`, `xchk_da_set_preen()`, `xchk_da_btree_hash()`, and `xchk_da_btree()`. Internal helpers include `xchk_da_btree_node_entry()`, `xchk_da_btree_ptr_ok()`, multiplexed buffer verifiers `xchk_da_btree_read_verify()`, `xchk_da_btree_write_verify()`, `xchk_da_btree_verify()`, sibling checkers, and `xchk_da_btree_block()`.

Control flow: `xchk_da_btree()` skips short-format forks, allocates `struct xchk_da_btree`, initializes `xfs_da_args` and `xfs_da_state`, chooses directory or attr geometry, and starts from the expected root block. `xchk_da_btree_block()` bounds-checks the block number, reads it with a scrub-specific verifier that accepts leaf1/leafn/node/attr leaf forms, checks owner and siblings, normalizes magic values, records max records/hash values, and verifies parent hash expectations. The main loop descends through node `before` pointers and calls the supplied record callback for leaf entries.

State and persistence: Traversal state is temporary in `xfs_da_state`, `path`, `altpath`, hash arrays, and max-record arrays. It reads buffers through the scrub transaction and releases them before returning. It only modifies scrub flags and buffer type annotations; it does not repair or persist metadata.

Dependencies and integration points: Used by directory and xattr scrub code. It depends on XFS DA geometry, dir/attr buffer verifiers, `xfs_da3_path_shift()` for sibling validation, DA hash helpers, transaction buffer lifetime, and `xchk_buffer_recheck()` from common infrastructure.

Risks and test signals: Risks include false positives around leaf1-as-leafn handling, missing holes in directory btrees, wrong `tree_level` tracking, unbounded or cyclic sibling/path traversal, and confusion between directory block ranges (`leafblk` to `freeblk`) and attr fork unbounded DA ranges. Test short format skip, block/leaf/node/attr leaf formats, missing root block, bad owner, nonzero CRC padding, sibling mismatch, out-of-order hashes, too-deep trees, and leaf callback early termination.
