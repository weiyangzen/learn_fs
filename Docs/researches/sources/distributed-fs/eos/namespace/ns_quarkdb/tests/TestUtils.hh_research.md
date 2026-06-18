# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/TestUtils.hh

Purpose: Shared small test utilities and the concrete GTest fixture type.
Important APIs/types/functions: debug macro `DBG`; overloaded template `verifyContents` for EOS-style iterators and STL iterator ranges; `NsTestsFixture` deriving from `NsTests` and `::testing::Test`.
Control flow: `verifyContents` walks an iterator/range, checks each element exists in an expected set, erases matched elements, and fails if unexpected items or missing expected items remain.
State/persistence: no persistent state; functions consume a copy of the expected set.
Dependencies/integration: includes GTest, namespace macros, and `NsTests.hh`; used by filesystem iterator and set tests.
Risks: diagnostics are minimal and do not print offending values; iterator overload assumes pointer-like `it->valid()/next()/getElement()` API.
Test signals: central assertion helper for unordered contents in QDB set/list iterator tests.
