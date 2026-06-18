# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/teststubs.S

Purpose: branch target functions with different BTI/PAC landing sequences for the BTI test matrix.

Important APIs/types/functions: defines `bti_none_func`, `bti_c_func`, `bti_j_func`, `bti_jc_func`, `paciasp_func`, and `nohint_func`.

Control flow: each function executes its landing hint/PAC pair if applicable and returns.

State and persistence: no state; emits GNU property note.

Dependencies/integration: called by trampolines from `test.c`.

Risks and test signals: landing hints encode the expected valid branch classes; wrong hint would flip expected SIGILL outcomes.
