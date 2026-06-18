# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_leaf.c

## Purpose
`xfs_attr_leaf.c` implements the storage formats and algorithms for inline shortform attributes and leaf blocks in the XFS attribute fork. It handles leaf block verification, endian conversion, shortform add/remove/get/verify, conversion between shortform, leaf, and node formats, leaf block creation, insertion, deletion, split/rebalance/unbalance, lookup, value extraction, and `INCOMPLETE` flag manipulation.

## Important APIs, types, and functions
Header conversion and verification are handled by `xfs_attr3_leaf_hdr_from_disk`, `xfs_attr3_leaf_hdr_to_disk`, `xfs_attr3_leaf_header_check`, `xfs_attr3_leaf_read`, and the `xfs_attr3_leaf_buf_ops` verifier set. Shortform operations include `xfs_attr_shortform_bytesfit`, `xfs_attr_shortform_create`, `xfs_attr_sf_findname`, `xfs_attr_shortform_replace`, `xfs_attr_shortform_add`, `xfs_attr_fork_remove`, `xfs_attr_sf_removename`, `xfs_attr_shortform_getvalue`, `xfs_attr_shortform_to_leaf`, `xfs_attr_shortform_allfit`, and `xfs_attr_shortform_verify`.

Leaf and node-format operations include `xfs_attr3_leaf_to_shortform`, `xfs_attr3_leaf_to_node`, `xfs_attr3_leaf_init`, `xfs_attr3_leaf_split`, `xfs_attr3_leaf_add`, `xfs_attr3_leaf_remove`, `xfs_attr3_leaf_toosmall`, `xfs_attr3_leaf_unbalance`, `xfs_attr3_leaf_lookup_int`, `xfs_attr3_leaf_getvalue`, `xfs_attr_leaf_lasthash`, `xfs_attr_leaf_order`, `xfs_attr_leaf_newentsize`, `xfs_attr3_leaf_clearflag`, `xfs_attr3_leaf_setflag`, and `xfs_attr3_leaf_flipflags`.

Important internal helpers include `xfs_attr_leaf_entries_end`, `xfs_attr_leaf_ichdr_freemaps_verify`, firstused disk conversion helpers, `xfs_attr3_leaf_verify_entry`, `xfs_attr3_leaf_verify`, namespace/value match helpers, `xfs_attr_copy_value`, `xfs_attr3_leaf_create`, `xfs_attr3_leaf_add_work`, `xfs_attr3_leaf_compact`, `xfs_attr3_leaf_rebalance`, `xfs_attr3_leaf_figure_balance`, `xfs_attr3_leaf_moveents`, and `xfs_attr_leaf_entsize`.

## Control flow
Shortform paths manipulate inode-local packed records directly. `xfs_attr_shortform_bytesfit` determines if a byte count fits in inode literal space while preserving data fork room. `xfs_attr_shortform_add` appends a variable-length record and updates `i_forkoff`; removal compacts the inline array and may remove the attr fork entirely if empty and safe. `xfs_attr_shortform_to_leaf` snapshots inline data, clears local fork data, grows the attr fork, creates block zero as a leaf, and reinserts each shortform entry into the new leaf.

Leaf add first loads the incore leaf header, calculates whether the new value is local or remote, searches the three-entry freemap, optionally compacts the block, and inserts a sorted entry. If a leaf cannot fit the new entry, split/rebalance logic allocates a new leaf and redistributes records. Node conversion copies the existing leaf to a new block and creates a root da-node at block zero that points to the copied leaf.

Lookup performs a binary search by hash, backs up to the first equal hash, then scans duplicate hashes for exact namespace/name/value match. Getvalue copies local values immediately or sets remote fields and delegates to `xfs_attr_rmtval_get` through `xfs_attr_copy_value`.

## State and persistence behavior
Leaf blocks store sorted `xfs_attr_leaf_entry` arrays growing forward from the header and name/value payloads growing backward from the block tail. The incore header uses a 32-bit `firstused` so 64 KiB attr blocks can be represented even though on-disk fields are 16-bit; zero is the special on-disk value for an empty max-size block. Free space is tracked by three freemap entries and a holes flag. All mutating paths log modified buffer ranges or full buffers through the transaction.

Crash-safe remote and replace behavior is centered on `XFS_ATTR_INCOMPLETE`. Adding a remote value creates an incomplete leaf entry before writing remote blocks. `xfs_attr3_leaf_clearflag` publishes it and stores the remote block/length. `xfs_attr3_leaf_setflag` hides an old entry before removal. `xfs_attr3_leaf_flipflags` clears the new entry and sets the old entry incomplete in one transaction for atomic replacement.

## Dependencies and integration points
This file depends on da-btree routines for node creation, split/join coordination, sibling path movement, and block linking; bmap for local-to-extents conversion and fork shrink/grow; transaction logging; buffer verifiers and CRC support; remote value retrieval; parent pointer matching semantics; superblock attr2 feature updates; health marking for corrupt attr forks; and trace/error injection infrastructure.

## Risks and edge cases
The packed leaf format is vulnerable to off-by-one and overlap bugs. Verification checks sorted hashes, name bounds, nonzero names, remote value block presence for complete entries, freemap bounds/alignment/overlap, and header-vs-payload collision. Split/rebalance must update insertion indexes and old/new replace locations accurately, including double splits and cross-block replacements. Compaction drops holes but must preserve CRC-era header fields. Empty leaf blocks are permitted after crash during format conversion. Parent pointers match on both name and value and do not support remote values. Any mismatch between local/remote sizing thresholds and remote block allocation can corrupt attr visibility.

## Test signals
Tests should cover shortform fit boundaries, dev inode and btree data fork forkoff rules, shortform verify rejection, shortform-to-leaf and leaf-to-shortform conversion, empty leaf verifier acceptance, local and remote leaf lookup with duplicate hashes, leaf insertion/removal with freemap coalescing, compaction after holes, split/rebalance/unbalance with replacement state, CRC and non-CRC leaf verification, 64 KiB block firstused conversion, parent pointer matching, and crash points around clear/set/flip incomplete flags.
