# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_may_goto_2.c

## Purpose
This small companion file covers C-level use of the experimental `can_loop` condition, which lowers to may-goto style verifier control flow.

## Important APIs, Types, And Functions
It includes `bpf_experimental.h`, declares global `gvar`, and defines a raw tracepoint C program `may_goto_c_code`.

## Control Flow
The program runs three bounded `for (i = 0; i < 3 && can_loop; i++)` loops: one zeroes a local stack array, one fills it from `gvar - i`, and one accumulates values back into `gvar`.

## State And Persistence
The global `gvar` persists as BPF global data for the object, while stack array `tmp[3]` is per invocation. Verifier state covers bounded stack indexing, may-goto lowering from `can_loop`, and loop progress.

## Dependencies And Integration Points
It depends on the BPF ISA and verifier support for may-goto instructions and is consumed by the same selftest harness as the other verifier programs.

## Risks
Small may-goto tests are important because parser or codegen regressions can otherwise be hidden by larger suites. Misvalidation here would indicate a control-flow soundness issue.

## Test Signals
The expected signal is `__success` for the raw tracepoint C program.
