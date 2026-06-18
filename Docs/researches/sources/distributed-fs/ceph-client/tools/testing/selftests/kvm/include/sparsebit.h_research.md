# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/sparsebit.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/sparsebit.h

Purpose: public API for a sparse 64-bit-index bitmap library used by KVM selftests to track guest virtual/physical page availability and memory-region state efficiently.

Important APIs/types/functions: opaque `struct sparsebit`, `sparsebit_idx_t`, `sparsebit_num_t`, allocation/free/copy, single/range set and clear operations, set/clear queries, `sparsebit_num_set`, any/all tests, first/next set/clear searches, contiguous range search helpers, `sparsebit_dump`, `sparsebit_validate_internal`, and `sparsebit_for_each_set_range`.

Control flow and state: callers allocate a sparsebit object, update ranges as pages become allocated/mapped/protected/unused, and search for free or used ranges. The internal representation is hidden and optimized for mostly contiguous ranges over a huge 64-bit index space.

Dependencies and integration: used by `kvm_util.h` for VM virtual page maps, physical page availability, and protected page tracking. It is independent C API with C++ guards.

Risks: callers must check `sparsebit_any_set()` before using the range iteration macro because first-set aborts on empty input. Off-by-one errors are easy because range APIs use start plus count while the iteration macro exposes inclusive ends.

Test signals: VM memory allocator tests, page mapping tests, and sparsebit-specific unit tests validate range operations, dumps, and internal consistency.
