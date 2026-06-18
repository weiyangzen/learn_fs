# sources/distributed-fs/ceph-client/security/commoncap_test.c

Purpose: KUnit tests for namespace-root helper behavior in `commoncap.c`, included in the same compilation unit under `CONFIG_SECURITY_COMMONCAP_KUNIT_TEST` so static helpers can be exercised.

Important APIs, types, and functions: tests cover `vfsuid_root_in_currentns()` and `kuid_root_in_ns()`. `create_test_user_ns_with_mapping()` builds minimal mock user namespaces with custom uid/gid maps for test cases.

Control flow: cases construct `kuid_t`, `vfsuid_t`, and mock namespaces, then assert whether each helper recognizes UID 0 or mapped namespace root. Multi-namespace tests ensure different mapped root kuids are distinguished while init UID 0 remains root through parent traversal.

State and persistence: all namespace objects are KUnit allocations. No persistent kernel state is intended.

Dependencies and integration: depends on KUnit, user namespace map structures, refcount initialization, and static inclusion by `commoncap.c`.

Risks and test signals: mock namespaces are minimal and may miss invariants expected by full namespace code, but they directly test the mapping logic used by file capability visibility/conversion. Passing tests signal correct handling for invalid vfsuids, nonzero UIDs, init namespace root, and custom mapped roots.
