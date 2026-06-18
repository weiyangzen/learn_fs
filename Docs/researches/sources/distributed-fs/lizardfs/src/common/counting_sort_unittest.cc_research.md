# sources/distributed-fs/lizardfs/src/common/counting_sort_unittest.cc

Purpose: tests `counting_sort_copy` for normal sorting and stability.

Important APIs/types/functions: `CountingSort.SimpleSort` compares sorted random integers against `std::sort`. `CountingSort.StableSort` prepares pairs, sorts by secondary field first, then checks that counting sort by primary field matches `std::stable_sort`.

Control flow: the tests fill random vectors, allocate output vectors, call `counting_sort_copy`, then compare with standard-library sorted data.

State and persistence: test-only vectors; no persistence.

Dependencies and integration: includes `common/counting_sort.h`, `gtest`, `algorithm`, and `numeric`.

Risks: random data is unseeded and deterministic under many C libraries but not explicitly controlled. The tests do not call either `counting_sort` overload, so the iterator overload's copy-direction bug is not covered.

Test signals: validates copy-mode correctness for positive integer keys and stable ordering, but coverage is incomplete for API surface and pathological key sizes.
