# sources/distributed-fs/ceph-client/fs/btrfs/tree-mod-log.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/tree-mod-log.h` declares the Btrfs tree modification log interface shared by tree mutation, backref, delayed-ref, and historical tree-walk code. The file was read as a complete 58-line header for this report.

## Important APIs, Types, and Functions

The header defines `struct btrfs_seq_list`, the caller-owned sequence blocker object placed on `fs_info->tree_mod_seq_list`, plus `BTRFS_SEQ_LIST_INIT` and `BTRFS_SEQ_LAST`. `enum btrfs_mod_log_op` names all mutation records the implementation can replay: key replacement, add, remove, remove while freeing, remove while moving, key moves, and root replacement.

Declared functions cover sequence lifetime (`btrfs_get_tree_mod_seq()`, `btrfs_put_tree_mod_seq()`), mutation logging (`btrfs_tree_mod_log_insert_root()`, `btrfs_tree_mod_log_insert_key()`, `btrfs_tree_mod_log_free_eb()`, `btrfs_tree_mod_log_eb_copy()`, `btrfs_tree_mod_log_insert_move()`), historical reconstruction (`btrfs_tree_mod_log_rewind()`, `btrfs_get_old_root()`, `btrfs_old_root_level()`), and global state query (`btrfs_tree_mod_log_lowest_seq()`).

## Control Flow

The header has no executable control flow. It establishes the protocol: callers that need historical consistency hold a `btrfs_seq_list` blocker, mutators log operations with the enum values that correspond to the mutation they are about to perform, and readers pass the captured sequence to old-root or rewind helpers.

## State and Persistence Behavior

The only state shape exposed here is `struct btrfs_seq_list`, which stores a list node and sequence number. The actual log records, rb-tree, locks, and pruning policy remain private to `tree-mod-log.c`. All state is volatile memory and does not encode an on-disk format.

## Dependencies and Integration Points

The header includes `<linux/list.h>` and forward declares Btrfs and extent-buffer types to keep include dependencies small. It is consumed by `ctree.c` for metadata mutation logging, by backref code for sequence acquisition and old-root lookup, and by delayed-ref code for lowest-sequence coordination.

## Risks and Edge Cases

The public enum values are tied to replay semantics in `tree-mod-log.c`; adding or reordering uses without implementing inverse replay would break historical reconstruction. Callers must initialize `btrfs_seq_list.seq` to zero before first use and must pair get/put calls or old records will remain pinned. Mutator callers must pass the correct operation type and slot before changing the extent buffer.

## Test Signals

Compile coverage should catch signature drift between callers and implementation. Runtime coverage should include backref and qgroup tests that acquire blockers while `ctree.c` performs every declared mutation type. Static analysis should confirm get/put pairing and that no caller logs leaf buffers unnecessarily.
