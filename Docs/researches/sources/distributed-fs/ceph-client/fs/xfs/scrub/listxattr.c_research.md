<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/listxattr.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/listxattr.c

Purpose: Provides a validation-oriented extended-attribute walker that calls a callback for every xattr in shortform, leaf, or node-format attr forks without cursor restarts.

Important APIs, types, and functions: Exports `xchk_xattr_walk()`. Internal helpers walk shortform entries, leaf block entries, single-leaf attr forks, find the leftmost node-format leaf, and traverse right-sibling leaf chains while detecting loops with `xdab_bitmap`.

Control flow: The public walker requires the inode ILOCK and returns immediately if the inode has no attrs. Shortform attrs are iterated from the in-core attr fork. Non-local attrs load attr fork extents, then either read block zero as a leaf or descend the dabtree to the leftmost leaf. Node traversal verifies node and leaf headers, records seen dablocks, walks leaf entries, optionally calls a leaf callback between leaves, follows `forw` sibling pointers, and rejects cycles or malformed levels. Leaf entries pass local values inline and remote values as `NULL` with the remote value length.

State and persistence: The walker only reads attr fork structures and transient buffers. It keeps an in-memory bitmap of seen dablocks for node-format loop detection and releases transaction buffers after each leaf.

Dependencies and integration points: Depends on XFS attr fork formats, attr leaf/node readers and verifiers, dab bitmap helpers, scrub transactions, and caller-provided callbacks. Used by scrub/repair code that needs deterministic xattr enumeration, including parent-pointer or attr validation.

Risks and test signals: Risks include malformed dabtrees causing loops, incorrect local vs remote value interpretation, level mismatch during descent, and walking without loaded extents or locks. Test shortform attrs, leaf local and remote entries, multi-leaf node chains, corrupt magic/header/count/level, sibling cycles, callback error propagation, remote value lengths, empty attr forks, and buffer release on all error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/listxattr.c -->
