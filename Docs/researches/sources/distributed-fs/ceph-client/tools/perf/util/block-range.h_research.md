# sources/distributed-fs/ceph-client/tools/perf/util/block-range.h

Purpose: declares the block-range rbtree node, iterator helpers, and public lookup/create/coverage APIs.

Important APIs and types: `struct block_range` contains rb node, symbol pointer, inclusive start/end, target/branch flags, coverage, entry, taken, and prediction counters. `struct block_range_iter` identifies a start and end range over newly created or affected block ranges. Inline helpers advance and validate iterators.

Control flow: inline `block_range__next()` uses `rb_next()`. `block_range_iter__next()` advances until the iterator reaches its end. Creation and lookup are implemented in the `.c` file.

State and persistence: the structure defines mutable per-range annotation state; storage is allocated and held by the global implementation tree.

Dependencies and integration points: includes Linux rbtree/types and forward declares `struct symbol`. Used by annotation paths that map branch observations to source/assembly block coverage.

Risks: callers must respect inclusive range semantics and iterator validity. Because the implementation uses a global tree, API consumers need a clear lifecycle/reset model outside this header.

Test signals: compile coverage in annotation code and iterator traversal tests over ranges created from overlapping branches.
