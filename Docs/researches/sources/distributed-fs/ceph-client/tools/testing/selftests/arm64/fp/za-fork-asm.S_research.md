<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-fork-asm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-fork-asm.S

Purpose: assembly setup and verification for testing ZA preservation across `fork`.

Important APIs and symbols: exports `fork_test` and `verify_fork`; tail-calls C function `fork_test_c`. Uses `smstart_za`, `_ldr_za`, `_str_za`, SVCR reads, and a `MAGIC` value stored in ZA row 0.

Control flow: `fork_test` enables ZA, writes `MAGIC` into scratch, loads it into ZA, then jumps to C. `verify_fork` checks SVCR has ZA enabled and SM disabled, stores ZA row 0 back into scratch, compares against `MAGIC`, and returns boolean.

State and persistence: `.data scratch` backs one vector-sized buffer. ZA architectural state is the tested state.

Dependencies and integration: paired with `za-fork.c`; includes `sme-inst.h`; built with nolibc constraints.

Risks: only verifies one word in one ZA vector, relying on broader ZA corruption coverage elsewhere. Assumes SVCR bit meanings from the test suite.

Test signals: C wrapper reports `fork_test` pass/fail based on parent and child `verify_fork`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-fork-asm.S -->
