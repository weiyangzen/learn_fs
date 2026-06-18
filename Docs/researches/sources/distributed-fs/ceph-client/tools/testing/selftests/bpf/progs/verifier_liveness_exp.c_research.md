# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_liveness_exp.c

## Purpose
This file is a targeted complexity regression test for exponential behavior in verifier subprogram liveness analysis. It constructs a valid BPF call graph whose liveness recursion would explode without complexity limits.

## Important APIs, Types, And Functions
It uses macros `C(fn, off)` and `CALLS_50(fn)` to generate repeated inline assembly calls with distinct frame-pointer-derived arguments. Static naked subprograms `exp_sub1` through `exp_sub7` form an eight-frame chain, and `liveness_exponential_complexity` is the raw tracepoint entry.

## Control Flow
Each non-leaf subprogram calls the next subprogram fifty times, changing `r1` to a different `r10 - offset` value at each call site. The entry repeats this pattern for `exp_sub1`, producing a theoretical branching factor of 50 across seven recursive levels.

## State And Persistence
There is no runtime state. The important state is verifier `arg_track` identity, callsite/depth instance tracking, and complexity accounting during `analyze_subprog()`.

## Dependencies And Integration Points
It depends on `bpf_misc.h` annotations and the raw tracepoint selftest loader. It integrates directly with verifier complexity guards for liveness analysis.

## Risks
Without bounded analysis or effective caching, this test can cause CPU soft lockups or memory exhaustion. It is intentionally valid BPF, so a simple verifier rejection for structural invalidity would be a regression.

## Test Signals
The expected result is failure with log level 2 and message `liveness analysis exceeded complexity limit`.
