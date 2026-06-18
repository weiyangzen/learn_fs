# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree-internal.h

## Purpose
Private header shared by btree implementation files.

## Main Definitions
- `enum node_flags`: `INTERNAL_NODE` and `LEAF_NODE`.
- `struct node_header`: common on-disk btree node header with checksum, flags, block number, entry counts, value size, and padding.
- `struct btree_node`: header followed by flexible key array; values are stored after the maximum key region.
- `struct ro_spine`: rolling two-node read-lock stack.
- `struct shadow_spine`: rolling two-node write/shadow stack plus current root.

## Helper APIs
- Block/node helpers: `bn_read_lock`, `new_block`, `unlock_block`.
- Reference helper: `inc_children`.
- Spine operations: init/exit/step/pop/current/parent/root.
- Layout helpers: `key_ptr`, `value_base`, `value_ptr`, `value64`.
- Search helper: `lower_bound`.
- Shared validator: `btree_node_validator`.
- Internal value type setup for `__le64` child pointers: `init_le64_type`.
- `btree_get_overwrite_leaf()` for single-level overwrite access.

## Role in Repository
This header defines the private on-disk btree node format and copy-on-write traversal helpers used by insertion, removal, cursor, and space-map overflow manipulation.
