# sources/distributed-fs/lizardfs/src/common/intrusive_list_unittest.cc

Purpose: tests intrusive-list operations against `std::vector` ordering.

Important APIs/types/functions: local `Node` derives from `intrusive_list_base_hook`; comparison helpers compare list content with vector content. Tests cover `PushBack`, `Erase`, `Insert`, and `Splice`.

Control flow: tests allocate nodes with `new`, add them to lists, mutate the list and an expected vector in parallel, compare, and call `clear_and_dispose` to delete nodes.

State and persistence: heap-allocated test nodes owned by test cleanup.

Dependencies and integration: includes `intrusive_list.h`, `gtest`, `algorithm`, and `numeric`.

Risks: tests do not cover push_front, pop variants, empty-list operations, move/swap, or misuse cases like double insertion.

Test signals: good coverage for common ordering and splice behavior.
