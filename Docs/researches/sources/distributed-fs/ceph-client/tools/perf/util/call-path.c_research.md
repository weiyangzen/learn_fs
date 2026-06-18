# sources/distributed-fs/ceph-client/tools/perf/util/call-path.c

## sources/distributed-fs/ceph-client/tools/perf/util/call-path.c

Purpose: this file implements an arena-backed tree of context-sensitive call paths for perf call-return/db-export style analysis.

Important APIs and functions: `call_path_root__new()` allocates and initializes a root. `call_path_root__free()` releases all arena blocks. `call_path__findnew()` finds or creates a child path under a parent keyed by symbol pointer or raw ip. Internal `call_path__new()` allocates nodes from fixed-size blocks, and `call_path__init()` initializes node fields.

Control flow: root allocation initializes an empty root call path and block list. New nodes are allocated from the last block until full, then a new block of `CALL_PATH_BLOCK_SIZE` nodes is appended. For non-root parents, `call_path__findnew()` searches the parent's red-black tree by `(sym, ip)` and inserts a new node if absent. If `sym` is non-null, `ip` is normalized to zero; `in_kernel` is computed by comparing ip to the kernel-start threshold.

State and persistence: all nodes live in blocks attached to `call_path_root`. Individual nodes are not freed; the whole root is freed at once. Each node owns its child RB tree.

Dependencies and integration: depends on Linux rbtree/list utilities and perf symbol pointers. Used where perf needs stable call path ids and parent-child context.

Risks: ordering by raw `struct symbol *` pointer is process-local and not persistent across runs; this is fine for in-memory lookup but not serialization. Allocation failure returns null and callers must handle it. `call_path__findnew()` with null parent always creates a new node instead of deduplicating root-like paths.

Test signals: create repeated paths with same symbol/ip and parent, different parents, null symbols, kernel/user thresholds, block-boundary allocations, and allocation failure injection.
