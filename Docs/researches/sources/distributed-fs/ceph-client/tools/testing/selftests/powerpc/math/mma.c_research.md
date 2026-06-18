<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/mma.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/mma.c

Purpose: C harness for the basic MMA arithmetic test. It prepares deterministic small matrices, invokes the assembly routine, and checks the resulting 4x4 product values.

Important APIs and types: Declares `extern void test_mma(...)`, implements `mma()`, and calls `test_harness(mma, "mma")` from `main`. Uses `uint16_t` operand arrays and `uint32_t` result arrays.

Control flow: `mma()` skips when `PPC_FEATURE2_MMA` is absent, initializes two 2x8 halfword rows, calls `test_mma`, compares each output lane with a fixed expected matrix, and reports failures through `FAIL_IF`.

State and persistence: State is stack-local test data only. Hardware MMA state is exercised by the assembly helper but not persisted by this file.

Dependencies and integration points: Depends on `utils.h` for HWCAP probing and harness macros, and on `mma.S` for the tested instruction sequence. It is built as a powerpc selftest.

Risks: Expected values encode the exact signed halfword matrix operation; changing operand layout in assembly or compiler ABI assumptions can silently invalidate the comparison. The test is hardware-gated, so non-MMA systems only provide skip coverage.

Test signals: Signals are skip on missing MMA and zero exit on exact matrix match. Failures identify data-path, assembler, or kernel context-management problems for MMA state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/mma.c -->
