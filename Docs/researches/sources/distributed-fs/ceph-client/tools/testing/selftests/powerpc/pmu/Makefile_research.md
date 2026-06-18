<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/Makefile

Purpose: Top-level build/run definition for powerpc PMU selftests. It builds basic PMU counter tests and recurses into EBB, sampling, and event-code subdirectories.

Important APIs and types: Defines `TEST_GEN_PROGS`, `EXTRA_SOURCES`, `SUB_DIRS`, custom `RUN_TESTS`, `emit_tests`, `INSTALL_RULE`, and `CLEAN`. Adds `-m64` and `loop.S` dependencies for instruction-count tests.

Control flow: Builds local tests, then creates per-subdir output directories and invokes sub-makes. Run/install/emit/clean logic wraps default kselftest behavior and then iterates subdirectories.

State and persistence: No runtime persistence beyond build outputs and recursive output trees.

Dependencies and integration points: Depends on `event.c`, `lib.c`, `../utils.c`, `../harness.c`, `loop.S`, and child directory Makefiles.

Risks: Recursive make logic can hide failures if output paths are wrong. `loop.S` must be built 64-bit for instruction count accuracy.

Test signals: Signals are correct emitted test names for local and child tests plus successful recursive builds/runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/Makefile -->
