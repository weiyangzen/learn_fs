# sources/distributed-fs/ceph-client/arch/arm64/net/bpf_timed_may_goto.S

## Purpose

provides the arm64 assembly implementation of arch_bpf_timed_may_goto(), a helper target emitted by
the BPF verifier for bounded timed loop continuation

## Important APIs, Types, and Functions

Source read size: 40 lines, 1150 bytes. Includes: `linux/linkage.h`. Assembly/global entries:
`arch_bpf_timed_may_goto`.

## Control Flow and Behavior

the routine uses the BPF custom convention with BPF_REG_AX in x9, reads the virtual counter,
compares elapsed time against the supplied budget, and returns whether execution may branch to the
loop target

## State and Persistence

it keeps no persistent state and only consumes architectural counter state at runtime

## Dependencies and Integration Points

integrates with arm64 BPF JIT helper-call lowering and the generic verifier's timed may-goto
transformation

## Risks and Test Signals

the custom register convention and counter arithmetic must match bpf_jit_comp.c; BPF verifier/JIT
selftests that exercise timed loops are the main signal
