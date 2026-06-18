<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/sparsebit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/sparsebit.c

## Purpose
`sparsebit.c` implements a memory-efficient sparse bitset for 64-bit indexes. KVM selftests use it to track large guest physical and virtual page spaces without allocating dense bitmaps. It supports single-bit and range set/clear queries, iteration over set or clear ranges, copy/free/dump helpers, and an internal validator.

## Important APIs, Types, and Functions
The public API is centered on `struct sparsebit`, `sparsebit_alloc()`, `sparsebit_free()`, `sparsebit_copy()`, `sparsebit_is_set()`, `sparsebit_is_set_num()`, `sparsebit_is_clear()`, `sparsebit_is_clear_num()`, `sparsebit_num_set()`, `sparsebit_any_set()`, `sparsebit_all_set()`, `sparsebit_first_set()`, `sparsebit_next_set()`, `sparsebit_next_set_num()`, `sparsebit_next_clear()`, `sparsebit_next_clear_num()`, `sparsebit_set_num()`, `sparsebit_clear_num()`, `sparsebit_set_all()`, `sparsebit_clear_all()`, `sparsebit_dump()`, and `sparsebit_validate_internal()`. Internally, `struct node` stores a binary-search-tree node with `idx`, a 32-bit `mask`, and `num_after` for a contiguous run following the mask.

## Control Flow
Lookup walks the BST by node start index, then checks whether the target bit falls in the mask or in `num_after`. Mutations first use `node_split()` and `node_add()` to ensure the affected range has mask-addressable boundaries, update the mask or run count, and then call `node_reduce()` to merge adjacent runs or remove empty nodes. Range operations handle unaligned leading/trailing bits with single-bit helpers and whole-mask middle ranges with splits, node deletion, and `num_after` expansion. Iterators use `node_first()`, `node_next()`, `node_prev()`, and `node_first_set()/node_first_clear()` to find the next requested bit or range.

## State and Persistence
All state is heap resident in a `struct sparsebit` tree. `num_set` is a redundant total used for O(1) counting and for all-set overflow semantics: zero means either none set or every possible bit set, so callers must use `sparsebit_any_set()`/`sparsebit_all_set()` for boolean tests. No filesystem or kernel state is persisted.

## Dependencies and Integration Points
The file depends on `sparsebit.h`, `test_util.h`, standard allocation/assert APIs, and compiler builtins such as `__builtin_popcount()` and `__builtin_ctz()`. KVM VM helpers integrate this structure with guest page allocation, valid-page tracking, protected-page tracking, and page table mapping decisions.

## Risks and Test Signals
The main risks are off-by-one errors near `UINT64_MAX`, wraparound in `idx + num - 1`, tree imbalance, stale parent pointers, incorrect `num_set` accounting, and invalid reductions that overlap adjacent nodes. Test signals include `sparsebit_validate_internal()` invariant checks, diagnostic dumps, assertions in all public operations, and the optional `FUZZ` driver that compares sparsebit behavior against a simple range log under random operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/sparsebit.c -->
