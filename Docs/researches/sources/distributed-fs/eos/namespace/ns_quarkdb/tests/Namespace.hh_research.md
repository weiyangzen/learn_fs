# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/Namespace.hh

Purpose: Small namespace macro helper for QuarkDB namespace tests.
Important APIs/types/functions: `USE_EOSNSTESTING`, `EOSNSTESTING_BEGIN`, and `EOSNSTESTING_END` macros wrap or import `eos::ns::testing`.
Control flow: no runtime behavior; this is preprocessor structure only.
State/persistence: none.
Dependencies/integration: included by fixtures, mocks, and tests to place utilities under the test namespace consistently.
Risks: macro-based namespace management can obscure braces and is sensitive to include order, but the file is simple and conventional for this test area.
Test signals: indirectly required for all fixture and mock compilation.
