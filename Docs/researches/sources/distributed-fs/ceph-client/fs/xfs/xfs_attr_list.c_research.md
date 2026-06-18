<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_list.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_list.c

Purpose: Implements listing extended attributes from XFS in shortform, leaf, and node formats with cursor-based continuation and corruption checks.

Important APIs and functions: `xfs_attr_list` is the external entry that locks the attr fork and delegates to `xfs_attr_list_ilocked`. `xfs_attr_list_ilocked` chooses shortform, leaf, or node path. `xfs_attr_shortform_list` handles inline attrs and sorting for partial buffers. `xfs_attr_node_list_lookup` descends the attr btree by hash and validates cursor targets. `xfs_attr_node_list`, `xfs_attr_leaf_list`, and exported `xfs_attr3_leaf_list_int` emit leaf entries through the caller's `put_listent` callback.

Control flow: Shortform listing returns entries directly when the buffer can hold all entries or when scanning with a zero-size/search callback; otherwise it builds a sorted hash/entry-number array to support stable cursor continuation. Leaf/node listing validates the caller cursor, redoes lookup from the btree root when necessary, processes leaf entries in hash order, follows forward leaf links, and updates cursor hash/offset as entries are emitted.

State and persistence: Does not mutate persistent metadata. It reads in-core or on-disk attr fork extents and updates only the caller's listing cursor and context flags such as `seen_enough`, `dupcnt`, and `resynch`.

Dependencies and integration: Uses attr fork locks, extent loading, attr leaf/node verifiers, name validation, hash functions, health marking, tracing, and caller-provided namespace/value emission callbacks.

Risks: Cursor validation is complex; stale or malicious cursor block/hash values must not return wrong entries or trust corrupt blocks. Shortform pointer bounds and namespace/name checks protect against malformed inline attrs. Incomplete attr entries are hidden unless context explicitly allows them.

Test signals: Listing all attrs in one buffer, partial-buffer continuation with duplicate hashes, shortform-to-leaf transitions, corrupted shortform/leaf/node blocks, incomplete attr filtering, and cursor resync after tree changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_list.c -->
