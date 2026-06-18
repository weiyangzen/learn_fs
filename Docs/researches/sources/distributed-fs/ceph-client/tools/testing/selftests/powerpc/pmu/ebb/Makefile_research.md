<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/Makefile

Purpose: Build definition for Event Based Branching selftests. It compiles all EBB tests with the shared handler, helpers, event library, and 64-bit/non-PIE constraints.

Important APIs and types: Defines a long `TEST_GEN_PROGS` list, includes build/lib/flags, forces `CFLAGS += -m64`, detects `-no-pie`, and links every test with `ebb.c`, `ebb_handler.S`, `trace.c`, `busy_loop.S`, PMU event/lib sources, harness, and utils.

Control flow: Normal builds produce each EBB binary. Special dependency adds `../loop.S` for `instruction_count_test` and extra `../lib.c` for `lost_exception_test`.

State and persistence: No runtime state beyond build outputs.

Dependencies and integration points: Depends on powerpc64 EBB assembly, perf event helpers, and toolchain support for non-PIE handler code.

Risks: PIE builds break absolute handler assumptions; missing `-m64` breaks the EBB handler ABI.

Test signals: Successful build of all EBB binaries is the primary Makefile test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/Makefile -->
