# sources/distributed-fs/ceph-client/scripts/gdb/linux/mapletree.py

## Purpose
`mapletree.py` implements enough of Linux maple tree lookup to support GDB commands that need sparse indexed kernel objects, notably IRQ descriptor lookup.

## Important APIs, Types, and Functions
`Mas` models a minimal maple allocation/search state. Low-level helpers decode tagged maple entries: `mte_safe_root()`, `mte_node_type()`, `mte_to_node()`, `mte_dead_node()`, `ma_pivots()`, `ma_slots()`, and `mt_slot()`. `mtree_load()` is the public lookup API.

## Control Flow
`mtree_load()` creates a `Mas`, starts from `ma_root`, handles empty and single-entry roots, then calls `mtree_lookup_walk()` for internal nodes. The walk chooses the first pivot covering the requested index, descends through slots until a leaf, retries if a dead node resets the state, and suppresses xarray zero entries.

## State and Persistence Behavior
The module is read-only. `Mas` is transient per lookup and contains traversal bounds, node, offset, and status copied from kernel state.

## Dependencies and Integration Points
It depends on generated maple constants, xarray tagging helpers, and `CachedType` lookups. `interrupts.py` consumes it for `sparse_irqs`.

## Risks and Test Signals
The implementation covers current 64-bit maple node layouts and dense/range/arange constants; kernel layout drift can break traversal. Type checking is strict but cannot validate logical tree corruption. Test against known maple-tree users such as IRQ descriptors and compare with in-kernel lookups.
