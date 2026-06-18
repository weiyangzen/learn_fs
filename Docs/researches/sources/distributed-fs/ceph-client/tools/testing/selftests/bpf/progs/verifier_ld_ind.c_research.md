# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ld_ind.c

## Purpose

`verifier_ld_ind.c` tests classic packet load instructions `LD_ABS` and `LD_IND`, including calling convention constraints, subprogram early-exit behavior on load failure, and rejection of void-returning subprograms that use these instructions.

## Important APIs, Types, and Functions

The file includes `filter.h` and uses `bpf_gen_ld_abs` for classic load instruction generation. It defines 12 socket programs and several naked subprograms. Expected diagnostics include unreadable registers `R1` through `R5`, `R9 !read_ok`, and `LD_ABS is only allowed in functions that return 'int'`.

## Control Flow

The calling-convention tests arrange register liveness around `LD_IND` and verify that only allowed registers remain readable after the instruction sequence. Subprogram tests call helpers that perform `LD_ABS` or `LD_IND`, then either require early exit on failure or prove both paths safe. Void-return subprograms deliberately violate the rule that classic packet load instructions may only appear in int-returning functions.

## State and Persistence Behavior

There are no maps. Runtime state is packet data accessed by classic load instructions. Verifier state tracks register invalidation/readability after `LD_ABS/LD_IND`, subprogram return type, and failure propagation.

## Dependencies and Integration Points

The file integrates with socket filter program semantics, classic BPF packet load translation, verifier register liveness rules, and subprogram validation.

## Risks and Test Signals

Risks include allowing stale registers after packet loads, failing to enforce early-exit requirements, or accepting classic loads in void subprograms. Test signals are the expected failures for unreadable registers and void returns, plus successes for safe subprogram paths.
