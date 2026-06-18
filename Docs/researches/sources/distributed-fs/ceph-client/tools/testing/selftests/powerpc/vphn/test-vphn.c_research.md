# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/test-vphn.c

Purpose: table-driven userspace test for unpacking VPHN associativity data returned as six packed 64-bit hypervisor registers.

Important APIs/types/functions: `struct test`, `all_tests[]`, `test_one()`, and `test_vphn()` are central. The file defines endian conversion helpers and includes `vphn.c` directly.

Control flow: each fixture supplies six packed register values and an expected big-endian associativity property. `test_one()` calls `vphn_unpack_associativity()`, verifies the reported length, then checks elements `1..len-1`; `test_vphn()` reports each case through subunit `test_finish()`.

State and persistence behavior: all state is static test data and stack output buffer. No external state.

Dependencies and integration points: depends on local VPHN header, `utils.h`, `subunit.h`, and direct inclusion of the implementation under test.

Risks and test signals: the element loop uses `i < len`, so it does not check the final element when length is the number of data cells; this weakens coverage. Some malformed expected entries include trailing values that are therefore inert.
