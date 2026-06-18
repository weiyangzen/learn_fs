# sources/distributed-fs/ceph-client/tools/testing/rbtree/Makefile

Purpose: builds userspace red-black tree and interval-tree test binaries from kernel library sources plus local shims.

Important APIs/types/functions: `TARGETS = rbtree_test interval_tree_test`; `OFILES` combines shared objects and `rbtree-shim.o`, `interval_tree-shim.o`, `maple-shim.o`; `DEPS` tracks rbtree/interval headers and library C files; adds `CONFIG_INTERVAL_TREE_SPAN_ITER` for interval-tree shim and test object.

Control flow: default `targets` builds both binaries after including `../shared/shared.mk`; target-specific dependencies force rebuilds when kernel headers/library code changes; `clean` removes binaries, objects, copied/generated files.

State and persistence: writes build outputs in the directory/OUTPUT context; no runtime state.

Dependencies/integration: integrated with the tools/testing shared userspace build system and kernel `lib/rbtree.c`, `lib/interval_tree.c`, `lib/rbtree_test.c`, and `lib/interval_tree_test.c`.

Risks and test signals: stale dependency lists can miss rebuilds after kernel API changes. Build success is the primary signal for this file.
