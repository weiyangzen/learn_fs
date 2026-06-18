# sources/distributed-fs/ceph-client/fs/btrfs/print-tree.c

Purpose: implements Btrfs diagnostic tree dumping. It formats root IDs, internal nodes, leaves, and many on-disk item payloads for kernel logs, making it a debugging and corruption-analysis aid rather than a normal data-path component.

Important APIs/types/functions: exported entry points are `btrfs_root_name()`, `btrfs_print_leaf()`, and `btrfs_print_tree()`. Helper printers decode chunks, devices, extent refs, UUID items, inode metadata, directory entries, file extents, csum ranges, RAID stripe items, remap items, and key type names. It relies heavily on accessor helpers so little-endian on-disk structures are read through the usual Btrfs abstraction layer.

Control flow: `btrfs_print_tree()` prints a node header and child pointers, optionally follows children with `read_tree_block()`, validates parent checks, recurses, and frees buffers. Leaves are delegated to `btrfs_print_leaf()`, which iterates slots, stringifies the item key, and dispatches by key type to payload-specific printers. Extent item printing walks inline refs until the item size boundary and warns on malformed sizes or unaligned shared parents.

State and persistence: this file does not mutate filesystem state or persist output. The only state is stack-local formatting and references taken while walking tree blocks. Log output reflects current or read tree buffers.

Dependencies and integration: integrates with `ctree`, `disk-io`, `file-item`, `accessors`, `tree-checker`, `volumes`, and RAID stripe tree definitions. It is used by debugging paths that need human-readable B-tree state.

Risks and test signals: malformed on-disk items can cause misleading output if length checks miss a variable-sized structure; recursive `follow` mode performs IO and can hit BUG checks on level mismatches. Useful signals are Btrfs selftests that print leaves with every key type, fault-injected `read_tree_block()` failures, corrupted extent inline ref sizes, RAID stripe tree item dumps, and debug builds that include extent-buffer lock/ref output.
