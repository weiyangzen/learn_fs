# sources/distributed-fs/lizardfs/src/common/flat_set_unittest.cc

Purpose: tests sorted-vector set semantics for `flat_set`.

Important APIs/types/functions: helper `simple_insert`; tests redundant inserts, hint insertion for lvalue/rvalue values, range and initializer inserts, equal range, simple find/iteration, swap, erase, constructors, and assignment.

Control flow: tests create sets, mutate them through public APIs, compare order/size/content with expected sequences, and ensure duplicates are suppressed.

State and persistence: test-only heap/stack state.

Dependencies and integration: includes `flat_set.h`, `gtest`, `algorithm`, and `numeric`.

Risks: no tests for malformed `sorted=true` input, custom comparator, move-only values, or performance. The hints test focuses on duplicate insert, not successful insertion with valid hints.

Test signals: solid coverage for standard small-set operations.
