<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest.cc -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest.cc

## Purpose
Main executable entry point for crcutil functionality and performance tests. It registers a matrix of CRC implementations and widths, then runs correctness checks before optional cycle-per-byte benchmarks.

## Important APIs, Types, and Functions
Defines `main(int argc, char **argv)`, conditionally detects GCC AMD64 `uint128_t`, declares `SetHiPri()`, and uses `CrcVerifier`, `CreateTest`, and `CrcVerifierFactory` from `unittest.h`. Command-line flags are `--canonical`, `--noperf`, `--perfall`, and `help`.

## Control Flow, State, and Persistence
Startup parses flags into `test_perf_main`, `test_perf_all`, and `canonical`, calls `SetHiPri`, then registers tests for 64-bit, 32-bit, 15-bit, 7-bit, SSE2 128/64/32-bit, compiler-native 128-bit, and multiple-stride generic variants. Performance defaults focus on main 32/64/128 cases; `--perfall` broadens smaller and alternate word/table combinations, while `--noperf` disables performance runs. State is in a stack `CrcVerifier`; no external persistence occurs beyond stdout/stderr reports.

## Dependencies and Integration Points
Depends on all crcutil generic/SSE/rolling CRC headers, platform feature macros, and `set_hi_pri.c`. It is the validation binary for the vendored crcutil implementation embedded under LizardFS.

## Risks and Test Signals
Risks include long runtime and high CPU/memory usage from performance tests, feature-macro mismatches for SSE2/int128 paths, `--canonical` only affecting factory-created tests that consume the flag, and exit status remaining success unless `CHECK` aborts. Test signals are successful completion with `--noperf`, expected help output, functional coverage across raw/canonical variants, performance CSV output when enabled, and conditional compilation on 32-bit, 64-bit, SSE2, and non-x86 targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest.cc -->
