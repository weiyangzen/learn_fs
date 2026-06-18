# sources/distributed-fs/ceph-client/tools/perf/util/block-range.c

Purpose: maintains a global red-black tree of non-overlapping basic-block address ranges for annotation. It splits, fills, and marks ranges so branch targets and branch instructions can be represented precisely even when observed blocks overlap.

Important APIs and functions: `block_range__find()` finds the range containing an address. `block_range__create()` creates or splits ranges covering an inclusive start/end block and returns an iterator over the affected ranges. `block_range__coverage()` normalizes a range's coverage by its symbol's maximum coverage. Internal helpers link new nodes to the left/right edge of existing nodes and `block_range__debug()` asserts ordering invariants in debug builds.

Control flow: `block_range__create()` searches for the range containing `start`; if none exists it either inserts a whole new range or a head before the next overlapping range. If an existing range starts before `start`, it splits a head. It then walks forward until `end` is covered, splitting tails, adding tails, or filling holes between adjacent ranges. The resulting first range is marked target and final range is marked branch.

State and persistence: `block_ranges` is a static global tree and block counter. Allocated `block_range` nodes persist for process lifetime unless cleaned elsewhere, and coverage/taken/pred counters are stored in nodes as annotation state.

Dependencies and integration points: uses Linux rbtree and annotation symbols. `block_range__coverage()` reaches into `symbol__annotation(sym)->branch->max_coverage`.

Risks: the global tree is not keyed per symbol or DSO in this file; callers must ensure address spaces do not collide or that lifecycle is reset appropriately. Allocation failure can return a partially useful iterator with missing tail work. The range math is inclusive and sensitive to underflow around zero, though comments note NULL is not executable. No locking is present.

Test signals: unit-style tests for non-overlapping insert, overlapping insert, split at start, split at end, holes, adjacent ranges, single-instruction blocks, allocation failure injection, and coverage with missing symbols/annotations.
