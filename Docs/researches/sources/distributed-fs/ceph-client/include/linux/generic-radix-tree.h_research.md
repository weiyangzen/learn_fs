<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/generic-radix-tree.h -->
# sources/distributed-fs/ceph-client/include/linux/generic-radix-tree.h

Purpose: Implements a typed wrapper interface for simple sparse arrays backed by a radix tree of fixed-size zeroed nodes.

Important APIs/types/functions: `GENRADIX(type)` and `DEFINE_GENRADIX()` declare typed containers. Internal types are `__genradix`, `genradix_root`, `genradix_node`, and `genradix_iter`. APIs/macros include `genradix_init()`, `genradix_free()`, `genradix_ptr()`, `genradix_ptr_inlined()`, `genradix_ptr_alloc()`, preallocated variants, iterator initialization/peek/advance/rewind, forward/reverse iteration, `genradix_last_pos()`, and `genradix_prealloc()`. Constants define 512-byte nodes, child fanout, depth encoding, and maximum depth.

Control flow: Typed macros convert element indexes into byte offsets, respecting non-power-of-two element sizes. Lookup reads the root pointer/depth, descends child pointers by offset bits, and returns a typed pointer into leaf data. Allocation creates missing nodes through `__genradix_ptr_alloc()`. Iterators skip to present nodes and expose logical positions.

State and persistence behavior: State is in memory under `radix->tree.root`, which encodes pointer plus depth in low alignment bits. Nodes are zero-initialized and freed by `genradix_free()`.

Dependencies and integration points: Depends on page constants, bug checks, log2/math helpers, slab allocation, types, and read-once semantics. Used by subsystems needing low-overhead sparse arrays without xarray features.

Risks: Stored element size must not exceed node size. Pointer/depth encoding relies on node alignment. Lookup is mostly lockless and caller synchronization is required around concurrent mutation. Non-power-of-two sizes require page-boundary offset rounding.

Test signals: Sparse allocation/lookup for power-of-two and non-power-of-two types, iteration forward/reverse, preallocation failure paths, maximum index boundaries, free/reinit behavior, and concurrent read/write tests under subsystem locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/generic-radix-tree.h -->
