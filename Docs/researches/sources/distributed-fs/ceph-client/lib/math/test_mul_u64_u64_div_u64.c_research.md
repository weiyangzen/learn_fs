# sources/distributed-fs/ceph-client/lib/math/test_mul_u64_u64_div_u64.c

Purpose: Loadable test module for `mul_u64_u64_div_u64()` and rounded product-plus-add division behavior.

Important APIs/types/functions: Defines `test_params`, vector table, `test_run()`, test wrappers, and includes `div64.c` with test macro overrides to exercise alternate implementations.

Control flow: Iterates edge/random triples `(a,b,d)`, checks floor result and rounded-up variant using `d - 1` addition, logs mismatches and timing. On 64-bit long builds, also tests a forced 32-bit division path.

State and persistence: No persistent state; only module-load log output and error count.

Dependencies/integration: Built by `CONFIG_TEST_MULDIV64`, includes math64 APIs and test-local inclusion of `div64.c`.

Risks: Vector table must stay synchronized with helper semantics; module init log must be inspected for failures.

Test signals: Explicit expected vectors cover overflow-prone high-bit products, divisors near powers of two, and random values.
