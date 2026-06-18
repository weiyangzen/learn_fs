# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/reg_bounds.c

## Purpose
Large verifier oracle for scalar register bounds. It generates BPF programs for combinations of signed/unsigned 64-bit and 32-bit ranges, simulates expected verifier refinement, parses verifier logs, and compares actual branch register states. The source was read as a complete 2253-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `num_is_small()`, `snprintf_num()`, `snprintf_range()`, `print_range()`, `range_eq()`, `is_valid_num()`, `is_valid_range()`, `range_canbe_op()`, `range_always_op()`, `range_never_op()`, `range_branch_taken_op()`, `range_cond()`, `print_reg_state()`, `print_refinement()`, `reg_state_refine()`, `reg_state_set_const()`, `reg_state_cond()`, `reg_state_branch_taken_op()`, `load_range_cmp_prog()`, `parse_reg_state()`, `parse_range_cmp_log()`, `assert_range_eq()`, `assert_reg_state_eq()`, `print_verifier_log()`, and 83 more.
- Includes and fixtures: `#include <limits.h>`, `#include <test_progs.h>`, `#include <linux/filter.h>`, `#include <linux/bpf.h>`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: Raw `bpf_prog_load()` with generated `struct bpf_insn`, `BPF_JMP/JMP32` macros, verifier log options, `ASSERT_*`, environment variables `SLOW_TESTS`, `REG_BOUNDS_MAX_FAILURE_CNT`, `REG_BOUNDS_RAND_CASE_CNT`, `REG_BOUNDS_RAND_SEED`, and test_progs subtest registration.

## Control Flow
The file defines numeric domains, range cast/refinement operations, branch-condition simulation, generated BPF program loading, verifier-log parsing, and comparison helpers. Crafted cases run normally via `test_reg_bounds_crafted()`. Generated exhaustive cases require `SLOW_TESTS=1`; randomized cases use configurable seed/count and report reproducible progress.

## State and Persistence Behavior
State is in `struct ctx`: generated values/ranges, counters, failure limits, random seed, and progress timestamps. Verifier state is not persisted; it is parsed from each generated load log. Allocated range arrays are freed by `cleanup_ctx()`.

## Dependencies and Integration Points
Depends on verifier log text format, Linux BPF instruction macros, raw tracepoint program loading, selftests verbosity/progress plumbing, and enough log buffer for state extraction.

## Risks and Edge Cases
Extremely coupled to verifier output syntax and scalar-bound semantics; exhaustive cases are slow and gated; random tests must report seed for reproduction; parser defaults must mirror verifier defaults exactly.

## Test Signals
Signals include successful generated program loads, parsed false/true branch register states for R6/R7, exact range equality across U64/U32/S64/S32 domains, crafted edge cases, progress output, and bounded failure count behavior. Named assertion/check labels observed in the source include: `branch taken inconsistency!\n`, `load_range_cmp_prog`, `parse_range_cmp_log`, `uranges_calloc`, `sranges_calloc`, `usubranges_calloc`, `ssubranges_calloc`, `REG_BOUNDS_MAX_FAILURE_CNT`, `REG_BOUNDS_RAND_CASE_CNT`, `REG_BOUNDS_RAND_SEED`, `gen_ranges`, `parse_env_vars`.
