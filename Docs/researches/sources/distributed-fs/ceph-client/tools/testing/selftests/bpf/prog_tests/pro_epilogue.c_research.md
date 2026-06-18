# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pro_epilogue.c

## Purpose
Exercises BPF prologue/epilogue generation paths for struct_ops, tail calls, gotos to start, exits, and kfunc use. The source was read as a complete 63-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_tailcall()`, `test_pro_epilogue()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "pro_epilogue.skel.h"`, `#include "epilogue_tailcall.skel.h"`, `#include "pro_epilogue_goto_start.skel.h"`, `#include "epilogue_exit.skel.h"`, `#include "pro_epilogue_with_kfunc.skel.h"`.
- Generated skeletons/objects referenced: `bpf_map`, `epilogue_exit`, `epilogue_tailcall`, `pro_epilogue`, `pro_epilogue_goto_start`, `pro_epilogue_with_kfunc`.
- Primary APIs and types: Skeletons `pro_epilogue`, `epilogue_tailcall`, `pro_epilogue_goto_start`, `epilogue_exit`, `pro_epilogue_with_kfunc`, `bpf_map_update_elem()`, `bpf_prog_test_run_opts()`, and struct_ops attach helpers.

## Control Flow
The tailcall subtest loads `epilogue_tailcall`, attaches struct_ops, updates a prog-array map, runs a program with test-run options, and checks argument/result mutations. Other subtests are selected through skeleton load/run macros for verifier/codegen coverage.

## State and Persistence Behavior
State includes prog-array entries, struct_ops links, and BPF-side argument/result globals. Cleanup is skeleton/link destruction.

## Dependencies and Integration Points
Requires generated skeletons, BPF struct_ops, tail-call map support, and kfunc availability for the relevant variant.

## Risks and Edge Cases
Feature-gated kernels may skip or fail kfunc/struct_ops pieces; tail-call map setup must match program fds exactly.

## Test Signals
Assertions check skeleton load, struct_ops attach, prog test run, argument value, and returned retval. Named assertion/check labels observed in the source include: `epilogue_tailcall__open_and_load`, `attach_struct_ops`, `bpf_prog_test_run_opts`, `args.a`, `topts.retval`.
