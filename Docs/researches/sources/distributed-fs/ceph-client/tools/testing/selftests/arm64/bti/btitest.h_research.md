# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/btitest.h

Purpose: declares BTI trampoline and target stub functions used by the C test.

Important APIs/types/functions: trampolines `call_using_br_x0()`, `call_using_br_x16()`, `call_using_blr()`; target stubs `nohint_func()`, `bti_none_func()`, `bti_c_func()`, `bti_j_func()`, `bti_jc_func()`, `paciasp_func()`.

Control flow: no direct flow.

State and persistence: none.

Dependencies/integration: connects `test.c` with `trampoline.S` and `teststubs.S`.

Risks and test signals: prototype mismatch would affect branch/call ABI and test validity.
