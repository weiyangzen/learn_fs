# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/arch-tests.c

## Purpose
This file is the x86 architecture test registry for perf's test harness. It declares suite objects and exposes the `arch_tests[]` array consumed by the generic perf test runner to discover x86-specific tests.

## Important APIs, Types, and Functions
The file uses perf test macros from `tests/tests.h` and local prototypes from `arch-tests.h`. It conditionally declares suites for the x86 instruction decoder, breakpoint modification, AMD IBS via core PMU, and AMD IBS sample period. It defines explicit `struct test_case` arrays for Intel PT and hybrid parsing, then wraps them in `struct test_suite suite__intel_pt` and `suite__hybrid`.

## Control Flow
There is no runtime algorithm beyond static registration. At compile time, feature macros decide which suite symbols are emitted and which pointers appear in `arch_tests[]`. At runtime, the generic harness walks `arch_tests[]` until the terminating `NULL`, presenting and executing each suite.

## State and Persistence
All state is static process memory: suite descriptors and arrays of test cases. The file writes no persistent data and owns no resources.

## Dependencies and Integration Points
This file integrates all x86 perf tests into the common test runner. It depends on externally defined suite/test entry points such as `intel_pt_pkt_decoder`, `intel_pt_hybrid_compat`, `dwarf_unwind`, `insn_x86`, `bp_modify`, `amd_ibs_via_core_pmu`, `amd_ibs_period`, `hybrid`, and `x86_topdown`. `HAVE_DWARF_UNWIND_SUPPORT`, `HAVE_EXTRA_TESTS`, and `__x86_64__` shape the final registry.

## Risks and Edge Cases
The main risk is registration drift: adding or renaming an x86 test without updating this array makes it invisible to the harness, while including a suite without a matching compiled symbol breaks the build. Ordering also matters for user-visible test lists and tests marked exclusive. `suite__amd_ibs_period` is exclusive, so it should remain registered through the exclusive macro.

## Test Signals
Build success verifies all declared suite symbols match enabled feature macros. Runtime `perf test` listing should show Intel PT, optional DWARF unwind and instruction decoder tests, x86 breakpoint modify on x86_64, AMD IBS tests, hybrid parsing, and x86 topdown.
