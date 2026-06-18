# sources/distributed-fs/ceph-client/fs/btrfs/print-tree.h

Purpose: declares the public debug-printing interface for Btrfs tree and leaf dumps.

Important APIs/types/functions: defines `BTRFS_ROOT_NAME_BUF_LEN` for callers that need a buffer for `btrfs_root_name()`, forward-declares `struct extent_buffer` and `struct btrfs_key`, and exposes `btrfs_print_leaf()`, `btrfs_print_tree()`, and `btrfs_root_name()`.

Control flow: none directly; it is a compile-time contract for callers that want to dump a single leaf, dump a whole tree optionally following children, or translate a root key objectid to a stable name.

State and persistence: no runtime state and no persistent data. The buffer-size constant is part of the ABI between `print-tree.c` and callers.

Dependencies and integration: includes only Linux types and avoids pulling in full Btrfs headers, keeping the diagnostic interface lightweight.

Risks and test signals: the main risk is contract drift if `btrfs_root_name()` ever formats longer names than `BTRFS_ROOT_NAME_BUF_LEN`. Compile coverage catches prototype drift; runtime debug output for relocation roots checks the offset-containing name case.
