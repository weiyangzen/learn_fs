<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/Makefile

Purpose: Build definition for the powerpc machine-check selftest directory. It currently builds the recoverable-address error injection program.

Important APIs and types: `TEST_GEN_PROGS := inject-ra-err` is the main exported target. It includes common `lib.mk` and powerpc `flags.mk`, and links generated programs with `../harness.c`.

Control flow: Invoking the directory without arguments recurses to the parent. Normal kselftest build compiles `inject-ra-err` with shared harness support.

State and persistence: No runtime state. Build outputs are produced under kselftest `OUTPUT` as usual.

Dependencies and integration points: Depends on the parent powerpc selftest build system and the local `inject-ra-err.c` source.

Risks: Small Makefile, but target name drift would make the test disappear from generated runs.

Test signals: Build success and `make run_tests` discovering `inject-ra-err` are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/Makefile -->
