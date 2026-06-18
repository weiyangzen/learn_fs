# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSBTreeSupport.cpp

Purpose: provides a small binary-search-tree utility for `AFSBTreeEntry` nodes keyed by `HashIndex`. It is used by control-device state such as process and AuthGroup lookup tables.

Important APIs/types/functions: `AFSLocateHashEntry()` walks left/right links to find a hash key and returns the located entry through an output pointer. `AFSInsertHashEntry()` inserts a new node below an existing top node and sets its parent link. `AFSRemoveHashEntry()` detaches a node, reconnects right and left subtrees, updates the top node if necessary, and clears the removed node links.

Control flow: lookup compares the target hash with the current node, descending right for larger hashes and left for smaller hashes. Insert repeats the same descent and attaches at the first missing child link; equal hashes trigger a warning, assertion, and failure. Remove handles leaf removal, right-subtree replacement, left-subtree reattachment to the leftmost node of the right subtree, or left-subtree promotion when no right child exists.

State/persistence: mutates only caller-owned in-memory tree pointers (`leftLink`, `rightLink`, `parentLink`, `HashIndex`). It does no allocation, freeing, or locking; callers own lifetime and synchronization.

Dependencies/integration: included through `AFSCommon.h`. Auth/process management uses these helpers with ERESOURCE locks around `ProcessTree` and `AuthGroupTree`.

Risks: the tree is unbalanced, so sorted or adversarial hash insertion can degrade lookup/insert/remove to linear time. Duplicate hash handling asserts and returns unsuccessful without collision chaining. `AFSLocateHashEntry()` returns `STATUS_SUCCESS` even when a non-null tree does not contain the key, leaving callers to check the output pointer. Remove assumes the node is actually in the supplied tree and that parent/child links are coherent.

Test signals: cover empty lookup, missing lookup with unchanged output pointer, duplicate insert, root/leaf/one-child/two-child removals, parent-link correctness after removal, and long ordered insertion sequences to observe performance and stack-free iterative behavior.
