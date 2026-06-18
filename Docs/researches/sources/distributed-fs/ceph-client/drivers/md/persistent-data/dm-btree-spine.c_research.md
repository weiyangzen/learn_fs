<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-spine.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-spine.c

## Purpose
Implements btree node validation, read-only rolling spines, copy-on-write shadow spines, and the internal `__le64` value type used for btree child block references.

## Important APIs, Types, And Functions
`btree_node_validator` prepares and checks btree nodes. `node_prepare_for_write()` stamps the block number and checksum. `node_check()` verifies expected block location, checksum, node capacity, entry count, and that the node is either internal or leaf.

Lock helpers are `bn_read_lock()`, `new_block()`, and `unlock_block()`. `bn_shadow()` calls `dm_tm_shadow_block()` and invokes `inc_children()` when a shared node is copied. Read-only spine APIs are `init_ro_spine()`, `exit_ro_spine()`, `ro_step()`, `ro_pop()`, and `ro_node()`. Shadow spine APIs are `init_shadow_spine()`, `exit_shadow_spine()`, `shadow_step()`, `shadow_current()`, `shadow_parent()`, `shadow_has_parent()`, and `shadow_root()`.

`init_le64_type()` creates a btree value type for child block pointers; its callbacks increment/decrement contiguous runs of child references through the transaction manager and compare little-endian block values.

## Control Flow
Readers use `ro_step()` to acquire a child and drop the grandparent when two nodes are already held. Mutators use `shadow_step()` similarly, except each step returns a writable shadow. The first shadowed block's location becomes the new root. Insertion/removal code later patches parent values to point to each new shadow.

## State And Persistence
Persistent state is the btree node header checksum and block-number stamp plus sorted key/value payload. Runtime spine state is just a small rolling array of held blocks. The `le64` value type ensures child metadata references stay correct when internal nodes are copied or deleted.

## Dependencies And Integration Points
This file integrates the btree layer with the transaction manager and block-manager validator interface. It is used by `dm-btree.c` and `dm-btree-remove.c`, and indirectly by array and space-map implementations.

## Risks
Validator correctness is critical because every btree metadata block depends on it. `node_check()` cannot validate full key ordering, so higher-level insert/remove paths must maintain sorted keys and separator semantics. Shadow spines require callers to patch parents; forgetting that produces valid blocks that are not reachable from the returned root.

## Test Signals
Signals include checksum/block-number corruption tests, lockdep coverage for rolling traversal, copy-on-write tests with shared nodes, internal-child refcount tests, and btree insert/remove stress that exercises parent patching after every shadow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-spine.c -->
