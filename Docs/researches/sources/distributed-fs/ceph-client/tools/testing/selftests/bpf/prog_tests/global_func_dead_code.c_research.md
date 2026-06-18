
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_func_dead_code.c

## Purpose

`global_func_dead_code.c` verifies that freplace can target a live global subprogram but cannot target a global subprogram eliminated as dead code.

## Important APIs, Types, and Functions

The test uses `verifier_global_subprogs.skel.h`, `freplace_dead_global_func.skel.h`, `bpf_program__set_autoload()`, `bpf_program__set_attach_target()`, `bpf_program__set_log_buf()`, and skeleton load calls.

## Control Flow and Data Flow

It loads the target skeleton with `chained_global_func_calls_success`, gets its FD, loads a freplace program targeting `global_good` and expects success, then opens another freplace skeleton targeting `global_dead`, captures verifier log, and expects load failure containing a missing-subprogram message.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the loaded target program and verifier log buffer. Dependencies include freplace, global function metadata, and dead-code elimination behavior. Integration is attach-target symbol resolution after verifier/linker optimization. Risks are verifier log wording drift and target BPF object changes. Test signals are successful live target replacement and failed dead target load with `Subprog global_dead doesn't exist`.
