# sources/distributed-fs/ceph-client/kernel/module/tree_lookup.c

## Purpose
Provides fast module address lookup using a latched red-black tree, optimized for perf, tracing, CFI, and stack unwinding paths that may query module addresses frequently or from restrictive contexts.

## Important APIs, Types, And Functions
Exports `mod_tree_insert`, `mod_tree_remove_init`, `mod_tree_remove`, and `mod_find`. Internal latch tree callbacks are `mod_tree_less` and `mod_tree_comp`; helpers `__mod_tree_val`, `__mod_tree_size`, `__mod_tree_insert`, and `__mod_tree_remove` operate on `struct module_memory` tree nodes.

## Control Flow
When a module enters the global list, every non-empty memory type is inserted into `mod_tree`. After successful init, init memory ranges are removed by `mod_tree_remove_init`. On unload or failed load cleanup, all remaining memory ranges are removed. Lookups call `latch_tree_find` with an address and return the owning module.

## State And Persistence
State lives in `mod_tree.root` and each `mod->mem[type].mtn` node. It is valid while the module memory range is registered and protected by module loader sequencing plus RCU lookup rules.

## Dependencies And Integration Points
Depends on `CONFIG_MODULES_TREE_LOOKUP`, `linux/rbtree_latch.h`, `module_mutex` serialization for updates, and `main.c` address bounds checks in `__module_address`.

## Risks And Edge Cases
Insert/remove operations must exactly mirror module memory lifetime. Removing init ranges after they are queued for freeing prevents stale lookup hits. Overlapping or zero-sized ranges would corrupt lookup semantics; zero sizes are skipped.

## Test Signals
Stress stack unwinding and module load/unload with perf/tracing/CFI enabled, verify `__module_address` and `__module_text_address` results, and check no stale init-memory matches after init cleanup.
